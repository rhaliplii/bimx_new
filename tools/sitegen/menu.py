"""Meniul principal (desktop: dropdown la hover sub fiecare element; mobil: aceeași structură în meniul temei), RO / EN / RU / UK.

Două tipare, aceleași reguli peste tot:
  „Listă”    – cel mult 6 linkuri: o coloană, doar titluri;
  „Coloane”  – peste 6 linkuri: coloane cu titlu de grup, doar titluri;
  bara de jos – în toate panourile: o linie de context și, dacă există, acțiunea principală (link text).
Marcajul păstrează clasele temei (menu-item-has-children, sub-menu, not_click, back_to_main_menu), ca meniul de pe mobil
să funcționeze ca până acum; aspectul de desktop e în site.css (.bx-dd), deschiderea la hover în replica.js.
Denumirile sunt cele existente pe site (aceleași traduceri); textele noi au traducerea aici.
"""
import re

from .chrome import NAV

UPLOADS = "wp-content/uploads"
PDF_STATUT = f"{UPLOADS}/2026/06/Statut-BIMx.pdf"
PDF_FIN = f"{UPLOADS}/2026/06/Situatii-financiare-BIMx-anul-2025.pdf"
PDF_AUDIT = f"{UPLOADS}/2026/06/Raportul-audit-financiar-BIMx-anul-2025.pdf"

IDX = {"ro": 0, "en": 1, "ru": 2, "uk": 3}

L = {   # eticheta: (RO, EN, RU, UK)
    "piata": NAV["408"], "listare": NAV["409"], "academy": NAV["410"], "despre": NAV["407"],
    "membri": ("Membri", "Members", "Участники", "Учасники"),
    "noutati": ("Noutăți", "News", "Новости", "Новини"),
    "g_real": ("Piață în timp real", "Real-Time Market", "Рынок в реальном времени", "Ринок у реальному часі"),
    "g_analiza": ("Analiză și date", "Analysis and Data", "Аналитика и данные", "Аналітика та дані"),
    "g_instr": ("Instrumente listate", "Listed Instruments", "Котируемые инструменты", "Інструменти в лістингу"),
    "g_tranz": ("Tranzacționare", "Trading", "Торги", "Торги"),
    "g_comp": ("Compania", "Company", "Компания", "Компанія"),
    "g_dezv": ("Dezvăluirea informației", "Information Disclosure", "Раскрытие информации", "Розкриття інформації"),
    "cotatii": ("Cotații în timp real", "Real-Time Quotes", "Котировки в режиме реального времени", "Котирування в реальному часі"),
    "indici": ("Indicii Bursei", "Exchange Indices", "Биржевые индексы", "Біржові індекси"),
    "istorice": ("Date Istorice", "Historical Data", "Исторические данные", "Історичні дані"),
    "rapoarte": ("Rapoarte proprii BIMx", "BIMx Reports", "Собственные отчёты BIMx", "Власні звіти BIMx"),
    "datepiata": ("Date de piață", "Market Data", "Рыночные данные", "Ринкові дані"),
    "actiuni": ("Acțiuni", "Shares", "Акции", "Акції"),
    "oblig": ("Obligațiuni și finanțare verde", "Bonds and Green Finance", "Облигации и зелёное финансирование", "Облігації та зелене фінансування"),
    "fise": ("Fișe detaliate", "Detailed Fact Sheets", "Подробные карточки", "Детальні картки"),
    "program": ("Program de tranzacționare", "Trading schedule", "Расписание торгов", "Розклад торгів"),
    "calendar": ("Calendarul de tranzacționare", "Trading calendar", "Торговый календарь", "Календар торгів"),
    "platforma": ("Platforma de tranzacționare", "Trading platform", "Торговая платформа", "Торговельна платформа"),
    "compensare": ("Compensare și decontare", "Clearing and Settlement", "Клиринг и расчёты", "Клірінг і розрахунки"),
    "model": ("Model operațional", "Operating Model", "Операционная модель", "Операційна модель"),
    "procesul": ("Procesul de listare", "Listing Process", "Процедура листинга", "Процедура лістингу"),
    "servicii": ("Servicii de listare", "Listing Services", "Услуги листинга", "Послуги з лістингу"),
    "tarife": ("Tarifele Bursei", "Exchange Fees", "Тарифы биржи", "Тарифи біржі"),
    "atestare": ("Atestarea brokerilor", "Broker Certification", "Аттестация брокеров", "Атестація брокерів"),   # RO: „agenților de bursă” (fixes)
    "lista": ("Lista societăților", "List of Firms", "Список обществ", "Перелік компаній"),
    "resurse": ("Resurse educaționale", "Learning Resources", "Образовательные ресурсы", "Освітні ресурси"),
    "glosar": ("Glosar", "Glossary", "Глоссарий", "Глосарій"),
    "formare": ("Cursuri și instruire", "Courses and training", "Курсы и обучение", "Курси та навчання"),
    "evenimente": ("Webinare și evenimente", "Webinars and events", "Вебинары и мероприятия", "Вебінари та заходи"),
    "feat_academy": ("Explorează BIMx Academy", "Explore BIMx Academy", "Откройте BIMx Academy", "Відкрийте BIMx Academy"),
    "publicatii": ("Publicații", "Publications", "Публикации", "Публікації"),
    "anunturi": ("Anunțuri BIMx", "BIMx announcements", "Объявления BIMx", "Оголошення BIMx"),
    "avize": ("Avize de piață", "Market notices", "Рыночные уведомления", "Ринкові повідомлення"),
    "emitenti": ("Anunțuri ale emitenților", "Issuer announcements", "Объявления эмитентов", "Оголошення емітентів"),
    "galerie": ("Galerie foto", "Photo gallery", "Фотогалерея", "Фотогалерея"),
    "identitate": ("Identitate", "Identity", "Идентичность", "Ідентичність"),
    "consiliu": ("Consiliul și Organul Executiv", "Council and Executive Body", "Совет и исполнительный орган", "Рада та виконавчий орган"),
    "fondatori": ("Fondatorii BIMx", "BIMx Founders", "Учредители BIMx", "Засновники BIMx"),
    "parteneri": ("Parteneri instituționali", "Institutional Partners", "Институциональные партнёры", "Інституційні партнери"),
    "cariere": ("Cariere", "Careers", "Карьера", "Кар’єра"),
    "contacte": ("Contacte", "Contacts", "Контакты", "Контакти"),
    "regulamente": ("Regulamente și acte normative", "Regulations and Legal Acts", "Регламенты и нормативные акты", "Регламенти та нормативні акти"),
    "statut": ("Statut", "Articles of Association", "Устав", "Статут"),
    "organigrama": ("Organigrama", "Organisational Chart", "Организационная структура", "Організаційна структура"),
    "situatii": ("Situații financiare 2025", "Financial Statements 2025", "Финансовая отчётность за 2025 год", "Фінансова звітність за 2025 рік"),
    "audit": ("Raport audit financiar 2025", "Financial Audit Report 2025", "Аудиторский отчёт за 2025 год", "Аудиторський звіт за 2025 рік"),
    "descarcare": ("Centru de descărcare", "Download Centre", "Центр загрузок", "Центр завантажень"),
    "prezentare": ("Prezentare generală", "Overview", "Общий обзор", "Загальний огляд"),
    # bara de jos
    "f_piata": ("Date demonstrative până la începerea tranzacționării", "Demo data until trading begins",
                "Демонстрационные данные до начала торгов", "Демонстраційні дані до початку торгів"),
    "f_listare": ("Pentru companii și municipalități", "For companies and municipalities", "Для компаний и муниципалитетов",
                  "Для компаній і муніципалітетів"),
    "c_listare": ("Aplicați pentru listare", "Apply for listing", "Подать заявку на листинг", "Подати заявку на лістинг"),
    "f_membri": ("Pentru agenți de bursă", "For brokers", "Для брокеров", "Для брокерів"),   # ca „Atestarea brokerilor” din același meniu
    "c_membri": ("Deveniți membru BIMx", "Become a BIMx member", "Станьте участником BIMx", "Станьте учасником BIMx"),
    "f_academy": ("Educație financiară pentru investitori", "Financial education for investors", "Финансовое образование для инвесторов",
                  "Фінансова освіта для інвесторів"),
    "f_noutati": ("Contact presă: office@bimx.md", "Press contact: office@bimx.md", "Контакт для прессы: office@bimx.md",
                  "Контакт для преси: office@bimx.md"),
    "c_noutati": ("Toate noutățile", "All news", "Все новости", "Усі новини"),
    "f_despre": ("Licență de operator de piață CNPF, seria 000945", "CNPF market operator licence, series 000945",
                 "Лицензия оператора рынка НКФР, серия 000945", "Ліцензія оператора ринку НКФР, серія 000945"),
}

# (cheie, pagină, PDF)
def _l(key, path, pdf=False):
    return (key, path, pdf)


# meniurile, în ordinea din bară: (cheie, id, tipar, grupuri, context, acțiune[, card de deasupra listei: titlu, subtitlu, pagină])
# BIMx Academy: în locul barei de jos, un card „Explorează BIMx Academy” deasupra listei (ca în machetă)
# grupuri: [(titlu, [linkuri], (coloană, rând) pe desktop)]; la „Listă” titlul grupului e eticheta meniului (vizibil doar pe mobil)
MENUS = [
    ("despre", "407", "cols", [
        ("g_comp", [_l("identitate", "identitate"), _l("consiliu", "consiliul-si-organul-executiv"), _l("organigrama", "organigrama"), _l("fondatori", "fondatori"),
                    _l("parteneri", "parteneri-institutionali"), _l("cariere", "cariere"), _l("contacte", "contacte")], (1, 1)),
        ("g_dezv", [_l("regulamente", "regulamente-si-acte-normative"), _l("statut", PDF_STATUT, True),
                    _l("situatii", PDF_FIN, True), _l("audit", PDF_AUDIT, True), _l("descarcare", "centru-de-descarcare")], (2, 1)),
    ], "f_despre", ("prezentare", "identitate")),
    ("piata", "408", "cols", [
        ("g_real", [_l("cotatii", "cotatii-in-timp-real"), _l("indici", "indicii-bursei")], (1, 1)),
        ("g_analiza", [_l("istorice", "date-istorice"), _l("rapoarte", "rapoarte"), _l("datepiata", "date-de-piata")], (1, 2)),
        ("g_instr", [_l("actiuni", "actiuni"), _l("oblig", "obligatiuni"), _l("fise", "fise-detaliate")], (2, 1)),
        ("g_tranz", [_l("program", "program-de-tranzactionare"), _l("calendar", "trading-calendar"), _l("platforma", "platforma-de-tranzactionare"),
                     _l("compensare", "compensare-si-decontare"), _l("model", "model-operational")], (3, 1)),
    ], "f_piata", ("prezentare", "prezentare-generala")),
    ("listare", "409", "list", [
        (None, [_l("procesul", "procesul-de-listare"), _l("servicii", "servicii-de-listare"), _l("tarife", "tarifele-bursei")], None),
    ], "f_listare", ("c_listare", "procesul-de-listare")),
    ("membri", "bx-membri", "list", [
        (None, [_l("atestare", "atestarea-brokerilor"), _l("lista", "lista-societatilor")], None),
    ], "f_membri", ("c_membri", "atestarea-brokerilor")),
    ("academy", "410", "list", [
        (None, [_l("resurse", "academy/index.html#directii"), _l("glosar", "academy/index.html#glosar"), _l("formare", "academy/index.html#formare"),
                _l("evenimente", "academy/index.html#evenimente"), _l("publicatii", "academy/index.html#publicatii")], None),
    ], None, None, ("feat_academy", "f_academy", "academy")),
    ("noutati", "411", "list", [
        (None, [_l("anunturi", "category/anunturi-bimx"), _l("avize", "category/avize-de-piata"),
                _l("emitenti", "category/anunturi-ale-emitentilor"), _l("galerie", "galerie-foto")], None),
    ], "f_noutati", ("c_noutati", "noutati")),
]

PDF_ATTR = ' target="_blank" rel="noopener"'
ARR = ('<svg class="bx-dd-arr" width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.3 8h9.4M8 3.3 12.7 8 8 12.7" '
       'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
CHEV = ('<svg class="bx-chev" width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _href(pg, path):
    """Linkul relativ spre o pagină (director sau fișier, eventual cu #ancoră)."""
    path, _, frag = path.partition("#")
    if not path.endswith((".html", ".pdf")):
        path += "/index.html"
    return pg.link(path) + (f"#{frag}" if frag else "")


def _current(pg, path):
    target = path.partition("#")[0]
    if not target.endswith((".html", ".pdf")):
        target += "/index.html"
    return str(pg.inner) == target and "#" not in path


def build_menu(text, pg, toggle, back):
    """Elementele de nivel 1 ale meniului, în ordinea și structura nouă."""
    i = IDX[pg.lang]
    out = []
    for key, mid, kind, groups, foot, cta, *extra in MENUS:
        cols, active = [], False
        feat = extra[0] if extra else None
        if feat:
            cols.append(f'<li class="bx-dd-feature menu-item"><a class="bx-dd-feat" href="{_href(pg, feat[2])}">'
                        f'<span class="bx-dd-feat-t">{L[feat[0]][i]}</span><span class="bx-dd-feat-s">{L[feat[1]][i]}</span>{ARR}</a></li>')
        for g, links, place in groups:
            items = []
            for k, path, pdf in links:
                cur = _current(pg, path)
                active |= cur
                badge = '<span class="bx-dd-pdf">PDF</span>' if pdf else ""
                items.append(f'<li class="menu-item{" current-menu-item" if cur else ""}"><a href="{_href(pg, path)}"'
                             f'{PDF_ATTR if pdf else ""}><span class="bx-dd-lbl">{L[k][i]}</span>{badge}{ARR}</a></li>')
            title = L[g][i] if g else L[key][i]
            pos = f' style="grid-column:{place[0]};grid-row:{place[1]}"' if place else ""
            cols.append(f'<li class="not_click menu-item menu-item-has-children bx-nav-col"{pos}><a class="bx-group-label">{title}</a>'
                        f'<ul class="sub-menu">{"".join(items)}</ul></li>')
        action = ""
        if cta:
            action = f'<a class="bx-dd-cta" href="{_href(pg, cta[1])}">{L[cta[0]][i]}{ARR}</a>'
        if foot:                                   # fără context și fără acțiune: fără bară de jos
            cols.append(f'<li class="bx-dd-foot menu-item"><span>{L[foot][i]}</span>{action}</li>')
        # secțiunea curentă: o pagină din meniu, plus Academy și paginile de noutăți / articolele
        inner = str(pg.inner)
        active |= (key == "academy" and pg.academy) or (key == "noutati" and inner.startswith(("noutati/", "category/", "galerie-foto/", "2026/")))
        cls = f"menu-item menu-item-has-children bx-dd bx-dd-{kind} bx-dd-{key}" + (" current-menu-ancestor" if active else "")
        out.append(f'<li id="menu-item-{mid}" class="{cls}"><a href="#" role="button" aria-haspopup="true" aria-expanded="false">{L[key][i]}{CHEV}</a>'
                   f'{toggle}\n<ul class="sub-menu">\n\t<li class="back_to_main_menu menu-item"><a href="#" role="button">{back}</a></li>'
                   f'{"".join(cols)}\n</ul>\n</li>\n')
    return "".join(out)


def apply_menu(text, pg):
    """Înlocuiește elementele de nivel 1 (Despre noi … Noutăți) cu meniul nou; elementele doar-mobil rămân la final."""
    start = text.find('<li id="menu-item-407"')
    end = text.find('<li class="hide_desktop bx-menu-apply')
    if start < 0 or end < start or "bx-dd-piata" in text:
        return text
    old = text[start:end]
    toggle = re.search(r'<button class="sub-menu-toggle"[\s\S]*?</button>', old)
    back = re.search(r'class="back_to_main_menu[^"]*"><a [^>]*>([^<]*)</a>', old)
    if not toggle or not back:
        return text
    return text[:start] + build_menu(text, pg, toggle.group(0), back.group(1)) + text[end:]
