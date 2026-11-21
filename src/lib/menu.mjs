// Main menu (desktop dropdowns + the theme's mobile menu), in RO / EN / RU / UK.
// Ported from tools/sitegen/menu.py. To add or rename a menu link, edit LABELS and MENUS below.
import { LANG_PREFIX, link } from './links.mjs';

const IDX = { ro: 0, en: 1, ru: 2, uk: 3 };

const UPLOADS = 'wp-content/uploads';
const PDF_STATUT = `${UPLOADS}/2026/06/Statut-BIMx.pdf`;
const PDF_FIN = `${UPLOADS}/2026/06/Situatii-financiare-BIMx-anul-2025.pdf`;
const PDF_AUDIT = `${UPLOADS}/2026/06/Raportul-audit-financiar-BIMx-anul-2025.pdf`;

// label: [RO, EN, RU, UK]
export const LABELS = {
  despre: ['Despre noi', 'About us', 'О нас', 'Про нас'],
  piata: ['Piață', 'Market', 'Рынок', 'Ринок'],
  listare: ['Listare', 'Listing', 'Листинг', 'Лістинг'],
  academy: ['BIMx Academy', 'BIMx Academy', 'BIMx Academy', 'BIMx Academy'],
  noutati: ['Noutăți', 'News', 'Новости', 'Новини'],
  membri: ['Membri', 'Members', 'Участники', 'Учасники'],
  g_real: ['Piață în timp real', 'Real-Time Market', 'Рынок в реальном времени', 'Ринок у реальному часі'],
  g_analiza: ['Analiză și date', 'Analysis and Data', 'Аналитика и данные', 'Аналітика та дані'],
  g_instr: ['Instrumente listate', 'Listed Instruments', 'Котируемые инструменты', 'Інструменти в лістингу'],
  g_tranz: ['Tranzacționare', 'Trading', 'Торги', 'Торги'],
  g_comp: ['Compania', 'Company', 'Компания', 'Компанія'],
  g_dezv: ['Dezvăluirea informației', 'Information Disclosure', 'Раскрытие информации', 'Розкриття інформації'],
  cotatii: ['Cotații în timp real', 'Real-Time Quotes', 'Котировки в режиме реального времени', 'Котирування в реальному часі'],
  indici: ['Indicii Bursei', 'Exchange Indices', 'Биржевые индексы', 'Біржові індекси'],
  istorice: ['Date Istorice', 'Historical Data', 'Исторические данные', 'Історичні дані'],
  rapoarte: ['Rapoarte proprii BIMx', 'BIMx Reports', 'Собственные отчёты BIMx', 'Власні звіти BIMx'],
  datepiata: ['Date de piață', 'Market Data', 'Рыночные данные', 'Ринкові дані'],
  actiuni: ['Acțiuni', 'Shares', 'Акции', 'Акції'],
  oblig: ['Obligațiuni și finanțare verde', 'Bonds and Green Finance', 'Облигации и зелёное финансирование', 'Облігації та зелене фінансування'],
  fise: ['Fișe detaliate', 'Detailed Fact Sheets', 'Подробные карточки', 'Детальні картки'],
  program: ['Program de tranzacționare', 'Trading schedule', 'Расписание торгов', 'Розклад торгів'],
  calendar: ['Calendarul de tranzacționare', 'Trading calendar', 'Торговый календарь', 'Календар торгів'],
  platforma: ['Platforma de tranzacționare', 'Trading platform', 'Торговая платформа', 'Торговельна платформа'],
  compensare: ['Compensare și decontare', 'Clearing and Settlement', 'Клиринг и расчёты', 'Клірінг і розрахунки'],
  model: ['Model operațional', 'Operating Model', 'Операционная модель', 'Операційна модель'],
  procesul: ['Procesul de listare', 'Listing Process', 'Процедура листинга', 'Процедура лістингу'],
  servicii: ['Servicii de listare', 'Listing Services', 'Услуги листинга', 'Послуги з лістингу'],
  tarife: ['Tarifele Bursei', 'Exchange Fees', 'Тарифы биржи', 'Тарифи біржі'],
  atestare: ['Atestarea agenților de bursă', 'Broker Certification', 'Аттестация брокеров', 'Атестація брокерів'],
  lista: ['Lista societăților', 'List of Firms', 'Список обществ', 'Перелік компаній'],
  resurse: ['Resurse educaționale', 'Learning Resources', 'Образовательные ресурсы', 'Освітні ресурси'],
  glosar: ['Glosar', 'Glossary', 'Глоссарий', 'Глосарій'],
  formare: ['Cursuri și instruire', 'Courses and training', 'Курсы и обучение', 'Курси та навчання'],
  evenimente: ['Webinare și evenimente', 'Webinars and events', 'Вебинары и мероприятия', 'Вебінари та заходи'],
  feat_academy: ['Explorează BIMx Academy', 'Explore BIMx Academy', 'Откройте BIMx Academy', 'Відкрийте BIMx Academy'],
  publicatii: ['Publicații', 'Publications', 'Публикации', 'Публікації'],
  anunturi: ['Anunțuri BIMx', 'BIMx announcements', 'Объявления BIMx', 'Оголошення BIMx'],
  avize: ['Avize de piață', 'Market notices', 'Рыночные уведомления', 'Ринкові повідомлення'],
  emitenti: ['Anunțuri ale emitenților', 'Issuer announcements', 'Объявления эмитентов', 'Оголошення емітентів'],
  galerie: ['Galerie foto', 'Photo gallery', 'Фотогалерея', 'Фотогалерея'],
  identitate: ['Identitate', 'Identity', 'Идентичность', 'Ідентичність'],
  consiliu: ['Consiliul și Organul Executiv', 'Council and Executive Body', 'Совет и исполнительный орган', 'Рада та виконавчий орган'],
  fondatori: ['Fondatorii BIMx', 'BIMx Founders', 'Учредители BIMx', 'Засновники BIMx'],
  parteneri: ['Parteneri instituționali', 'Institutional Partners', 'Институциональные партнёры', 'Інституційні партнери'],
  cariere: ['Cariere', 'Careers', 'Карьера', 'Кар’єра'],
  contacte: ['Contacte', 'Contacts', 'Контакты', 'Контакти'],
  regulamente: ['Regulamente și acte normative', 'Regulations and Legal Acts', 'Регламенты и нормативные акты', 'Регламенти та нормативні акти'],
  statut: ['Statut', 'Articles of Association', 'Устав', 'Статут'],
  organigrama: ['Organigrama', 'Organisational Chart', 'Организационная структура', 'Організаційна структура'],
  situatii: ['Situații financiare 2025', 'Financial Statements 2025', 'Финансовая отчётность за 2025 год', 'Фінансова звітність за 2025 рік'],
  audit: ['Raport audit financiar 2025', 'Financial Audit Report 2025', 'Аудиторский отчёт за 2025 год', 'Аудиторський звіт за 2025 рік'],
  descarcare: ['Centru de descărcare', 'Download Centre', 'Центр загрузок', 'Центр завантажень'],
  prezentare: ['Prezentare generală', 'Overview', 'Общий обзор', 'Загальний огляд'],
  // bottom bar of each dropdown
  f_piata: ['Date demonstrative până la începerea tranzacționării', 'Demo data until trading begins', 'Демонстрационные данные до начала торгов', 'Демонстраційні дані до початку торгів'],
  f_listare: ['Pentru companii și municipalități', 'For companies and municipalities', 'Для компаний и муниципалитетов', 'Для компаній і муніципалітетів'],
  c_listare: ['Aplicați pentru listare', 'Apply for listing', 'Подать заявку на листинг', 'Подати заявку на лістинг'],
  f_membri: ['Pentru agenți de bursă', 'For brokers', 'Для брокеров', 'Для брокерів'],
  c_membri: ['Deveniți membru BIMx', 'Become a BIMx member', 'Станьте участником BIMx', 'Станьте учасником BIMx'],
  f_academy: ['Educație financiară pentru investitori', 'Financial education for investors', 'Финансовое образование для инвесторов', 'Фінансова освіта для інвесторів'],
  f_noutati: ['Contact presă: office@bimx.md', 'Press contact: office@bimx.md', 'Контакт для прессы: office@bimx.md', 'Контакт для преси: office@bimx.md'],
  c_noutati: ['Toate noutățile', 'All news', 'Все новости', 'Усі новини'],
  f_despre: ['Licență de operator de piață CNPF, seria 000945', 'CNPF market operator licence, series 000945', 'Лицензия оператора рынка НКФР, серия 000945', 'Ліцензія оператора ринку НКФР, серія 000945'],
};

// the context line of a bottom bar can link to its page
const FOOT_LINK = { f_despre: 'regulamente-si-acte-normative#licente' };

const l = (key, path, pdf = false) => ({ key, path, pdf });

// Menus in bar order. kind: "list" (≤ 6 links, one column) or "cols" (grouped columns).
// groups: [title, links, [column, row] on desktop]; feature: card above the list (BIMx Academy).
// "Date Istorice" is hidden for now: to bring it back, add l('istorice', 'date-istorice') to g_analiza.
export const MENUS = [
  {
    key: 'despre', id: '407', kind: 'cols', foot: 'f_despre', cta: ['prezentare', 'identitate'],
    groups: [
      ['g_comp', [l('identitate', 'identitate'), l('consiliu', 'consiliul-si-organul-executiv'), l('organigrama', 'organigrama'), l('fondatori', 'fondatori'),
        l('parteneri', 'parteneri-institutionali'), l('cariere', 'cariere'), l('contacte', 'contacte')], [1, 1]],
      ['g_dezv', [l('regulamente', 'regulamente-si-acte-normative'), l('statut', PDF_STATUT, true),
        l('situatii', PDF_FIN, true), l('audit', PDF_AUDIT, true), l('descarcare', 'centru-de-descarcare')], [2, 1]],
    ],
  },
  {
    key: 'piata', id: '408', kind: 'cols', foot: 'f_piata', cta: ['prezentare', 'prezentare-generala'],
    groups: [
      ['g_real', [l('cotatii', 'cotatii-in-timp-real'), l('indici', 'indicii-bursei')], [1, 1]],
      ['g_analiza', [l('rapoarte', 'rapoarte'), l('datepiata', 'date-de-piata')], [1, 2]],
      ['g_instr', [l('actiuni', 'actiuni'), l('oblig', 'obligatiuni'), l('fise', 'fise-detaliate')], [2, 1]],
      ['g_tranz', [l('program', 'program-de-tranzactionare'), l('calendar', 'trading-calendar'), l('platforma', 'platforma-de-tranzactionare'),
        l('compensare', 'compensare-si-decontare'), l('model', 'model-operational')], [3, 1]],
    ],
  },
  {
    key: 'listare', id: '409', kind: 'list', foot: 'f_listare', cta: ['c_listare', 'procesul-de-listare'],
    groups: [[null, [l('procesul', 'procesul-de-listare'), l('servicii', 'servicii-de-listare'), l('tarife', 'tarifele-bursei')], null]],
  },
  {
    key: 'membri', id: 'bx-membri', kind: 'list', foot: 'f_membri', cta: ['c_membri', 'atestarea-brokerilor'],
    groups: [[null, [l('atestare', 'atestarea-brokerilor'), l('lista', 'lista-societatilor')], null]],
  },
  {
    key: 'academy', id: '410', kind: 'list', foot: null, cta: null, feature: ['feat_academy', 'f_academy', 'academy'],
    groups: [[null, [l('resurse', 'academy/index.html#directii'), l('glosar', 'academy/index.html#glosar'), l('formare', 'academy/index.html#formare'),
      l('evenimente', 'academy/index.html#evenimente'), l('publicatii', 'academy/index.html#publicatii')], null]],
  },
  {
    key: 'noutati', id: '411', kind: 'list', foot: 'f_noutati', cta: ['c_noutati', 'noutati'],
    groups: [[null, [l('anunturi', 'category/anunturi-bimx'), l('avize', 'category/avize-de-piata'),
      l('emitenti', 'category/anunturi-ale-emitentilor'), l('galerie', 'galerie-foto')], null]],
  },
];

const PDF_ATTR = ' target="_blank" rel="noopener"';
const ARR = '<svg class="bx-dd-arr" width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.3 8h9.4M8 3.3 12.7 8 8 12.7" '
  + 'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const CHEV = '<svg class="bx-chev" width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" '
  + 'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

/** Absolute target of a menu path ("identitate", "academy/index.html#glosar", "wp-content/…pdf") in the page language. */
function target(lang, path) {
  const [p, frag] = path.split('#');
  const prefix = p.startsWith('wp-content/') || p.startsWith('assets/') ? '' : LANG_PREFIX[lang];
  let abs = '/' + prefix + p;
  if (abs.endsWith('/index.html')) abs = abs.slice(0, -'index.html'.length);
  else if (!/\.(html|pdf)$/.test(abs)) abs += '/';
  return abs + (frag ? `#${frag}` : '');
}

/** Section of the menu that contains the page, besides direct links (Academy, news pages and articles). */
function inSection(key, page) {
  if (key === 'academy') return page.inner === 'academy/' || page.inner.startsWith('academy/');
  if (key === 'noutati') return ['noutati/', 'category/', 'galerie-foto/', '2026/'].some((p) => page.inner.startsWith(p));
  return false;
}

/**
 * Top-level menu items for a page. `toggle` is the theme's sub-menu toggle button and `back` the label of the
 * "back to main menu" item, both taken from the theme header of the page language (src/shell/<lang>/menu.json).
 */
export function buildMenu(page, { toggle, back }) {
  const i = IDX[page.lang];
  const href = (path) => link(page.route, target(page.lang, path));
  const current = (path) => !path.includes('#') && target(page.lang, path) === '/' + page.route;
  let out = '';
  for (const m of MENUS) {
    const cols = [];
    let active = false;
    if (m.feature) {
      const [t, s, path] = m.feature;
      cols.push(`<li class="bx-dd-feature menu-item"><a class="bx-dd-feat" href="${href(path)}">`
        + `<span class="bx-dd-feat-t">${LABELS[t][i]}</span><span class="bx-dd-feat-s">${LABELS[s][i]}</span>${ARR}</a></li>`);
    }
    for (const [g, links, place] of m.groups) {
      const items = links.map(({ key, path, pdf }) => {
        const cur = current(path);
        active ||= cur;
        const badge = pdf ? '<span class="bx-dd-pdf">PDF</span>' : '';
        return `<li class="menu-item${cur ? ' current-menu-item' : ''}"><a href="${href(path)}"`
          + `${pdf ? PDF_ATTR : ''}><span class="bx-dd-lbl">${LABELS[key][i]}</span>${badge}${ARR}</a></li>`;
      });
      const title = g ? LABELS[g][i] : LABELS[m.key][i];
      const pos = place ? ` style="grid-column:${place[0]};grid-row:${place[1]}"` : '';
      cols.push(`<li class="not_click menu-item menu-item-has-children bx-nav-col"${pos}><a class="bx-group-label">${title}</a>`
        + `<ul class="sub-menu">${items.join('')}</ul></li>`);
    }
    const action = m.cta ? `<a class="bx-dd-cta" href="${href(m.cta[1])}">${LABELS[m.cta[0]][i]}${ARR}</a>` : '';
    if (m.foot) {
      let ctx = LABELS[m.foot][i];
      if (FOOT_LINK[m.foot]) ctx = `<a class="bx-dd-foot-link" href="${href(FOOT_LINK[m.foot])}">${ctx}</a>`;
      cols.push(`<li class="bx-dd-foot menu-item"><span>${ctx}</span>${action}</li>`);
    }
    active ||= inSection(m.key, page);
    const cls = `menu-item menu-item-has-children bx-dd bx-dd-${m.kind} bx-dd-${m.key}` + (active ? ' current-menu-ancestor' : '');
    out += `<li id="menu-item-${m.id}" class="${cls}"><a href="#" role="button" aria-haspopup="true" aria-expanded="false">${LABELS[m.key][i]}${CHEV}</a>`
      + `${toggle}\n<ul class="sub-menu">\n\t<li class="back_to_main_menu menu-item"><a href="#" role="button">${back}</a></li>`
      + `${cols.join('')}\n</ul>\n</li>\n`;
  }
  return out;
}
