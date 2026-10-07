"""Galeria foto (în meniul Noutăți), în RO, EN, RU și UK.

  galerie-foto/            albumele, câte unul pe eveniment (copertă, dată, eveniment, numărul de fotografii)
  galerie-foto/<album>/    fotografiile albumului, cu fotografia mărită la clic (replica.js), legătura spre comunicat
                           și arhiva ZIP a albumului (generată la build)

Paginile se creează din pagina temei category/anunturi-bimx/ (ca secțiunea Noutăți), înainte de corecturi.
Fotografiile stau în src/site/img/news/ și se copiază în dist/assets/img/news/.
"""
import posixpath
import re
import zipfile

from .config import DIST, LANG_PREFIX, SITE_LANGS
from .news import IDX, PAGE, SEP, SITE_URL, date_parts, relocate

HUB = "galerie-foto/index.html"
IMG = "assets/img/news/"

# albumele, de la cel mai nou: slug, dată, titlu, eveniment, comunicatul legat, fotografii (fișier, lățime, înălțime, alt, legendă)
ALBUMS = [
    {"slug": "capital-market-forum-2026", "date": "2026-09-28",
     "title": ("Capital Market Forum 2026",) * 4,
     "event": ("Moldova Business Week",) * 4,
     "article": "2026/09/28/capital-market-forum-2026/index.html",
     "photos": [
         ("capital-market-forum-2026.jpg", 1200, 705,
          ("Veronica Arpintin, CEO BIMx, la tribuna Capital Market Forum 2026",
           "Veronica Arpintin, BIMx CEO, speaking at Capital Market Forum 2026",
           "Вероника Арпинтин, генеральный директор BIMx, выступает на Capital Market Forum 2026",
           "Вероніка Арпінтін, CEO BIMx, виступає на Capital Market Forum 2026"),
          ("Veronica Arpintin, CEO BIMx, la Capital Market Forum 2026. Foto: BIMx",
           "Veronica Arpintin, BIMx CEO, at Capital Market Forum 2026. Photo: BIMx",
           "Вероника Арпинтин, генеральный директор BIMx, на Capital Market Forum 2026. Фото: BIMx",
           "Вероніка Арпінтін, CEO BIMx, на Capital Market Forum 2026. Фото: BIMx")),
         ("capital-market-forum-2026-clopot.jpg", 699, 466,
          ("Veronica Arpintin, CEO BIMx, pe scenă lângă clopotul BIMx",
           "Veronica Arpintin, BIMx CEO, on stage next to the BIMx bell",
           "Вероника Арпинтин, генеральный директор BIMx, на сцене рядом с колоколом BIMx",
           "Вероніка Арпінтін, CEO BIMx, на сцені поруч із дзвоном BIMx"),
          ("Veronica Arpintin, CEO BIMx, lângă clopotul BIMx, la Capital Market Forum 2026. Foto: Moldpres",
           "Veronica Arpintin, BIMx CEO, next to the BIMx bell at Capital Market Forum 2026. Photo: Moldpres",
           "Вероника Арпинтин, генеральный директор BIMx, рядом с колоколом BIMx на Capital Market Forum 2026. Фото: Moldpres",
           "Вероніка Арпінтін, CEO BIMx, поруч із дзвоном BIMx на Capital Market Forum 2026. Фото: Moldpres")),
     ]},
]

T = {
    "title": ("Galerie foto", "Photo gallery", "Фотогалерея", "Фотогалерея"),
    "news": ("Noutăți & Comunicate", "News & Announcements", "Новости и Объявления", "Новини та Оголошення"),
    "lead": ("Fotografii de la evenimentele Bursei Internaționale a Moldovei. Presa le poate folosi cu mențiunea autorului din legendă.",
             "Photos from Moldova International Stock Exchange events. The press may use them, crediting the author named in the caption.",
             "Фотографии с мероприятий Международной фондовой биржи Молдовы. СМИ могут использовать их с указанием автора из подписи.",
             "Фотографії із заходів Міжнародної фондової біржі Молдови. Преса може використовувати їх із зазначенням автора з підпису."),
    "albums": ("Albume", "Albums", "Альбомы", "Альбоми"),
    "photos": ("fotografii", "photos", "фото", "фото"),
    "read": ("Citiți comunicatul", "Read the announcement", "Читать сообщение", "Читати повідомлення"),
    "zip": ("Descărcați albumul (ZIP)", "Download the album (ZIP)", "Скачать альбом (ZIP)", "Завантажити альбом (ZIP)"),
    "open": ("Deschideți fotografia", "Open photo", "Открыть фото", "Відкрити фото"),
    "of": ("din", "of", "из", "з"),
    "prev": ("Fotografia anterioară", "Previous photo", "Предыдущее фото", "Попереднє фото"),
    "next": ("Fotografia următoare", "Next photo", "Следующее фото", "Наступне фото"),
    "close": ("Închideți", "Close", "Закрыть", "Закрити"),
    "download": ("Descărcați fotografia", "Download photo", "Скачать фото", "Завантажити фото"),
}

ICON_DL = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>')


def album_path(a):
    return f"galerie-foto/{a['slug']}/index.html"


def zip_name(a):
    return f"{a['slug']}.zip"


def page_of(pg):
    """None, „hub” sau albumul afișat de pg."""
    inner = str(pg.inner)
    if inner == HUB:
        return "hub"
    return next((a for a in ALBUMS if inner == album_path(a)), None)


def hub_html(pg):
    i = IDX[pg.lang]
    cards = []
    for a in ALBUMS:
        cover = a["photos"][0]
        _, full = date_parts(a["date"], pg.lang)
        cards.append(f'<a class="bx-album" href="{pg.link(album_path(a))}">'
                     f'<span class="bx-album-cover"><img src="{pg.asset(IMG + cover[0])}" alt="" width="{cover[1]}" height="{cover[2]}" loading="lazy" decoding="async">'
                     f'<span class="bx-album-count">{len(a["photos"])} {T["photos"][i]}</span></span>'
                     f'<span class="bx-album-body"><span class="bx-album-meta"><time datetime="{a["date"]}">{full}</time> · {a["event"][i]}</span>'
                     f'<span class="bx-album-title" role="heading" aria-level="2">{a["title"][i]}</span></span></a>')
    return f'<div class="container bx-gallery"><div class="bx-albums">{"".join(cards)}</div></div>'


def album_html(pg, a):
    i = IDX[pg.lang]
    n = len(a["photos"])
    tiles = []
    for k, (src, w, h, alts, caps) in enumerate(a["photos"]):
        tiles.append(f'<button type="button" class="bx-photo" data-full="{pg.asset(IMG + src)}" data-w="{w}" data-h="{h}" '
                     f'data-caption="{caps[i]}" data-alt="{alts[i]}" aria-label="{T["open"][i]} {k + 1} {T["of"][i]} {n}: {alts[i]}">'
                     f'<img src="{pg.asset(IMG + src)}" alt="" width="{w}" height="{h}" loading="lazy" decoding="async"></button>')
    actions = (f'<div class="bx-album-actions"><a class="bx-btn-secondary" href="{pg.link(a["article"])}">{T["read"][i]}</a>'
               f'<a class="bx-btn-primary" href="{zip_name(a)}" download>{ICON_DL}<span>{T["zip"][i]}</span></a></div>')
    lightbox = (f'<dialog class="bx-lb" aria-label="{a["title"][i]}">'
                f'<div class="bx-lb-bar"><span class="bx-lb-count"></span><span class="bx-lb-tools">'
                f'<a class="bx-lb-btn bx-lb-dl" href="#" download>{ICON_DL}<span>{T["download"][i]}</span></a>'
                f'<button type="button" class="bx-lb-btn bx-lb-close" aria-label="{T["close"][i]}">✕</button></span></div>'
                f'<div class="bx-lb-stage"><button type="button" class="bx-lb-nav bx-lb-prev" aria-label="{T["prev"][i]}">‹</button>'
                f'<figure><img alt=""><figcaption></figcaption></figure>'
                f'<button type="button" class="bx-lb-nav bx-lb-next" aria-label="{T["next"][i]}">›</button></div></dialog>')
    return f'<div class="container bx-gallery">{actions}<div class="bx-photos">{"".join(tiles)}</div>{lightbox}</div>'


def head_links(pg, path):
    url = lambda lang: SITE_URL + LANG_PREFIX[lang] + path.replace("index.html", "")
    links = [f'<link rel="canonical" href="{url(pg.lang)}">']
    links += [f'<link rel="alternate" hreflang="{x}" href="{url(x)}">' for x in SITE_LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{url("ro")}">')
    return "\n".join(links)


def build_gallery_page(text, pg):
    what = page_of(pg)
    if not what or "bx-gallery" in text:
        return text
    i = IDX[pg.lang]
    hero = re.search(r'<div class="archive_main_section">[\s\S]*?</div>\s*</div>', text)
    if not hero:
        return text
    h = hero.group(0)
    home = re.search(r'<li><a href="[^"]*">[^<]*</a></li>', h).group(0)
    crumbs = [home, SEP, f'<li><a href="{pg.link("noutati/index.html")}">{T["news"][i]}</a></li>', SEP]
    if what == "hub":
        title, lead, body, path = T["title"][i], T["lead"][i], hub_html(pg), HUB
        crumbs.append(f'<li><span aria-current="page">{title}</span></li>')
    else:
        a = what
        _, full = date_parts(a["date"], pg.lang)
        title, path = a["title"][i], album_path(a)
        lead = f'{full} · {a["event"][i]} · {len(a["photos"])} {T["photos"][i]}'
        body = album_html(pg, a)
        crumbs += [f'<li><a href="{pg.link(HUB)}">{T["title"][i]}</a></li>', SEP, f'<li><span aria-current="page">{title}</span></li>']
    h = re.sub(r'<ul class="breadcrumbs">[\s\S]*?</ul>', lambda m: '<ul class="breadcrumbs">' + "".join(crumbs) + "</ul>", h, count=1)
    h = re.sub(r'\s*<div class="cat_name">[\s\S]*?</div>', "", h, count=1)
    h = re.sub(r'(<h1[^>]*>)[\s\S]*?(</h1>)', lambda m: m.group(1) + title + m.group(2), h, count=1)
    h = re.sub(r'<p>[\s\S]*?</p>', lambda m: f'<p>{lead}</p>', h, count=1)
    text = text[:hero.start()] + h + text[hero.end():]
    text = re.sub(r'<div class="container_fluid">\s*<div class="filter_wrap">[\s\S]*?</div>\s*</div>\s*</div>', "", text, count=1)
    text = re.sub(r'<div class="container">\s*<section class="featured-post-section">[\s\S]*?'
                  r'(?=<div class="container_fluid">\s*<div class="related_categories">)', lambda m: body, text, count=1)
    text = re.sub(r'\s*<div class="related_categories">[\s\S]*?</section>\s*</div>', "", text, count=1)
    full_title = title if what == "hub" else f'{title} – {T["title"][i]}'
    text = re.sub(r'<title>[^<]*</title>', f'<title>{full_title} – BIMx</title>', text, count=1)
    text = re.sub(r'\s*<link rel="canonical"[^>]*>', "", text)
    return text.replace("</title>", "</title>\n" + head_links(pg, path), 1)


def create_gallery_pages():
    """Paginile galeriei (toate limbile) din pagina temei category/anunturi-bimx/; arhiva ZIP a fiecărui album."""
    for lang in SITE_LANGS:
        pre = LANG_PREFIX[lang]
        src = DIST / pre / PAGE
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8")
        old_dir = posixpath.dirname(pre + PAGE)
        for path in [HUB] + [album_path(a) for a in ALBUMS]:
            dest = DIST / pre / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            new_dir = posixpath.dirname(pre + path)
            dest.write_text(text if old_dir.count("/") == new_dir.count("/") else relocate(text, old_dir, new_dir), encoding="utf-8")
        for a in ALBUMS:
            with zipfile.ZipFile(DIST / pre / posixpath.dirname(album_path(a)) / zip_name(a), "w", zipfile.ZIP_STORED) as z:
                for n, (f, *_rest) in enumerate(a["photos"], 1):
                    z.write(DIST / IMG / f, f"{a['slug']}-{n:02d}{f[f.rfind('.'):]}")
