"""Corecturile din auditul UI/UX (audits/ui-ux-audit.html), aplicate peste paginile generate în dist/.

Paginile bimx.md vin neschimbate din src/bimx-mirror/ (reîmprospătate de `make mirror`), așa că toate
corecturile se fac aici, la build, în ambele limbi: un nou mirror nu le pierde. Fiecare corectură e
etichetată cu numărul problemei din audit (UI-xx). Ordinea în build: după detach(), înainte de căutare.
"""
import datetime
import html as _html
import re
import shutil
from pathlib import Path

from . import chrome
from .config import CYRILLIC, DIST, LANG_PREFIX, LOCALES, SITE_LANGS, SRC, lang_of, pick
from .util import relto

IDX = {"ro": 0, "en": 1, "ru": 2, "uk": 3}  # poziția limbii în tuplurile (RO, EN, RU, UK) de mai jos

UPLOADS = "wp-content/uploads"
NOMENCLATOR_OLD = f"{UPLOADS}/2026/09/Nomenclatorul_taxelor_si_comisioanelor.pdf"
NOMENCLATOR = f"{UPLOADS}/2026/09/Nomenclatorul_taxelor_si_comisioanelor-1.pdf"   # versiunea din 17.09.2026
LINKEDIN = "https://linkedin.com/company/moldova-international-stock-exchange-bursa-internationala-a-moldovei"
FACEBOOK = "https://www.facebook.com/BIMx.MD/"

# UI-02 / UI-22: tickerul (date demonstrative) rămâne doar pe paginile de piață, nu și pe prima pagină
TICKER_PAGES = {"cotatii-in-timp-real", "indicii-bursei", "actiuni", "obligatiuni", "fise-detaliate",
                "date-istorice", "rapoarte", "valori-mobiliare", "date-de-piata", "prezentare-generala"}

# UI-13: rute duplicate → o singură adresă (redirecționare); UI-01: „Indici” → pagina existentă „Indicii Bursei”
REDIRECTS = {
    "stiri": "category/stiri",
    "anunturi-bimx": "category/anunturi-bimx",
    "anunturi-ale-emitentilor": "category/anunturi-ale-emitentilor",
    "indici": "indicii-bursei",
}

# UI-26: documentele din Centrul de descărcare, în ordinea din pagină (identică în RO și EN); None = fișier inexistent
DOWNLOADS = [
    f"{UPLOADS}/2026/06/Statut-BIMx.pdf",
    f"{UPLOADS}/2026/06/Organigrama-Final.pdf",
    f"{UPLOADS}/2026/06/Situatii-financiare-BIMx-anul-2025.pdf",
    None,                                                    # Raport anual BIMx
    f"{UPLOADS}/2026/06/Raportul-audit-financiar-BIMx-anul-2025.pdf",
    f"{UPLOADS}/2026/09/Regulile-PR-Final.pdf",
    f"{UPLOADS}/2026/09/Regulile-MTF-Final.pdf",
    None, None,                                              # regulamentul și procedura de atestare
    NOMENCLATOR,
    None, None, None, None, None, None, None,                # formulare și contracte
    None, None,                                              # prezentări
]

TXT = {
    "ro": {
        "prelaunch": "Pre-lansare", "prelaunch_more": " · Platforma ARENA intră în producție la 1 octombrie 2026",
        "skip": "Salt la conținut", "home": "Acasă", "breadcrumb": "Breadcrumb",
        "search_open": "Căutați pe site", "search_close": "Închide căutarea", "menu": "Deschide meniul", "close": "Închide",
        "soon": "În curând", "demo": "Date demonstrative", "pause": "Pauză", "play": "Porniți",
        "ticker_label": "Bandă cu cotații demonstrative",
        "popup": "Notificare privind datele de piață",
        "stay": "Rămâi informat", "stay_p": "Urmăriți BIMx pe LinkedIn și Facebook pentru anunțuri, comunicate și noutăți despre lansarea pieței.",
        "address": "str. Vlaicu Pârcălab 63, MD-2012, Chișinău, Republica Moldova",
        "copyright": "© 2026 Bursa Internațională a Moldovei. Operator de piață licențiat de CNPF la 21 august 2026 pentru "
                     "Piața Reglementată și MTF. Platforma de tranzacționare ARENA intră în producție la 1 octombrie 2026; "
                     "prima listare este planificată până la sfârșitul anului 2026.",
        "calendar": "Calendarul de tranzacționare", "accessibility": "Accesibilitate",
        "partners": {"invest": "Invest Moldova", "oda": "ODA – Organizația pentru Dezvoltarea Antreprenoriatului",
                     "cnpf": "CNPF – Comisia Națională a Pieței Financiare"},
        "notes": ["Prima listare: până la sfârșitul anului 2026", "Admiterea emitenților: din 28 septembrie 2026",
                  "Admiterea brokerilor: din 28 septembrie 2026"],
        "read_more": "Citiți mai mult", "pdf": "PDF", "new_tab": "(se deschide într-o filă nouă)",
        "doc_download": "Descărcați", "in_prep": "Pagina este în pregătire.",
        "section": {"piata": "Piață", "despre": "Despre noi", "juridic": "Juridic și conformitate", "servicii": "Servicii"},
    },
    "en": {
        "prelaunch": "Pre-launch", "prelaunch_more": " · The ARENA trading platform goes live on 1 October 2026",
        "skip": "Skip to content", "home": "Home", "breadcrumb": "Breadcrumb",
        "search_open": "Search the site", "search_close": "Close search", "menu": "Open menu", "close": "Close",
        "soon": "Coming soon", "demo": "Demo data", "pause": "Pause", "play": "Play",
        "ticker_label": "Ticker with demonstration quotes",
        "popup": "Notice on market data",
        "stay": "Stay informed", "stay_p": "Follow BIMx on LinkedIn and Facebook for announcements, press releases and news about the market launch.",
        "address": "63 Vlaicu Pârcălab St., MD-2012, Chișinău, Republic of Moldova",
        "copyright": "© 2026 Moldova International Stock Exchange. Market operator licensed by the CNPF on 21 August 2026 for "
                     "the Regulated Market and the MTF. The ARENA trading platform goes live on 1 October 2026; the first "
                     "listing is planned by the end of 2026.",
        "calendar": "Trading calendar", "accessibility": "Accessibility",
        "partners": {"invest": "Invest Moldova", "oda": "ODA – Organisation for Entrepreneurship Development",
                     "cnpf": "CNPF – National Commission for Financial Markets"},
        "notes": ["First listing: by the end of 2026", "Admission of issuers: from 28 September 2026",
                  "Admission of brokers: from 28 September 2026"],
        "read_more": "Read more", "pdf": "PDF", "new_tab": "(opens in a new tab)",
        "doc_download": "Download", "in_prep": "This page is being prepared.",
        "section": {"piata": "Market", "despre": "About us", "juridic": "Legal &amp; Compliance", "servicii": "Services"},
    },
    "ru": {
        "prelaunch": "Подготовка к запуску", "prelaunch_more": " · Торговая платформа ARENA вводится в эксплуатацию 1 октября 2026 г.",
        "skip": "Перейти к содержанию", "home": "Главная", "breadcrumb": "Навигационная цепочка",
        "search_open": "Поиск по сайту", "search_close": "Закрыть поиск", "menu": "Открыть меню", "close": "Закрыть",
        "soon": "Скоро", "demo": "Демонстрационные данные", "pause": "Пауза", "play": "Запустить",
        "ticker_label": "Бегущая строка с демонстрационными котировками",
        "popup": "Уведомление о рыночных данных",
        "stay": "Будьте в курсе", "stay_p": "Следите за BIMx в LinkedIn и Facebook: объявления, пресс-релизы и новости о запуске рынка.",
        "address": "ул. Влайку Пыркэлаб, 63, MD-2012, Кишинёв, Республика Молдова",
        "copyright": "© 2026 Международная фондовая биржа Молдовы. Оператор рынка, лицензированный НКФР 21 августа 2026 г. для "
                     "регулируемого рынка и MTF. Торговая платформа ARENA вводится в эксплуатацию 1 октября 2026 г.; "
                     "первый листинг запланирован до конца 2026 г.",
        "calendar": "Торговый календарь", "accessibility": "Доступность",
        "partners": {"invest": "Invest Moldova", "oda": "ODA — Организация по развитию предпринимательства",
                     "cnpf": "НКФР — Национальная комиссия по финансовому рынку"},
        "notes": ["Первый листинг: до конца 2026 г.", "Допуск эмитентов: с 28 сентября 2026 г.",
                  "Допуск брокеров: с 28 сентября 2026 г."],
        "read_more": "Подробнее", "pdf": "PDF", "new_tab": "(откроется в новой вкладке)",
        "doc_download": "Скачать", "in_prep": "Страница находится в разработке.",
        "section": {"piata": "Рынок", "despre": "О нас", "juridic": "Право и комплаенс", "servicii": "Услуги"},
    },
    "uk": {
        "prelaunch": "Підготовка до запуску", "prelaunch_more": " · Торговельна платформа ARENA запрацює 1 жовтня 2026 р.",
        "skip": "Перейти до вмісту", "home": "Головна", "breadcrumb": "Навігаційний ланцюжок",
        "search_open": "Пошук на сайті", "search_close": "Закрити пошук", "menu": "Відкрити меню", "close": "Закрити",
        "soon": "Незабаром", "demo": "Демонстраційні дані", "pause": "Пауза", "play": "Запустити",
        "ticker_label": "Рядок із демонстраційними котируваннями",
        "popup": "Повідомлення щодо ринкових даних",
        "stay": "Будьте в курсі", "stay_p": "Стежте за BIMx у LinkedIn і Facebook: оголошення, прес-релізи та новини про запуск ринку.",
        "address": "вул. Влайку Пиркелаб, 63, MD-2012, Кишинів, Республіка Молдова",
        "copyright": "© 2026 Міжнародна фондова біржа Молдови. Оператор ринку, ліцензований НКФР 21 серпня 2026 р. для "
                     "регульованого ринку та MTF. Торговельна платформа ARENA запрацює 1 жовтня 2026 р.; "
                     "перший лістинг заплановано до кінця 2026 р.",
        "calendar": "Календар торгів", "accessibility": "Доступність",
        "partners": {"invest": "Invest Moldova", "oda": "ODA — Організація з розвитку підприємництва",
                     "cnpf": "НКФР — Національна комісія з фінансового ринку"},
        "notes": ["Перший лістинг: до кінця 2026 р.", "Допуск емітентів: з 28 вересня 2026 р.",
                  "Допуск брокерів: з 28 вересня 2026 р."],
        "read_more": "Детальніше", "pdf": "PDF", "new_tab": "(відкриється в новій вкладці)",
        "doc_download": "Завантажити", "in_prep": "Сторінка готується.",
        "section": {"piata": "Ринок", "despre": "Про нас", "juridic": "Право та комплаєнс", "servicii": "Послуги"},
    },
}

# UI-01, UI-33: paginile „În curând” devin pagini reale (titlu, breadcrumbs, conținut)
PAGES = {
    "trading-calendar": {
        "section": "piata",
        "ro": ("Calendarul de tranzacționare", "Etapele lansării pieței BIMx, conform comunicărilor oficiale ale BIMx."),
        "en": ("Trading calendar", "The launch stages of the BIMx market, as set out in BIMx's official communications."),
        "ru": ("Торговый календарь", "Этапы запуска рынка BIMx согласно официальным сообщениям BIMx."),
        "uk": ("Календар торгів", "Етапи запуску ринку BIMx відповідно до офіційних повідомлень BIMx."),
        "kind": "calendar",
    },
    "statut": {"section": "despre", "ro": ("Statut", "Statutul Bursei Internaționale a Moldovei."),
               "en": ("Articles of association", "The articles of association of the Moldova International Stock Exchange."),
               "ru": ("Устав", "Устав Международной фондовой биржи Молдовы."),
               "uk": ("Статут", "Статут Міжнародної фондової біржі Молдови."),
               "kind": "docs", "docs": [(f"{UPLOADS}/2026/06/Statut-BIMx.pdf", "Statut BIMx", "BIMx articles of association", "Устав BIMx", "Статут BIMx")]},
    "organigrama": {"section": "despre", "ro": ("Organigrama", "Structura organizatorică a BIMx."),
                    "en": ("Organisational chart", "The organisational structure of BIMx."),
                    "ru": ("Организационная структура", "Организационная структура BIMx."),
                    "uk": ("Організаційна структура", "Організаційна структура BIMx."),
                    "kind": "org", "docs": [(f"{UPLOADS}/2026/06/Organigrama-Final.pdf", "Organigrama BIMx (PDF)", "BIMx organisational chart (PDF)",
                                             "Организационная структура BIMx (PDF)", "Організаційна структура BIMx (PDF)")]},
    "situatii-financiare": {
        "section": "despre", "ro": ("Situații financiare", "Situațiile financiare anuale și raportul auditorului."),
        "en": ("Financial statements", "The annual financial statements and the auditor's report."),
        "ru": ("Финансовая отчётность", "Годовая финансовая отчётность и аудиторское заключение."),
        "uk": ("Фінансова звітність", "Річна фінансова звітність і аудиторський звіт."),
        "kind": "docs", "docs": [
            (f"{UPLOADS}/2026/06/Situatii-financiare-BIMx-anul-2025.pdf", "Situații financiare BIMx, anul 2025", "BIMx financial statements, 2025",
             "Финансовая отчётность BIMx за 2025 год", "Фінансова звітність BIMx за 2025 рік"),
            (f"{UPLOADS}/2026/06/Raportul-audit-financiar-BIMx-anul-2025.pdf", "Raportul de audit financiar, anul 2025", "Financial audit report, 2025",
             "Аудиторское заключение за 2025 год", "Аудиторський звіт за 2025 рік"),
        ]},
    "statistici-de-piata": {"section": "piata", "ro": ("Statistici de piață", ""), "en": ("Market statistics", ""),
                            "ru": ("Рыночная статистика", ""), "uk": ("Ринкова статистика", ""), "kind": "prep",
                            "see": ("date-de-piata/index.html", "Date de piață", "Market data", "Рыночные данные", "Ринкові дані")},
    "platforma-de-tranzactionare": {"section": "servicii", "ro": ("Platforma de tranzacționare", ""),
                                    "en": ("Trading platform", ""), "ru": ("Торговая платформа", ""),
                                    "uk": ("Торговельна платформа", ""), "kind": "prep",
                                    "see": ("model-operational/index.html", "Modelul operațional și platforma ARENA",
                                            "The operating model and the ARENA platform", "Операционная модель и платформа ARENA",
                                            "Операційна модель і платформа ARENA")},
    "servicii": {"section": "servicii", "ro": ("Servicii", ""), "en": ("Services", ""), "ru": ("Услуги", ""), "uk": ("Послуги", ""), "kind": "prep",
                 "see": ("servicii-de-listare/index.html", "Servicii de listare", "Listing services", "Услуги по листингу", "Послуги з лістингу")},
    "politica-de-confidentialitate": {"section": "juridic", "ro": ("Politica de confidențialitate", ""),
                                      "en": ("Privacy policy", ""), "ru": ("Политика конфиденциальности", ""),
                                      "uk": ("Політика конфіденційності", ""), "kind": "prep",
                                      "see": ("contacte/index.html", "Contacte", "Contacts", "Контакты", "Контакти")},
    "politica-cookie": {"section": "juridic", "ro": ("Politica cookie", ""), "en": ("Cookie policy", ""),
                        "ru": ("Политика использования файлов cookie", ""), "uk": ("Політика щодо файлів cookie", ""), "kind": "prep",
                        "see": ("contacte/index.html", "Contacte", "Contacts", "Контакты", "Контакти")},
}

# Etapele din calendar: (data exactă sau None, RO: (dată, titlu, detalii), EN: ...). Starea se calculează la build.
CALENDAR = [
    (datetime.date(2025, 9, 15), ("15 septembrie 2025", "Memorandum de înțelegere (Moldova Business Week)", "Memorandumul de înțelegere privind crearea Bursei Internaționale a Moldovei este semnat în cadrul Moldova Business Week 2025."),
                                 ("15 September 2025", "Memorandum of understanding (Moldova Business Week)", "The memorandum of understanding on creating the Moldova International Stock Exchange is signed at Moldova Business Week 2025."),
                                 ("15 сентября 2025", "Меморандум о взаимопонимании (Moldova Business Week)", "Меморандум о взаимопонимании о создании Международной фондовой биржи Молдовы подписан в рамках Moldova Business Week 2025."),
                                 ("15 вересня 2025", "Меморандум про взаєморозуміння (Moldova Business Week)", "Меморандум про взаєморозуміння щодо створення Міжнародної фондової біржі Молдови підписано в межах Moldova Business Week 2025.")),
    (datetime.date(2025, 10, 15), ("15 octombrie 2025", "Guvernul aprobă crearea societății pe acțiuni", "Guvernul Republicii Moldova aprobă crearea societății pe acțiuni care va administra noua bursă."),
                                  ("15 October 2025", "The Government approves the creation of the joint-stock company", "The Government of the Republic of Moldova approves the creation of the joint-stock company that will operate the new exchange."),
                                 ("15 октября 2025", "Правительство одобряет создание акционерного общества", "Правительство Республики Молдова одобряет создание акционерного общества, которое будет управлять новой биржей."),
                                 ("15 жовтня 2025", "Уряд схвалює створення акціонерного товариства", "Уряд Республіки Молдова схвалює створення акціонерного товариства, яке керуватиме новою біржею.")),
    (datetime.date(2025, 12, 12), ("12 decembrie 2025", "Înregistrare oficială la Agenția Servicii Publice", "Bursa Internațională a Moldovei S.A. este înregistrată oficial ca persoană juridică la Agenția Servicii Publice."),
                                  ("12 December 2025", "Official registration with the Public Services Agency", "Moldova International Stock Exchange S.A. is officially registered as a legal entity with the Public Services Agency."),
                                 ("12 декабря 2025", "Официальная регистрация в Агентстве государственных услуг", "АО «Международная фондовая биржа Молдовы» официально зарегистрировано как юридическое лицо в Агентстве государственных услуг."),
                                 ("12 грудня 2025", "Офіційна реєстрація в Агентстві державних послуг", "АТ «Міжнародна фондова біржа Молдови» офіційно зареєстроване як юридична особа в Агентстві державних послуг.")),
    (datetime.date(2026, 1, 20), ("20 ianuarie 2026", "CNPF înregistrează emisiunea de constituire", "Comisia Națională a Pieței Financiare înregistrează emisiunea de acțiuni plasată la constituirea societății."),
                                 ("20 January 2026", "The CNPF registers the founding share issue", "The National Commission for Financial Markets registers the share issue placed at the company's incorporation."),
                                 ("20 января 2026", "НКФР регистрирует учредительную эмиссию", "Национальная комиссия по финансовому рынку регистрирует эмиссию акций, размещённых при учреждении общества."),
                                 ("20 січня 2026", "НКФР реєструє засновницьку емісію", "Національна комісія з фінансового ринку реєструє емісію акцій, розміщених під час заснування товариства.")),
    (datetime.date(2026, 8, 21), ("21 august 2026", "Licența de operator de piață obținută de la CNPF",
                                  "CNPF acordă BIMx licența de operator de piață și autorizațiile pentru Piața Reglementată și sistemul multilateral de tranzacționare (Hotărârea CNPF nr. 42/3)."),
                                 ("21 August 2026", "Market operator licence obtained from the CNPF",
                                  "The CNPF grants BIMx the market operator licence and the authorisations for the Regulated Market and the multilateral trading facility (CNPF Decision No. 42/3)."),
                                 ("21 августа 2026", "Лицензия оператора рынка получена от НКФР",
                                  "НКФР выдаёт BIMx лицензию оператора рынка и разрешения на управление регулируемым рынком и многосторонней торговой системой (Постановление НКФР № 42/3)."),
                                 ("21 серпня 2026", "Ліцензію оператора ринку отримано від НКФР",
                                  "НКФР видає BIMx ліцензію оператора ринку та дозволи на регульований ринок і багатосторонню торговельну систему (Постанова НКФР № 42/3).")),
    (datetime.date(2026, 9, 28), ("28 septembrie 2026", "Începe admiterea brokerilor și a emitenților",
                                  "Societățile de investiții pot solicita admiterea ca membri ai bursei, iar emitenții – admiterea valorilor mobiliare la tranzacționare."),
                                 ("28 September 2026", "Admission of brokers and issuers opens",
                                  "Investment firms can apply for exchange membership, and issuers can apply for the admission of their securities to trading."),
                                 ("28 сентября 2026", "Начинается допуск брокеров и эмитентов",
                                  "Инвестиционные компании могут подать заявку на участие в торгах на бирже, а эмитенты — на допуск своих ценных бумаг к торгам."),
                                 ("28 вересня 2026", "Розпочинається допуск брокерів і емітентів",
                                  "Інвестиційні компанії можуть подати заявку на членство в біржі, а емітенти — на допуск своїх цінних паперів до торгів.")),
    (datetime.date(2026, 10, 1), ("1 octombrie 2026", "Platforma ARENA, sistemul de tranzacționare BIMx, intră în producție",
                                  "Platforma de tranzacționare ARENA, dezvoltată de Bursa de Valori București, devine operațională pentru membrii admiși."),
                                 ("1 October 2026", "ARENA, the BIMx trading system, goes live",
                                  "The ARENA trading platform, developed by the Bucharest Stock Exchange, becomes operational for admitted members."),
                                 ("1 октября 2026", "Платформа ARENA, торговая система BIMx, вводится в эксплуатацию",
                                  "Торговая платформа ARENA, разработанная Бухарестской фондовой биржей, начинает работать для допущенных участников."),
                                 ("1 жовтня 2026", "Платформа ARENA, торговельна система BIMx, починає роботу",
                                  "Торговельна платформа ARENA, розроблена Бухарестською фондовою біржею, починає працювати для допущених учасників.")),
    (None, ("Până la sfârșitul anului 2026", "Prima listare și prima ședință de tranzacționare",
            "Prima listare la BIMx este planificată până la sfârșitul anului 2026. Ședințele de tranzacționare încep după prima listare."),
           ("By the end of 2026", "First listing and first trading session",
            "The first listing on BIMx is planned by the end of 2026. Trading sessions start after the first listing."),
                                 ("До конца 2026 года", "Первый листинг и первая торговая сессия",
            "Первый листинг на BIMx запланирован до конца 2026 года. Торговые сессии начнутся после первого листинга."),
                                 ("До кінця 2026 року", "Перший лістинг і перша торгова сесія",
            "Перший лістинг на BIMx заплановано до кінця 2026 року. Торгові сесії розпочнуться після першого лістингу.")),
]
CAL_STATE = {"ro": {"done": "Finalizat", "next": "Urmează", "planned": "Planificat"},
             "en": {"done": "Completed", "next": "Next", "planned": "Planned"},
             "ru": {"done": "Завершено", "next": "Следующий этап", "planned": "Запланировано"},
             "uk": {"done": "Завершено", "next": "Наступний етап", "planned": "Заплановано"}}
CALENDAR_NOTE = {
    "ro": ("Programul zilnic al ședințelor este descris pe pagina {link}. Datele se actualizează pe măsură ce BIMx publică noi comunicate.",
           "Programul de tranzacționare"),
    "en": ("The daily session schedule is described on the {link} page. Dates are updated as BIMx publishes new announcements.",
           "Trading schedule"),
    "ru": ("Ежедневное расписание торговых сессий приведено на странице «{link}». Даты обновляются по мере публикации BIMx новых сообщений.",
           "Расписание торгов"),
    "uk": ("Щоденний розклад торгових сесій наведено на сторінці «{link}». Дати оновлюються в міру того, як BIMx публікує нові повідомлення.",
           "Розклад торгів"),
}

# UI-36: iconițe SVG din setul liniar al site-ului (în locul PNG-urilor de 28 px)
AUDIENCE_ICONS = [
    '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>',
    '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h3"/></svg>',
    '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/><path d="M6 13l3-3 3 2 5-5"/></svg>',
]
# UI-38: destinațiile butoanelor din „Pentru cine este BIMx?”
AUDIENCE_LINKS = ["lista-societatilor/index.html", "procesul-de-listare/index.html", "atestarea-brokerilor/index.html"]

SEP = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M5.25 10.5L8.75 7L5.25 3.5" '
       'stroke="white" stroke-opacity="0.6" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_DOC = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H6a2 2 0 00-2 2v14a2 2 0 002 2h12a2 2 0 002-2V9z"/>'
            '<path d="M14 3v6h6M8 13h8M8 17h5"/></svg>')
ICON_LINKEDIN = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 11-.01 5 2.5 2.5 0 01.01-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.6 8.65 21 11.2 21 14.5V21h-4v-5.8c0-1.4-.03-3.2-1.95-3.2-1.95 0-2.25 1.52-2.25 3.1V21H9z"/></svg>')
ICON_FACEBOOK = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.87.25-1.46 1.5-1.46h1.6V4.46A21 21 0 0014.3 4.3c-2.3 0-3.8 1.4-3.8 3.95v2.25H8v3h2.5V21z"/></svg>')


# breadcrumbs care contraziceau meniul: secțiunea corectă (cheile din TXT[...]["section"])
CRUMB_SECTION = {"regulamente-si-acte-normative": "despre", "parteneri-institutionali": "despre",
                 "atestarea-brokerilor": "piata", "lista-societatilor": "piata"}


# breadcrumbs: fiecare nivel de secțiune duce la pagina principală a secțiunii (etichete în toate limbile, fără majuscule)
SECTION_HUBS = {
    "despre noi": "identitate", "about us": "identitate",
    "piață": "prezentare-generala", "piaţă": "prezentare-generala", "market": "prezentare-generala",
    "listare": "procesul-de-listare", "listing": "procesul-de-listare",
    "noutăți & comunicate": "category/anunturi-bimx", "news & announcements": "category/anunturi-bimx",
    "participanți": "lista-societatilor", "participants": "lista-societatilor",
    "servicii": "servicii-de-listare", "services": "servicii-de-listare",
    "juridic și conformitate": "regulamente-si-acte-normative", "legal & compliance": "regulamente-si-acte-normative",
    # rusă
    "о нас": "identitate", "рынок": "prezentare-generala", "листинг": "procesul-de-listare",
    "новости и объявления": "category/anunturi-bimx", "новости и сообщения": "category/anunturi-bimx",
    "участники": "lista-societatilor", "услуги": "servicii-de-listare", "право и комплаенс": "regulamente-si-acte-normative",
    # ucraineană
    "про нас": "identitate", "ринок": "prezentare-generala", "лістинг": "procesul-de-listare",
    "новини та оголошення": "category/anunturi-bimx", "учасники": "lista-societatilor", "послуги": "servicii-de-listare",
    "право та комплаєнс": "regulamente-si-acte-normative",
}


def link_crumbs(text, pg):
    def fix(m):
        label = m.group(1)
        key = _html.unescape(label).strip().lower()
        hub = SECTION_HUBS.get(key)
        if not hub:
            return m.group(0)
        target = DIST / (LANG_PREFIX[pg.lang] + hub) / "index.html"
        if target.resolve() == pg.path.resolve():          # pagina principală a secțiunii: nivelul e de prisos
            return "<!--bx-drop-crumb-->"
        return f'<a href="{pg.link(hub + "/index.html")}">{label}</a>'
    text = re.sub(r'<span class="without_click">([^<]*)</span>', fix, text)
    return re.sub(r'<li[^>]*>\s*<!--bx-drop-crumb-->\s*</li>\s*<li aria-hidden="true">[\s\S]*?</li>\s*', "", text)


# ---------------------------------------------------------------- utilitare

class Page:
    def __init__(self, path):
        self.path = path
        self.rel = path.relative_to(DIST)
        self.lang = lang_of(self.rel.parts)
        parts = self.rel.parts[1:] if self.lang != "ro" else self.rel.parts
        self.inner = Path(*parts)                                      # calea paginii în interiorul limbii
        self.key = parts[0] if len(parts) > 1 else parts[0]          # „index.html” sau numele primului director
        self.academy = self.key == "academy"
        self.home = parts == ("index.html",)
        self.t = TXT[self.lang]

    def link(self, path):
        """Link relativ spre o pagină (cale RO, de la rădăcină) în limba paginii curente."""
        prefix = LANG_PREFIX[self.lang] if not path.startswith(("wp-content/", "assets/")) else ""
        return relto(DIST / (prefix + path), self.path.parent) or "index.html"

    def alt(self, lang):
        """Link relativ spre aceeași pagină în altă limbă (selectorul de limbă)."""
        return relto(DIST / LANG_PREFIX[lang] / self.inner, self.path.parent) or "index.html"

    def asset(self, path):
        return relto(DIST / path, self.path.parent)


def human_size(path, lang):
    size = (DIST / path).stat().st_size
    if size >= 1024 * 1024:
        val = f"{size / 1024 / 1024:.1f}"
        return (val if lang == "en" else val.replace(".", ",")) + pick(lang, " MB", " MB", " МБ", " МБ")
    return f"{round(size / 1024)}" + pick(lang, " KB", " KB", " КБ", " КБ")


def strip_tags(text):
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


# ---------------------------------------------------------------- antet (toate paginile, inclusiv Academy)

def fix_header(text, pg):
    t = pg.t
    # UI-02: „Market Open / Live Data” → „Pre-lansare” (nu există tranzacții, deci nici date live)
    text = re.sub(r'<div class="market_detail">\s*<span class="icon"[^>]*></span>\s*[^<]*</div>',
                  f'<div class="market_detail bx-prelaunch"><span class="icon" aria-hidden="true"></span>{t["prelaunch"]}'
                  f'<span class="bx-prelaunch-more">{t["prelaunch_more"]}</span></div>', text, count=1)
    text = re.sub(r'<div class="market_detail">\s*<svg[\s\S]*?</svg>\s*Live Data\s*</div>', "", text, count=1)
    # „Intră în cont” duce la pagina de autentificare (sitegen/login.py); „Log In” din subsol dispare (e în antet)
    from .login import header_button
    text = header_button(text, pg)
    text = re.sub(r'<li [^>]*><a href="#" data-unavailable>[^<]*</a></li>\s*', "", text)
    # UI-04: butoanele antetului sunt DIV-uri → rol, focus și nume accesibil (tastatura: replica.js)
    text = text.replace('<div class="search">',
                        f'<div class="search" role="button" tabindex="0" aria-label="{t["search_open"]}" aria-expanded="false">', 1)
    text = text.replace('<div class="burger">',
                        f'<div class="burger" role="button" tabindex="0" aria-label="{t["menu"]}" aria-expanded="false">', 1)
    text = text.replace('<div class="modal_search_form">', '<div class="modal_search_form" id="bx-search" role="search">', 1)
    text = re.sub(r'(<div class="modal_search_form"[^>]*>\s*<div class="container">\s*)<div class="close">',
                  rf'\1<div class="close" role="button" tabindex="0" aria-label="{t["search_close"]}">', text, count=1)
    text = re.sub(r'<div class="close">', f'<div class="close" role="button" tabindex="0" aria-label="{t["close"]}">', text)
    # meniul Piață: grupul „Tranzacționare” (programul și calendarul de tranzacționare)
    if "bx-nav-trading" not in text:
        L = pg.lang
        group = (f'<li class="not_click menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children bx-nav-trading">'
                 f'<a href="#">{pick(L, "Tranzacționare", "Trading", "Торги", "Торги")}</a><ul class="sub-menu">'
                 f'<li class="menu-item"><a href="{pg.link("program-de-tranzactionare/index.html")}">{pick(L, "Program de tranzacționare", "Trading schedule", "Расписание торгов", "Розклад торгів")}</a></li>'
                 f'<li class="menu-item"><a href="{pg.link("trading-calendar/index.html")}">{pick(L, "Calendarul de tranzacționare", "Trading calendar", "Торговый календарь", "Календар торгів")}</a></li>'
                 f'</ul></li>\n\t')
        cur = {"program-de-tranzactionare": "program-de-tranzactionare/index.html", "trading-calendar": "trading-calendar/index.html"}.get(pg.key)
        if cur:   # pagina curentă e în grupul nou: marcată în meniu, iar „Piață” devine secțiunea activă
            group = group.replace(f'<li class="menu-item"><a href="{pg.link(cur)}">', f'<li class="menu-item current-menu-item"><a href="{pg.link(cur)}" aria-current="page">', 1)
            text = re.sub(r'(<li id="menu-item-408" class=")', r"\1current-menu-ancestor ", text, count=1)
        text = text.replace('<li id="menu-item-541"', group + '<li id="menu-item-541"', 1)
    # UI-05: meniurile de nivel 1 sunt declanșatoare, nu linkuri; titlurile de grup nu sunt linkuri
    text = re.sub(r'(<li id="menu-item-4(?:07|08|09|10|11)"[^>]*>)<a href="#">',
                  r'\1<a href="#" role="button" aria-haspopup="true" aria-expanded="false">', text)
    text = re.sub(r'(<li [^>]*class="not_click[^"]*"[^>]*>)<a href="#">', r'\1<a class="bx-group-label">', text)
    text = re.sub(r'(<li [^>]*class="back_to_main_menu[^"]*"[^>]*>)<a href="#">', r'\1<a href="#" role="button">', text)
    # butoanele sub-menu-toggle ale temei-părinte sunt ascunse și duplicate: scoase din ordinea de tab
    text = text.replace('<button class="sub-menu-toggle" aria-expanded="false"', '<button class="sub-menu-toggle" tabindex="-1" aria-hidden="true" aria-expanded="false"')
    # UI-28: logo-ul are nume
    text = re.sub(r'(<img[^>]*class="custom-logo"[^>]*?)alt=""', r'\1alt="BIMx"', text)
    # logo-ul duce la prima pagină și pe prima pagină (convenția universală; WordPress îl punea acolo într-un <span>)
    text = re.sub(r'<span class="custom-logo-link">([\s\S]*?)</span>',
                  lambda m: f'<a href="{pg.link("index.html")}" class="custom-logo-link" rel="home" aria-current="page">{m.group(1)}</a>',
                  text, count=1)
    # logo-ul din antet: vectorial (SVG), clar la orice mărime și densitate, în locul PNG-ului de 242 × 72 px
    text = re.sub(r'<img[^>]*class="custom-logo"[^>]*>',
                  f'<img width="2048" height="587" src="{pg.asset("assets/img/bimx-logo.svg")}" class="custom-logo" alt="BIMx">',
                  text, count=1)
    # Organigrama din meniu deschide pagina cu schema (nu direct PDF-ul)
    text = re.sub(r'(<li id="menu-item-599"[^>]*>)<a [^>]*>', lambda m: m.group(1) + f'<a href="{pg.link("organigrama/index.html")}">', text, count=1)
    # BIMx Academy: primul link duce la începutul paginii Academy (celelalte duc la secțiuni)
    if "bx-nav-academy-home" not in text:
        label = pick(pg.lang, "Prezentare generală", "Overview", "Общий обзор", "Загальний огляд")
        cur = ' class="menu-item current-menu-item bx-nav-academy-home"' if pg.key == "academy" and pg.path.name == "index.html" and len(pg.rel.parts) <= 3 else ' class="menu-item bx-nav-academy-home"'
        text = re.sub(r'(<li id="menu-item-410"[\s\S]*?<ul class="sub-menu">\s*<li[^>]*back_to_main_menu[^>]*>[\s\S]*?</li>)',
                      lambda m: m.group(1) + f'\n\t<li{cur}><a href="{pg.link("academy/index.html")}">{label}</a></li>', text, count=1)
    return menu_columns(text, pg.lang)



# ---------------------------------------------------------------- meniul: panouri pe coloane cu titlu

def _top_level_items(inner):
    """Elementele <li> de pe primul nivel dintr-un <ul> (ca text), cu poziția lor."""
    items, depth, start = [], 0, None
    for m in re.finditer(r"<(/?)(li|ul)\b[^>]*>", inner):
        closing, tag = m.group(1) == "/", m.group(2)
        if tag == "li" and not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        elif tag == "li" and closing:
            depth -= 1
            if depth == 0 and start is not None:
                items.append(inner[start:m.end()])
                start = None
    return items


def menu_columns(text, lang):
    """Fiecare panou de nivel 1: linkurile simple se adună într-o coloană cu titlul secțiunii; grupurile rămân coloane."""
    for mid in ("407", "408", "409", "410", "411"):
        m = re.search(rf'(<li id="menu-item-{mid}"[^>]*>\s*<a [^>]*>([^<]*)</a>[\s\S]*?<ul class="sub-menu">)', text)
        if not m or f'bx-nav-col-{mid}' in text:
            continue
        label = chrome.NAV[mid][IDX[lang]]
        start = m.end()
        # sfârșitul panoului: </ul> care închide sub-meniul de nivel 1
        depth, pos, end = 1, start, None
        for t in re.finditer(r"<(/?)ul\b[^>]*>", text[start:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = start + t.start()
                break
        if end is None:
            continue
        items = _top_level_items(text[start:end])
        back = [i for i in items if "back_to_main_menu" in i]
        groups = [i for i in items if "not_click" in i]
        simple = [i for i in items if i not in back and i not in groups]
        cols = []
        if simple:
            cols.append(f'<li class="not_click menu-item menu-item-has-children bx-nav-col bx-nav-col-{mid}"><a class="bx-group-label">{label}</a>'
                        f'<ul class="sub-menu">{"".join(simple)}</ul></li>')
        new_inner = "\n\t" + "".join(back) + "".join(cols) + "".join(groups) + "\n"
        text = text[:start] + new_inner + text[end:]
    return text


# ---------------------------------------------------------------- subsol

def fix_footer(text, pg):
    t = pg.t
    f0 = text.find('<footer id="colophon"')
    f1 = text.find("</footer>", f0)
    if f0 < 0 or f1 < 0:
        return text
    foot = text[f0:f1]

    # UI-08: newsletterul MailPoet nu poate funcționa fără server (și era invizibil) → abonare prin rețelele sociale
    n0 = foot.find('<div class="newsletter"')
    n1 = foot.find('<div class="container">\n        <div class="footer_content">')
    if n0 >= 0 and n1 > n0:
        tag = re.match(r'<div class="newsletter"[^>]*>', foot[n0:]).group(0)
        block = (f'{tag}\n        <div class="container">\n            <div class="wrap">\n                <div class="left_side">\n'
                 f'                    <h3>{t["stay"]}</h3>\n                    <p>{t["stay_p"]}</p>\n                </div>\n'
                 f'                <div class="right_side bx-follow">\n'
                 f'                    <a href="{LINKEDIN}" target="_blank" rel="noopener" class="bx-follow-btn">{ICON_LINKEDIN}LinkedIn</a>\n'
                 f'                    <a href="{FACEBOOK}" target="_blank" rel="noopener" class="bx-follow-btn">{ICON_FACEBOOK}Facebook</a>\n'
                 f'                </div>\n            </div>\n        </div>\n    </div>\n    ')
        if pg.home:                     # la cererea BIMx, prima pagină nu are blocul „Rămâi informat”
            block = ""
        foot = foot[:n0] + block + foot[n1:]

    # UI-25: adresa completă, telefon apelabil, rețele sociale
    foot = re.sub(r'(<svg[\s\S]*?</svg>\s*)(Chișinău, Republica Moldova|Chișinău, Republic of Moldova)',
                  lambda m: m.group(1) + t["address"], foot, count=1)
    foot = foot.replace('href="tel:+373 22  89 77 00"', 'href="tel:+37322897700"')
    foot = foot.replace('<a href="mailto:office@bimx.md">office@bimx.md</a>\n',
                        '<a href="mailto:office@bimx.md">office@bimx.md</a></p>\n', 1)
    social = (f'<p class="bx-social"><a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON_LINKEDIN}</a>'
              f'<a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook">{ICON_FACEBOOK}</a></p>')
    foot = re.sub(r'(<div class="contacts">[\s\S]*?)(\s*</div>\s*</div>\s*<div class="column">)', rf'\1{social}\2', foot, count=1)
    foot = re.sub(r'(<img src="[^"]*logo_2\.png") alt="[^"]*"', r'\1 alt="BIMx"', foot)

    # UI-01 / UI-25: fără pagini goale și fără dubluri în coloane; „Indici” → „Indicii Bursei”
    for item in ("121", "122", "148", "146", "150"):          # statistici, platformă, confidențialitate, cookie, Centru media (dublat)
        foot = re.sub(rf'<li id="menu-item-{item}"[^>]*>[\s\S]*?</li>\s*', "", foot)
    foot = re.sub(r'(<li id="menu-item-120"[^>]*><a [^>]*>)[^<]*', rf'\1{t["calendar"]}', foot)
    # BIMx Academy (Servicii) și Accesibilitate (Juridic)
    foot = re.sub(r'(<li id="menu-item-126"[^>]*>[\s\S]*?</li>)',
                  rf'\1\n<li class="menu-item bx-academy-link"><a href="{pg.link("academy/index.html")}">BIMx Academy</a></li>', foot, count=1)
    foot = re.sub(r'(<li id="menu-item-149"[^>]*>[\s\S]*?</li>)',
                  rf'\1\n<li class="menu-item"><a href="{pg.link("accesibilitate-incluziune-si-diversitate/index.html")}">{t["accessibility"]}</a></li>',
                  foot, count=1)
    # navigațiile din coloane: nume după titlul coloanei (erau toate „Primary menu”)
    foot = re.sub(r'<h4>([^<]*)</h4>(\s*)<nav id="site-navigation" class="([^"]*)"\s*aria-label="Primary menu">',
                  lambda m: f'<h4>{m.group(1)}</h4>{m.group(2)}<nav class="{m.group(3)}" aria-label="{m.group(1).strip()}">', foot)
    foot = foot.replace('<nav id="site-navigation" class="lang-navigation"', '<nav class="lang-navigation"')
    # logo-urile partenerilor: nume accesibil, tab nou anunțat
    for key, host in (("invest", "invest.gov.md"), ("oda", "oda.md"), ("cnpf", "cnpf.md")):
        foot = re.sub(rf'(<a href="https://(?:www\.)?{re.escape(host)}[^"]*" target="_blank")>(\s*<img [^>]*?)alt=""',
                      rf'\1 rel="noopener">\2alt="{t["partners"][key]}"', foot)
    # C-01: nota de copyright depășită
    foot = re.sub(r'(<div class="footer_bottom">\s*<p>)[\s\S]*?(</p>)', rf'\g<1>{t["copyright"]}\2', foot, count=1)
    return text[:f0] + foot + text[f1:]


# ---------------------------------------------------------------- toate paginile

def fix_common(text, pg):
    t = pg.t
    # UI-20: skip-link spre conținutul principal
    m = re.search(r'<main\b[^>]*>', text)
    if m and "skip-link" not in text:
        main_id = re.search(r'\sid="([^"]+)"', m.group(0))
        if not main_id:
            text = text.replace(m.group(0), m.group(0)[:-1] + ' id="main">', 1)
        target = main_id.group(1) if main_id else "main"
        text = re.sub(r'(<body\b[^>]*>)', rf'\1\n<a class="skip-link" href="#{target}">{t["skip"]}</a>', text, count=1)
    # UI-07: scripturile Contact Form 7 și MailPoet cer un server WordPress (404 + excepție pe fiecare pagină)
    text = re.sub(r'<script[^>]*\sid="(?:swv-js|contact-form-7-js[\w-]*|wp-hooks-js|wp-i18n-js[\w-]*|mailpoet_public-js[\w-]*)"[^>]*>[\s\S]*?</script>\s*', "", text)
    text = re.sub(r"<link rel='stylesheet' id='mailpoet_public-css'[^>]*>\s*", "", text)
    # UI-08: formularul de contact validează câmpurile obligatorii (replica.js oprește trimiterea)
    if "wpcf7-form" in text:
        text = text.replace('class="wpcf7-form init" aria-label', 'class="wpcf7-form init bx-validate" aria-label')
        text = re.sub(r'(<form [^>]*class="wpcf7-form[^"]*"[^>]*?) novalidate="novalidate"', r"\1", text)
        for name in ("your-name", "your-email"):
            text = re.sub(rf'(<input [^>]*name="{name}")', r"\1 required", text)
        text = re.sub(r'(<textarea [^>]*name="your-message")', r'\1 required aria-required="true"', text)
        for name in ("tel-439", "select-331"):                     # opționale (fără * în etichetă)
            text = re.sub(rf'(<(?:input|select) [^>]*?)aria-required="true"([^>]*name="{name}")', r'\1\2', text)
        if pg.lang == "ro":
            text = text.replace(">Nu gasesc actiuni<", ">Nu găsesc acțiuni<").replace(">Vreau sa imi public compania<", ">Vreau să îmi listez compania<")

    # UI-16: avertizarea apare imediat, cu buton de închidere tradus și nume de dialog
    text = text.replace('"open_delay":"3"', '"open_delay":"0"')
    if pg.lang == "ro":
        text = text.replace('"close_content":"Close"', '"close_content":"Închide"')
    text = re.sub(r'<div class="ds-popup" id="ds-popup-1" role="dialog" aria-label="[^"]*">',
                  f'<div class="ds-popup" id="ds-popup-1" role="dialog" aria-modal="true" aria-label="{t["popup"]}">', text)
    # iconița: aceeași plăcuță cu scut ca în sistemul de iconițe al site-ului (în locul PNG-ului)
    from .siteicons import svg as site_svg
    text = re.sub(r'<h2>(<img [^>]*wp-image-243[^>]*>)</h2>',
                  lambda m: f'<div class="ds-popup-icon"><span class="bx-ic-plate">{site_svg("shield-check")}</span></div>', text)
    text = text.replace('<button class="ds-button ds-close-popup is-medium is-fullwidth" style="color:#ffffff; background:rgb(26,34,102)">',
                        '<button class="ds-button ds-close-popup bx-popup-ok" type="button">')
    # butonul de închidere generat de plugin: „×” fin, ca în căutare
    text = text.replace('"close_type":"-icon"', '"close_type":"-text"').replace('"close_content":"Închide"', '"close_content":"×"').replace('"close_content":"Close"', '"close_content":"×"')
    text = re.sub(r'"close_css":\{[^}]*\}', '"close_css":{"font-size":"28px","color":"#1A2266"}', text)
    text = text.replace('"height":"450px"', '"height":"auto"')

    # UI-11 / UI-12: breadcrumbs – „Acasă” duce acasă, nivelul de secțiune e text, nav + aria-current
    def crumbs(m):
        ul = m.group(0)
        ul = re.sub(r'<li><a href="">(Acasă|Home|Главная|Головна)</a></li>', lambda x: f'<li><a href="{pg.link("index.html")}">{x.group(1)}</a></li>', ul)
        ul = re.sub(r'<a href="#"(?: class="without_click")?>([^<]*)</a>', r'<span class="without_click">\1</span>', ul)
        ul = re.sub(r"<li>(\s*<svg)", r'<li aria-hidden="true">\1', ul)
        ul = re.sub(r'<li><span>([^<]*)</span></li>(\s*</ul>)', r'<li><span aria-current="page">\1</span></li>\2', ul)
        # secțiunea din breadcrumbs = secțiunea din meniu în care se află pagina (ex. Regulamente → Despre noi)
        section = CRUMB_SECTION.get(pg.key)
        if section:
            ul = re.sub(r'<li><span(?: class="without_click")?>[^<]*</span></li>',
                        f'<li><span class="without_click">{t["section"][section]}</span></li>', ul, count=1)
        ul = ul.replace(">Despre Noi<", ">Despre noi<").replace(">About Us<", ">About us<")
        return f'<nav aria-label="{t["breadcrumb"]}">{ul}</nav>'
    if not pg.academy:
        text = re.sub(r'<ul class="breadcrumbs">[\s\S]*?</ul>', crumbs, text)

    # UI-02 / UI-22: tickerul doar pe paginile de piață, marcat „Date demonstrative”, cu buton de pauză
    ticker = re.compile(r'<div class="bimx-ticker-wrap">\s*<div class="bimx-ticker" id="bimx-ticker-content">\s*</div>\s*</div>')
    if pg.key in TICKER_PAGES:
        text = ticker.sub(
            f'<div class="bimx-ticker-wrap bx-ticker" role="region" aria-label="{t["ticker_label"]}">'
            f'<span class="bx-ticker-label">{t["demo"]}</span>'
            f'<div class="bimx-ticker" id="bimx-ticker-content"></div>'
            f'<button type="button" class="bx-ticker-toggle" aria-pressed="false" data-pause="{t["pause"]}" data-play="{t["play"]}">'
            f'{t["pause"]}</button></div>', text)
    else:
        text = ticker.sub("", text)

    # UI-26: toate PDF-urile se deschid în filă nouă; un singur Nomenclator; linkurile PDF goale devin „În curând”
    text = text.replace(NOMENCLATOR_OLD.split("/")[-1] + '"', NOMENCLATOR.split("/")[-1] + '"')
    text = re.sub(r'<a href="([^"#]+\.pdf)"(?![^>]*target=)', r'<a href="\1" target="_blank" rel="noopener"', text)
    text = re.sub(r'<a target="_blank" href="([^"]+\.pdf)">', r'<a href="\1" target="_blank" rel="noopener">', text)
    text = re.sub(r'<a href="" download>\s*<svg[\s\S]*?</svg>\s*[^<]*</a>', f'<span class="bx-soon">{t["soon"]}</span>', text)

    # UI-11 / UI-25: rețelele sociale din Contacte – fără link gol, cu nume accesibil
    if "social_block" in text:
        text = re.sub(r'\s*<a href="">\s*<svg[\s\S]*?</svg>\s*</a>', "", text)
        # aceleași iconițe ca în subsol
        text = re.sub(rf'<a href="{re.escape(LINKEDIN)}">\s*<svg[\s\S]*?</svg>\s*</a>',
                      lambda m: f'<a href="{LINKEDIN}" class="bx-social-btn">{chrome.ICON_LINKEDIN}</a>', text)
        text = re.sub(r'<a href="(https://www\.facebook\.com/[^"]*)">\s*<svg[\s\S]*?</svg>\s*</a>',
                      lambda m: f'<a href="{m.group(1)}" class="bx-social-btn">{chrome.ICON_FACEBOOK}</a>', text)
        text = text.replace(f'<a href="{LINKEDIN}" class="bx-social-btn">', f'<a href="{LINKEDIN}" class="bx-social-btn" target="_blank" rel="noopener" aria-label="LinkedIn">')
        text = re.sub(r'<a href="(https://www\.facebook\.com/[^"]*)" class="bx-social-btn">', r'<a href="\1" class="bx-social-btn" target="_blank" rel="noopener" aria-label="Facebook">', text)

    # UI-24: iframe-ul hărții are titlu
    text = re.sub(r'<iframe (src="https://www\.google\.com/maps[^"]*")', rf'<iframe title="{pick(pg.lang, "Harta sediului BIMx", "Map of the BIMx office", "Карта офиса BIMx", "Карта офісу BIMx")}" \1', text)
    # UI-28: miniatura de 300 px nu mai e aleasă pentru carduri afișate la ~450 px
    text = re.sub(r',\s*[^",]*article_image-300x200\.png 300w', "", text)

    # UI-31 / UI-25: texte de interfață netraduse și fără diacritice
    if pg.lang == "ro":
        for a, b in (("Regulamente si Acte normative", "Regulamente și acte normative"), ("Dezvaluirea informatiei", "Dezvăluirea informației"),
                     ("Situatii financiare 2025", "Situații financiare 2025"), ("Parteneri Instiutuţionali", "Parteneri instituționali"),
                     (">Ştiri<", ">Știri<"), ("<h4>Piaţă</h4>", "<h4>Piață</h4>"), (">Piaţă<", ">Piață<"),
                     ("Citeste mai mult", "Citiți mai mult"), ("Citește mai mult", "Citiți mai mult"), (">Continue reading <span", ">Citiți mai mult <span")):
            text = text.replace(a, b)
    return text


RU_FONT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&amp;display=swap">\n')
SITE_URL = "https://rhaliplii.github.io/bimx_new/"      # adresa publică a site-ului (pentru imaginea și linkurile de partajare)
OG_IMAGE = "assets/img/og-bimx.png"


def fix_og(text, pg):
    """Meta-date de partajare (Open Graph și Twitter): titlu, descriere, adresă, limbă și imaginea BIMx 1200 × 630."""
    head_end = text.find("</head>")
    if head_end < 0 or 'property="og:image"' in text[:head_end]:
        return text
    title = re.search(r"<title>([^<]*)</title>", text)
    title = _html.unescape(title.group(1)).strip() if title else "BIMx"
    if pg.home:
        title = pick(pg.lang, "Bursa Internațională a Moldovei (BIMx)", "Moldova International Stock Exchange (BIMx)",
                     "Международная фондовая биржа Молдовы (BIMx)", "Міжнародна фондова біржа Молдови (BIMx)")
    desc = re.search(r'<meta name="description" content="([^"]*)"', text)
    desc = _html.unescape(desc.group(1)) if desc else ""
    url = SITE_URL + str(pg.rel).replace("\\", "/").removesuffix("index.html")
    e = lambda v: _html.escape(v, quote=True)
    locale = LOCALES[pg.lang][1]
    alts = "".join(f'\n<meta property="og:locale:alternate" content="{LOCALES[x][1]}">' for x in SITE_LANGS if x != pg.lang)
    # scoatem meta-datele vechi (WordPress), ca să nu fie duble
    head = re.sub(r'\s*<meta (?:property="og:[^"]*"|name="twitter:[^"]*")[^>]*>', "", text[:head_end])
    tags = (f'\n<meta property="og:type" content="website">'
            f'\n<meta property="og:site_name" content="BIMx">'
            f'\n<meta property="og:title" content="{e(title)}">'
            f'\n<meta property="og:description" content="{e(desc)}">'
            f'\n<meta property="og:url" content="{e(url)}">'
            f'\n<meta property="og:locale" content="{locale}">'
            f'{alts}'
            f'\n<meta property="og:image" content="{SITE_URL}{OG_IMAGE}">'
            f'\n<meta property="og:image:width" content="1200">'
            f'\n<meta property="og:image:height" content="630">'
            f'\n<meta property="og:image:alt" content="{pick(pg.lang, "BIMx – Bursa Internațională a Moldovei", "BIMx – Moldova International Stock Exchange", "BIMx — Международная фондовая биржа Молдовы", "BIMx — Міжнародна фондова біржа Молдови")}">'
            f'\n<meta name="twitter:card" content="summary_large_image">'
            f'\n<meta name="twitter:title" content="{e(title)}">'
            f'\n<meta name="twitter:description" content="{e(desc)}">'
            f'\n<meta name="twitter:image" content="{SITE_URL}{OG_IMAGE}">\n')
    return head + tags + text[head_end:]


def fix_meta(text, pg):
    """UI-20: meta description generată din descrierea paginii sau din primul paragraf (Academy are deja)."""
    if '<meta name="description"' in text:
        return text
    desc = re.search(r'<div class="page_description">([\s\S]*?)</div>', text)
    desc = strip_tags(re.sub(r"<!--[\s\S]*?-->|-->|<!--", "", desc.group(1))) if desc else ""
    if len(desc) < 25:                         # descriere goală sau doar resturi de comentarii
        desc = ""
    if not desc:
        main = text[text.find("<main"):text.find("</main>")]
        ps = [strip_tags(p) for p in re.findall(r"<p\b[^>]*>([\s\S]*?)</p>", main)]
        desc = next((p for p in ps if len(p) > 60), "")
    if not desc:
        title = re.search(r"<title>([^<]*)</title>", text)
        name = strip_tags(title.group(1)).split(" – ")[0] if title else "BIMx"
        desc = f"{name} – " + pick(pg.lang, "Bursa Internațională a Moldovei (BIMx).", "Moldova International Stock Exchange (BIMx).",
                                   "Международная фондовая биржа Молдовы (BIMx).", "Міжнародна фондова біржа Молдови (BIMx).")
    desc = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "…"
    return text.replace("</title>", f'</title>\n<meta name="description" content="{_html.escape(desc)}">', 1)



# ---------------------------------------------------------------- conținut: fapte confirmate și afirmații depășite

COMPANY_PAGE = "https://app.gov.md/companies/operator-de-piata-bursa-internationala-a-moldovei-s-a/"
IDNO = "1025600073907"                        # confirmat de BIMx (24.09.2026)

# (RO vechi, RO nou, EN vechi, EN nou); în rusă textele corectate sunt direct în catalogul i18n/ru.json. Documentele (comunicatul și scrisorile BIMx) spun: licența CNPF la 21.08.2026,
# admiterea brokerilor și a emitenților din 28.09.2026, ARENA în producție la 1.10.2026, prima listare până la sfârșitul
# anului 2026, fără transfer automat al emitenților de la BVM. „28 septembrie” nu e data primei ședințe de tranzacționare.
TEXT_FIXES = [
    ("Începând cu 28 septembrie 2026, Bursa Internațională a Moldovei publică datele de piață pentru toate instrumentele admise la tranzacționare",
     "După începerea tranzacționării, Bursa Internațională a Moldovei va publica datele de piață pentru toate instrumentele admise la tranzacționare",
     "From 28 September 2026, the Moldova International Stock Exchange will publish market data for all instruments admitted to trading",
     "Once trading begins, the Moldova International Stock Exchange will publish market data for all instruments admitted to trading"),
    ("Prima ședință de tranzacționare are loc pe 28 septembrie 2026.",
     "Admiterea brokerilor și a emitenților începe pe 28 septembrie 2026, iar prima listare este planificată până la sfârșitul anului 2026.",
     "The first trading session takes place on 28 September 2026.",
     "Admission of brokers and issuers opens on 28 September 2026, and the first listing is planned by the end of 2026."),
    ("Lista membrilor Bursei Internaționale a Moldovei este publicată pe această pagină începând cu 28 septembrie 2026.",
     "Lista membrilor Bursei Internaționale a Moldovei va fi publicată pe această pagină după admiterea primilor membri (admiterea începe pe 28 septembrie 2026).",
     "The list of members of the Moldova International Stock Exchange is published on this page from 28 September 2026.",
     "The list of members of the Moldova International Stock Exchange will be published on this page once the first members are admitted (admission opens on 28 September 2026)."),
    # C-13: Prezentare generală afirma o preluare automată a tranzacționării de la BVM
    ("La momentul operaționalizării, BIMx preia continuitatea tranzacționării pentru acțiunile și obligațiunile (corporative, municipale și de stat).",
     "Emitenții și instrumentele tranzacționate în prezent la BVM pot fi admise pe piețele BIMx printr-un proces distinct de admitere, conform Regulilor BIMx; documentele existente pot fi reutilizate dacă sunt valabile și actualizate.",
     "Upon becoming operational, BIMx assumes continuity of trading in shares and bonds (corporate, municipal and government).",
     "Issuers and instruments currently traded on the BVM can be admitted to the BIMx markets through a separate admission process under the BIMx Rules; existing documents can be reused if they are valid and up to date."),
    # C-11: pagina Obligațiuni afirma că toate categoriile sunt deja admise (data 28.09 și transferul de la BVM)
    ("Bursa Internațională a Moldovei administrează tranzacționarea a trei categorii de instrumente cu venit fix aflate anterior în tranzacționare la Bursa de Valori a Moldovei",
     "Bursa Internațională a Moldovei poate admite la tranzacționare trei categorii de instrumente cu venit fix: valori mobiliare de stat, obligațiuni municipale și obligațiuni corporative.",
     "The Moldova International Stock Exchange operates trading in three categories of fixed-income instruments previously traded on the Moldova Stock Exchange",
     "The Moldova International Stock Exchange can admit three categories of fixed-income instruments to trading: government securities, municipal bonds and corporate bonds."),
    ("Emise de Ministerul Finanțelor al Republicii Moldova.",
     "Emise de Ministerul Finanțelor al Republicii Moldova. Cele cu termen lung sunt admise de drept, la inițiativa Ministerului Finanțelor; bonurile de trezorerie nu intră în această procedură.",
     "Issued by the Ministry of Finance of the Republic of Moldova.",
     "Issued by the Ministry of Finance of the Republic of Moldova. Long-term securities are admitted by right, at the initiative of the Ministry of Finance; treasury bills are not covered by this procedure."),
    ("Emise de autorități ale administrației publice locale.",
     "Emise de autorități ale administrației publice locale. Pot fi admise pe Piața Reglementată printr-un dosar depus de un Participant inițiator.",
     "Issued by local public authorities.",
     "Issued by local public authorities. They can be admitted to the Regulated Market through a file submitted by an initiating participant."),
    ("Toate cele trei categorii sunt admise la tranzacționare pe piețele BIMx începând cu 28 septembrie 2026. Filtrele din secțiunea „Cotații în timp real” permit selectarea instrumentelor pe tip de emitent, scadență și randament.",
     "Obligațiunile municipale pot fi admise pe Piața Reglementată BIMx printr-un dosar depus de un Participant inițiator (decizia consiliului local, certificatul CNPF, Angajamentul de admitere și menținere, dovada tarifului, două persoane de legătură). Valorile mobiliare de stat cu termen lung sunt admise de drept, la inițiativa Ministerului Finanțelor; bonurile de trezorerie nu intră în această procedură. Admiterea la BIMx este un proces distinct, fără transfer automat de la BVM.",
     "All three categories are admitted to trading on the BIMx markets from 28 September 2026. The filters in the “Real-Time Quotes” section allow instruments to be selected by issuer type, maturity and yield.",
     "Municipal bonds can be admitted to the BIMx Regulated Market through a file submitted by an initiating participant (the local council decision, the CNPF certificate, the Admission and Maintenance Undertaking, proof of payment of the fee and two contact persons). Long-term government securities are admitted by right, at the initiative of the Ministry of Finance; treasury bills are not covered by this procedure. Admission to BIMx is a separate process, with no automatic transfer from the BVM."),
    ("Până la lansarea operațională (Septembrie 2026), fiecare categorie de participanți are deja un rol.",
     "Până la începerea tranzacționării, fiecare categorie de participanți are deja un rol.",
     "Ahead of the operational launch (September 2026), every category of participant already has a role to play.",
     "Ahead of the start of trading, every category of participant already has a role to play."),
    ("Bursa Internațională a Moldovei preia acțiuni aflate anterior în tranzacționare la Bursa de Valori a Moldovei (BVM) și le admite pe piețele administrate de BIMx.",
     "Emitenții ale căror acțiuni sunt tranzacționate la Bursa de Valori a Moldovei (BVM) pot solicita admiterea la BIMx; nu există un transfer automat.",
     "The Moldova International Stock Exchange is taking over shares previously traded on the Moldova Stock Exchange (BVM) and admitting them to the markets operated by BIMx.",
     "Issuers whose shares are traded on the Moldova Stock Exchange (BVM) can apply for admission to BIMx; there is no automatic transfer."),
    ("<h4>Companii noi</h4>", "<h4>Emitenți noi</h4>", "<h4>New companies</h4>", "<h4>New issuers</h4>"),
    # C-06: cardul „Integrarea emitenților BVM” prezenta preluarea ca automată și certă
    ("Integrarea emitenților BVM", "Admiterea emitenților BVM", "Integration of BVM issuers", "Admission of BVM issuers"),
    ("Emitenții care au avut acțiuni admise la tranzacționare pe piețele BVM sunt integrați în cadrul BIMx printr-un proces de admitere structurat, care asigură continuitatea accesului investitorilor la aceste instrumente financiare.",
     "Emitenții ale căror acțiuni sunt tranzacționate la BVM pot solicita admiterea la BIMx. Admiterea este un proces distinct, conform Regulilor BIMx; documentele existente pot fi reutilizate dacă sunt valabile și actualizate.",
     "Issuers whose shares were admitted to trading on the BVM markets are being integrated into BIMx through a structured admission process that ensures investors retain continuous access to these financial instruments.", "Issuers whose shares are traded on the BVM can apply for admission to BIMx. Admission is a separate process under the BIMx Rules; existing documents can be reused if they are valid and up to date."),
    ("În paralel cu preluarea emitenților existenți,", "În paralel cu admiterea emitenților listați anterior la BVM,",
     "Alongside the takeover of existing issuers,", "Alongside the admission of issuers previously listed on the BVM,"),
    ("Aprintin", "Arpintin", "Aprintin", "Arpintin"),
    ("Cele mai recente actualizări de la BIMx și companiile listate", "Cele mai recente comunicate și anunțuri ale BIMx",
     "The latest updates from BIMx and listed companies", "The latest BIMx press releases and announcements"),
]

# Blocurile „Disponibilitate – 28 septembrie 2026”: starea reală și pasul următor, pe fiecare pagină
STATUS_BLOCKS = {
    "actiuni": ("Lista acțiunilor admise la tranzacționare, cu datele de referință și clasificarea pe piețe, va fi publicată după admiterea primilor emitenți. Prima listare este planificată până la sfârșitul anului 2026.",
                "The list of shares admitted to trading, with reference data and market classification, will be published once the first issuers are admitted. The first listing is planned by the end of 2026.",
               "Список акций, допущенных к торгам, с базовыми данными и распределением по рынкам будет опубликован после допуска первых эмитентов. Первый листинг запланирован до конца 2026 года.",
               "Перелік акцій, допущених до торгів, із довідковими даними та розподілом за ринками буде опубліковано після допуску перших емітентів. Перший лістинг заплановано до кінця 2026 року."),
    "cotatii-in-timp-real": ("Cotațiile vor fi publicate după începerea tranzacționării, care urmează primei listări (planificată până la sfârșitul anului 2026).",
                             "Quotes will be published once trading begins, following the first listing (planned by the end of 2026).",
                            "Котировки будут публиковаться после начала торгов, которые последуют за первым листингом (запланирован до конца 2026 года).",
                            "Котирування публікуватимуться після початку торгів, які розпочнуться після першого лістингу (запланованого до кінця 2026 року)."),
    "fise-detaliate": ("Fișele detaliate devin active odată cu admiterea primelor instrumente la tranzacționare.",
                       "Detailed factsheets go live once the first instruments are admitted to trading.",
                      "Подробные карточки станут доступны с допуском первых инструментов к торгам.",
                      "Детальні картки стануть доступними з допуском перших інструментів до торгів."),
    "indicii-bursei": ("Indicii vor fi calculați după ce tranzacționarea atinge o bază suficientă de calcul. Metodologia fiecărui indice va fi publicată înainte de lansarea lui.",
                       "Indices will be calculated once trading provides a sufficient basis. The methodology of each index will be published before it is launched.",
                      "Индексы будут рассчитываться, когда объём торгов обеспечит достаточную базу для расчёта. Методика каждого индекса будет опубликована до его запуска.",
                      "Індекси розраховуватимуться, коли обсяг торгів забезпечить достатню базу для розрахунку. Методику кожного індексу буде опубліковано до його запуску."),
    "program-de-tranzactionare": ("Calendarul zilelor de tranzacționare va fi publicat pe această pagină înainte de prima ședință de tranzacționare, care urmează primei listări.",
                                  "The calendar of trading days will be published on this page before the first trading session, which follows the first listing.",
                                 "Календарь торговых дней будет опубликован на этой странице до первой торговой сессии, которая последует за первым листингом.",
                                 "Календар торговельних днів буде опубліковано на цій сторінці до першої торгової сесії, яка відбудеться після першого лістингу."),
    "rapoarte": ("Rapoartele proprii BIMx devin disponibile după începerea tranzacționării.",
                 "BIMx's own reports become available once trading begins.",
                "Собственные отчёты BIMx станут доступны после начала торгов.",
                "Власні звіти BIMx стануть доступними після початку торгів."),
    "valori-mobiliare": ("Datele de tranzacționare vor fi publicate în secțiunea „Cotații în timp real” după începerea tranzacționării.",
                         "Trading data will be published in the “Real-Time Quotes” section once trading begins.",
                        "Торговые данные будут публиковаться в разделе «Котировки в режиме реального времени» после начала торгов.",
                        "Торговельні дані публікуватимуться в розділі «Котирування в реальному часі» після початку торгів."),
}
# pe Procesul de listare data de 28 septembrie e corectă: e data de la care emitenții pot cere admiterea
LISTING_BLOCK = (("Admiterea emitenților", "Emitenții pot depune cererea de admitere începând cu 28 septembrie 2026. Prima listare este planificată până la sfârșitul anului 2026."),
                 ("Admission of issuers", "Issuers can apply for admission from 28 September 2026. The first listing is planned by the end of 2026."),
                 ("Допуск эмитентов", "Эмитенты могут подать заявку на допуск с 28 сентября 2026 г. Первый листинг запланирован до конца 2026 года."),
                 ("Допуск емітентів", "Емітенти можуть подати заявку на допуск із 28 вересня 2026 р. Перший лістинг заплановано до кінця 2026 року."))


# Adresarea formală (dvs.) în interfața și textele bimx.md: forma de „tu” → forma de politețe
FORMAL_RO = [(">Vezi toate", ">Vedeți toate"), (">Vezi pe hartă", ">Vedeți pe hartă"), ("Contactează-ne!", "Contactați-ne!"),
             (">Descarcă PDF", ">Descărcați PDF"), (">Descarcă Nomenclatorul", ">Descărcați Nomenclatorul"), (">Descarcă<", ">Descărcați<"),
             ("Devino membru BIMx", "Deveniți membru BIMx"), (">Explorează și<", ">Explorați și<"), ("Urmărește-ne", "Urmăriți-ne"), ("Fii la curent", "Fiți la curent"),
             ('placeholder="Caută pe site..."', 'placeholder="Căutați pe site…"'), ('aria-label="Caută"', 'aria-label="Căutați"')]


# C-05 (audit de conținut): articolul din 17.06.2026 indică un capital de 3.000.000 EUR; comunicatul BIMx (sursa de
# adevăr) indică un capital social inițial de 29.475.000 lei (1,5 mil. EUR). Articolul fiind datat, textul original
# rămâne, iar dedesubt se adaugă o notă „Actualizare:” cu cifra din comunicat.
CAPITAL_ARTICLE = "bimx-depune-dosarul-pentru-obtinerea-licentei-de-operator-de-piata"
CAPITAL_SENTENCE = re.compile(r"(3[.,\s\u00a0]000[.,\s\u00a0]000\s*(?:EUR|евро|євро)\.)(</p>)")
CAPITAL_NOTE = {
    "ro": ("Actualizare", "Capitalul social inițial al BIMx este de 29.475.000 de lei (1,5 milioane de euro)."),
    "en": ("Update", "BIMx's initial share capital is MDL 29,475,000 (EUR 1.5 million)."),
    "ru": ("Обновление", "Первоначальный уставный капитал BIMx составляет 29\u00a0475\u00a0000 леев (1,5 млн евро)."),
    "uk": ("Оновлення", "Початковий статутний капітал BIMx становить 29\u00a0475\u00a0000 леїв (1,5 млн євро)."),
}


def fix_council_en(text, pg):
    """EN, pagina Consiliul și Organul Executiv: „Exchange Council” → „BIMx Board” (titlu, funcții, biografii)."""
    if pg.lang != "en" or pg.key != "consiliul-si-organul-executiv":
        return text
    text = text.replace("Exchange Council Member", "Board Member").replace("the Council members", "the Board members")
    text = text.replace("Chair of the Exchange Council", "Chair of the Board")
    return text.replace("Exchange Council", "BIMx Board")


# Parteneri instituționali: CNPF (logo din subsol) și partenerii de dezvoltare (logo-urile din partners/, redimensionate)
PARTNER_CARDS = [
    ("wp-content/themes/victor-child/assets/img/CNPF.png", 154, 84,
     ("CNPF – Comisia Națională a Pieței Financiare", "CNPF – National Commission for Financial Markets",
      "НКФР — Национальная комиссия по финансовому рынку", "НКФР — Національна комісія з фінансового ринку"),
     ("Autoritatea de reglementare și supraveghere a pieței financiare nebancare", "The regulatory and supervisory authority for the non-banking financial market",
      "Орган регулирования и надзора за небанковским финансовым рынком", "Орган регулювання та нагляду за небанківським фінансовим ринком")),
    ("assets/img/partners/canada.png", 456, 160,
     ("Guvernul Canadei", "Government of Canada", "Правительство Канады", "Уряд Канади"),
     ("Partener de dezvoltare internațional", "International development partner", "Международный партнёр по развитию",
      "Міжнародний партнер із розвитку")),
    ("assets/img/partners/un-women.png", 720, 125,
     ("UN Women", "UN Women", "Структура «ООН-женщины»", "Структура ООН-Жінки"),
     ("Entitatea ONU pentru egalitatea de gen și abilitarea femeilor", "The UN entity for gender equality and the empowerment of women",
      "Структура ООН по вопросам гендерного равенства и расширения прав и возможностей женщин",
      "Структура ООН з питань гендерної рівності та розширення прав і можливостей жінок")),
    ("assets/img/partners/undp.png", 79, 160,
     ("PNUD – Programul Națiunilor Unite pentru Dezvoltare", "UNDP – United Nations Development Programme",
      "ПРООН — Программа развития Организации Объединённых Наций", "ПРООН — Програма розвитку Організації Об’єднаних Націй"),
     ("Agenția ONU pentru dezvoltare durabilă", "The UN agency for sustainable development",
      "Агентство ООН по устойчивому развитию", "Агентство ООН зі сталого розвитку")),
    ("assets/img/partners/sparkassenstiftung.png", 720, 130,
     ("German Sparkassenstiftung Moldova", "German Sparkassenstiftung Moldova", "German Sparkassenstiftung Moldova",
      "German Sparkassenstiftung Moldova"),
     ("Fundația germană a caselor de economii pentru cooperare internațională", "The German Savings Banks Foundation for International Cooperation",
      "Фонд немецких сберегательных касс по международному сотрудничеству",
      "Фонд німецьких ощадних кас з міжнародного співробітництва")),
    ("assets/img/partners/brd.png", 463, 160,
     ("BRD – Biroul Relații cu Diaspora", "BRD – Diaspora Relations Bureau", "BRD — Бюро по связям с диаспорой",
      "BRD — Бюро зі зв’язків з діаспорою"),
     ("Instituția guvernamentală responsabilă de relațiile cu diaspora Republicii Moldova",
      "The government body responsible for relations with the diaspora of the Republic of Moldova",
      "Государственное учреждение, ответственное за связи с диаспорой Республики Молдова",
      "Державна установа, відповідальна за зв’язки з діаспорою Республіки Молдова")),
    # logo (varianta RO pe pagina română, EN în rest) și descriere preluate de pe eba.md
    (("assets/img/partners/eba-ro.png", "assets/img/partners/eba-en.png", "assets/img/partners/eba-en.png", "assets/img/partners/eba-en.png"), 349, 179,
     ("EBA – Asociația Businessului European", "EBA – European Business Association", "EBA — Европейская бизнес-ассоциация",
      "EBA — Європейська бізнес-асоціація"),
     ("Organizație independentă, neguvernamentală, care urmărește alinierea economiei naționale și a legislației de business la standardele UE",
      "An independent, non-governmental organisation aimed at aligning the national economy and business legislation with EU standards",
      "Независимая неправительственная организация, стремящаяся привести национальную экономику и деловое законодательство в соответствие со стандартами ЕС",
      "Незалежна неурядова організація, що прагне узгодити національну економіку та законодавство у сфері бізнесу зі стандартами ЄС")),
    # logo și descriere preluate de pe frankfurt-school.de (fs_logo_blue.svg și descrierea paginii principale)
    ("assets/img/partners/frankfurt-school.svg", 174, 75,
     ("Frankfurt School of Finance &amp; Management",) * 4,
     ("Una dintre principalele școli de business din Europa, care îmbină excelența academică cu relevanța practică",
      "One of Europe’s leading business schools, combining academic excellence with practical relevance",
      "Одна из ведущих бизнес-школ Европы, сочетающая академическое превосходство с практической направленностью",
      "Одна з провідних бізнес-шкіл Європи, що поєднує академічну досконалість із практичною спрямованістю")),
]

# ordinea de afișare (după CNPF urmează Invest Moldova, cardul existent pe pagină): BRD, EBA, Canada, UN Women, PNUD, Frankfurt School, Sparkassenstiftung
_ORDER = ("CNPF.png", "brd.png", "eba-", "canada.png", "un-women.png", "undp.png", "frankfurt-school.svg", "sparkassenstiftung.png")
PARTNER_CARDS.sort(key=lambda c: next(i for i, n in enumerate(_ORDER) if n in (c[0] if isinstance(c[0], str) else c[0][0])))

def fix_partners(text, pg):
    """Parteneri instituționali: logo-ul Invest Moldova ca imagine (SVG-ul cu PNG încorporat nu se afișa); fără cardul ODA."""
    if pg.key != "parteneri-institutionali" or "bx-partner-logo" in text:
        return text
    items = list(re.finditer(r'<div class="item">\s*<div class="icon">\s*<svg[\s\S]*?</svg>\s*</div>[\s\S]*?</div>', text))
    if len(items) < 2:
        return text
    oda, invest = items[1], items[0]
    text = text[:oda.start()] + text[oda.end():]                              # cardul ODA dispare
    logo = (f'<div class="icon bx-partner-logo"><img src="{pg.asset("wp-content/themes/victor-child/assets/img/Invest.png")}" '
            f'alt="Invest Moldova" width="154" height="84"></div>')
    text = re.sub(r'<div class="icon">\s*<svg[\s\S]*?</svg>\s*</div>', lambda m: logo, text, count=1)
    # cardurile noi (CNPF și partenerii de dezvoltare), după Invest Moldova
    card = lambda img, w, h, name, desc: (
        f'\n                <div class="item"><div class="icon bx-partner-logo"><img src="{pg.asset(img if isinstance(img, str) else img[IDX[pg.lang]])}" alt="{name[IDX[pg.lang]]}" '
        f'width="{w}" height="{h}" loading="lazy"></div><h3>{name[IDX[pg.lang]]}</h3><p>{desc[IDX[pg.lang]]}</p></div>')
    first = re.search(r'<div class="item">\s*<div class="icon bx-partner-logo">[\s\S]*?</p>\s*</div>', text)
    if not first:
        return text
    # ordinea: CNPF, Invest Moldova, apoi partenerii de dezvoltare
    before = card(*PARTNER_CARDS[0]) + "\n                "
    after = "".join(card(*c) for c in PARTNER_CARDS[1:])
    return text[:first.start()] + before + text[first.start():first.end()] + after + text[first.end():]


def fix_capital(text, pg):
    if CAPITAL_ARTICLE not in str(pg.rel) or "bx-update-note" in text:
        return text
    label, note = CAPITAL_NOTE[pg.lang]
    return CAPITAL_SENTENCE.sub(
        lambda m: f'{m.group(1)}{m.group(2)}\n<p class="bx-update-note"><strong>{label}:</strong> {note}</p>', text, count=1)


def fix_content(text, pg):
    if pg.lang == "ro" and not pg.academy:
        for a, b in FORMAL_RO:
            text = text.replace(a, b)
        text = re.sub(r">(\s*)Vezi toate", r">\1Vedeți toate", text)
        text = re.sub(r">(\s*)Citește mai mult", r">\1Citiți mai mult", text)
        text = re.sub(r">(\s*)Descarcă(\s)", r">\1Descărcați\2", text)
    if pg.lang in ("ro", "en"):            # în rusă și ucraineană, cataloagele i18n/ conțin deja textele corectate
        i = 1 if pg.lang == "ro" else 3
        for row in TEXT_FIXES:
            text = text.replace(row[i - 1], row[i])
    # în română, separatorul zecimal al procentelor e virgula (26,67%), ca în documente
    if pg.lang == "ro":
        text = re.sub(r">(\s*)(\d{1,3})\.(\d{1,2})%(\s*)<", r">\1\2,\3%\4<", text)
    # IDNO confirmat, cu link spre fișa companiei (app.gov.md); licența: fără numărul provizoriu „000123”
    text = re.sub(r"<b>1003600028020</b>",
                  f'<b><a href="{COMPANY_PAGE}" target="_blank" rel="noopener" class="bx-idno">{IDNO}</a></b>', text)
    # licența: seria reală CNPF 000945 (în locul numărului provizoriu „000123” din copia bimx.md), cu data acordării
    from .chrome import LICENCE_NO
    text = re.sub(r"<b>(?:CNPF, seri(?:a|es) CNPF N(?:r|o)\.|НКФР, сери[яї] CNPF №|НКФР, сері[яї] CNPF №) 000123</b>",
                  pick(pg.lang, f"<b>Licență de operator de piață CNPF, seria {LICENCE_NO} (21 august 2026)</b>",
                       f"<b>CNPF market operator licence, series {LICENCE_NO} (21 August 2026)</b>",
                       f"<b>Лицензия оператора рынка НКФР, серия {LICENCE_NO} (21 августа 2026 г.)</b>",
                       f"<b>Ліцензія оператора ринку НКФР, серія {LICENCE_NO} (21 серпня 2026 р.)</b>"), text)

    def status(m):
        block = m.group(0)
        if not re.search(r"<h2>\s*28 (?:septembrie|September|сентября|вересня) 2026(?: [гр]\.)?\s*</h2>", block):
            return block
        if pg.key == "procesul-de-listare":
            label, desc = LISTING_BLOCK[IDX[pg.lang]]
            value = pick(pg.lang, "28 septembrie 2026", "28 September 2026", "28 сентября 2026 г.", "28 вересня 2026 р.")
        else:
            texts = STATUS_BLOCKS.get(pg.key)
            label, value = pick(pg.lang, ("Stare", "În pregătire"), ("Status", "In preparation"), ("Статус", "В подготовке"), ("Статус", "У підготовці"))
            desc = texts[IDX[pg.lang]] if texts else None
        block = re.sub(r"(<h6[^>]*>)[\s\S]*?(</h6>)", rf"\g<1>{label}\2", block, count=1)
        block = re.sub(r"<h2>[^<]*</h2>", f"<h2>{value}</h2>", block, count=1)
        if desc:
            block = re.sub(r'(<div class="right_side">)[\s\S]*?(</div>\s*</div>\s*</div>\s*$)', rf"\1<p>{desc}</p>\2", block, count=1)
        return block.replace('class="date_section"', 'class="date_section bx-status-block"', 1)
    return re.sub(r'<div class="date_section">[\s\S]*?</div>\s*</div>\s*</div>', status, text)


# ---------------------------------------------------------------- prima pagină

def fix_home(text, pg):
    t = pg.t
    # UI-14 / UI-15: secțiunile de piață ascunse (și biblioteca de grafice de pe unpkg.com) nu se mai încarcă
    text = re.sub(r'<script src="https://unpkg\.com/[^"]*"></script>\s*', "", text)
    text = re.sub(r'<section class="market_overview">[\s\S]*?</section>\s*', "", text, count=1)
    text = re.sub(r'<div class="container">\s*<div class="numbers">[\s\S]*?</div>\s*</div>\s*</div>\s*(?=<div class="container_fluid">)',
                  "", text, count=1)
    text = re.sub(r'<div class="container_fluid">\s*<div class="market_gainers">[\s\S]*?</table>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*',
                  "", text, count=1)
    text = re.sub(r"<script>\s*async function loadBimxMovers\(\)[\s\S]*?</script>\s*", "", text, count=1)
    # UI-32: „Află mai multe” → procesul de listare (evenimentul pregătește primele listări)
    text = re.sub(r'(<div class="buttons">\s*<a href=")#(" class="btn2">)', rf'\g<1>{pg.link("procesul-de-listare/index.html")}\2', text, count=1)
    # UI-11: „Vezi toate” → toate anunțurile
    text = re.sub(r'(<div class="home_posts">[\s\S]*?<a href=")#(" class="btn3">)', rf'\g<1>{pg.link("category/anunturi-bimx/index.html")}\2', text, count=1)

    # UI-36 / UI-37 / UI-38: cardurile „Pentru cine este BIMx?”
    blocks = iter(range(3))

    def card(m):
        i = next(blocks)
        b = m.group(0)
        b = re.sub(r'<div class="icon">\s*<img [^>]*>\s*</div>', f'<div class="icon bx-icon">{AUDIENCE_ICONS[i]}</div>', b)
        b = re.sub(r'\s*<span class="note">[^<]*</span>', "", b)   # cifrele din notă nu erau reale; nota dispare
        b = re.sub(r'<a href="[^"]*">', f'<a href="{pg.link(AUDIENCE_LINKS[i])}">', b, count=1)
        return b
    text = re.sub(r'<div class="block">\s*<div class="icon">\s*<img [^>]*p[123]\.png[\s\S]*?</a>\s*</div>', card, text)
    # hero-ul original, recompus: ilustrația „Pomul vieții” și calendarul scurt (sitegen/home.py)
    from .home import restructure_home
    return restructure_home(text, pg)


# ---------------------------------------------------------------- Centrul de descărcare, Regulamente

def fix_downloads(text, pg):
    if pg.key == "centru-de-descarcare":
        docs = iter(DOWNLOADS)
        start = text.find('class="categorii_documente"')
        end = text.find("</main>", start)

        def item(m):
            name = " ".join(m.group(1).split())
            target = next(docs, None)
            if target:
                meta = f'{t_pdf} · {human_size(target, pg.lang)} · RO'
                return (f'<a href="{pg.asset(target)}" target="_blank" rel="noopener">{name} '
                        f'<span class="bx-file">{meta}<span class="screen-reader-text"> {pg.t["new_tab"]}</span></span></a>')
            return f'<span class="bx-doc-soon">{name} <span class="bx-file">{pg.t["soon"]}</span></span>'
        t_pdf = pg.t["pdf"]
        body = re.sub(r'<a href="[^"]*"(?: target="_blank" rel="noopener")?>\s*([^<]*?)\s*</a>', item, text[start:end])
        text = text[:start] + body + text[end:]
    if pg.key == "regulamente-si-acte-normative":
        def label(m):
            href = m.group(1)
            target = (pg.path.parent / href).resolve().relative_to(DIST.resolve()).as_posix()
            return m.group(0) + f' <span class="bx-file">PDF · {human_size(target, pg.lang)}</span>'
        text = re.sub(r'<a href="([^"]+\.pdf)" target="_blank" rel="noopener"(?: download)?>\s*<svg[\s\S]*?</svg>\s*[^<]*?(?=\s*</a>)', label, text)
    return text


# ---------------------------------------------------------------- pagini noi în locul celor „În curând”

def hero(pg, title, desc, section):
    t = pg.t
    crumbs = (f'<nav aria-label="{t["breadcrumb"]}"><ul class="breadcrumbs">'
              f'<li><a href="{pg.link("index.html")}">{t["home"]}</a></li><li aria-hidden="true">{SEP}</li>'
              f'<li><span class="without_click">{t["section"][section]}</span></li><li aria-hidden="true">{SEP}</li>'
              f'<li><span aria-current="page">{title}</span></li></ul></nav>')
    desc_html = f'<div class="page_description"><p>{desc}</p></div>' if desc else ""
    return (f'<div class="container_fluid"><div class="second_main_section"><div class="container">'
            f'<div class="secont_main_section_content">{crumbs}<h1 class="page_title">{title}</h1>{desc_html}'
            f'</div></div></div></div>')


def page_body(pg, spec):
    t, lang = pg.t, pg.lang
    title, desc = spec[lang]
    if spec["kind"] == "calendar":
        today = datetime.date.today()
        kinds = ["done" if row[0] and row[0] <= today else "todo" for row in CALENDAR]
        first = next((i for i, k in enumerate(kinds) if k == "todo"), None)
        kinds = [k if k == "done" else ("next" if i == first else "planned") for i, k in enumerate(kinds)]
        items = []
        for i, (row, k) in enumerate(zip(CALENDAR, kinds)):
            dt, (d, h, p) = row[0], row[1 + IDX[lang]]
            seg = " seg-done" if k == "done" and i + 1 < len(kinds) and kinds[i + 1] == "done" else ""
            items.append(f'<li class="bx-step is-{k}{seg}" data-date="{dt.isoformat() if dt else ""}"><span class="bx-step-dot" aria-hidden="true"></span>'
                         f'<p class="bx-step-meta"><time>{d}</time><span class="bx-step-state">{CAL_STATE[lang][k]}</span></p>'
                         f'<h2>{h}</h2>{f"<p>{p}</p>" if p else ""}</li>')
        items = "".join(items)
        note, label = CALENDAR_NOTE[lang]
        note = note.format(link=f'<a href="{pg.link("program-de-tranzactionare/index.html")}">{label}</a>')
        st = CAL_STATE[lang]
        content = (f'<ol class="bx-timeline" data-done="{st["done"]}" data-next="{st["next"]}" data-planned="{st["planned"]}">{items}</ol>'
                   f'<p class="bx-page-note">{note}</p>')
    elif spec["kind"] == "org":
        from .org import org_chart
        path, *names = spec["docs"][0]
        name = names[IDX[lang]]
        content = (org_chart(lang) + f'<ul class="bx-docs bx-org-doc"><li class="bx-doc">{ICON_DOC}<div><h2>{name}</h2>'
                   f'<p class="bx-file">PDF · {human_size(path, lang)} · RO</p></div><a class="bx-doc-btn" href="{pg.asset(path)}" '
                   f'target="_blank" rel="noopener">{t["doc_download"]}<span class="screen-reader-text"> {name} {t["new_tab"]}</span></a></li></ul>')
    elif spec["kind"] == "docs":
        cards = []
        for path, *names in spec["docs"]:
            name = names[IDX[lang]]
            cards.append(
                f'<li class="bx-doc">{ICON_DOC}<div><h2>{name}</h2><p class="bx-file">PDF · {human_size(path, lang)} · RO</p></div>'
                f'<a class="bx-doc-btn" href="{pg.asset(path)}" target="_blank" rel="noopener">{t["doc_download"]}'
                f'<span class="screen-reader-text"> {name} {t["new_tab"]}</span></a></li>')
        content = f'<ul class="bx-docs">{"".join(cards)}</ul>'
    else:
        path, *names = spec["see"]
        see = pick(lang, "Până atunci, consultați: ", "In the meantime, see: ", "Пока вы можете ознакомиться с разделом ",
                   "Поки що ви можете ознайомитися з розділом ")
        label = names[IDX[lang]]
        label = f"«{label}»" if lang in CYRILLIC else label
        content = (f'<div class="bx-prep"><p><strong>{t["in_prep"]}</strong></p>'
                   f'<p>{see}<a href="{pg.link(path)}">{label}</a>.</p></div>')
    return hero(pg, title, desc, spec["section"]) + f'<div class="container"><div class="bx-page">{content}</div></div>'


def fix_placeholder(text, pg):
    spec = PAGES.get(pg.key)
    if not spec or pg.home:
        return text
    body = page_body(pg, spec)
    new = re.sub(r'<div class="container">\s*<div class="in_curand">\s*<h2>[^<]*</h2>\s*</div>\s*</div>', lambda m: body, text, count=1)
    if new == text:                                              # politica-cookie: articol WordPress gol
        new = re.sub(r'<article id="post-\d+"[\s\S]*?</article><!-- #post-\d+ -->', lambda m: body, text, count=1)
    title, _ = spec[pg.lang]
    return re.sub(r"<title>[^<]*</title>", f"<title>{title} – BIMx</title>", new, count=1)


# ---------------------------------------------------------------- titluri (UI-19)

HEADING = re.compile(r"<h([1-6])\b([^>]*)>([\s\S]*?)</h\1>")


def fix_headings(text):
    """Ierarhie fără salturi pentru tehnologiile asistive: nivelul corect în aria-level, aspectul neschimbat.

    Paginile bimx.md folosesc nivelul titlului pentru mărime (h6 pentru etichete, h4 pentru carduri), iar
    stilurile temei depind de tag; nivelul logic se corectează cu aria-level, fără a schimba tag-ul.
    Subsolul și dialogurile încep o regiune nouă (primul titlu ≤ h2).
    """
    f0, f1 = text.find("<footer"), text.find("</footer>")
    regions = [(0, f0 if f0 > 0 else len(text))]
    if f0 > 0:
        regions += [(f0, f1), (f1, len(text))]
    out, pos = [], 0
    for start, end in regions:
        prev, seen_h1 = (0 if start == 0 else 1), False
        for m in HEADING.finditer(text, start, end):
            level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
            if not strip_tags(inner):
                continue
            want = level
            if level == 1:
                want = 2 if seen_h1 or start else 1
                seen_h1 = True
            want = min(want, prev + 1) if prev else want
            prev = want
            if want != level and "aria-level" not in attrs:
                out.append(text[pos:m.start()])
                out.append(f'<h{level}{attrs} aria-level="{want}">{inner}</h{level}>')
                pos = m.end()
    out.append(text[pos:])
    return "".join(out)


# ---------------------------------------------------------------- stilurile temei (UI-06, UI-17)

THEME_CSS = DIST / "wp-content" / "themes" / "victor-child" / "assets" / "css" / "main.css"
BODY_TEXT = re.compile(r"(?:^|[\s>])(?:p|li|td|dd)(?:[:.\[][^\s,]*)?$")
SMALL_PRINT = ("footer", "header", ".breadcrumbs", ".post-date", ".note", ".label", ".number", "ticker", ".date-",
               ".top_details", ".article_meta", ".post-category", ".hour", "table thead")


def transform_theme_css():
    """Transformă, la build, stilurile temei bimx.md (UI-17): corpul de text (p, li, td, dd) de 12 px → 14 px
    și de 14 px → 16 px; textele „meta” rămân. Albastrul de brand (#1DB0F0) rămâne neschimbat, la cererea BIMx.
    """
    if not THEME_CSS.exists():
        return 0
    css = THEME_CSS.read_text(encoding="utf-8")
    changes = 0

    def rule(m):
        nonlocal changes
        sel, body = m.group(1), m.group(2)
        sels = [x.strip() for x in sel.split(",")]
        new = body
        if all(BODY_TEXT.search(x) for x in sels) and not any(k in sel for k in SMALL_PRINT):
            new = re.sub(r"(font-size:\s*)14px", r"\g<1>16px", new)
            new = re.sub(r"(font-size:\s*)12px", r"\g<1>14px", new)
        if new != body:
            changes += 1
        return sel + "{" + new + "}"
    css = re.sub(r"([^{}]+)\{([^{}]*)\}", rule, css)
    # redesign: aceeași scară de spațiere, colțuri și umbre pe tot site-ul (tokenurile din src/site/site.css)
    for a, b in ((r"margin: 100px 0", "margin: 72px 0"), (r"margin: 85px 0", "margin: 72px 0"), (r"margin: 60px 0", "margin: 56px 0"),
                 (r"padding: 100px 0", "padding: 72px 0"), (r"padding: 80px 0", "padding: 64px 0"),
                 (r"border-radius: (?:24|20)px", "border-radius: 16px"), (r"border-radius: (?:10|7|6|5|4)px", "border-radius: 8px"),
                 (r"border: 0\.8px solid #E5E7EB", "border: 1px solid #E3E6EE"), (r"#E5E7EB", "#E3E6EE"),
                 (r"box-shadow: 0px 2px 6px 0px rgba\((?:106, 113, 129|86, 91, 101), 0\.4\)",
                  "box-shadow: 0 1px 2px rgba(20, 26, 61, .04), 0 12px 28px -16px rgba(20, 26, 61, .28)")):
        css, n = re.subn(a, b, css)
        changes += n
    THEME_CSS.write_text(css, encoding="utf-8")
    return changes


# ---------------------------------------------------------------- rulare

def redirect_page(dest, target_dir, lang):
    here = dest.parent
    target = relto(DIST / (LANG_PREFIX[lang] + target_dir) / "index.html", here)
    dest.write_text(
        f'<!doctype html>\n<html lang="{LOCALES[lang][0]}"><head><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{target}"><title>BIMx</title></head>'
        f'<body><a href="{target}">BIMx</a></body></html>\n', encoding="utf-8")


def retarget_links(text, here):
    """Linkurile spre rutele redirecționate (UI-13, „Indici”) duc direct la pagina finală."""
    def fix(m):
        attr, val = m.group(1), m.group(2)
        if val.startswith(("#", "http", "mailto:", "tel:", "data:")) or "index.html" not in val:
            return m.group(0)
        path, _, frag = val.partition("#")
        try:
            target = (here / path).resolve().relative_to(DIST.resolve())
        except ValueError:
            return m.group(0)
        parts = target.parts
        lang = LANG_PREFIX[lang_of(parts)]
        rest = parts[1:] if lang else parts
        if len(rest) == 2 and rest[0] in REDIRECTS and rest[1] == "index.html":
            new = relto(DIST / (lang + REDIRECTS[rest[0]]) / "index.html", here) + (f"#{frag}" if frag else "")
            return f'{attr}="{new}"'
        return m.group(0)
    return re.sub(r'(href)="([^"]*)"', fix, text)


def apply_fixes():
    transform_theme_css()
    (DIST / "assets" / "img").mkdir(parents=True, exist_ok=True)
    for name in ("og-bimx.png", "hero-x.webp", "bimx-logo.svg", "bimx-logo-light.svg"):
        shutil.copy2(SRC / "site" / "img" / name, DIST / "assets" / "img" / name)
    shutil.copytree(SRC / "site" / "img" / "partners", DIST / "assets" / "img" / "partners", dirs_exist_ok=True)
    changed = 0
    for f in sorted(DIST.rglob("*.html")):
        rel = f.relative_to(DIST)
        if rel.parts[0] in ("wp-content", "wp-includes", "assets"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if 'http-equiv="refresh"' in text[:600]:
            continue
        pg = Page(f)
        new = fix_header(text, pg)
        new = fix_footer(new, pg)
        new = chrome.header(new, pg)      # antet compact, limba și contul în meniu, căutare ca dialog
        new = chrome.footer(new, pg)      # subsolul nou
        new = fix_common(new, pg)
        new = fix_content(new, pg)
        new = fix_capital(new, pg)
        new = fix_council_en(new, pg)
        new = fix_partners(new, pg)
        if pg.home:
            new = fix_home(new, pg)
        new = fix_downloads(new, pg)
        new = fix_placeholder(new, pg)
        new = fix_meta(new, pg)
        if not pg.academy:                  # sistemul unitar de iconițe (sitegen/siteicons.py)
            from .siteicons import apply_icons
            new, _ = apply_icons(new, pg.key, pg.lang)
        new = link_crumbs(new, pg)
        new = fix_og(new, pg)
        if pg.lang in CYRILLIC and "family=Montserrat" not in new:     # fontul cu chirilică (vezi site.css)
            new = new.replace("</head>", RU_FONT + "</head>", 1)
        new = fix_headings(new)
        new = retarget_links(new, f.parent)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed += 1
    # pagina „Intră în cont” (în toate limbile), construită din pagina-șablon deja corectată
    from .login import build_login_pages
    build_login_pages(Page)
    # rutele duplicate devin redirecționări; vechiul Nomenclator nu mai e folosit
    for lang in SITE_LANGS:
        for src, dst in REDIRECTS.items():
            dest = DIST / (LANG_PREFIX[lang] + src) / "index.html"
            if dest.exists():
                redirect_page(dest, dst, lang)
    old = DIST / NOMENCLATOR_OLD
    if old.exists():
        old.unlink()
    return changed
