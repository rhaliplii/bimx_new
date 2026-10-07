# -*- coding: utf-8 -*-
"""Pagina „Tarifele Bursei” (tarifele-bursei/): înlocuiește pagina „Costuri” și linkurile directe spre PDF.

Tabelul e cel din „Nomenclatorul taxelor și comisioanelor” (PDF), cu textul românesc copiat exact; EN/RU/UK sunt traduceri.
Pagina se face din pagina temei costuri/ (aceeași adâncime), iar costuri/ devine o redirecționare (fixes.REDIRECTS).
"""
import re

from .config import DIST, LANG_PREFIX, SITE_LANGS
from .news import IDX, SITE_URL

PATH = "tarifele-bursei/index.html"
SOURCE = "costuri/index.html"
PDF = "wp-content/uploads/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"

T = {
    "title": ("Tarifele Bursei", "Exchange Fees", "Тарифы биржи", "Тарифи біржі"),
    "table": ("Tarifele Bursei Internaționale a Moldovei", "Fees of the Moldova International Stock Exchange",
              "Тарифы Международной фондовой биржи Молдовы", "Тарифи Міжнародної фондової біржі Молдови"),
    "nr": ("Nr.", "No.", "№", "№"),
    "desc": ("Descriere serviciu", "Service description", "Описание услуги", "Опис послуги"),
    "fee": ("Tarif BIM propus", "Proposed BIM fee", "Предлагаемый тариф BIM", "Запропонований тариф BIM"),
    "doc": ("Tarifele Bursei (PDF)", "Exchange fees (PDF)", "Тарифы биржи (PDF)", "Тарифи біржі (PDF)"),
    # antetul și subsolul PDF-ului tradus (ca în PDF-ul oficial)
    "company": ("O.P. Bursa Internațională a Moldovei S.A", "Moldova International Stock Exchange JSC",
                "АО «Международная фондовая биржа Молдовы»", "АТ «Міжнародна фондова біржа Молдови»"),
    "capital": ("Capital social: 29.475.000 lei", "Share capital: MDL 29,475,000", "Уставный капитал: 29 475 000 леев",
                "Статутний капітал: 29 475 000 леїв"),
    "address": ("MD 2012, Republica Moldova, mun. Chișinău, str. Vlaicu Pârcălab 63, et. 5",
                "MD 2012, Republic of Moldova, Chișinău, 63 Vlaicu Pârcălab St., 5th floor",
                "MD 2012, Республика Молдова, мун. Кишинэу, ул. Влайку Пыркэлаб, 63, 5-й этаж",
                "MD 2012, Республіка Молдова, мун. Кишинеу, вул. Влайку Пиркелаб, 63, 5-й поверх"),
}

# (secțiune, [(descriere, tarif)]) – în ordinea și numerotarea din PDF; descrierile RO sunt textul exact din PDF
SECTIONS = [
    (("A. PIAȚA REGLEMENTATĂ – Admitere și Menținere Acțiuni", "A. REGULATED MARKET – Admission and Maintenance of Shares",
      "A. РЕГУЛИРУЕМЫЙ РЫНОК – Допуск и поддержание акций", "A. РЕГУЛЬОВАНИЙ РИНОК – Допуск і підтримання акцій"), [
        (("Comision de procesare a documentelor la înscrierea acțiunilor pe piața reglementată",
          "Document processing fee for the admission of shares to the regulated market",
          "Комиссия за обработку документов при включении акций на регулируемый рынок",
          "Комісія за опрацювання документів під час включення акцій на регульований ринок"),
         ("10.000 MDL", "MDL 10,000", "10 000 MDL", "10 000 MDL")),
        (("Comision de menținere a acțiunilor pe piața reglementată (per an calendaristic)",
          "Maintenance fee for shares on the regulated market (per calendar year)",
          "Комиссия за поддержание акций на регулируемом рынке (за календарный год)",
          "Комісія за підтримання акцій на регульованому ринку (за календарний рік)"),
         ("30.000 MDL", "MDL 30,000", "30 000 MDL", "30 000 MDL")),
        (("Taxă pentru înscrierea acțiunilor din emisiunea suplimentară pe piața reglementată",
          "Fee for the admission of shares from an additional issue to the regulated market",
          "Сбор за включение акций дополнительной эмиссии на регулируемый рынок",
          "Збір за включення акцій додаткової емісії на регульований ринок"),
         ("1.000 MDL", "MDL 1,000", "1 000 MDL", "1 000 MDL")),
        (("Taxă pentru introducerea modificărilor în datele emitenților", "Fee for amending issuer data",
          "Сбор за внесение изменений в данные эмитентов", "Збір за внесення змін до даних емітентів"),
         ("0",) * 4),
        (("Taxă de admitere/menținere instrumente financiare emise de Ministerul Finanțelor",
          "Admission/maintenance fee for financial instruments issued by the Ministry of Finance",
          "Сбор за допуск/поддержание финансовых инструментов, выпущенных Министерством финансов",
          "Збір за допуск/підтримання фінансових інструментів, випущених Міністерством фінансів"),
         ("0",) * 4),
    ]),
    (("B. PIAȚA REGLEMENTATĂ – Admitere și Menținere Obligațiuni Corporative/Municipale",
      "B. REGULATED MARKET – Admission and Maintenance of Corporate/Municipal Bonds",
      "B. РЕГУЛИРУЕМЫЙ РЫНОК – Допуск и поддержание корпоративных/муниципальных облигаций",
      "B. РЕГУЛЬОВАНИЙ РИНОК – Допуск і підтримання корпоративних/муніципальних облігацій"), [
        (("Taxă de admitere a obligațiunilor corporative/municipale", "Admission fee for corporate/municipal bonds",
          "Сбор за допуск корпоративных/муниципальных облигаций", "Збір за допуск корпоративних/муніципальних облігацій"),
         ("0,02% din vol. emisiunii (min 2.500 lei)", "0.02% of issue volume (min MDL 2,500)",
          "0,02% от объёма эмиссии (мин. 2 500 леев)", "0,02% від обсягу емісії (мін. 2 500 леїв)")),
        (("Taxă de menținere a obligațiunilor corporative/municipale (per an calendaristic)",
          "Maintenance fee for corporate/municipal bonds (per calendar year)",
          "Сбор за поддержание корпоративных/муниципальных облигаций (за календарный год)",
          "Збір за підтримання корпоративних/муніципальних облігацій (за календарний рік)"),
         ("0,05% din vol. emisiunii (min 2.500, max 10.000)", "0.05% of issue volume (min 2,500, max 10,000)",
          "0,05% от объёма эмиссии (мин. 2 500, макс. 10 000)", "0,05% від обсягу емісії (мін. 2 500, макс. 10 000)")),
    ]),
    (("C. SISTEM MTF (Multilateral Trading Facility)", "C. MTF SYSTEM (Multilateral Trading Facility)",
      "C. СИСТЕМА MTF (Multilateral Trading Facility)", "C. СИСТЕМА MTF (Multilateral Trading Facility)"), [
        (("Comision de procesare a documentelor la înscrierea valorilor mobiliare în cadrul MTF",
          "Document processing fee for the admission of securities to the MTF",
          "Комиссия за обработку документов при включении ценных бумаг в MTF",
          "Комісія за опрацювання документів під час включення цінних паперів до MTF"),
         ("2.000 MDL", "MDL 2,000", "2 000 MDL", "2 000 MDL")),
        (("Taxă pentru introducerea modificărilor în datele emitenților MTF", "Fee for amending MTF issuer data",
          "Сбор за внесение изменений в данные эмитентов MTF", "Збір за внесення змін до даних емітентів MTF"),
         ("0",) * 4),
        (("Comision de menținere a acțiunilor (per an calendaristic)", "Maintenance fee for shares (per calendar year)",
          "Комиссия за поддержание акций (за календарный год)", "Комісія за підтримання акцій (за календарний рік)"),
         ("15.000 MDL", "MDL 15,000", "15 000 MDL", "15 000 MDL")),
        (("Taxă de admitere a obligațiunilor corporative și municipale (MTF)", "Admission fee for corporate and municipal bonds (MTF)",
          "Сбор за допуск корпоративных и муниципальных облигаций (MTF)", "Збір за допуск корпоративних і муніципальних облігацій (MTF)"),
         ("0,01% din vol. emisiunii (min 1.000 lei)", "0.01% of issue volume (min MDL 1,000)",
          "0,01% от объёма эмиссии (мин. 1 000 леев)", "0,01% від обсягу емісії (мін. 1 000 леїв)")),
        (("Taxă de menținere a obligațiunilor corporative/municipale MTF (per an calendaristic)",
          "Maintenance fee for MTF corporate/municipal bonds (per calendar year)",
          "Сбор за поддержание корпоративных/муниципальных облигаций MTF (за календарный год)",
          "Збір за підтримання корпоративних/муніципальних облігацій MTF (за календарний рік)"),
         ("0,02% din vol. emisiunii (max 2.500 MDL)", "0.02% of issue volume (max MDL 2,500)",
          "0,02% от объёма эмиссии (макс. 2 500 MDL)", "0,02% від обсягу емісії (макс. 2 500 MDL)")),
    ]),
    (("D. COMISIOANE DE TRANZACȚIONARE", "D. TRADING FEES", "D. ТОРГОВЫЕ КОМИССИИ", "D. ТОРГОВЕЛЬНІ КОМІСІЇ"), [
        (("Comision de tranzacționare – Secția de bază (negocieri bursiere) [cumpărător + vânzător]",
          "Trading fee – Main section (exchange trading) [buyer + seller]",
          "Торговая комиссия – Основная секция (биржевые торги) [покупатель + продавец]",
          "Торговельна комісія – Основна секція (біржові торги) [покупець + продавець]"),
         ("0,20% (0,1% cump. + 0,1% vânz.)", "0.20% (0.1% buyer + 0.1% seller)",
          "0,20% (0,1% покуп. + 0,1% продав.)", "0,20% (0,1% покуп. + 0,1% продав.)")),
        (("Comision tranzacționare – Tranzacții directe (excl. REPO)", "Trading fee – Direct transactions (excl. REPO)",
          "Торговая комиссия – Прямые сделки (кроме РЕПО)", "Торговельна комісія – Прямі угоди (крім РЕПО)"),
         ("0,1% per parte", "0.1% per side", "0,1% с каждой стороны", "0,1% з кожної сторони")),
        (("Tranzacții de tip REPO", "REPO transactions", "Сделки РЕПО", "Угоди РЕПО"),
         ("0,05% per parte", "0.05% per side", "0,05% с каждой стороны", "0,05% з кожної сторони")),
        (("Comision de tranzacționare a obligațiunilor corporative", "Trading fee for corporate bonds",
          "Комиссия за торговлю корпоративными облигациями", "Комісія за торгівлю корпоративними облігаціями"),
         ("0,02% per parte", "0.02% per side", "0,02% с каждой стороны", "0,02% з кожної сторони")),
        (("Valori mobiliare de stat", "Government securities", "Государственные ценные бумаги", "Державні цінні папери"),
         ("0,01% per parte", "0.01% per side", "0,01% с каждой стороны", "0,01% з кожної сторони")),
    ]),
    (("E. ALTE TAXE ȘI SERVICII", "E. OTHER FEES AND SERVICES", "E. ПРОЧИЕ СБОРЫ И УСЛУГИ", "E. ІНШІ ЗБОРИ ТА ПОСЛУГИ"), [
        (("Taxă de menținere a Membrilor (PR/MTF)", "Membership maintenance fee (RM/MTF)",
          "Сбор за поддержание членства (РР/MTF)", "Збір за підтримання членства (РР/MTF)"),
         ("100 EUR / lună", "EUR 100 / month", "100 EUR / месяц", "100 EUR / місяць")),
        (("Atestarea și acreditarea Agenților de Bursă", "Certification and accreditation of Stockbrokers",
          "Аттестация и аккредитация биржевых агентов", "Атестація та акредитація біржових агентів"),
         ("1.000 MDL", "MDL 1,000", "1 000 MDL", "1 000 MDL")),
        (("Buletin informativ (varianta electronică)", "Newsletter (electronic version)",
          "Информационный бюллетень (электронная версия)", "Інформаційний бюлетень (електронна версія)"),
         ("0",) * 4),
        (("Statistică zilnică a tranzacțiilor bursiere", "Daily statistics of exchange transactions",
          "Ежедневная статистика биржевых сделок", "Щоденна статистика біржових угод"),
         ("500 MDL / lună", "MDL 500 / month", "500 MDL / месяц", "500 MDL / місяць")),
    ]),
]

def table_html(pg):
    i = IDX[pg.lang]
    rows, n = [], 0
    for title, items in SECTIONS:
        rows.append(f'<tr class="bx-fee-sec"><th colspan="3" scope="rowgroup">{title[i]}</th></tr>')
        for desc, fee in items:
            n += 1
            rows.append(f'<tr><td class="bx-fee-nr">{n}</td><td class="bx-fee-desc">{desc[i]}</td><td class="bx-fee-val">{fee[i]}</td></tr>')
    return (f'<div class="bx-fees-wrap"><table class="bx-fees"><caption>{T["table"][i]}</caption>'
            f'<thead><tr><th scope="col" class="bx-fee-nr">{T["nr"][i]}</th><th scope="col">{T["desc"][i]}</th>'
            f'<th scope="col" class="bx-fee-val">{T["fee"][i]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


PRINT_CSS = """
@page { size: A4; margin: 12mm 14mm 24mm 14mm;
  @bottom-left { content: "+373-22-897-700  |  office@bimx.md  |  www.bimx.md\\A %(address)s"; white-space: pre; font: 8.5pt/1.5 Arial, Helvetica, sans-serif;   /* nu Prompt: cu diacritice, Chrome omite casetele de margine */
    color: #1DB0F0; vertical-align: top; padding-top: 4mm; width: 100%%; } }
html, body { margin: 0; background: #fff; }
body { font: 9pt/1.3 Prompt, sans-serif; color: #1F2333; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 18pt; margin-bottom: 7mm; }
.head img { flex: none; height: 26pt; width: 92pt; }
.head div { flex: 1 1 auto; min-width: 0; font-size: 8.5pt; color: #1A2266; text-align: right; }
table { width: 100%%; border-collapse: collapse; }
caption { padding: 6pt; background: #1DB0F0; color: #fff; font-weight: 700; font-size: 11pt; text-transform: uppercase; border: .75pt solid #1A2266; border-bottom: 0; }
th, td { border: .75pt solid #1A2266; padding: 3.5pt 6pt; }
thead th { background: #1DB0F0; color: #fff; font-weight: 700; }
.sec th { background: #1A2266; color: #fff; text-align: left; font-weight: 700; }
.nr { width: 22pt; text-align: center; }
.val { width: 27%%; text-align: center; font-weight: 700; color: #1A2266; }
thead .val { color: #fff; }
tr { break-inside: avoid; }
"""


def print_html(lang, logo):
    i = IDX[lang]
    rows, n = [], 0
    for title, items in SECTIONS:
        rows.append(f'<tr class="sec"><th colspan="3">{title[i]}</th></tr>')
        for desc, fee in items:
            n += 1
            rows.append(f'<tr><td class="nr">{n}</td><td>{desc[i]}</td><td class="val">{fee[i]}</td></tr>')
    css = PRINT_CSS % {"address": T["address"][i]}
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{T["table"][i]}</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&amp;display=block" rel="stylesheet">'
            f'<style>{css}</style></head><body><header class="head"><img src="{logo}" alt="BIMx">'
            f'<div>{T["company"][i]}  |  {T["capital"][i]}  |  IDNO 1025600073907</div></header>'
            f'<table><caption>{T["table"][i]}</caption><thead><tr><th class="nr">{T["nr"][i]}</th><th>{T["desc"][i]}</th>'
            f'<th class="val">{T["fee"][i]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></body></html>')


def pdf_path(lang):
    """PDF-ul pentru limba paginii: RO = documentul oficial; EN/RU/UK = traducerea generată la build (dacă există)."""
    own = LANG_PREFIX[lang] + PATH.replace("index.html", f"BIMx-tarifele-bursei-{lang}.pdf")
    return own if lang != "ro" and (DIST / own).exists() else PDF


def head_links(pg):
    url = lambda lang: SITE_URL + LANG_PREFIX[lang] + PATH.replace("index.html", "")
    links = [f'<link rel="canonical" href="{url(pg.lang)}">']
    links += [f'<link rel="alternate" hreflang="{x}" href="{url(x)}">' for x in SITE_LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{url("ro")}">')
    return "\n".join(links)


def build_tariffs_page(text, pg):
    if str(pg.inner) != PATH or "bx-fees" in text:
        return text
    i = IDX[pg.lang]
    title = T["title"][i]
    text = re.sub(r'<span aria-current="page">[^<]*</span>', f'<span aria-current="page">{title}</span>', text, count=1)
    text = re.sub(r'(<h1 class="page_title">)[^<]*(</h1>)', lambda m: m.group(1) + title + m.group(2), text, count=1)
    # conținutul: în locul categoriilor de comisioane și al blocului „Nomenclatorul complet” vin tabelul și descărcarea PDF
    start = text.find('<div class="container">\n        <div class="costs">')
    end = text.find('<div class="new_call_to_action">')
    if start < 0 or end < 0:
        return text
    end = text.rfind('<div class="container">', start, end)
    from .fixes import ICON_DOC, human_size
    path = pdf_path(pg.lang)
    name, new_tab = T["doc"][i], pg.t["new_tab"]
    doc = (f'<ul class="bx-docs bx-org-doc"><li class="bx-doc">{ICON_DOC}<div><h2>{name}</h2>'
           f'<p class="bx-file">PDF · {human_size(path, pg.lang)} · {pg.lang.upper() if path != PDF else "RO"}</p></div>'
           f'<a class="bx-doc-btn" href="{pg.asset(path)}" target="_blank" rel="noopener">{pg.t["doc_download"]}'
           f'<span class="screen-reader-text"> {name} {new_tab}</span></a></li></ul>')
    body = f'<div class="container bx-fees-page">{table_html(pg)}{doc}</div>\n    <hr>\n    '
    text = text[:start] + body + text[end:]
    text = re.sub(r'<title>[^<]*</title>', f'<title>{title} – BIMx</title>', text, count=1)
    text = re.sub(r'\s*<link rel="canonical"[^>]*>', "", text)
    return text.replace("</title>", "</title>\n" + head_links(pg), 1)


def create_tariffs_pages():
    """Pagina „Tarifele Bursei” în toate limbile, din pagina costuri/ (aceeași adâncime, deci linkurile relative rămân valabile),
    și PDF-urile traduse (EN/RU/UK), tipărite cu Chrome din tabel; fără Chrome, toate limbile primesc PDF-ul oficial (RO)."""
    import tempfile
    from pathlib import Path
    from .pdf import find_chrome, print_pdf
    chrome = find_chrome()
    logo = DIST / "assets/img/bimx-logo.svg"
    for lang in SITE_LANGS:
        if lang == "ro" or not chrome or not logo.exists():
            continue
        out = DIST / LANG_PREFIX[lang] / PATH.replace("index.html", f"BIMx-tarifele-bursei-{lang}.pdf")
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "tarife.html"
            src.write_text(print_html(lang, logo.as_uri()), encoding="utf-8")
            if not print_pdf(chrome, src, out) and out.exists():
                out.unlink()
    for lang in SITE_LANGS:
        src = DIST / LANG_PREFIX[lang] / SOURCE
        if not src.exists():
            continue
        dest = DIST / LANG_PREFIX[lang] / PATH
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def rename_cost_links(text, pg):
    """Linkurile spre pagina unificată poartă numele ei („Costuri” → „Tarifele Bursei”), în toate limbile."""
    title = T["title"][IDX[pg.lang]]
    return re.sub(r'(<a href="[^"]*(?:costuri|tarifele-bursei)/(?:index\.html)?"[^>]*>)(\s*)(?:Costuri|Costs|Расходы|Витрати)(\s*<)',
                  lambda m: m.group(1) + m.group(2) + title + m.group(3), text)
