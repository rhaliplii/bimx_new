"""Decuplează dist/ de serverul bimx.md: nicio pagină nu mai trimite, nu mai încarcă și nu mai partajează bimx.md.

- linkurile https://bimx.md/... spre pagini copiate devin linkuri relative locale (plus aliasurile din LINK_ALIASES);
- „Log In” / „Intra in cont” rămân, dar nu mai duc la bimx.md: replica.js afișează un mesaj (autentificarea
  există doar pe serverul bimx.md);
- <link> spre feed-uri, wp-json, xmlrpc și CSS-uri inexistente dispar, la fel scripturile emoji WordPress;
- formularele de newsletter și contact nu mai trimit nimic: replica.js afișează un mesaj; căutarea rulează local (search.py);
- butoanele de partajare folosesc adresa paginii curente, nu bimx.md;
- datele de piață (ticker, panou, top-uri, grafic) vin din snapshot-ul src/bimx-mirror/data/market.json.
"""
import json
import re
from pathlib import Path

from .config import DIST, SRC
from .util import relto

ORIGIN = re.compile(r"https?:(?:\\?/){2}(?:www\.)?bimx\.md")
REPLICA_JS = DIST / "assets" / "js" / "replica.js"
MARKET_JS = DIST / "assets" / "js" / "market-data.js"
SITE_CSS = DIST / "assets" / "css" / "site.css"
MARKET_DATA = SRC / "bimx-mirror" / "data" / "market.json"

# Linkuri de pe bimx.md care duc la pagini inexistente (404 și pe original), cu echivalentul local.
LINK_ALIASES = {
    "/calendar": "/trading-calendar/",
}

COMMENT = re.compile(r"<!--[\s\S]*?-->")
LINK_TAG = re.compile(r"<link\b[^>]*>\s*", re.I)
SCRIPT = re.compile(r"<script\b[^>]*>[\s\S]*?</script>\s*", re.I)
STYLE_OR_SCRIPT = re.compile(r"(<(script|style)\b[^>]*>)([\s\S]*?)(</\2>)", re.I)
LOGIN_HREF = re.compile(r'href="https://bimx\.md/(?:wp-login\.php|contul-meu/?)"', re.I)
FORM = re.compile(r"<form\b[^>]*>", re.I)
HREF = re.compile(r'(\s(?:href|src|content))=(["\'])(https?://(?:www\.)?bimx\.md)([^"\']*)\2', re.I)
SHARE = re.compile(r'href="(https://[^"]*?[?&](?:u|url)=)https?%3A%2F%2F(?:www\.)?bimx\.md[^"&]*([^"]*)"', re.I)
DATA_LINK = re.compile(r'data-link="https?://(?:www\.)?bimx\.md[^"]*"', re.I)


def local_target(path, en=False):
    """Fișierul din dist/ care corespunde unei căi bimx.md (în engleză pentru paginile EN), sau None."""
    path = path.split("#")[0].split("?")[0] or "/"
    path = LINK_ALIASES.get(path.rstrip("/") or "/", path)
    if path.rstrip("/") in ("/en", "/en/home"):
        path = "/en/"
    candidates = [path]
    if en and not path.startswith("/en/"):
        candidates.insert(0, "/en" + path)
    for p in candidates:
        local = DIST / p.lstrip("/")
        if p.endswith("/") or not local.suffix:
            local = local / "index.html"
        if local.is_file():
            return local
    return None


def detach_page(text, here):
    text = COMMENT.sub(lambda m: "" if "bimx.md" in m.group(0) else m.group(0), text)
    text = LINK_TAG.sub(lambda m: "" if ORIGIN.search(m.group(0)) else m.group(0), text)
    text = SCRIPT.sub(lambda m: "" if "wp-emoji" in m.group(0) else m.group(0), text)
    text = LOGIN_HREF.sub('href="#" data-unavailable', text)

    def form(m):
        tag = m.group(0)
        if "search-form-custom" in tag:  # căutarea funcționează local (sitegen/search.py + src/site/search.js)
            return re.sub(r'\saction="[^"]*"', ' action="#"', tag)[:-1].rstrip() + " data-search>"
        if ORIGIN.search(tag) or "wpcf7-form" in tag:
            tag = re.sub(r'\saction="[^"]*"', ' action="#"', tag)
            tag = tag[:-1].rstrip() + " data-unavailable>"
        return tag
    text = FORM.sub(form, text)

    text = SHARE.sub(lambda m: f'href="{m.group(1)}{m.group(2)}" data-share-base="{m.group(1)}" data-share-rest="{m.group(2)}"', text)
    text = DATA_LINK.sub('data-link="" data-share-self', text)

    def href(m):
        attr, q, _, path = m.groups()
        target = local_target(path, en=here.relative_to(DIST).parts[:1] == ("en",))
        if not target:
            return m.group(0)
        frag = "#" + path.split("#", 1)[1] if "#" in path else ""
        return f"{attr}={q}{relto(target, here) or 'index.html'}{frag}{q}"
    text = HREF.sub(href, text)

    # URL-urile din configurațiile JS și comentariile sourceURL devin căi relative la rădăcină.
    text = STYLE_OR_SCRIPT.sub(lambda m: m.group(1) + ORIGIN.sub("", m.group(3)) + m.group(4), text)

    script = f'<script src="{relto(REPLICA_JS, here)}" defer></script>\n'
    if "replica.js" not in text:
        text = text.replace("</body>", script + "</body>", 1)
    # corecturile de stil peste temă (src/site/site.css), după stilurile temei
    if "assets/css/site.css" not in text:
        text = text.replace("</head>", f'<link rel="stylesheet" href="{relto(SITE_CSS, here)}">\n</head>', 1)
    # în <head>, sincron: scripturile inline din pagină cer datele de piață încă de la încărcare
    market = f'<script src="{relto(MARKET_JS, here)}"></script>\n'
    if MARKET_JS.exists() and "market-data.js" not in text:
        text = text.replace("</head>", market + "</head>", 1)
    return text


def detach():
    REPLICA_JS.parent.mkdir(parents=True, exist_ok=True)
    REPLICA_JS.write_text((SRC / "site" / "replica.js").read_text(encoding="utf-8"), encoding="utf-8")
    SITE_CSS.parent.mkdir(parents=True, exist_ok=True)
    SITE_CSS.write_text((SRC / "site" / "site.css").read_text(encoding="utf-8"), encoding="utf-8")
    if MARKET_DATA.exists():
        responses = json.loads(MARKET_DATA.read_text(encoding="utf-8"))["responses"]
        MARKET_JS.write_text("window.BIMX_MARKET_DATA = " + json.dumps(responses, ensure_ascii=False, separators=(",", ":"))
                             + ";\n" + (SRC / "site" / "market.js").read_text(encoding="utf-8"), encoding="utf-8")
    changed = 0
    for f in sorted(DIST.rglob("*.html")):
        text = f.read_text(encoding="utf-8", errors="replace")
        new = detach_page(text, f.parent)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed += 1
    return changed
