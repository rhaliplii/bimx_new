"""Căutarea din site: indexul paginilor (RO și EN) generat la build și scriptul care îl folosește.

Site-ul e static, deci căutarea rulează în browser: pentru fiecare limbă se scrie un fișier
dist/assets/search/{ro,en}.js cu titlul, secțiunea și textul principal al fiecărei pagini (fără antet,
subsol, meniuri, secțiuni ascunse sau teste). Fișierele sunt JavaScript, nu JSON, ca să funcționeze și
când site-ul e deschis direct din disc (file://). src/site/search.js le încarcă la prima căutare.
"""
import html
import json
import re
import unicodedata
from html.parser import HTMLParser

from .config import DIST, SRC, SITE_LANGS, lang_of
from .util import relto

SEARCH_JS = DIST / "assets" / "js" / "search.js"
INDEX_DIR = DIST / "assets" / "search"
MAX_TEXT = 12000  # caractere de text per pagină în index

# Subarbori excluși din index: navigație, elemente repetate, secțiuni ascunse în copie, teste.
SKIP_TAGS = {"script", "style", "svg", "noscript", "form", "nav", "select", "button", "template", "iframe"}
SKIP_CLASSES = {"market_overview", "market_gainers", "bimx-ticker-wrap", "breadcrumbs", "modal_search_form", "ds-popup",
                "ds-popup-wrapper", "quiz", "lesson_nav", "toc", "guide_toc", "pager", "complete_bar", "disclaimer",
                "section_nav_wrap", "read_progress", "share", "share-list", "contact_modal_overlay",
                "numbers"}  # statisticile de piață ascunse de pe prima pagină
PLACEHOLDER = re.compile(r"^\s*(În curând|Coming soon)\s*$")


class _Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = 0
        self.skip = None          # [tag, adâncime] pentru subarborele sărit
        self.parts, self.heads, self.h1 = [], [], []
        self.cur_head = None
        self.crumbs, self.in_crumbs, self.crumb_depth = [], False, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if "breadcrumbs" in cls:
            self.in_crumbs, self.crumb_depth = True, 0
        if self.in_crumbs:
            self.crumb_depth += tag == "ul"
        if tag == "main":
            self.in_main += 1
        if self.skip:
            if tag == self.skip[0]:
                self.skip[1] += 1
            return
        hidden = "display:none" in (a.get("style") or "").replace(" ", "") or "hidden" in a
        if self.in_main and (tag in SKIP_TAGS or cls & SKIP_CLASSES or hidden):
            self.skip = [tag, 1]
            return
        if tag in ("h1", "h2", "h3") and self.in_main:
            self.cur_head = [tag, []]
        if tag in ("p", "li", "br", "div", "td", "th", "h1", "h2", "h3", "h4", "h5", "dt", "dd", "section", "article"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if self.in_crumbs and tag == "ul":
            self.crumb_depth -= 1
            if self.crumb_depth <= 0:
                self.in_crumbs = False
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        if self.skip:
            if tag == self.skip[0]:
                self.skip[1] -= 1
                if self.skip[1] == 0:
                    self.skip = None
            return
        if self.cur_head and tag == self.cur_head[0]:
            text = " ".join("".join(self.cur_head[1]).split())
            if text:
                (self.h1 if tag == "h1" else self.heads).append(text)
            self.cur_head = None

    def handle_data(self, data):
        if self.in_crumbs and data.strip():
            self.crumbs.append(data.strip())
        if not self.in_main or self.skip:
            return
        self.parts.append(data)
        if self.cur_head:
            self.cur_head[1].append(data)


def _page(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if 'http-equiv="refresh"' in text[:500]:
        return None
    p = _Extract()
    p.feed(text)
    body = unicodedata.normalize("NFC", " ".join("".join(p.parts).split()))
    title = p.h1[0] if p.h1 else html.unescape(re.search(r"<title>(.*?)</title>", text, re.S).group(1))
    title = re.sub(r"\s+[–-]\s+(BIMx Academy|Ghid BIMx Academy|BIMx Academy guide|BIMx)$", "", title.strip())
    if PLACEHOLDER.match(title) or PLACEHOLDER.match(body) or len(body.split()) < 12:
        return None
    crumbs = [c for c in p.crumbs[1:-1] if c not in ("Acasă", "Home", "Главная")]
    fix = {"Despre Noi": "Despre noi", "Piaţă": "Piață", "Ştiri": "Știri"}
    section = " › ".join(fix.get(c, c) for c in crumbs) or ("BIMx Academy" if "/academy/" in "/" + str(path) else "BIMx")
    return {"u": str(path.relative_to(DIST)).replace("\\", "/"), "t": unicodedata.normalize("NFC", title),
            "s": section, "h": " · ".join(dict.fromkeys(p.heads))[:600], "x": body[:MAX_TEXT]}


def build_search():
    """Scrie indexurile de căutare (câte unul pe limbă) și scriptul de căutare; adaugă scriptul pe paginile care au formularul de căutare."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    pages = {lang: [] for lang in SITE_LANGS}
    for f in sorted(DIST.rglob("*.html")):
        rel = f.relative_to(DIST)
        if rel.parts[0] in ("assets", "wp-content", "wp-includes"):
            continue
        entry = _page(f)
        if entry:
            pages[lang_of(rel.parts)].append(entry)
    for lang, entries in pages.items():
        data = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
        (INDEX_DIR / f"{lang}.js").write_text(
            f"window.BIMX_SEARCH = window.BIMX_SEARCH || {{}};\nwindow.BIMX_SEARCH.{lang} = {data};\n", encoding="utf-8")
    SEARCH_JS.parent.mkdir(parents=True, exist_ok=True)
    SEARCH_JS.write_text((SRC / "site" / "search.js").read_text(encoding="utf-8"), encoding="utf-8")

    injected = 0
    for f in DIST.rglob("*.html"):
        text = f.read_text(encoding="utf-8", errors="replace")
        if "search-form-custom" not in text or "assets/js/search.js" in text:
            continue
        root = relto(DIST, f.parent)
        root = root + "/" if root else ""
        tag = f'<script src="{root}assets/js/search.js" data-root="{root}" defer></script>\n'
        f.write_text(text.replace("</body>", tag + "</body>", 1), encoding="utf-8")
        injected += 1
    return {k: len(v) for k, v in pages.items()}, injected
