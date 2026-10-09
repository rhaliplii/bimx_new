"""SEO pe adresa publică (SITE_URL = https://bimx.md/): canonical, hreflang, robots.txt, sitemap.xml, .htaccess și 404.html.

Ultimul pas al build-ului, peste paginile terminate:
- fiecare pagină are un singur canonical cu adresă completă, iar paginile indexabile au hreflang (ro, en, uk, ru,
  x-default) spre variantele lor indexabile – aceleași adrese ca în og:url și în sitemap;
- linkurile interne „…/index.html” devin „…/”: o singură adresă pe pagină (.htaccess redirecționează restul);
- noindex pe paginile „în pregătire” (bx-prep) și pe autentificare (formularul nu trimite nimic); ies și din sitemap;
- prima pagină: titlul complet și datele organizației (JSON-LD);
- redirecționările meta (rutele vechi) au canonical spre pagina finală și 301 în .htaccess;
- robots.txt, sitemap.xml cu variantele de limbă, .htaccess și pagina 404.html (cu adrese de la rădăcină).

Copia de test (GitHub Pages, config.TEST_COPY): noindex, nofollow pe toate paginile, robots.txt Disallow: /, fără sitemap.
"""
import html
import json
import posixpath
import re
from pathlib import PurePosixPath
from urllib.parse import quote

from .config import DIST, LANG_PREFIX, LOCALES, SITE_LANGS, SITE_URL, TEST_COPY, lang_of
from .fixes import FACEBOOK, LINKEDIN

SKIP = ("assets", "wp-content", "wp-includes")
NOINDEX_KEYS = {"autentificare"}          # formularul de autentificare nu funcționează pe site-ul static
REFRESH = re.compile(r'<meta http-equiv="refresh" content="0; url=([^"]*)">')
ROBOTS = re.compile(r'\s*<meta name=["\']robots["\'][^>]*>')
HEAD_LINKS = re.compile(r'\s*<link\b[^>]*\brel=["\'](?:canonical|alternate|shortlink)["\'][^>]*>')
# link local spre „…/index.html” (nu http:, mailto:, //…), în href și în valorile selectorului de taburi (replica.js)
INDEX_LINK = re.compile(r'((?:\shref|<option value)=")(?!//)([^"#?:]*/)?index\.html(?=[#?"])')
REFRESH_INDEX = re.compile(r'(http-equiv="refresh" content="0; url=)([^"#?:]*/)?index\.html')
SEARCH_INDEX = re.compile(r'("u":")([^"]*/)?index\.html"')


def url_of(rel):
    """Adresa publică a unui fișier din dist/: „en/identitate/index.html” → „https://bimx.md/en/identitate/”."""
    return SITE_URL + quote(PurePosixPath(rel).as_posix().removesuffix("index.html"))


def local_dir_links(text):
    """„identitate/index.html#x” → „identitate/#x”, „index.html” → „./”."""
    text = INDEX_LINK.sub(lambda m: m.group(1) + (m.group(2) or "./"), text)
    return REFRESH_INDEX.sub(lambda m: m.group(1) + (m.group(2) or "./"), text)


def _inner(rel):
    lang = lang_of(rel.parts)
    return lang, PurePosixPath(*(rel.parts[1:] if lang != "ro" else rel.parts))


def _kind(text, rel):
    head = text[:text.find("</head>")]
    if REFRESH.search(head):
        return "redirect"
    _, inner = _inner(rel)
    if (TEST_COPY or any("noindex" in m for m in ROBOTS.findall(head))
            or 'class="bx-prep"' in text or inner.parts[0] in NOINDEX_KEYS):
        return "noindex"
    return "page"


def _alternates(rel, kinds):
    """hreflang: variantele indexabile ale aceleiași pagini (cel puțin două), plus x-default = româna."""
    _, inner = _inner(rel)
    alts = {}
    for x in SITE_LANGS:
        other = PurePosixPath(LANG_PREFIX[x]) / inner
        if kinds.get(other) == "page":
            alts[x] = url_of(other)
    if len(alts) < 2:
        return {}
    if "ro" in alts:
        alts["x-default"] = alts["ro"]
    return alts


def _organization(text, lang):
    """Datele organizației (schema.org) pe prima pagină: numele din og:title, adresa și rețelele din subsol."""
    og = re.search(r'<meta property="og:title" content="([^"]*)"', text)
    name = html.unescape(og.group(1)).removesuffix(" (BIMx)") if og else "BIMx"
    org = SITE_URL + "#organization"
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": org, "name": name, "alternateName": "BIMx", "url": SITE_URL,
         "logo": SITE_URL + "assets/img/bimx-logo.svg", "email": "office@bimx.md",
         "address": {"@type": "PostalAddress", "streetAddress": "str. Vlaicu Pârcălab 63", "postalCode": "MD-2012",
                     "addressLocality": "Chișinău", "addressCountry": "MD"},
         "sameAs": [LINKEDIN, FACEBOOK]},
        {"@type": "WebSite", "@id": SITE_URL + "#website", "name": "BIMx", "url": SITE_URL,
         "inLanguage": LOCALES[lang][0], "publisher": {"@id": org}}]}
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


def _page_head(text, rel, kind, alts):
    lang, inner = _inner(rel)
    end = text.find("</head>")
    head = HEAD_LINKS.sub("", ROBOTS.sub("", text[:end]))
    tags = [f'<link rel="canonical" href="{url_of(rel)}">']
    tags += [f'<link rel="alternate" hreflang="{x}" href="{u}">' for x, u in alts.items()]
    robots = "noindex, nofollow" if TEST_COPY else "noindex, follow" if kind == "noindex" else "max-image-preview:large"
    tags.append(f'<meta name="robots" content="{robots}">')
    if inner == PurePosixPath("index.html"):
        # titlul primei pagini: numele complet al bursei (ca în og:title), nu doar „BIMx”
        og = re.search(r'<meta property="og:title" content="([^"]*)"', head)
        if og:
            head = re.sub(r"<title>BIMx</title>", lambda m: f"<title>{og.group(1)}</title>", head, count=1)
        tags.append(_organization(head, lang))
    return head.rstrip() + "\n" + "\n".join(tags) + "\n" + text[end:]


def _redirect_target(rel, text):
    """Ținta unei redirecționări meta: (calea de la rădăcină, fragmentul)."""
    url = REFRESH.search(text).group(1)
    path, _, frag = url.partition("#")
    path = posixpath.normpath(posixpath.join(posixpath.dirname(rel.as_posix()), path))
    path = "" if path == "." else path.removesuffix("index.html").rstrip("/")
    return (path + "/" if path else ""), frag


def _redirect_head(text, rel):
    path, _ = _redirect_target(rel, text)
    text = HEAD_LINKS.sub("", text)
    return text.replace("</title>", f'</title><link rel="canonical" href="{SITE_URL + quote(path)}">', 1)


def _apache(s):
    return re.sub(r"([.^$*+?()\[\]{}|\\-])", r"\\\1", s)


def write_htaccess(redirects):
    """301 în locul redirecționărilor meta, „…/index.html” → „…/”, sitemap-urile WordPress → sitemap.xml, pagina 404."""
    # „/stiri”, „/stiri/” și „/stiri/index.html” → un singur 301, fără pasul intermediar al slash-ului final
    rules = [f"RewriteRule ^{_apache(src.rstrip('/'))}(?:/(?:index\\.html)?)?$ /{dst}{'#' + frag if frag else ''} [R=301,L,NE]"
             for src, dst, frag in sorted(redirects)]
    (DIST / ".htaccess").write_text(
        "# bimx.md – site static generat de tools/build.py (sitegen/seo.py). Nu se editează pe server.\n"
        "# HTTPS și www → bimx.md sunt setate în panoul găzduirii, nu aici.\n"
        "DirectoryIndex index.html\n"
        "ErrorDocument 404 /404.html\n\n"
        "<IfModule mod_rewrite.c>\n"
        "RewriteEngine On\n"
        "RewriteBase /\n\n"
        "# rutele vechi, unite cu alte pagini (aceleași ca paginile cu redirecționare meta din dist/)\n"
        + "\n".join(rules) + "\n\n"
        "# sitemap-urile vechi WordPress\n"
        "RewriteRule ^(?:wp-sitemap[^/]*|sitemap_index)\\.xml$ /sitemap.xml [R=301,L]\n\n"
        "# o singură adresă pe pagină: /pagina/index.html → /pagina/\n"
        "RewriteCond %{THE_REQUEST} \\s/+((?:[^?\\s]*/)?)index\\.html[?\\s]\n"
        "RewriteRule ^ /%1 [R=301,L,NE]\n"
        "</IfModule>\n", encoding="utf-8")


def write_sitemap(entries):
    rows = []
    for loc, alts in entries:
        links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{x}" href="{html.escape(u)}"/>' for x, u in alts.items())
        rows.append(f"  <url>\n    <loc>{html.escape(loc)}</loc>{links}\n  </url>")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


def write_robots():
    text = "User-agent: *\nDisallow: /\n" if TEST_COPY else f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"
    (DIST / "robots.txt").write_text(text, encoding="utf-8")


NOT_FOUND = {
    "ro": ("Pagina nu a fost găsită", "Adresa nu există sau pagina a fost mutată. Folosiți meniul sau căutarea "
           "ori reveniți la prima pagină.", "Prima pagină"),
    "en": ("Page not found", "Go to the home page"),
    "uk": ("Сторінку не знайдено", "Перейти на головну"),
    "ru": ("Страница не найдена", "Перейти на главную"),
}
ROOT_ATTR = re.compile(r'(\s(?:href|src|data-src|data-full|action|data-root)=)(["\'])(.*?)\2')
ROOT_SRCSET = re.compile(r'(\ssrcset=)(["\'])(.*?)\2')
EXTERNAL = ("#", "/", "http:", "https:", "mailto:", "tel:", "data:", "javascript:", "{")


def _from_root(url):
    if url.startswith(EXTERNAL):
        return url
    return "/" + url.removeprefix("./")


def _drop_div(text, marker):
    """Scoate elementul <div> care începe cu marker (cu tot conținutul, numărând div-urile imbricate)."""
    start = text.find(marker)
    if start < 0:
        return text
    depth, pos = 0, start
    for m in re.compile(r"<div\b|</div>").finditer(text, start):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            pos = m.end()
            break
    return text[:start] + text[pos:]


def write_404():
    """404.html din prima pagină (RO): antetul și subsolul site-ului, adrese de la rădăcină (servită la orice adresă)."""
    text = (DIST / "index.html").read_text(encoding="utf-8")
    title, lead, home = NOT_FOUND["ro"]
    others = "".join(f'<li lang="{x}"><a href="/{LANG_PREFIX[x]}">{NOT_FOUND[x][0]} – {NOT_FOUND[x][1]}</a></li>'
                     for x in SITE_LANGS if x != "ro")
    main = (f'<main id="main" class="site-main"><div class="container bx-404">'
            f'<p class="bx-404-code" aria-hidden="true">404</p><h1>{title}</h1><p>{lead}</p>'
            f'<p><a class="bx-btn-primary" href="./">{home}</a></p><ul class="bx-404-langs">{others}</ul></div></main>')
    text = re.sub(r'<main id="main"[^>]*>[\s\S]*?</main>', lambda m: main, text, count=1)
    # avertizarea despre datele de piață nu are rost aici: fără fereastră și fără scriptul ei (ar da eroare fără fereastră)
    text = _drop_div(text, '<div class="ds-popup" id="ds-popup-1"')
    text = re.sub(r'<script id="popup-box-js(?:-extra)?"[^>]*>[\s\S]*?</script>\s*', "", text)
    end = text.find("</head>")
    head = HEAD_LINKS.sub("", ROBOTS.sub("", text[:end]))
    head = re.sub(r'\s*<meta (?:property="og:[^"]*"|name="twitter:[^"]*"|name="description")[^>]*>', "", head)
    head = re.sub(r'\s*<script type="application/ld\+json">[\s\S]*?</script>', "", head)
    head = re.sub(r"<title>[^<]*</title>", f"<title>{title} – BIMx</title>", head, count=1)
    style = ("<style>.bx-404{padding:72px 16px 96px;text-align:center}.bx-404-code{margin:0;font-size:72px;font-weight:700;"
             "line-height:1;color:var(--bx-navy,#141A3D)}.bx-404 h1{margin:16px 0 12px;font-size:32px;line-height:40px;font-weight:700;"
             "color:var(--bx-navy,#141A3D)}.bx-404>p{max-width:560px;margin:0 auto 24px}"
             ".bx-404-langs{list-style:none;margin:32px 0 0;padding:0;display:grid;gap:8px}</style>")
    text = head.rstrip() + '\n<meta name="robots" content="noindex">\n' + style + "\n" + text[end:]
    text = ROOT_ATTR.sub(lambda m: m.group(1) + m.group(2) + _from_root(m.group(3)) + m.group(2), text)
    text = ROOT_SRCSET.sub(lambda m: m.group(1) + m.group(2) + ", ".join(
        " ".join([_from_root(p.split()[0])] + p.split()[1:]) for p in m.group(3).split(",") if p.strip()) + m.group(2), text)
    (DIST / "404.html").write_text(text, encoding="utf-8")


def apply_seo():
    files = [f for f in sorted(DIST.rglob("*.html")) if f.relative_to(DIST).parts[0] not in SKIP]
    texts = {PurePosixPath(f.relative_to(DIST).as_posix()): f.read_text(encoding="utf-8", errors="replace") for f in files}
    kinds = {rel: _kind(text, rel) for rel, text in texts.items()}
    redirects, sitemap = [], []
    for rel, text in texts.items():
        if kinds[rel] == "redirect":
            new = _redirect_head(text, rel)
            dst, frag = _redirect_target(rel, text)
            redirects.append((rel.as_posix().removesuffix("index.html"), dst, frag))
        else:
            alts = _alternates(rel, kinds) if kinds[rel] == "page" else {}
            new = _page_head(text, rel, kinds[rel], alts)
            if kinds[rel] == "page":
                sitemap.append((url_of(rel), alts))
        new = local_dir_links(new)
        if new != text:
            (DIST / rel).write_text(new, encoding="utf-8")
    for f in (DIST / "assets" / "search").glob("*.js"):
        f.write_text(SEARCH_INDEX.sub(lambda m: m.group(1) + (m.group(2) or "./") + '"', f.read_text(encoding="utf-8")),
                     encoding="utf-8")
    order = {x: i for i, x in enumerate(SITE_LANGS)}
    sitemap.sort(key=lambda e: (order[lang_of(PurePosixPath(e[0].removeprefix(SITE_URL)).parts)], e[0]))
    if TEST_COPY:
        (DIST / "sitemap.xml").unlink(missing_ok=True)
    else:
        write_sitemap(sitemap)
    write_robots()
    write_htaccess(redirects)
    write_404()
    return {k: list(kinds.values()).count(k) for k in ("page", "noindex", "redirect")}, len(sitemap), len(redirects)
