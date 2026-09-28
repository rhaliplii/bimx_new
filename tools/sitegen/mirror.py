"""Copia bimx.md: paginile RO din src/bimx-mirror/ro/ → dist/ și, traduse cu cataloagele i18n/{en,ru,uk}.json,
→ dist/en/, dist/ru/ și dist/uk/.

bimx.md nu are alte versiuni de limbă (doar o pagină /en/home/ provizorie), așa că fiecare pagină EN și RU se
generează din pagina RO corespunzătoare: aceleași căi (dist/X ↔ dist/en/X ↔ dist/ru/X ↔ dist/uk/X), texte din catalog, linkuri
spre paginile din aceeași limbă și lang="en-GB" / "ru-RU". Resursele (wp-content, wp-includes) sunt comune.
"""
import json
import os
import re
import shutil
from pathlib import Path

from . import translate
from .config import ACADEMY_REDIRECTS, BIMX, DIST, LANG_PREFIX, LANGS, LOCALES, MIRROR, SITE_LANGS, lang_of
from .util import relto

LINK_ATTR = re.compile(r'\s(href|src|srcset|data-src|poster)=(["\'])([^"\']*)\2')
CSS_URL = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")
RO_PAGES = MIRROR / "ro"


def catalog_file(lang):
    return MIRROR / "i18n" / f"{lang}.json"


def load_catalog(lang):
    f = catalog_file(lang)
    if not f.exists():
        return {"text": {}, "js": {}}
    data = json.loads(f.read_text(encoding="utf-8"))
    return {"text": data.get("text", {}), "js": data.get("js", {})}


def page_dest(rest, lang):
    """Calea din dist/ a paginii `rest` (relativă la ro/) în limba dată."""
    return DIST / LANG_PREFIX[lang] / rest


def academy_target(site_file):
    """Dacă ținta e o pagină bimx.md înlocuită de Academy, întoarce indexul Academy în limba ei + ancora."""
    try:
        parts = site_file.relative_to(DIST).parts
    except ValueError:
        return None
    lang = lang_of(parts)
    parts = parts[1:] if lang != "ro" else parts
    if len(parts) == 2 and parts[1] == "index.html" and parts[0] in ACADEMY_REDIRECTS:
        return LANGS[lang]["out"] / "index.html", ACADEMY_REDIRECTS[parts[0]]
    return None


def rewrite_links(text, src, dest, lang):
    """Rebazează căile relative (href, src, srcset, data-src, poster, url()) pentru pagina scrisă în dest."""
    def move(val):
        if not val or val.startswith(("#", "http:", "https:", "//", "mailto:", "tel:", "javascript:", "data:")):
            return val
        path, _, frag = val.partition("#")
        if not path:
            return val
        target = Path(os.path.normpath(src.parent / path))
        try:
            rest = target.relative_to(RO_PAGES)
        except ValueError:
            try:
                target.relative_to(MIRROR / "en")        # vechiul link spre /en/home/ din selectorul de limbă
            except ValueError:
                return val
            rest = Path("en")
        if rest.parts[:1] == ("en",):
            site_target = DIST / "en" / "index.html"
        elif target.suffix == ".html":                     # pagină: în limba paginii curente
            site_target = page_dest(rest, lang)
        else:                                              # resursă comună
            site_target = DIST / rest
        mapped = academy_target(site_target)
        if mapped:
            site_target, anchor = mapped
            frag = anchor[1:]
        return relto(site_target, dest.parent) + (f"#{frag}" if frag else "")

    def attr(m):
        name, q, val = m.groups()
        if name == "srcset":
            val = ", ".join(" ".join([move(c.split(" ")[0])] + c.split(" ")[1:])
                            for c in (x.strip() for x in val.split(",")) if c)
        else:
            val = move(val)
        return f" {name}={q}{val}{q}"

    text = LINK_ATTR.sub(attr, text)
    return CSS_URL.sub(lambda m: f"url({m.group(1)}{move(m.group(2))}{m.group(1)})", text)


def set_language(text, rest, dest, lang):
    """lang/og:locale, selectorul RO/EN spre aceeași pagină și limba marcată ca activă (selectorul final: chrome.py)."""
    html_lang, og_locale = LOCALES[lang]
    text = re.sub(r'(<html[^>]*\slang=")[^"]*"', rf'\g<1>{html_lang}"', text, count=1)
    text = re.sub(r'(property="og:locale"\s+content=")[^"]*"', rf'\g<1>{og_locale}"', text)
    ro, en = relto(page_dest(rest, "ro"), dest.parent), relto(page_dest(rest, "en"), dest.parent)
    text = re.sub(r'href="[^"]*"(\s+lang="ro-RO"\s+hreflang="ro-RO")', lambda m: f'href="{ro}"{m.group(1)}', text)
    text = re.sub(r'href="[^"]*"(\s+lang="en-GB"\s+hreflang="en-GB")', lambda m: f'href="{en}"{m.group(1)}', text)

    def classes(m):
        cls = m.group(2).replace(" current-lang", "").replace(" no-translation", "")
        if f"lang-item-{lang}" in cls:
            cls = cls.replace(f"lang-item-{lang}", f"lang-item-{lang} current-lang")
        return f'{m.group(1)}{cls}"'
    text = re.sub(r'(<li\b[^>]*class=")([^"]*\blang-item-(?:ro|en)\b[^"]*)"', classes, text)
    if lang != "ro":
        text = text.replace('<a href="#pll_switcher">RO</a>', f'<a href="#pll_switcher">{lang.upper()}</a>')
    return text


def translate_js(text, js):
    for ro, en in js.items():
        text = text.replace(ro, en)
    return text


def write_js_translations(js, lang):
    """Copii .<lang>.js ale scripturilor temei care conțin texte românești; întoarce {cale RO: cale tradusă}."""
    out = {}
    if not js:
        return out
    for f in sorted((DIST / "wp-content" / "themes").rglob("*.js")):
        if re.search(r"\.(%s)\.js$" % "|".join(SITE_LANGS[1:]), f.name):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        new = translate_js(text, js)
        if new != text:
            dest = f.with_name(f"{f.stem}.{lang}.js")
            dest.write_text(new, encoding="utf-8")
            out[f] = dest
    return out


def redirect(dest, target, lang):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={target}"><title>BIMx</title></head>'
        f'<body><a href="{target}">BIMx</a></body></html>\n', encoding="utf-8")


def build_snapshot():
    """Copiază resursele, scrie paginile în toate limbile; întoarce (pagini, {limbă: texte netraduse})."""
    if not RO_PAGES.exists():
        raise SystemExit("Lipsește src/bimx-mirror/ro/ (rulați tools/mirror_bimx.py)")
    for src in sorted((MIRROR / "shared").rglob("*")):
        if src.is_file() and src.name != ".DS_Store":
            dest = DIST / src.relative_to(MIRROR / "shared")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    catalogs = {lang: load_catalog(lang) for lang in SITE_LANGS if lang != "ro"}
    js_files = {lang: write_js_translations(cat["js"], lang) for lang, cat in catalogs.items()}
    pages, missing = 0, {lang: {} for lang in catalogs}
    for src in sorted(RO_PAGES.rglob("*.html")):
        rest = src.relative_to(RO_PAGES)
        original = src.read_text(encoding="utf-8", errors="replace")
        for lang in SITE_LANGS:
            dest = page_dest(rest, lang)
            dest.parent.mkdir(parents=True, exist_ok=True)
            text = original
            if lang != "ro":
                cat = catalogs[lang]
                text, miss = translate.apply(text, cat["text"])
                for key in miss:
                    missing[lang].setdefault(key, str(rest))
                text = re.sub(r"(<script(?![^>]*\bsrc=)[^>]*>)([\s\S]*?)(</script>)",
                              lambda m, js=cat["js"]: m.group(1) + translate_js(m.group(2), js) + m.group(3), text)
            text = rewrite_links(text, src, dest, lang)
            text = set_language(text, rest, dest, lang)
            if lang != "ro":
                for ro_js, tr_js in js_files[lang].items():
                    text = text.replace(f'"{relto(ro_js, dest.parent)}', f'"{relto(tr_js, dest.parent)}')
                    text = text.replace(f"'{relto(ro_js, dest.parent)}", f"'{relto(tr_js, dest.parent)}")
            dest.write_text(text, encoding="utf-8")
            pages += 1

    # paginile bimx.md înlocuite de Academy devin redirecționări; /en/home/ (adresa veche EN) → /en/
    for lang in SITE_LANGS:
        for page, anchor in ACADEMY_REDIRECTS.items():
            dest = page_dest(Path(page) / "index.html", lang)
            redirect(dest, relto(LANGS[lang]["out"] / "index.html", dest.parent) + anchor, lang)
    redirect(DIST / "en" / "home" / "index.html", "../index.html", "en")
    return pages, missing


def localize_links(folder, lang):
    """În paginile Academy, linkurile https://bimx.md/... devin linkuri către copia locală în aceeași limbă."""
    def fix(m, here):
        attr, q, url = m.groups()
        path = url[len(BIMX):].split("#")[0].split("?")[0]
        if not path.startswith("/"):
            return m.group(0)
        if path in ("/en", "/en/", "/en/home/"):
            path = "/en/"
        prefixes = tuple(f"/{x}/" for x in SITE_LANGS[1:])
        if lang != "ro" and not path.startswith(prefixes):
            path = f"/{lang}" + path
        elif lang not in ("ro", "en") and path.startswith("/en/"):
            path = f"/{lang}/" + path[4:]
        local = DIST / path.lstrip("/")
        if path.endswith("/") or not local.suffix:
            local = local / "index.html"
        mapped = academy_target(local)
        if mapped:
            local = mapped[0]
        if not local.exists():
            return m.group(0)
        return f"{attr}={q}{relto(local, here)}{q}"

    pattern = re.compile(r'(\s(?:href|src))=(["\'])(https://bimx\.md[^"\']*)\2')
    for f in folder.rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        new = pattern.sub(lambda m: fix(m, f.parent), text)
        if new != text:
            f.write_text(new, encoding="utf-8")
