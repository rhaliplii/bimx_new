"""Antetul compact și subsolul nou, pe toate paginile (bimx.md și BIMx Academy), în RO, EN, RU și UK.

Antet: fără bara de sus; logo + eticheta „Pre-lansare”; meniul în sentence case; în dreapta căutarea, comutatorul
de limbă (meniu RO / EN / RU / UA) și „Intră în cont”. Căutarea devine o fereastră de dialog (stilurile în src/site/site.css, comportamentul în
src/site/search.js): se închide cu „×”, Escape sau clic în afara ei.

Subsol: identitate și contact, rețele sociale, patru coloane cu paginile funcționale, partenerii instituționali,
avertizarea despre datele de piață (textul original al notificării de pe bimx.md) și linia legală.
Formularul de contact (fereastra modală din subsolul temei) se păstrează.
"""
import re

from .config import LANG_CODES, LANG_NAMES, SITE_LANGS, pick

LINKEDIN = "https://linkedin.com/company/moldova-international-stock-exchange-bursa-internationala-a-moldovei"
FACEBOOK = "https://www.facebook.com/BIMx.MD/"

LICENCE_NO = "000945"  # numărul licenței de operator de piață acordate de CNPF
CNPF_REGISTER = "https://www.cnpf.md/ro/registrele-actelor-permisive-6412.html"

# Logo-ul din subsol, vectorial (PNG-ul original are 130 × 43 px și e neclar pe ecranele retina):
# „BIM” în fontul site-ului (Prompt 700), „x” desenat ca în logo – două brațe albe și săgeata albastră.
WORDMARK = ('<span class="bx-wordmark" aria-hidden="true"><span>BIM</span>'
            '<svg viewBox="0 0 40 34" width="30" height="26"><path fill="#fff" d="M0 0h11l29 34H29z"/>'
            '<path fill="#fff" d="M40 0H29L0 34h11z"/><path fill="#1DB0F0" d="M9 6h10l11 11-11 11H9l11-11z"/></svg></span>')

PDF_ATTR = ' target="_blank" rel="noopener"'

NAV = {"407": ("Despre noi", "About us", "О нас", "Про нас"), "408": ("Piață", "Market", "Рынок", "Ринок"),
       "409": ("Listare", "Listing", "Листинг", "Лістинг"), "410": ("BIMx Academy", "BIMx Academy", "BIMx Academy", "BIMx Academy"),
       "411": ("Noutăți & Comunicate", "News & Announcements", "Новости и Объявления", "Новини та Оголошення")}
IDX = {"ro": 0, "en": 1, "ru": 2, "uk": 3}

T = {
    "ro": {
        "prelaunch": "Pre-lansare", "strip_text": "Tranzacționarea începe până la sfârșitul anului 2026", "licence": "Licență CNPF", "register": "vezi în registru", "prelaunch_title": "Tranzacționarea nu a început; platforma ARENA intră în producție la 1 octombrie 2026",
        "lang": "Limba", "close": "Închideți căutarea", "search_hint": "Apăsați Esc pentru a închide",
        "about": "Bursa Internațională a Moldovei (BIMx) — o piață transparentă și reglementată din 2026.",
        "address": "str. Vlaicu Pârcălab 63, MD-2012, Chișinău, Republica Moldova",
        "follow": "Urmăriți BIMx",
        "cols": [
            ("Companie", [("Identitate", "identitate/index.html"), ("Consiliul și Organul Executiv", "consiliul-si-organul-executiv/index.html"),
                          ("Fondatorii BIMx", "fondatori/index.html"), ("Parteneri instituționali", "parteneri-institutionali/index.html"),
                          ("Cariere", "cariere/index.html"), ("Contacte", "contacte/index.html")]),
            ("Piață", [("Prezentare generală", "prezentare-generala/index.html"), ("Cotații în timp real", "cotatii-in-timp-real/index.html"),
                       ("Indicii Bursei", "indicii-bursei/index.html"), ("Acțiuni", "actiuni/index.html"),
                       ("Obligațiuni și finanțare verde", "obligatiuni/index.html"), ("Program de tranzacționare", "program-de-tranzactionare/index.html"),
                       ("Calendarul de tranzacționare", "trading-calendar/index.html")]),
            ("Servicii", [("Platforma de tranzacționare", "platforma-de-tranzactionare/index.html"), ("Servicii de listare", "servicii-de-listare/index.html"),
                          ("Compensare și decontare", "compensare-si-decontare/index.html"), ("Date de piață", "date-de-piata/index.html"),
                          ("Model operațional", "model-operational/index.html")]),
            ("Listare", [("Procesul de listare", "procesul-de-listare/index.html"), ("Costuri", "wp-content/uploads/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"),
                         ("Atestarea brokerilor", "atestarea-brokerilor/index.html"), ("Lista societăților", "lista-societatilor/index.html")]),
            ("Juridic și Conformitate", [("Regulamente și acte normative", "regulamente-si-acte-normative/index.html"),
                                         ("Politica de confidențialitate", "politica-de-confidentialitate/index.html"),
                                         ("Politica cookie", "politica-cookie/index.html"), ("Centru de descărcare", "centru-de-descarcare/index.html"),
                                         ("Accesibilitate", "accesibilitate-incluziune-si-diversitate/index.html")]),
        ],
        "resources": [("BIMx Academy", "academy/index.html"), ("Anunțuri BIMx", "category/anunturi-bimx/index.html"),
                      ("Știri", "category/stiri/index.html"), ("Centru media", "centru-media/index.html")],
        "resources_h": "Resurse",
        "partners": "Parteneri instituționali",
        "disclaimer_h": "Notificare privind datele de piață",
        "disclaimer": "Vă informăm că datele de piață prezentate pe această platformă au, în această etapă, caracter pur demonstrativ. "
                      "Valorile, indicii, variațiile procentuale și statisticile afișate sunt generate în scop ilustrativ, pentru a demonstra "
                      "funcționalitățile platformei, și nu reflectă tranzacții reale sau cotații în timp real ale valorilor mobiliare.",
        "accessibility": "Accesibilitate",
        "partner_names": {"invest": "Invest Moldova", "oda": "ODA – Organizația pentru Dezvoltarea Antreprenoriatului",
                          "cnpf": "CNPF – Comisia Națională a Pieței Financiare"},
    },
    "en": {
        "prelaunch": "Pre-launch", "strip_text": "Trading starts by the end of 2026", "licence": "CNPF licence", "register": "see the register", "prelaunch_title": "Trading has not started; the ARENA platform goes live on 1 October 2026",
        "lang": "Language", "close": "Close search", "search_hint": "Press Esc to close",
        "about": "Moldova International Stock Exchange (BIMx) — a transparent, regulated market since 2026.",
        "address": "63 Vlaicu Pârcălab St., MD-2012, Chișinău, Republic of Moldova",
        "follow": "Follow BIMx",
        "cols": [
            ("Company", [("Identity", "identitate/index.html"), ("Council and Executive Body", "consiliul-si-organul-executiv/index.html"),
                         ("BIMx Founders", "fondatori/index.html"), ("Institutional Partners", "parteneri-institutionali/index.html"),
                         ("Careers", "cariere/index.html"), ("Contacts", "contacte/index.html")]),
            ("Market", [("Overview", "prezentare-generala/index.html"), ("Real-Time Quotes", "cotatii-in-timp-real/index.html"),
                        ("Exchange Indices", "indicii-bursei/index.html"), ("Shares", "actiuni/index.html"),
                        ("Bonds and Green Finance", "obligatiuni/index.html"), ("Trading schedule", "program-de-tranzactionare/index.html"),
                        ("Trading calendar", "trading-calendar/index.html")]),
            ("Services", [("Trading Platform", "platforma-de-tranzactionare/index.html"), ("Listing Services", "servicii-de-listare/index.html"),
                          ("Clearing and Settlement", "compensare-si-decontare/index.html"), ("Market Data", "date-de-piata/index.html"),
                          ("Operating Model", "model-operational/index.html")]),
            ("Listing", [("Listing Process", "procesul-de-listare/index.html"), ("Costs", "wp-content/uploads/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"),
                         ("Broker Certification", "atestarea-brokerilor/index.html"), ("List of Firms", "lista-societatilor/index.html")]),
            ("Legal &amp; Compliance", [("Regulations and Legal Acts", "regulamente-si-acte-normative/index.html"),
                                        ("Privacy Policy", "politica-de-confidentialitate/index.html"),
                                        ("Cookie Policy", "politica-cookie/index.html"), ("Download Centre", "centru-de-descarcare/index.html"),
                                        ("Accessibility", "accesibilitate-incluziune-si-diversitate/index.html")]),
        ],
        "resources": [("BIMx Academy", "academy/index.html"), ("BIMx Announcements", "category/anunturi-bimx/index.html"),
                      ("News", "category/stiri/index.html"), ("Media Centre", "centru-media/index.html")],
        "resources_h": "Resources",
        "partners": "Institutional partners",
        "disclaimer_h": "Market data notice",
        "disclaimer": "Please note that, at this stage, the market data shown on this platform is for demonstration purposes only. "
                      "The values, indices, percentage changes and statistics displayed are generated for illustrative purposes, to "
                      "demonstrate the platform's features, and do not reflect real transactions or real-time quotes of securities.",
        "accessibility": "Accessibility",
        "partner_names": {"invest": "Invest Moldova", "oda": "ODA – Organisation for Entrepreneurship Development",
                          "cnpf": "CNPF – National Commission for Financial Markets"},
    },
    "ru": {
        "prelaunch": "Подготовка к запуску", "strip_text": "Торги начнутся до конца 2026 года", "licence": "Лицензия НКФР", "register": "смотреть в реестре", "prelaunch_title": "Торги ещё не начались; платформа ARENA вводится в эксплуатацию 1 октября 2026 г.",
        "lang": "Язык", "close": "Закрыть поиск", "search_hint": "Нажмите Esc, чтобы закрыть",
        "about": "Международная фондовая биржа Молдовы (BIMx) — прозрачный регулируемый рынок с 2026 года.",
        "address": "ул. Влайку Пыркэлаб, 63, MD-2012, Кишинёв, Республика Молдова",
        "follow": "BIMx в соцсетях",
        "cols": [
            ("Компания", [("О бирже", "identitate/index.html"), ("Совет и исполнительный орган", "consiliul-si-organul-executiv/index.html"),
                          ("Учредители BIMx", "fondatori/index.html"), ("Институциональные партнёры", "parteneri-institutionali/index.html"),
                          ("Карьера", "cariere/index.html"), ("Контакты", "contacte/index.html")]),
            ("Рынок", [("Общий обзор", "prezentare-generala/index.html"), ("Котировки в реальном времени", "cotatii-in-timp-real/index.html"),
                       ("Биржевые индексы", "indicii-bursei/index.html"), ("Акции", "actiuni/index.html"),
                       ("Облигации и зелёное финансирование", "obligatiuni/index.html"), ("Расписание торгов", "program-de-tranzactionare/index.html"),
                       ("Торговый календарь", "trading-calendar/index.html")]),
            ("Услуги", [("Торговая платформа", "platforma-de-tranzactionare/index.html"), ("Услуги по листингу", "servicii-de-listare/index.html"),
                        ("Клиринг и расчёты", "compensare-si-decontare/index.html"), ("Рыночные данные", "date-de-piata/index.html"),
                        ("Операционная модель", "model-operational/index.html")]),
            ("Листинг", [("Процедура листинга", "procesul-de-listare/index.html"), ("Тарифы", "wp-content/uploads/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"),
                         ("Аттестация брокеров", "atestarea-brokerilor/index.html"), ("Список компаний", "lista-societatilor/index.html")]),
            ("Право и комплаенс", [("Регламенты и нормативные акты", "regulamente-si-acte-normative/index.html"),
                                   ("Политика конфиденциальности", "politica-de-confidentialitate/index.html"),
                                   ("Политика cookie", "politica-cookie/index.html"), ("Центр загрузок", "centru-de-descarcare/index.html"),
                                   ("Доступность", "accesibilitate-incluziune-si-diversitate/index.html")]),
        ],
        "resources": [("BIMx Academy", "academy/index.html"), ("Объявления BIMx", "category/anunturi-bimx/index.html"),
                      ("Новости", "category/stiri/index.html"), ("Медиацентр", "centru-media/index.html")],
        "resources_h": "Ресурсы",
        "partners": "Институциональные партнёры",
        "disclaimer_h": "Уведомление о рыночных данных",
        "disclaimer": "Обращаем ваше внимание, что на данном этапе рыночные данные, представленные на этой платформе, носят исключительно "
                      "демонстрационный характер. Отображаемые значения, индексы, процентные изменения и статистика сформированы в "
                      "иллюстративных целях, чтобы продемонстрировать возможности платформы, и не отражают реальные сделки или котировки "
                      "ценных бумаг в режиме реального времени.",
        "accessibility": "Доступность",
        "partner_names": {"invest": "Invest Moldova", "oda": "ODA — Организация по развитию предпринимательства",
                          "cnpf": "НКФР — Национальная комиссия по финансовому рынку"},
    },
    "uk": {
        "prelaunch": "Підготовка до запуску", "strip_text": "Торги розпочнуться до кінця 2026 року", "licence": "Ліцензія НКФР", "register": "переглянути в реєстрі", "prelaunch_title": "Торги ще не розпочалися; платформа ARENA запрацює 1 жовтня 2026 р.",
        "lang": "Мова", "close": "Закрити пошук", "search_hint": "Натисніть Esc, щоб закрити",
        "about": "Міжнародна фондова біржа Молдови (BIMx) — прозорий регульований ринок із 2026 року.",
        "address": "вул. Влайку Пиркелаб, 63, MD-2012, Кишинів, Республіка Молдова",
        "follow": "BIMx у соцмережах",
        "cols": [
            ("Компанія", [("Про біржу", "identitate/index.html"), ("Рада та виконавчий орган", "consiliul-si-organul-executiv/index.html"),
                          ("Засновники BIMx", "fondatori/index.html"), ("Інституційні партнери", "parteneri-institutionali/index.html"),
                          ("Кар’єра", "cariere/index.html"), ("Контакти", "contacte/index.html")]),
            ("Ринок", [("Загальний огляд", "prezentare-generala/index.html"), ("Котирування в реальному часі", "cotatii-in-timp-real/index.html"),
                       ("Біржові індекси", "indicii-bursei/index.html"), ("Акції", "actiuni/index.html"),
                       ("Облігації та зелене фінансування", "obligatiuni/index.html"), ("Розклад торгів", "program-de-tranzactionare/index.html"),
                       ("Календар торгів", "trading-calendar/index.html")]),
            ("Послуги", [("Торговельна платформа", "platforma-de-tranzactionare/index.html"), ("Послуги з лістингу", "servicii-de-listare/index.html"),
                         ("Клірінг і розрахунки", "compensare-si-decontare/index.html"), ("Ринкові дані", "date-de-piata/index.html"),
                         ("Операційна модель", "model-operational/index.html")]),
            ("Лістинг", [("Процедура лістингу", "procesul-de-listare/index.html"), ("Тарифи", "wp-content/uploads/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"),
                         ("Атестація брокерів", "atestarea-brokerilor/index.html"), ("Перелік компаній", "lista-societatilor/index.html")]),
            ("Право та комплаєнс", [("Регламенти та нормативні акти", "regulamente-si-acte-normative/index.html"),
                                    ("Політика конфіденційності", "politica-de-confidentialitate/index.html"),
                                    ("Політика щодо cookie", "politica-cookie/index.html"), ("Центр завантажень", "centru-de-descarcare/index.html"),
                                    ("Доступність", "accesibilitate-incluziune-si-diversitate/index.html")]),
        ],
        "resources": [("BIMx Academy", "academy/index.html"), ("Оголошення BIMx", "category/anunturi-bimx/index.html"),
                      ("Новини", "category/stiri/index.html"), ("Медіацентр", "centru-media/index.html")],
        "resources_h": "Ресурси",
        "partners": "Інституційні партнери",
        "disclaimer_h": "Повідомлення щодо ринкових даних",
        "disclaimer": "Звертаємо вашу увагу, що на цьому етапі ринкові дані, представлені на платформі, мають виключно "
                      "демонстраційний характер. Відображені значення, індекси, відсоткові зміни та статистика сформовані з "
                      "ілюстративною метою, щоб продемонструвати можливості платформи, і не відображають реальних угод чи котирувань "
                      "цінних паперів у реальному часі.",
        "accessibility": "Доступність",
        "partner_names": {"invest": "Invest Moldova", "oda": "ODA — Організація з розвитку підприємництва",
                          "cnpf": "НКФР — Національна комісія з фінансового ринку"},
    },
}

ICON_PIN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0119 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
ICON_PHONE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.7a2 2 0 01-.5 2.1L8 9.8a16 16 0 006 6l1.3-1.3a2 2 0 012.1-.4c.9.3 1.8.5 2.7.6a2 2 0 011.7 2z"/></svg>'
ICON_MAIL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/></svg>'
ICON_LINKEDIN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 11-.01 5 2.5 2.5 0 01.01-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.6 8.65 21 11.2 21 14.5V21h-4v-5.8c0-1.4-.03-3.2-1.95-3.2-1.95 0-2.25 1.52-2.25 3.1V21H9z"/></svg>'
ICON_FACEBOOK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.87.25-1.46 1.5-1.46h1.6V4.46A21 21 0 0014.3 4.3c-2.3 0-3.8 1.4-3.8 3.95v2.25H8v3h2.5V21z"/></svg>'
ICON_INFO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>'
ICON_GLOBE = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/></svg>')
ICON_CHEVRON = ('<svg class="bx-lang-chev" width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">'
                '<path d="M3 4.5l3 3 3-3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_CHECK = ('<svg class="bx-lang-check" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
              '<path d="M3.5 8.5l3 3 6-6.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_CLOSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'


# meniul mobil: al doilea CTA (admiterea) și, jos, contactul cu programul de lucru
MENU_APPLY = {"ro": "Aplicați pentru admitere", "en": "Apply for admission", "ru": "Подать заявку на допуск", "uk": "Подати заявку на допуск"}
MENU_CONTACT = {"ro": "Contact", "en": "Contact", "ru": "Контакты", "uk": "Контакти"}
ICON_CLOCK = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>')


def menu_extras(pg, login_li):
    from .home import HOURS
    label, days, closed = HOURS[pg.lang]
    apply_li = (f'<li class="hide_desktop bx-menu-apply menu-item"><a href="{pg.link("atestarea-brokerilor/index.html")}">'
                f'{MENU_APPLY[pg.lang]} →</a></li>')
    contact_li = (f'<li class="bx-menu-contact menu-item"><p class="bx-menu-contact-h">{MENU_CONTACT[pg.lang]}</p>'
                  f'<a href="tel:+37322897700">{ICON_PHONE}+373 22 89 77 00</a>'
                  f'<a href="mailto:office@bimx.md">{ICON_MAIL}office@bimx.md</a>'
                  f'<p class="bx-menu-hours">{ICON_CLOCK}<span><strong>{label}</strong> {days}<br>{closed}</span></p></li>')
    return apply_li + "\n" + login_li + "\n" + contact_li


CURRENT = ' aria-current="true"'


def lang_menu(pg, t):
    """Selectorul de limbă: buton compact (glob + codul limbii) care deschide lista limbilor (replica.js)."""
    items = "".join(
        f'<li><a href="{pg.alt(x)}" lang="{x}" hreflang="{x}"{CURRENT if x == pg.lang else ""}>'
        f'<span class="bx-lang-code">{LANG_CODES[x]}</span><span class="bx-lang-name">{LANG_NAMES[x]}</span>'
        f'{ICON_CHECK if x == pg.lang else ""}</a></li>' for x in SITE_LANGS)
    return (f'<div class="bx-lang"><button type="button" class="bx-lang-btn" aria-haspopup="true" aria-expanded="false" '
            f'aria-controls="bx-lang-menu" aria-label="{t["lang"]}: {LANG_NAMES[pg.lang]}">{ICON_GLOBE}'
            f'<span>{LANG_CODES[pg.lang]}</span>{ICON_CHEVRON}</button>'
            f'<ul class="bx-lang-menu" id="bx-lang-menu" hidden>{items}</ul></div>')


def header(text, pg):
    t = T[pg.lang]
    h0 = text.find('<header id="masthead"')
    h1 = text.find("</header>", h0)
    if h0 < 0 or h1 < 0 or "bx-lang" in text[h0:h1]:
        return text
    head = text[h0:h1]
    # bara de sus (starea pieței, ceasul, limba) dispare: starea devine o etichetă lângă logo, limba intră în meniu
    t0, t1 = head.find('<div class="top_header">'), head.find('<div class="header_mask">')
    if t0 >= 0 and t1 > t0:
        head = head[:t0] + head[t1:]
    # banda de stare deasupra meniului: pre-lansare (stânga) și licența CNPF cu link spre registru (dreapta)
    lic = f'{t["licence"]} {pick(pg.lang, "nr.", "No.", "№", "№")} {LICENCE_NO}' if LICENCE_NO else t["licence"]
    strip = (f'<div class="bx-status-strip"><div class="container bx-status-inner">'
             f'<p class="bx-status-left"><span class="bx-status-dot" aria-hidden="true"></span><strong>{t["prelaunch"]}</strong>'
             f'<span class="bx-strip"><span class="bx-strip-move"><span class="bx-strip-item">'
             f'<span class="bx-strip-text">{t["strip_text"]}</span></span></span></span></p>'
             f'<a class="bx-status-right" href="{CNPF_REGISTER}" target="_blank" rel="noopener">{lic} — {t["register"]} ↗</a>'
             f'</div></div>')
    head = head.replace('<div class="header_mask">', strip + '\n    <div class="header_mask">', 1)
    # comutatorul RO/EN al temei originale (în meniul mobil) dispare: limba se alege din selectorul nou din antet
    head = re.sub(r'\s*<li id="menu-item-253"[^>]*class="pll-parent-menu-item[\s\S]*?</ul>\s*</li>', "", head, count=1)
    head = re.sub(r'(<li id="menu-item-252"[^>]*>[\s\S]*?</li>)', lambda m: menu_extras(pg, m.group(1)), head, count=1)
    for mid, labels in NAV.items():
        head = re.sub(rf'(<li id="menu-item-{mid}"[^>]*><a [^>]*>)[^<]*(</a>)', rf"\g<1>{labels[IDX[pg.lang]]}\2", head, count=1)
    head = re.sub(r'(\s*<a href="[^"]*" class="btn1 bx-login")', lambda m: "\n                    " + lang_menu(pg, t) + m.group(1), head, count=1)
    # căutarea: butonul de închidere e un „×” clar, cu nume accesibil
    head = re.sub(r'(<div class="close" role="button" tabindex="0" aria-label=")[^"]*(">)\s*<svg[\s\S]*?</svg>',
                  rf'\g<1>{t["close"]}\2{ICON_CLOSE}', head, count=1)
    text = text[:h0] + head + text[h1:]
    # scriptul ceasului din bara de sus nu mai are element țintă
    return re.sub(r"<script>\s*\(function \(\) \{\s*function updateTime\(\)[\s\S]*?</script>", "", text, count=1)


def footer(text, pg):
    t = T[pg.lang]
    f0 = text.find('<footer id="colophon"')
    f1 = text.find("</footer>", f0)
    if f0 < 0 or f1 < 0 or "bx-footer" in text[f0:f1]:
        return text
    old = text[f0:f1]
    modal = re.search(r'<div class="contact_modal_overlay">[\s\S]*$', old)
    logo = re.search(r'<img src="([^"]*logo_2\.png)"', old)
    imgs = {k: re.search(rf'<img src="([^"]*/{name})"', old) for k, name in (("invest", "Invest.png"), ("oda", "oda.png"), ("cnpf", "CNPF.png"))}
    urls = {"invest": "https://invest.gov.md/", "oda": "https://oda.md/ro/", "cnpf": "https://www.cnpf.md/"}
    bottom = re.search(r'<div class="footer_bottom">\s*<p>([\s\S]*?)</p>', old)

    # pe mobil fiecare coloană e o secțiune pliabilă (<details>, deschisă implicit pe desktop – replica.js)
    cols = "".join(
        f'<details class="bx-f-col" open><summary><h2>{title}</h2></summary><ul>'
        + "".join(f'<li><a href="{pg.link(href)}"{PDF_ATTR if href.endswith(".pdf") else ""}>{label}</a></li>' for label, href in links)
        + "</ul></details>"
        for title, links in t["cols"])
    resources = (f'<nav class="bx-f-resources" aria-label="{t["resources_h"]}"><span>{t["resources_h"]}</span>'
                 + "".join(f'<a href="{pg.link(h)}">{label}</a>' for label, h in t["resources"]) + "</nav>")
    partners = "".join(
        f'<a href="{urls[k]}" target="_blank" rel="noopener" class="bx-f-partner"><img src="{m.group(1)}" alt="{t["partner_names"][k]}"></a>'
        for k, m in imgs.items() if m)
    lang = (f'<nav class="bx-f-lang" aria-label="{t["lang"]}">'
            + "".join(f'<a href="{pg.alt(x)}" lang="{x}" hreflang="{x}"{CURRENT if x == pg.lang else ""}>{LANG_CODES[x]}</a>' for x in SITE_LANGS)
            + "</nav>")

    new = f'''<footer id="colophon" class="site-footer bx-footer">
  <div class="container">
    <div class="bx-f-top">
      <div class="bx-f-brand">
        <a href="{pg.link("index.html")}" class="bx-f-logo" aria-label="BIMx">{WORDMARK}</a>
        <p>{t["about"]}</p>
        <ul class="bx-f-contact">
          <li>{ICON_PIN}<span>{t["address"]}</span></li>
          <li>{ICON_PHONE}<a href="tel:+37322897700">+373 22 89 77 00</a></li>
          <li>{ICON_MAIL}<a href="mailto:office@bimx.md">office@bimx.md</a></li>
        </ul>
        <div class="bx-f-social" id="newsletter"><span>{t["follow"]}</span>
          <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON_LINKEDIN}</a>
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook">{ICON_FACEBOOK}</a>
        </div>
      </div>
      <div class="bx-f-cols">{cols}</div>
    </div>
    {resources}
    <div class="bx-f-partners"><h2>{t["partners"]}</h2><div>{partners}</div></div>
    <div class="bx-f-disclaimer">{ICON_INFO}<p><strong>{t["disclaimer_h"]}.</strong> {t["disclaimer"]}</p></div>
    <div class="bx-f-bottom">
      <p>{bottom.group(1).strip() if bottom else ""}</p>
      <div class="bx-f-bottom-links">{lang}</div>
    </div>
  </div>
  {modal.group(0) if modal else ""}
'''
    return text[:f0] + new + text[f1:]
