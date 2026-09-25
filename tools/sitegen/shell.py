"""Antetul și subsolul reale bimx.md, preluate din copia locală și aplicate paginilor Academy."""
import os
import re
from pathlib import Path

from .config import ACADEMY_ASSETS, ACADEMY_SRC, DIST, LANG_PREFIX, SITE_LANGS
from .util import relto

SCOPE = ".bx-academy"
SHELL_SRC = {lang: DIST / LANG_PREFIX[lang] / "index.html" for lang in SITE_LANGS}
# Scripturile temei preluate în Academy; „main.” prinde și main.en.js / main.ru.js, variantele traduse.
THEME_SCRIPTS = ("jquery-3.7.0.min.js", "slick.js", "lightbox.js", "victor-child/assets/js/main.", "primary-navigation.js")
_SHELLS = {}


def rebase(fragment, from_dir, to_dir):
    """Recalculează căile relative dintr-un fragment HTML/CSS mutat din from_dir în to_dir."""
    def move(val):
        if not val or val.startswith(("#", "http:", "https:", "//", "mailto:", "tel:", "javascript:", "data:")):
            return val
        path, sep, frag = val.partition("#")
        target = Path(os.path.normpath(from_dir / path))
        return relto(target, to_dir) + (sep + frag if sep else "")

    def attr(m):
        name, q, val = m.groups()
        if name == "srcset":
            val = ", ".join(" ".join([move(x.split(" ")[0])] + x.split(" ")[1:]) for x in (v.strip() for v in val.split(",")) if x)
        else:
            val = move(val)
        return f" {name}={q}{val}{q}"

    fragment = re.sub(r'\s(href|src|srcset|data-src)=(["\'])([^"\']*)\2', attr, fragment)
    return re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", lambda m: f'url("{move(m.group(2))}")', fragment)


def load_shell(lang):
    if lang in _SHELLS:
        return _SHELLS[lang]
    src = SHELL_SRC[lang]
    text = src.read_text(encoding="utf-8", errors="replace")
    head = text[:text.find("</head>")]
    styles = re.findall(r"<link[^>]*rel=['\"]stylesheet['\"][^>]*>|<style[^>]*>[\s\S]*?</style>", head)
    scripts = [m.group(0) for m in re.finditer(r"<script[^>]*src=['\"]([^'\"]+)['\"][^>]*>\s*</script>", head)
               if any(k in m.group(1) for k in THEME_SCRIPTS)]
    h0 = text.find("<header"); h1 = text.find("</header>", h0) + len("</header>")
    f0 = text.find("<footer"); f1 = text.find("</footer>", f0) + len("</footer>")
    header, footer = text[h0:h1], text[f0:f1]
    # Pe prima pagină WordPress pune logo-ul într-un <span> (ești deja acasă); în Academy devine link spre ea.
    header = re.sub(r'<span class="custom-logo-link">(<img\b[^>]*?)alt=""([^>]*>)</span>',
                    r'<a href="index.html" class="custom-logo-link" rel="home">\1alt="BIMx"\2</a>', header)
    # „BIMX ACADEMY” devine elementul curent din meniu
    header = re.sub(r'(<li[^>]*class=")([^"]*)("[^>]*>\s*<a[^>]*>\s*BIMX ACADEMY)',
                    lambda m: m.group(1) + m.group(2) + " current-menu-item current-menu-ancestor" + m.group(3), header, flags=re.I)
    if 'id="newsletter"' not in footer:
        footer = footer.replace('<div class="newsletter"', '<div class="newsletter" id="newsletter"', 1)
    _SHELLS[lang] = {"dir": src.parent, "head": "\n".join(styles), "scripts": "\n".join(scripts),
                     "header": header, "footer": footer}
    return _SHELLS[lang]


def shell_parts(lang, page_dir, switch):
    sh = load_shell(lang)
    parts = {k: rebase(sh[k], sh["dir"], page_dir) for k in ("head", "scripts", "header", "footer")}
    ro, en = switch[:2]
    for k in ("header", "footer"):
        parts[k] = re.sub(r'href="[^"]*"(\s+lang="ro-RO"\s+hreflang="ro-RO")', lambda m: f'href="{ro}"{m.group(1)}', parts[k])
        parts[k] = re.sub(r'href="[^"]*"(\s+lang="en-GB"\s+hreflang="en-GB")', lambda m: f'href="{en}"{m.group(1)}', parts[k])
    return parts


def scope_css(css, in_print=False):
    """Limitează stilurile Academy la <main class="bx-academy">, ca să nu atingă antetul și subsolul bimx.md."""
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    out, i = [], 0
    while True:
        j = css.find("{", i)
        if j < 0:
            out.append(css[i:])
            break
        head = css[i:j].strip()
        depth, k = 1, j + 1
        while depth and k < len(css):
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        body = css[j + 1:k - 1]
        if head.startswith("@media") or head.startswith("@supports"):
            out.append(f"{head} {{{scope_css(body, in_print or 'print' in head)}}}\n")
        elif head.startswith("@"):
            out.append(f"{head} {{{body}}}\n")
        else:
            sels = []
            for sel in head.split(","):
                sel = sel.strip()
                if sel in (":root", "body"):
                    sels.append(SCOPE)
                elif sel.startswith("html"):
                    sels.append(sel)
                elif in_print and sel.startswith((".top_header", ".site-header", "footer")):
                    sels.append(sel)
                else:
                    sels.append(f"{SCOPE} {sel}")
            out.append(f"{', '.join(sels)} {{{body}}}\n")
        i = k
    return "".join(out)


SHELL_CSS = f"""
/* Integrare în antetul bimx.md */
{SCOPE} {{ display: block; padding-bottom: 96px; }}  /* spațiul de deasupra subsolului bimx.md */
@media (max-width: 768px) {{ {SCOPE} {{ padding-bottom: 56px; }} }}
@media print {{ {SCOPE} {{ padding-bottom: 0; }} }}
{SCOPE} .read_progress {{ position: fixed; top: 0; left: 0; right: 0; bottom: auto; z-index: 1000; }}
"""


def write_scoped_css():
    for name in ("main.css", "academy.css"):
        src = ACADEMY_SRC / "assets" / "css" / name
        extra = SHELL_CSS if name == "academy.css" else ""
        (ACADEMY_ASSETS / "css" / name).write_text(scope_css(src.read_text(encoding="utf-8")) + extra, encoding="utf-8")

