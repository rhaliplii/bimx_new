"""Secțiunea „Noutăți & Comunicate”, în RO, EN, RU și UK: o pagină de ansamblu și câte o pagină pentru fiecare tab.

  noutati/                              Toate (pagina de ansamblu, în meniu)
  category/anunturi-bimx/               Anunțuri BIMx (cu filtre pe categorii)
  category/avize-de-piata/              Avize de piață (reguli, comisioane, calendar, membri, instrumente)
  category/anunturi-ale-emitentilor/    Anunțuri ale emitenților

Taburile sunt linkuri între pagini cu adrese proprii (fiecare pagină are titlul, descrierea, canonical și hreflang ei), iar
lista e generată la build din NEWS / NOTICES / ISSUERS, deci conținutul e în HTML, fără JavaScript. replica.js face doar
filtrarea pe categorii din „Anunțuri BIMx” (?cat=…). Paginile fără conținut au o stare goală și noindex până la primul articol.
Paginile se creează din pagina temei category/anunturi-bimx/ (create_tab_pages), înainte de corecturi.
"""
import datetime
import os
import posixpath
import re

from .config import DIST, LANG_PREFIX, SITE_LANGS

IDX = {"ro": 0, "en": 1, "ru": 2, "uk": 3}

# categoriile comunicatelor BIMx: (singular pe rând, plural pe filtru), fiecare în RO, EN, RU, UK
CATS = {
    "parteneriat": (("Parteneriat", "Partnership", "Партнёрство", "Партнерство"),
                    ("Parteneriate", "Partnerships", "Партнёрства", "Партнерства")),
    "evenimente": (("Evenimente", "Events", "События", "Події"), ("Evenimente", "Events", "События", "Події")),
    "admitere": (("Admitere", "Admission", "Допуск", "Допуск"), ("Admitere", "Admission", "Допуск", "Допуск")),
    "licenta": (("Licență", "Licence", "Лицензия", "Ліцензія"), ("Licență", "Licence", "Лицензия", "Ліцензія")),
    "actionari": (("Acționari", "Shareholders", "Акционеры", "Акціонери"), ("Acționari", "Shareholders", "Акционеры", "Акціонери")),
}

# comunicatele BIMx, de la cel mai nou: (cale, dată, categorie, cheia din home.NEWS_EDIT, rezumat RO/EN/RU/UK, fotografie)
# fotografia (fișier, text alternativ, legendă) apare doar în articol și ca imagine de partajare, nu în listă
NEWS = [
    ("2026/10/05/bimx-si-frankfurt-school-semneaza-un-memorandum-de-intelegere", "2026-10-05", "parteneriat", "bimx-si-frankfurt-school",
     ("Cooperarea vizează dezvoltarea pieței de capital, pregătirea profesională a specialiștilor și consolidarea capacităților participanților la piață.",
      "The cooperation covers capital market development, professional education and capacity building for market participants.",
      "Сотрудничество охватывает развитие рынка капитала, профессиональную подготовку специалистов и укрепление потенциала участников рынка.",
      "Співпраця охоплює розвиток ринку капіталу, професійну підготовку фахівців і зміцнення потенціалу учасників ринку."), None),
    ("2026/09/28/capital-market-forum-2026", "2026-09-28", "evenimente", "capital-market-forum-2026",
     ("BIMx urmărește ca, până în 2030, capitalizarea bursieră a Republicii Moldova să ajungă la 18% din PIB.",
      "BIMx aims for the market capitalisation of the Republic of Moldova to reach 18% of GDP by 2030.",
      "BIMx стремится к тому, чтобы к 2030 году рыночная капитализация Республики Молдова достигла 18 % ВВП.",
      "BIMx прагне, щоб до 2030 року ринкова капіталізація Республіки Молдова досягла 18 % ВВП."),
     ("assets/img/news/capital-market-forum-2026.webp",
      ("Veronica Arpintin, CEO BIMx, la tribuna Capital Market Forum 2026",
       "Veronica Arpintin, BIMx CEO, speaking at Capital Market Forum 2026",
       "Вероника Арпинтин, генеральный директор BIMx, выступает на Capital Market Forum 2026",
       "Вероніка Арпінтін, CEO BIMx, виступає на Capital Market Forum 2026"),
      ("Veronica Arpintin, CEO BIMx, la Capital Market Forum 2026. Foto: BIMx",
       "Veronica Arpintin, BIMx CEO, at Capital Market Forum 2026. Photo: BIMx",
       "Вероника Арпинтин, генеральный директор BIMx, на Capital Market Forum 2026. Фото: BIMx",
       "Вероніка Арпінтін, CEO BIMx, на Capital Market Forum 2026. Фото: BIMx"))),
    ("2026/09/28/bimx-a-initiat-procesul-de-admitere-a-participantilor", "2026-09-28", "admitere", "bimx-a-initiat-procesul-de-admitere",
     ("Agenții de bursă și emitenții pot începe procedurile de admitere. Prima listare este planificată până la sfârșitul anului 2026.",
      "Brokers and issuers can now start the admission procedures. The first listing is planned by the end of 2026.",
      "Брокеры и эмитенты могут начать процедуры допуска. Первый листинг запланирован до конца 2026 года.",
      "Брокери та емітенти можуть розпочати процедури допуску. Перший лістинг заплановано до кінця 2026 року."), None),
    ("2026/08/25/comunicat-de-presa", "2026-08-25", "licenta", "comunicat-de-presa",
     ("Licența și autorizațiile permit administrarea unei piețe reglementate și a unui sistem multilateral de tranzacționare.",
      "The licence and authorisations allow BIMx to manage a regulated market and a multilateral trading facility.",
      "Лицензия и разрешения позволяют управлять регулируемым рынком и многосторонней торговой системой.",
      "Ліцензія та дозволи дають змогу управляти регульованим ринком і багатосторонньою торговельною системою."), None),
    ("2026/08/25/in-atentia-actionarilor-o-p-bursa-internationala-a-moldovei-s-a-bim", "2026-08-25", "actionari", "in-atentia-actionarilor",
     ("Comunicat informativ privind hotărârile adoptate de adunarea generală extraordinară a acționarilor.",
      "Information notice on the resolutions adopted by the extraordinary general meeting of shareholders.",
      "Информационное сообщение о решениях внеочередного общего собрания акционеров.",
      "Інформаційне повідомлення про рішення позачергових загальних зборів акціонерів."), None),
    ("2026/06/17/bimx-depune-dosarul-pentru-obtinerea-licentei-de-operator-de-piata", "2026-06-17", "licenta", "bimx-depune-dosarul",
     ("BIMx a depus la Comisia Națională a Pieței Financiare dosarul pentru obținerea licenței de operator de piață.",
      "BIMx has filed its application for a market operator licence with the National Commission for Financial Markets.",
      "BIMx подала в Национальную комиссию по финансовому рынку документы на получение лицензии оператора рынка.",
      "BIMx подала до Національної комісії з фінансового ринку документи на отримання ліцензії оператора ринку."), None),
    ("2026/06/11/comunicat-informativ-11-iunie-2026", "2026-06-11", "actionari", "comunicat-informativ-11-iunie",
     ("Hotărârea adunării generale extraordinare a acționarilor din 11 iunie 2026.",
      "Resolution of the extraordinary general meeting of shareholders of 11 June 2026.",
      "Решение внеочередного общего собрания акционеров от 11 июня 2026 г.",
      "Рішення позачергових загальних зборів акціонерів від 11 червня 2026 р."), None),
    ("2026/05/28/comunicat-informativ-28-mai-2026", "2026-05-28", "actionari", "comunicat-informativ-28-mai",
     ("Hotărârea adunării generale extraordinare a acționarilor din 28 mai 2026.",
      "Resolution of the extraordinary general meeting of shareholders of 28 May 2026.",
      "Решение внеочередного общего собрания акционеров от 28 мая 2026 г.",
      "Рішення позачергових загальних зборів акціонерів від 28 травня 2026 р."), None),
    ("2026/04/02/comunicat-informativ-02-aprilie-2026", "2026-04-02", "actionari", "comunicat-informativ-02-aprilie",
     ("Hotărârea adunării generale extraordinare a acționarilor din 2 aprilie 2026.",
      "Resolution of the extraordinary general meeting of shareholders of 2 April 2026.",
      "Решение внеочередного общего собрания акционеров от 2 апреля 2026 г.",
      "Рішення позачергових загальних зборів акціонерів від 2 квітня 2026 р."), None),
]

# avizele de piață (reguli, comisioane, calendar, membri, instrumente admise sau suspendate), de la cel mai nou; niciunul încă
NOTICES = []

# anunțurile emitenților: niciunul până la primele listări
ISSUERS = []

# taburile: cheie → pagina (calea în interiorul limbii)
TABS = [("toate", "noutati/index.html"), ("bimx", "category/anunturi-bimx/index.html"),
        ("avize", "category/avize-de-piata/index.html"), ("emitenti", "category/anunturi-ale-emitentilor/index.html")]
SITE_URL = "https://rhaliplii.github.io/bimx_new/"   # adresa publică (canonical și hreflang cer adrese complete)

MONTHS = {  # (numele lunii în dată, abrevierea din insignă)
    "ro": [("ianuarie", "IAN."), ("februarie", "FEBR."), ("martie", "MART."), ("aprilie", "APR."), ("mai", "MAI"), ("iunie", "IUN."),
           ("iulie", "IUL."), ("august", "AUG."), ("septembrie", "SEPT."), ("octombrie", "OCT."), ("noiembrie", "NOIEMBR."), ("decembrie", "DEC.")],
    "en": [("January", "JAN"), ("February", "FEB"), ("March", "MAR"), ("April", "APR"), ("May", "MAY"), ("June", "JUN"),
           ("July", "JUL"), ("August", "AUG"), ("September", "SEP"), ("October", "OCT"), ("November", "NOV"), ("December", "DEC")],
    "ru": [("января", "ЯНВ."), ("февраля", "ФЕВР."), ("марта", "МАРТА"), ("апреля", "АПР."), ("мая", "МАЯ"), ("июня", "ИЮН."),
           ("июля", "ИЮЛ."), ("августа", "АВГ."), ("сентября", "СЕНТ."), ("октября", "ОКТ."), ("ноября", "НОЯБ."), ("декабря", "ДЕК.")],
    "uk": [("січня", "СІЧ."), ("лютого", "ЛЮТ."), ("березня", "БЕР."), ("квітня", "КВІТ."), ("травня", "ТРАВ."), ("червня", "ЧЕРВ."),
           ("липня", "ЛИП."), ("серпня", "СЕРП."), ("вересня", "ВЕР."), ("жовтня", "ЖОВТ."), ("листопада", "ЛИСТ."), ("грудня", "ГРУД.")],
}

T = {
    "title": ("Noutăți & Comunicate", "News & Announcements", "Новости и Объявления", "Новини та Оголошення"),
    "lead_toate": ("Anunțurile Bursei Internaționale a Moldovei, avizele de piață și anunțurile emitenților admiși la tranzacționare.",
                   "Announcements of the Moldova International Stock Exchange, market notices and announcements by issuers admitted to trading.",
                   "Объявления Международной фондовой биржи Молдовы, рыночные уведомления и объявления эмитентов, допущенных к торгам.",
                   "Оголошення Міжнародної фондової біржі Молдови, ринкові повідомлення та оголошення емітентів, допущених до торгів."),
    "lead_bimx": ("Anunțurile oficiale ale Bursei Internaționale a Moldovei: licențiere, admitere, parteneriate, evenimente și hotărârile acționarilor.",
                  "Official announcements of the Moldova International Stock Exchange: licensing, admission, partnerships, events and shareholder resolutions.",
                  "Официальные объявления Международной фондовой биржи Молдовы: лицензирование, допуск, партнёрства, события и решения акционеров.",
                  "Офіційні оголошення Міжнародної фондової біржі Молдови: ліцензування, допуск, партнерства, події та рішення акціонерів."),
    "lead_avize": ("Avizele operaționale ale BIMx: modificări ale regulilor, comisioane, calendarul de tranzacționare, membri și instrumente admise sau suspendate.",
                   "BIMx operational notices: rule changes, fees, the trading calendar, admitted members and instruments admitted or suspended.",
                   "Операционные уведомления BIMx: изменения правил, комиссии, торговый календарь, допущенные участники и инструменты, допущенные или приостановленные.",
                   "Операційні повідомлення BIMx: зміни правил, комісії, торговельний календар, допущені учасники та інструменти, допущені або призупинені."),
    "lead_emitenti": ("Raportări curente, rapoarte financiare și hotărâri ale adunărilor generale publicate de emitenții admiși la tranzacționare.",
                      "Current reports, financial reports and general meeting resolutions published by issuers admitted to trading.",
                      "Текущие отчёты, финансовые отчёты и решения общих собраний, публикуемые эмитентами, допущенными к торгам.",
                      "Поточні звіти, фінансові звіти та рішення загальних зборів, які публікують емітенти, допущені до торгів."),
    "tabs_label": ("Tipul publicației", "Publication type", "Тип публикации", "Тип публікації"),
    "tab_all": ("Toate", "All", "Все", "Усі"),
    "tab_bimx": ("Anunțuri BIMx", "BIMx announcements", "Объявления BIMx", "Оголошення BIMx"),
    "tab_avize": ("Avize de piață", "Market notices", "Рыночные уведомления", "Ринкові повідомлення"),
    "tab_issuers": ("Anunțuri ale emitenților", "Issuer announcements", "Объявления эмитентов", "Оголошення емітентів"),
    "type_bimx": ("Anunț BIMx", "BIMx announcement", "Объявление BIMx", "Оголошення BIMx"),
    "type_aviz": ("Aviz de piață", "Market notice", "Рыночное уведомление", "Ринкове повідомлення"),
    "cat": ("Categoria", "Category", "Категория", "Категорія"),
    "cat_all": ("Toate categoriile", "All categories", "Все категории", "Усі категорії"),
    "year": ("Anul", "Year", "Год", "Рік"),
    "year_all": ("Toți anii", "All years", "Все годы", "Усі роки"),
    "none": ("Nu există publicații pentru filtrele alese.", "There are no publications for the selected filters.",
             "Нет публикаций по выбранным фильтрам.", "Немає публікацій за обраними фільтрами."),
    "new": ("Nou", "New", "Новое", "Нове"),
    "read": ("Citiți comunicatul", "Read the announcement", "Читать сообщение", "Читати повідомлення"),
    "read_aviz": ("Citiți avizul", "Read the notice", "Читать уведомление", "Читати повідомлення"),
    "empty_h": ("Încă nu există anunțuri ale emitenților", "No issuer announcements yet",
                "Объявлений эмитентов пока нет", "Оголошень емітентів поки немає"),
    "empty_p": ("Anunțurile companiilor admise la tranzacționare (raportări curente, rapoarte financiare și hotărâri ale adunărilor "
                "generale) vor fi publicate aici după primele listări, planificate până la sfârșitul anului 2026.",
                "Announcements by companies admitted to trading (current reports, financial reports and general meeting resolutions) "
                "will be published here after the first listings, planned by the end of 2026.",
                "Объявления компаний, допущенных к торгам (текущие отчёты, финансовые отчёты и решения общих собраний), будут "
                "публиковаться здесь после первых листингов, запланированных до конца 2026 года.",
                "Оголошення компаній, допущених до торгів (поточні звіти, фінансові звіти та рішення загальних зборів), "
                "публікуватимуться тут після перших лістингів, запланованих до кінця 2026 року."),
    "empty_hint": ("Le veți putea filtra după emitent, tipul raportului și perioadă.",
                   "You will be able to filter them by issuer, report type and period.",
                   "Их можно будет фильтровать по эмитенту, типу отчёта и периоду.",
                   "Їх можна буде фільтрувати за емітентом, типом звіту та періодом."),
    "avize_empty_h": ("Încă nu există avize de piață", "No market notices yet", "Рыночных уведомлений пока нет", "Ринкових повідомлень поки немає"),
    "avize_empty_p": ("Aici vor fi publicate avizele de piață: modificări ale regulilor, comisioane, calendarul de tranzacționare și zilele "
                      "nelucrătoare, membrii admiși și instrumentele admise sau suspendate. Primele avize vor apărea odată cu admiterea primilor membri.",
                      "Market notices will be published here: rule changes, fees, the trading calendar and non-trading days, admitted members "
                      "and instruments admitted or suspended. The first notices will appear when the first members are admitted.",
                      "Здесь будут публиковаться рыночные уведомления: изменения правил, комиссии, торговый календарь и неторговые дни, "
                      "допущенные участники и инструменты, допущенные или приостановленные. Первые уведомления появятся с допуском первых участников.",
                      "Тут публікуватимуться ринкові повідомлення: зміни правил, комісії, торговельний календар і неторговельні дні, "
                      "допущені учасники та інструменти, допущені або призупинені. Перші повідомлення з’являться з допуском перших учасників."),
    "calendar": ("Calendarul de tranzacționare", "Trading calendar", "Календарь торгов", "Календар торгів"),
    "empty_bimx": ("Vedeți anunțurile BIMx", "See BIMx announcements", "Смотреть объявления BIMx", "Переглянути оголошення BIMx"),
    "empty_listing": ("Procesul de listare", "Listing process", "Процесс листинга", "Процес лістингу"),
    "press_h": ("Contact pentru presă", "Press contact", "Контакты для прессы", "Контакти для преси"),
    "press_p": ("Întrebări despre anunțurile BIMx și solicitări de interviu.",
                "Questions about BIMx announcements and interview requests.",
                "Вопросы об объявлениях BIMx и запросы на интервью.",
                "Запитання щодо повідомлень BIMx і запити на інтерв’ю."),
}

ARROW = ('<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.3 8h9.4M8 3.3 12.7 8 8 12.7" '
         'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_BUILDING = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/></svg>')

ICON_CHART = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/></svg>')

PAGE = "category/anunturi-bimx/index.html"     # pagina temei din care se creează toate paginile secțiunii
HUB = "noutati/index.html"


def tab_of(pg):
    return next((k for k, path in TABS if str(pg.inner) == path), None)


def entries(tab):
    """(intrare, sursă) pentru tabul dat; Toate = toate sursele, cele mai noi primele."""
    rows = {"bimx": [(e, "bimx") for e in NEWS], "avize": [(e, "aviz") for e in NOTICES], "emitenti": [(e, "emitent") for e in ISSUERS]}
    if tab != "toate":
        return rows[tab]
    return sorted(rows["bimx"] + rows["avize"] + rows["emitenti"], key=lambda r: r[0][1], reverse=True)


def date_parts(iso, lang):
    d = datetime.date.fromisoformat(iso)
    name, abbr = MONTHS[lang][d.month - 1]
    short = abbr.lower().capitalize() if lang == "en" else abbr.lower()     # „28 sept. 2026”, „28 Sep 2026”
    return f"{d.day} {short} {d.year}", f"{d.day} {name} {d.year}"


NEW_DAYS = 30          # eticheta „Nou” stă pe cel mai recent articol cel mult atâtea zile (replica.js o ascunde după)


def item_html(entry, source, pg, pos, show_type):
    """pos: poziția în listă; cel mai recent articol (pos 0) primește eticheta „Nou”."""
    from .home import NEWS_EDIT
    path, iso, cat, key, excerpts, photo = entry
    i = IDX[pg.lang]
    title = NEWS_EDIT[key][i][1]
    _, full = date_parts(iso, pg.lang)
    d = datetime.date.fromisoformat(iso)
    abbr = MONTHS[pg.lang][d.month - 1][1]
    new = f'<span class="bx-n-new" data-date="{iso}" data-days="{NEW_DAYS}">{T["new"][i]}</span>' if pos == 0 else ""
    kind = f'<span class="bx-n-type">{T["type_aviz" if source == "aviz" else "type_bimx"][i]}</span>' if show_type else ""
    return (f'<a class="bx-news-item" href="{pg.link(path + "/index.html")}" data-source="{source}" data-cat="{cat}" data-year="{iso[:4]}">'
            f'<time class="bx-n-date" datetime="{iso}" title="{full}"><span class="bx-n-day">{d.day}</span><span class="bx-n-mon">{abbr}</span></time>'
            f'<span class="bx-n-body">'
            f'<span class="bx-n-meta">{kind}<span class="bx-n-cat">{CATS[cat][0][i]}</span>{new}</span>'
            f'<span class="bx-n-title" role="heading" aria-level="2">{title}</span>'
            f'<span class="bx-n-ex">{excerpts[i]}</span>'
            f'</span>{ARROW}</a>')


ARROW = ('<svg class="bx-n-arr" width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.3 8h9.4M8 3.3 12.7 8 8 12.7" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def cat_html(pg, tab):
    """Filtrul pe categorie (doar la „Anunțuri BIMx”), în rândul taburilor, lângă „Anul”."""
    if tab != "bimx":
        return ""
    i = IDX[pg.lang]
    opts = [f'<option value="toate" selected>{T["cat_all"][i]}</option>']
    for k, (_, plural) in CATS.items():
        n = sum(1 for e in NEWS if e[2] == k)
        if n:
            opts.append(f'<option value="{k}">{plural[i]} ({n})</option>')
    return (f'<label class="bx-news-year bx-news-cat"><span>{T["cat"][i]}</span><select data-filter="cat">{"".join(opts)}</select></label>')


def tab_label(tab, i):
    return T["title"][i] if tab == "toate" else T[{"bimx": "tab_bimx", "avize": "tab_avize", "emitenti": "tab_issuers"}[tab]][i]


def year_html(pg, tab):
    """Filtrul pe an, în rândul taburilor: implicit cel mai recent an (ca la burse); „Toți anii” arată toată arhiva."""
    i = IDX[pg.lang]
    years = sorted({e[1][:4] for e, _ in entries(tab)}, reverse=True)
    if not years:                                   # pagină fără publicații: nimic de filtrat
        return ""
    opts = "".join(f'<option value="{y}"{" selected" if n == 0 else ""}>{y}</option>' for n, y in enumerate(years))
    return (f'<label class="bx-news-year"><span>{T["year"][i]}</span><select data-filter="an" data-default="{years[0]}">'
            f'{opts}<option value="toate">{T["year_all"][i]}</option></select></label>')


def tabs_html(pg, current):
    """Taburile: linkuri spre paginile secțiunii (pagina curentă are aria-current); filtrul pe an, dacă e cazul, în dreapta."""
    i = IDX[pg.lang]
    labels = {"toate": T["tab_all"][i], "bimx": T["tab_bimx"][i], "avize": T["tab_avize"][i], "emitenti": T["tab_issuers"][i]}
    out = []
    for k, path in TABS:
        cur = ' aria-current="page"' if k == current else ""
        out.append(f'<a class="bx-news-tab" href="{pg.link(path)}"{cur}>{labels[k]}</a>')
    nav = f'<nav class="bx-news-tabs" aria-label="{T["tabs_label"][i]}">{"".join(out)}</nav>'
    # pe mobil, taburile devin un select (navighează la schimbare; replica.js)
    opts = "".join(f'<option value="{pg.link(path)}"{" selected" if k == current else ""}>{labels[k]}</option>' for k, path in TABS)
    nav += (f'<label class="bx-news-year bx-news-tabsel"><span class="bx-vh">{T["tabs_label"][i]}</span>'
            f'<select data-nav="tab">{opts}</select></label>')
    filters = cat_html(pg, current) + year_html(pg, current)
    filters = f'<div class="bx-news-filters">{filters}</div>' if filters else ""
    return f'<div class="bx-news-tabbar">{nav}{filters}</div>'


def empty_html(pg, tab):
    i = IDX[pg.lang]
    if tab == "avize":
        icon, head, body, hint, second = (ICON_CHART, T["avize_empty_h"][i], T["avize_empty_p"][i], "",
                                          (T["calendar"][i], "trading-calendar/index.html"))
    else:
        icon, head, body, hint, second = (ICON_BUILDING, T["empty_h"][i], T["empty_p"][i], T["empty_hint"][i],
                                          (T["empty_listing"][i], "procesul-de-listare/index.html"))
    hint = f'<p class="bx-news-empty-hint">{hint}</p>' if hint else ""
    return (f'<section class="bx-empty bx-news-empty" aria-labelledby="bx-empty-h">'
            f'<span class="bx-news-empty-icon">{icon}</span><h2 id="bx-empty-h">{head}</h2><p>{body}</p>{hint}'
            f'<div class="bx-news-empty-actions"><a class="bx-btn-primary" href="{pg.link(TABS[1][1])}">{T["empty_bimx"][i]}</a>'
            f'<a class="bx-btn-secondary" href="{pg.link(second[1])}">{second[0]}</a></div></section>')


def body_html(pg, tab):
    i = IDX[pg.lang]
    rows = entries(tab)
    # tipul publicației apare doar în „Toate”, unde se amestecă sursele (și doar când există mai multe surse)
    show_type = tab == "toate" and len({src for _, src in rows}) > 1
    items = "".join(item_html(e, src, pg, n, show_type) for n, (e, src) in enumerate(rows))
    listing = (f'<div class="bx-news-list">{items}</div><p class="bx-news-none" hidden>{T["none"][i]}</p>' if rows
               else empty_html(pg, tab))
    press = (f'<section class="bx-news-press" aria-labelledby="bx-news-press-h"><div><h2 id="bx-news-press-h">{T["press_h"][i]}</h2>'
             f'<p>{T["press_p"][i]}</p></div><div class="bx-news-press-links"><a href="mailto:office@bimx.md">office@bimx.md</a>'
             f'<a href="tel:+37322897700">+373 22 89 77 00</a></div></section>')
    return f'<div class="container bx-news">{listing}{press}</div>'


SEP = ('<li aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.25 10.5L8.75 7L5.25 3.5" '
       'stroke="white" stroke-opacity="0.6" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/></svg></li>')


def head_links(pg, tab):
    """canonical și hreflang cu adrese complete; noindex pe paginile fără conținut (se scoate singur la primul articol)."""
    path = dict(TABS)[tab]
    url = lambda lang: SITE_URL + LANG_PREFIX[lang] + path.replace("index.html", "")
    links = [f'<link rel="canonical" href="{url(pg.lang)}">']
    links += [f'<link rel="alternate" hreflang="{x}" href="{url(x)}">' for x in SITE_LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{url("ro")}">')
    if not entries(tab):
        links.append('<meta name="robots" content="noindex, follow">')
    return "\n".join(links)


def build_news_page(text, pg):
    """O pagină a secțiunii: antetul (breadcrumb, titlu, descriere, taburi), lista generată, fără „Alte categorii”."""
    tab = tab_of(pg)
    if not tab or "bx-news-tabs" in text:
        return text
    i = IDX[pg.lang]
    title = tab_label(tab, i)
    hero = re.search(r'<div class="archive_main_section">[\s\S]*?</div>\s*</div>', text)
    if not hero:
        return text
    h = hero.group(0).replace('class="archive_main_section"', 'class="archive_main_section bx-news-hero"', 1)
    home = re.search(r'<li><a href="[^"]*">[^<]*</a></li>', h).group(0)          # „Acasă”, cu linkul și textul în limba paginii
    crumbs = [home, SEP]
    if tab == "toate":
        crumbs.append(f'<li><span aria-current="page">{T["title"][i]}</span></li>')
    else:
        crumbs += [f'<li><a href="{pg.link(HUB)}">{T["title"][i]}</a></li>', SEP, f'<li><span aria-current="page">{title}</span></li>']
    h = re.sub(r'<ul class="breadcrumbs">[\s\S]*?</ul>', lambda m: '<ul class="breadcrumbs">' + "".join(crumbs) + "</ul>", h, count=1)
    h = re.sub(r'\s*<div class="cat_name">[\s\S]*?</div>', "", h, count=1)
    h = re.sub(r'(<h1[^>]*>)[\s\S]*?(</h1>)', lambda m: m.group(1) + title + m.group(2), h, count=1)
    h = re.sub(r'<p>[\s\S]*?</p>', lambda m: f'<p>{T["lead_" + tab][i]}</p>{tabs_html(pg, tab)}', h, count=1)
    text = text[:hero.start()] + h + text[hero.end():]
    # bara de filtre a temei (o singură etichetă, linkuri spre aceeași pagină) iese
    text = re.sub(r'<div class="container_fluid">\s*<div class="filter_wrap">[\s\S]*?</div>\s*</div>\s*</div>', "", text, count=1)
    # lista temei (articolul recomandat, grila, paginarea) și „Alte categorii” ies; buletinul de la final rămâne
    text = re.sub(r'<div class="container">\s*<section class="featured-post-section">[\s\S]*?'
                  r'(?=<div class="container_fluid">\s*<div class="related_categories">)', lambda m: body_html(pg, tab), text, count=1)
    text = re.sub(r'\s*<div class="related_categories">[\s\S]*?</section>\s*</div>', "", text, count=1)
    full = title if tab == "toate" else f'{title} – {T["title"][i]}'
    text = re.sub(r'<title>[^<]*</title>', f'<title>{full} – BIMx</title>', text, count=1)
    text = re.sub(r'\s*<link rel="canonical"[^>]*>', "", text)
    return text.replace("</title>", "</title>\n" + head_links(pg, tab), 1)


URL_ATTR = re.compile(r'(\s(?:href|src|action)=(["\']))(.*?)(\2)|(\ssrcset=(["\']))(.*?)(\6)|(url\(\s*[\'"]?)([^\'")]+)')


def relocate(text, old_dir, new_dir):
    """Linkurile relative ale unei pagini mutate din old_dir în new_dir (căi relative la dist/)."""
    def move(url):
        if not url or url.startswith(("#", "/", "http:", "https:", "mailto:", "tel:", "data:", "javascript:", "{")):
            return url
        path, rest = re.match(r"([^?#]*)(.*)", url).groups()        # rest: ?query și #fragment, neschimbate
        if not path:
            return url
        target = posixpath.normpath(posixpath.join(old_dir, path))
        return os.path.relpath(target, new_dir).replace(os.sep, "/") + rest
    def fix(m):
        if m.group(1):                                            # href / src / action, cu ghilimele duble sau simple
            return m.group(1) + move(m.group(3)) + m.group(4)
        if m.group(5):
            parts = [p.strip().split(" ", 1) for p in m.group(7).split(",")]
            return m.group(5) + ", ".join(" ".join([move(p[0])] + p[1:]) for p in parts) + m.group(8)
        return m.group(9) + move(m.group(10))
    return URL_ATTR.sub(fix, text)


def create_tab_pages():
    """Paginile secțiunii se creează din pagina temei category/anunturi-bimx/, în toate limbile, înainte de corecturi."""
    for lang in SITE_LANGS:
        pre = LANG_PREFIX[lang]
        src = DIST / pre / PAGE
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8")
        for _, path in TABS:
            if path == PAGE:
                continue
            dest = DIST / pre / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            old_dir, new_dir = posixpath.dirname(pre + PAGE), posixpath.dirname(pre + path)
            dest.write_text(text if old_dir.count("/") == new_dir.count("/") else relocate(text, old_dir, new_dir), encoding="utf-8")


def photo_for(pg):
    """(fișier, text alternativ, legendă) pentru articolul pe care îl afișează pg, dacă are fotografie."""
    i = IDX[pg.lang]
    for path, *_, photo in NEWS:
        if photo and str(pg.inner) == path + "/index.html":
            src, alts, captions = photo
            return src, alts[i], captions[i]
    return None


def article_photo(text, pg):
    """Fotografia comunicatului, la începutul textului articolului, cu legendă (în listă nu apar imagini)."""
    found = photo_for(pg)
    if not found or "bx-article-photo" in text:
        return text
    src, alt, caption = found
    fig = (f'<figure class="bx-article-photo"><img src="{pg.asset(src)}" alt="{alt}" width="1200" height="705" decoding="async">'
           f'<figcaption>{caption}</figcaption></figure>')
    return text.replace('<div class="ev_description">', '<div class="ev_description">' + fig, 1)
