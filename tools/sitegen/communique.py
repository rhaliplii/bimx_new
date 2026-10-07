# -*- coding: utf-8 -*-
"""Pagina unui comunicat: bara laterală „Distribuiți” (Facebook, X, LinkedIn, copiere link) și comunicatul în PDF.

PDF-ul e varianta instituțională a comunicatului (fără fotografii, ca la BVB): antet cu logo și licență, data și
tipul, titlul, textul, „Despre BIMx”; pe fiecare pagină un subsol cu datele companiei și „Pagina X din Y”, iar de la
pagina 2 un antet discret. Se generează la build cu Chrome headless (aceeași rutină ca la ghidurile Academy); fără
Chrome, bara rămâne doar cu butoanele de distribuire.
"""
import html as htmlmod
import posixpath
import re
import tempfile
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .config import DIST, LANG_PREFIX, SITE_LANGS
from .news import IDX, NEWS, SITE_URL
from .pdf import find_chrome, print_pdf

T = {   # textele, în ordinea ro, en, ru, uk
    "share": ("Distribuiți", "Share", "Поделиться", "Поділитися"),
    "rail": ("Acțiuni pentru acest comunicat", "Actions for this press release", "Действия с пресс-релизом", "Дії з прес-релізом"),
    "pdf": ("Deschideți comunicatul în format PDF (filă nouă)", "Open the press release as PDF (new tab)",
            "Открыть пресс-релиз в формате PDF (новая вкладка)", "Відкрити прес-реліз у форматі PDF (нова вкладка)"),
    "city": ("Chișinău", "Chișinău", "Кишинэу", "Кишинеу"),
    "company": ("Bursa Internațională a Moldovei", "Moldova International Stock Exchange", "Международная фондовая биржа Молдовы",
                "Міжнародна фондова біржа Молдови"),
    "company_sa": ("Bursa Internațională a Moldovei S.A.", "Moldova International Stock Exchange JSC", "АО «Международная фондовая биржа Молдовы»",
                   "АТ «Міжнародна фондова біржа Молдови»"),
    "licence": ("Licență de operator de piață CNPF\\Aseria 000945 din 21.08.2026", "CNPF market operator licence\\Aseries 000945 of 21.08.2026",
                "Лицензия оператора рынка НКФР\\Aсерия 000945 от 21.08.2026", "Ліцензія оператора ринку НКФР\\Aсерія 000945 від 21.08.2026"),
    "address": ("str. Vlaicu Pârcălab 63, MD-2012, Chișinău, Republica Moldova", "63 Vlaicu Pârcălab St., MD-2012, Chișinău, Republic of Moldova",
                "ул. Влайку Пыркэлаб, 63, MD-2012, Кишинэу, Республика Молдова", "вул. Влайку Пиркелаб, 63, MD-2012, Кишинеу, Республіка Молдова"),
    "ids": ("IDNO 1025600073907 · Licență CNPF seria 000945", "IDNO 1025600073907 · CNPF licence series 000945",
            "IDNO 1025600073907 · Лицензия НКФР серия 000945", "IDNO 1025600073907 · Ліцензія НКФР серія 000945"),
    "page": ("Pagina \" counter(page) \" din \" counter(pages)", "Page \" counter(page) \" of \" counter(pages)",
             "Страница \" counter(page) \" из \" counter(pages)", "Сторінка \" counter(page) \" з \" counter(pages)"),
    "about_t": ("Despre BIMx", "About BIMx", "О BIMx", "Про BIMx"),
    "about": (
        "Bursa Internațională a Moldovei (BIMx) este operator de piață licențiat de Comisia Națională a Pieței Financiare (CNPF) "
        "la 21 august 2026 pentru Piața Reglementată și sistemul multilateral de tranzacționare (MTF). Acționariatul reunește zece "
        "entități instituționale din Republica Moldova și România; Bursa de Valori București (BVB) este acționar și partener strategic.",
        "Moldova International Stock Exchange (BIMx) is a market operator licensed by the National Commission for Financial Markets "
        "(CNPF) on 21 August 2026 for the Regulated Market and the multilateral trading facility (MTF). Its shareholders are ten "
        "institutional entities from the Republic of Moldova and Romania; the Bucharest Stock Exchange (BVB) is a shareholder and "
        "strategic partner.",
        "Международная фондовая биржа Молдовы (BIMx) — оператор рынка, лицензированный Национальной комиссией по финансовому рынку "
        "(НКФР) 21 августа 2026 г. для регулируемого рынка и многосторонней торговой системы (MTF). Акционерами являются десять "
        "институциональных организаций из Республики Молдова и Румынии; Бухарестская фондовая биржа (BVB) — акционер и "
        "стратегический партнёр.",
        "Міжнародна фондова біржа Молдови (BIMx) — оператор ринку, ліцензований Національною комісією з фінансового ринку (НКФР) "
        "21 серпня 2026 р. для регульованого ринку та багатосторонньої торговельної системи (MTF). Акціонерами є десять "
        "інституційних організацій з Республіки Молдова та Румунії; Бухарестська фондова біржа (BVB) — акціонер і стратегічний "
        "партнер."),
}

ICON_DOWNLOAD = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>')
# iconițele LinkedIn și Facebook din subsolul PDF-ului (o singură imagine, în caseta din dreapta jos a paginii)
SOCIAL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="54" height="24" viewBox="0 0 54 24">'
    '<rect width="24" height="24" rx="7" fill="#EEF0F6"/><g transform="translate(5 5) scale(.58)" fill="#1A2266"><path d="M4.98 3.5a2.5 '
    '2.5 0 11-.01 5 2.5 2.5 0 01.01-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.6 8.65 21 11.2 21 14.5V21h-4v-5.8c0-1.4'
    '-.03-3.2-1.95-3.2-1.95 0-2.25 1.52-2.25 3.1V21H9z"/></g><rect x="30" width="24" height="24" rx="7" fill="#EEF0F6"/><g '
    'transform="translate(35 5) scale(.58)" fill="#1A2266"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.87.25-1.46 1.5-1.46h1.6V4.46A21 '
    '21 0 0014.3 4.3c-2.3 0-3.8 1.4-3.8 3.95v2.25H8v3h2.5V21z"/></g></svg>')

PRINT_CSS = """
@page { size: A4; margin: 24mm 19mm 38mm 30mm;
  @bottom-left { content: "%(foot)s"; white-space: pre; width: 72%%; font: 7.8pt/1.5 Prompt, sans-serif; color: #3A3F52;
    vertical-align: top; text-align: left; border-top: 1.5pt solid #1DB0F0; padding-top: 3mm; margin-top: 6mm; }
  @bottom-right { content: url("%(social)s") "\\A %(page)s; white-space: pre; width: 28%%; font: 7.8pt/1.5 Prompt, sans-serif;
    color: #4A4F63; vertical-align: top; text-align: right; border-top: 1.5pt solid #1DB0F0; padding-top: 3mm; margin-top: 6mm; }
  @top-left { content: url("%(logo_small)s"); vertical-align: bottom; padding-bottom: 3mm; margin-bottom: 6mm; border-bottom: .75pt solid #C9CEDA; }
  @top-right { content: "%(running)s"; font: 7.8pt Prompt, sans-serif; color: #4A4F63; vertical-align: bottom; padding-bottom: 3mm;
    margin-bottom: 6mm; border-bottom: .75pt solid #C9CEDA; }
}
@page :first { @top-left { content: none; border: 0; } @top-right { content: none; border: 0; } }
html, body { margin: 0; background: #fff; }
body { font: 10.5pt/1.55 Prompt, sans-serif; color: #1F2333; }
a { color: #0E5E8C; text-decoration: none; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18pt; }
.head img { height: 30pt; width: auto; }
.head div { text-align: right; font-size: 8.5pt; line-height: 1.5; color: #4A4F63; white-space: pre-line; }
.meta { margin-top: 24pt; font-size: 9.5pt; line-height: 1.5; }
.meta .place { color: #4A4F63; }
.meta .kind { font-weight: 600; letter-spacing: .9pt; text-transform: uppercase; color: #1DB0F0; }
h1 { margin: 10pt 0 14pt; font-size: 16.5pt; line-height: 1.3; font-weight: 700; color: #1A2266; text-wrap: balance; }
.text { text-align: justify; hyphens: auto; }
.text p { margin: 0 0 8pt; orphans: 3; widows: 3; }
.text h2, .text h3 { font-size: 11pt; color: #1A2266; margin: 14pt 0 6pt; break-after: avoid; }
.text ul, .text ol { margin: 0 0 8pt; padding-left: 18pt; }
.text li { margin-bottom: 3pt; }
.text blockquote { margin: 10pt 0; padding-left: 12pt; border-left: 2pt solid #1DB0F0; }
.text p.bx-quote { margin: 12pt 0; padding-left: 11pt; border-left: 1.5pt solid #1DB0F0; break-inside: avoid; }
.text p.bx-quote em, .text blockquote p { font-style: italic; }
.text p.bx-quote strong { font-weight: 600; color: #1A2266; }
.text pre { margin: 10pt 0 0; font: 600 10pt/1.5 Prompt, sans-serif; color: #1A2266; white-space: pre-wrap; }
.about { margin-top: 20pt; padding-top: 9pt; border-top: .75pt solid #C9CEDA; break-inside: avoid; }
.about h2 { margin: 0 0 3pt; font-size: 8.5pt; font-weight: 700; letter-spacing: .8pt; text-transform: uppercase; color: #1A2266; }
.about p { margin: 0; font-size: 9.3pt; line-height: 1.55; color: #3A3F52; text-align: justify; }
"""


def _t(key, lang):
    return T[key][IDX[lang]]


def _data_uri(svg):
    return "data:image/svg+xml," + urllib.parse.quote(svg)


def _small_logo(logo_svg):
    """Logo-ul pentru antetul paginilor 2+: o imagine în caseta de margine nu se poate redimensiona din CSS,
    așa că dimensiunea se scrie direct în SVG."""
    svg = re.sub(r'(<svg\b[^>]*?)\s(width|height)="[^"]*"', r"\1", logo_svg, count=2)
    return _data_uri(svg.replace("<svg", '<svg width="66" height="19"', 1))


# Citatele din comunicate: doar un stil (bară cyan) pe paragraful original; textul nu se modifică.
UP, LOW = "A-ZĂÂÎȘȚÀ-ÝА-ЯЁІЇЄҐ", "a-zăâîșțß-ÿа-яёіїєґ’'\\-"
TAIL_NAME = re.compile(rf"([{UP}][{LOW}]+ [{UP}][{LOW}]+)(\.?\s*)$")


def _bold_name(rest):
    """Numele persoanei citate (două cuvinte cu majusculă, la finalul unui segment al atribuirii) primește doar <strong>."""
    parts = rest.split(", ")
    for k, part in enumerate(parts):
        if "<" in part:
            continue
        m = TAIL_NAME.search(part)
        if m:
            parts[k] = part[:m.start()] + f"<strong>{m.group(1)}</strong>" + m.group(2)
            return ", ".join(parts)
    return rest


def _quotes(body):
    """Paragrafele care încep cu un citat („<em>…</em>”, a declarat …) primesc clasa bx-quote, iar numele celui citat
    e îngroșat; cuvintele și ordinea lor rămân cele originale."""
    def mark(m):
        cls = ((m.group(1) or "") + " bx-quote").strip()
        return f'<p class="{cls}">{m.group(2)}{m.group(3)}</em>{_bold_name(m.group(4))}</p>'
    return re.sub(r'<p(?:\s+class="([^"]*)")?>(\s*[„“«"]\s*<em>)([\s\S]*?)</em>((?:(?!</p>)[\s\S])*)</p>', mark, body)


# Textele copiate din PDF (comunicatele informative): rânduri rupte cu <br>, titluri și sub-puncte amestecate într-o listă.
# La build se refac paragrafele și structura comunicatului din 25 august: titlurile de secțiune și punctele de pe ordinea de zi
# în bold, numerotate; sub-punctele („1.1.”) ca paragrafe. Textul rămâne cel original.
ITEM = re.compile(r"^\d{1,2}(?:\.\d{1,2})+\.?\s|^\d{1,2}\.\s")   # „1.1.”, „2.”; nu datele („11.06.2026”)


def _plain(x):
    return htmlmod.unescape(re.sub(r"<[^>]+>", "", x)).replace("\xa0", " ").strip()


def _is_heading(line):
    t = _plain(line)
    return t.endswith(":") and len(t) < 60 and t[:1].isupper()     # „Chestiune organizatorică:”, nu „următoarele hotărâri:”


def _join_lines(chunk):
    """Rândurile despărțite prin <br> → paragrafe logice (un rând nou doar după final de propoziție, la un punct sau titlu)."""
    out = []
    for line in re.split(r"<br\s*/?>", chunk):
        line = line.replace("&nbsp;", " ").strip()
        if not line:
            continue
        if out:
            prev = _plain(out[-1])
            first = _plain(line)[:1]
            new = (ITEM.match(_plain(line)) or prev.endswith(":") or _is_heading(line)
                   or (re.search(r"[.;!?»”\"]$", prev) and (first.isupper() or first.isdigit() or first in "„“«\"")))
            if not new:
                out[-1] = out[-1].rstrip() + " " + line
                continue
        out.append(line)
    return out



def _restructure(body):
    """Doar rândurile rupte de copierea din PDF se lipesc la loc; cuvintele, ordinea și numerotarea rămân cele originale."""
    def lists(m):
        intro = "<br>".join(_join_lines(m.group(2)))
        items = "".join(f"<li>{'<br>'.join(_join_lines(li))}</li>" for li in re.findall(r"<li[^>]*>([\s\S]*?)</li>", m.group(3)))
        return f"{m.group(1)}{intro}</p>\n<ol>{items}</ol>"
    return re.sub(r'(<p[^>]*>)([\s\S]*?)</p>\s*<ol[^>]*>([\s\S]*?)</ol>', lists, body)


def _words(html):
    return " ".join(_plain(re.sub(r"<br\s*/?>|</p>|</li>", " ", html)).split())


def _clean(body):
    """Stilul pe textul original; dacă vreo transformare ar schimba vreun cuvânt, rămâne textul original neatins."""
    out = _quotes(_restructure(body))
    return out if _words(out) == _words(body) else body


def _body(text, page_url):
    """Textul comunicatului din pagină: fără fotografii și atribute de stil; linkurile relative devin adrese complete."""
    m = re.search(r'<div class="ev_description">([\s\S]*?)</div>\s*</div>\s*<div class="ev_sidebar">', text)
    if not m:
        return None
    body = re.sub(r"<figure[\s\S]*?</figure>|<img[^>]*>|<!--[\s\S]*?-->", "", m.group(1))
    body = re.sub(r'\s(?:class|style|id|data-[a-z-]+)="[^"]*"', "", body)

    def absolute(m):
        href = m.group(1)
        if re.match(r"^(?:[a-z]+:|#)", href):
            return m.group(0)
        return f'href="{urllib.parse.urljoin(page_url, href)}"'
    return _clean(re.sub(r'href="([^"]*)"', absolute, body))


def _print_html(text, lang, page_url, logo_svg):
    title = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", text).group(1).strip()
    kind = re.search(r'<ul class="post-tags-list"><li>([^<]*)</li>', text)
    date = re.search(r'<div class="subtitle">[\s\S]*?<p>\s*<svg[\s\S]*?</svg>\s*([^<]+?)\s*</p>', text)
    body = _body(text, page_url)
    if body is None or not date:
        return None
    kind = kind.group(1).strip() if kind else ""
    date = date.group(1).strip()
    place = f"{_t('city', lang)}, {date}"

    def css_str(s):
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\\\\A", "\\A")
    foot = "\\A".join([_t("company_sa", lang), _t("address", lang), "T: +373 22 89 77 00 · E: office@bimx.md · W: bimx.md", _t("ids", lang)])
    css = PRINT_CSS % {
        "foot": css_str(foot), "social": _data_uri(SOCIAL_SVG), "page": _t("page", lang),
        "logo_small": _small_logo(logo_svg), "running": css_str(htmlmod.unescape(f"{kind} · {place}" if kind else place)),
    }
    licence = _t("licence", lang).replace("\\A", "\n")
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Prompt:ital,wght@0,400;0,500;0,600;0,700;1,400&amp;display=block" rel="stylesheet">'
            f'<style>{css}</style></head><body>'
            f'<header class="head"><img src="{_data_uri(logo_svg)}" alt="BIMx"><div>{_t("company", lang)}\n{licence}</div></header>'
            f'<div class="meta"><div class="place">{place}</div>' + (f'<div class="kind">{kind}</div>' if kind else "") + '</div>'
            f'<h1>{title}</h1><div class="text">{body}</div>'
            f'<section class="about"><h2>{_t("about_t", lang)}</h2><p>{_t("about", lang)}</p></section>'
            '</body></html>')


def _close_div(text, start):
    """Poziția de după </div>-ul care închide elementul <div> de la `start`."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", text[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("div neînchis")


ICON_MAIL = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>')
ICON_PHONE = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1DB0F0" stroke-width="1.8" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 '
              '19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 '
              '2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>')
ICON_CLOCK = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8A90A3" stroke-width="1.8" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>')
ICON_BACK = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M12.7 8H3.3M8 12.7 3.3 8 8 3.3" '
             'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

P = {   # textele paginii (ro, en, ru, uk)
    "home": ("Acasă", "Home", "Главная", "Головна"),
    "news": ("Noutăți", "News", "Новости", "Новини"),
    "bimx": ("Anunțuri BIMx", "BIMx announcements", "Объявления BIMx", "Оголошення BIMx"),
    "info": ("Informații despre comunicat", "About this press release", "О пресс-релизе", "Про прес-реліз"),
    "pdf_btn": ("Descărcați PDF", "Download PDF", "Скачать PDF", "Завантажити PDF"),
    "similar": ("Comunicate similare", "Related press releases", "Похожие пресс-релизы", "Схожі прес-релізи"),
    "all": ("Toate noutățile", "All news", "Все новости", "Усі новини"),
    "press_q": ("Întrebări din partea presei?", "Media enquiries?", "Вопросы от прессы?", "Запитання від преси?"),
    "press": ("Contact presă", "Press contact", "Контакт для прессы", "Контакт для преси"),
    "hours_t": ("Program", "Hours", "График работы", "Графік роботи"),
    "hours": ("Lun – Vin: 09:00 – 18:00 · Weekend și sărbători: închis", "Mon – Fri: 09:00 – 18:00 · Weekends and public holidays: closed",
              "Пн – Пт: 09:00 – 18:00 · Выходные и праздничные дни: закрыто", "Пн – Пт: 09:00 – 18:00 · Вихідні та святкові дні: зачинено"),
}


def _p(key, lang):
    return P[key][IDX[lang]]


def _share_items(text):
    """Butoanele de distribuire existente (Facebook, X, LinkedIn, copiere link), cu iconițele și hover-ul lor."""
    m = re.search(r'<ul class="share-buttons-list">([\s\S]*?)</ul>', text)
    return m.group(1).strip() if m else None


def _similar(item, lang, root):
    """Trei comunicate: întâi cele din aceeași categorie, apoi cele mai recente."""
    from .home import NEWS_EDIT
    from .news import CATS, date_parts
    others = [e for e in NEWS if e[0] != item[0]]
    others.sort(key=lambda e: (e[2] != item[2], [-int(x) for x in e[1].split("-")]))
    i = IDX[lang]
    cards = []
    for e in others[:3]:
        _, full = date_parts(e[1], lang)
        cards.append(f'<a class="bx-pr-card" href="{root}{e[0]}/index.html"><span class="bx-pr-card-m"><span>{CATS[e[2]][0][i]}</span> · '
                     f'<time datetime="{e[1]}">{full}</time></span><span class="bx-pr-card-t">{NEWS_EDIT[e[3]][i][1]}</span></a>')
    return "".join(cards)


def _redesign(text, lang, item, pdf_name):
    """Pagina comunicatului după macheta „E”: antet alb (tip · loc și dată, titlu, lead), textul pe o coloană cu „Despre BIMx”
    la final, cardul lateral (PDF + Distribuiți), comunicate similare și contactul pentru presă."""
    from .news import date_parts
    start = text.find('<div class="single_anunturi_bimx">')
    if start < 0:
        return text
    end = _close_div(text, start)
    old = text[start:end]
    title = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", old).group(1).strip()
    kind = re.search(r'<ul class="post-tags-list"><li>([^<]*)</li>', old)
    kind = kind.group(1).strip() if kind else ""
    home = re.search(r'<ul class="breadcrumbs">\s*<li><a href="([^"]*)index\.html"', old)
    body = re.search(r'<div class="ev_description">([\s\S]*?)</div>\s*</div>\s*<div class="ev_sidebar', old)
    share = _share_items(old)
    if not (home and body and share):
        return text
    root = home.group(1)
    i = IDX[lang]
    _, full = date_parts(item[1], lang)
    place = f"{_t('city', lang)}, {full}"
    lead = item[4][i]
    # sub lead, deasupra liniei: doar locul și data („Chișinău, 5 octombrie 2026”)
    byline = f'<p class="bx-pr-byline"><span>{place}</span></p>'
    body = _clean(body.group(1))
    styles = "".join(re.findall(r"<style>[\s\S]*?</style>", old))   # stilurile temei din bloc (ticker) rămân
    # breadcrumb-ul original al paginii (Acasă › Noutăți & Comunicate › titlul scurt), în stilul antetului alb
    ul = re.search(r'<ul class="breadcrumbs">([\s\S]*?)</ul>', old).group(1)
    links = re.findall(r'<li><a href="([^"]*)">([\s\S]*?)</a></li>', ul)
    current = re.search(r'<span aria-current="page">([\s\S]*?)</span>', ul)
    sep = ('<span class="bx-pr-sep" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.25 10.5 8.75 7 '
           '5.25 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')
    parts = [f'<a href="{h}">{t.strip()}</a>' for h, t in links]
    if current:
        parts.append(f'<span aria-current="page">{current.group(1).strip()}</span>')
    crumbs = f'<nav class="bx-pr-crumbs" aria-label="Breadcrumb">{sep.join(parts)}</nav>'
    meta = f'<div class="bx-pr-meta"><span class="bx-pr-kind">{kind}</span></div>' if kind else ""
    pdf = ""
    if pdf_name:
        label = _t("pdf", lang)
        pdf = (f'<section class="bx-pr-box"><a class="bx-pr-pdf" href="{pdf_name}" target="_blank" rel="noopener" title="{label}">'
               f'{ICON_DOWNLOAD}<span>{_p("pdf_btn", lang)}</span></a></section>')
    aside = (f'<aside class="bx-pr-aside" aria-label="{_p("info", lang)}"><div class="bx-pr-card-box">{pdf}'
             f'<section class="bx-pr-box"><h2>{_t("share", lang)}</h2><ul class="share-buttons-list bx-pr-share">{share}</ul></section>'
             f'</div></aside>')
    about = (f'<section class="bx-pr-about" aria-labelledby="bx-pr-about-h"><h2 id="bx-pr-about-h">{_t("about_t", lang)}</h2>'
             f'<p>{_t("about", lang)}</p></section>')
    similar = (f'<section class="bx-pr-similar" aria-labelledby="bx-pr-sim-h"><div class="container">'
               f'<div class="bx-pr-similar-head"><h2 id="bx-pr-sim-h">{_p("similar", lang)}</h2>'
               f'<a class="bx-pr-back" href="{root}noutati/index.html">{ICON_BACK}<span>{_p("all", lang)}</span></a></div>'
               f'<div class="bx-pr-cards">{_similar(item, lang, root)}</div></div></section>')
    contact = (f'<section class="bx-pr-contact" aria-label="{_p("press", lang)}"><div class="container">'
               f'<h2>{_p("press_q", lang)}</h2><div class="bx-pr-contact-r"><div class="bx-pr-contact-l">'
               f'<a href="mailto:office@bimx.md">{ICON_MAIL.replace("currentColor", "#1DB0F0")}office@bimx.md</a><span aria-hidden="true">·</span>'
               f'<a href="tel:+37322897700">{ICON_PHONE}+373 22 89 77 00</a></div>'
               f'<p>{ICON_CLOCK}<span><strong>{_p("hours_t", lang)}:</strong> {_p("hours", lang)}</span></p></div></div></section>')
    page = (f'<div class="single_anunturi_bimx bx-pr">{styles}'
            f'<section class="bx-pr-head"><div class="container">{crumbs}{meta}<h1>{title}</h1><p class="bx-pr-lead">{lead}</p>{byline}</div></section>'
            f'<div class="container bx-pr-main"><article class="bx-pr-article"><div class="bx-pr-text">{body}</div>{about}</article>{aside}</div>'
            f'{similar}{contact}</div>')
    return text[:start] + page + text[end:]


def build_communiques():
    """PDF-urile comunicatelor și pagina lor (macheta „E”); întoarce (pagini, PDF-uri)."""
    chrome = find_chrome()
    logo_svg = (DIST / "assets/img/bimx-logo.svg").read_text(encoding="utf-8")
    jobs = []
    with tempfile.TemporaryDirectory() as tmp:
        for lang in SITE_LANGS:
            for item in NEWS:
                path, short = item[0], item[3]
                page = DIST / LANG_PREFIX[lang] / path / "index.html"
                if not page.exists():
                    continue
                text = page.read_text(encoding="utf-8")
                if "bx-pr-head" in text:
                    continue
                name = f"BIMx-{short}.pdf"
                src = _print_html(text, lang, SITE_URL + posixpath.join(LANG_PREFIX[lang], path) + "/", logo_svg) if chrome else None
                html_file = Path(tmp) / f"{lang}-{short}.html"
                if src:
                    html_file.write_text(src, encoding="utf-8")
                jobs.append((page, text, lang, name, html_file if src else None, item))

        def run(job):
            page, text, lang, name, html_file, item = job
            ok = bool(html_file) and print_pdf(chrome, html_file, page.parent / name)
            page.write_text(_redesign(text, lang, item, name if ok else None), encoding="utf-8")
            return ok
        with ThreadPoolExecutor(max_workers=4) as pool:
            made = sum(pool.map(run, jobs))
    return len(jobs), made
