// News & press releases ("Noutăți & Comunicate").
//
// Each press release is one folder in src/content/news/<date>-<name>/:
//   news.json        path (address), date, section, category, PDF and the short texts in RO / EN / RU / UK:
//                    title, summary (lead and list excerpt), description (search engines);
//                    optional: cardTitle (lists, home page), crumb (breadcrumb), pageTitle (browser tab),
//                    photo, shareText; "legacy" keeps WordPress ids of the old pages
//   ro.html, en.html, ru.html, uk.html   the text of the press release (HTML; links from the site root, "/assets/…")
// Categories are in src/content/news/categories.json, interface texts in src/data/news-texts.json.
// From these the build makes the press release pages, the news lists and the news on the home page.
// Ported from tools/sitegen/communique.py, news.py and home.py.
import { LANG_PREFIX, link } from './links.mjs';
import { escapeHtml, unescapeHtml } from './seo.mjs';

export const IDX = { ro: 0, en: 1, ru: 2, uk: 3 };

// ---------------------------------------------------------------- dates

export function dateParts(iso, lang, texts) {
  const [y, m, d] = iso.split('-').map(Number);
  const [name, abbr] = texts.MONTHS[lang][m - 1];
  const short = lang === 'en' ? abbr.toLowerCase().replace(/^./, (c) => c.toUpperCase()) : abbr.toLowerCase();
  return { short: `${d} ${short} ${y}`, full: `${d} ${name} ${y}`, day: d, abbr, year: y };
}

/** Newest first; items of the same day keep their order in the folder list. */
export function sortNews(items) {
  return [...items].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : (a.order ?? 0) - (b.order ?? 0)));
}

/** Python urllib.parse.quote_plus, for the text of the "share on X" link. */
export function quotePlus(s) {
  return Array.from(new TextEncoder().encode(s), (b) => {
    const c = String.fromCharCode(b);
    if (/[A-Za-z0-9_.~-]/.test(c)) return c;
    if (c === ' ') return '+';
    return '%' + b.toString(16).toUpperCase().padStart(2, '0');
  }).join('');
}

// ---------------------------------------------------------------- press release page

const SEP = '<span class="bx-pr-sep" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.25 10.5 8.75 7 '
  + '5.25 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
const ICON_DOWNLOAD = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>';
const ICON_MAIL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1DB0F0" stroke-width="1.8" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>';
const ICON_PHONE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1DB0F0" stroke-width="1.8" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 '
  + '19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 '
  + '2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>';
const ICON_CLOCK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8A90A3" stroke-width="1.8" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';
const ICON_BACK = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M12.7 8H3.3M8 12.7 3.3 8 8 3.3" '
  + 'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

/** File name of the PDF of a press release (news.json "pdf", or BIMx-<last part of the address>.pdf). */
export const pdfName = (item) => item.pdf ?? `BIMx-${item.path.split('/').pop()}.pdf`;

/** Short title used in lists, on the home page and in "related" cards (defaults to the title). */
export const cardTitle = (item, lang) => item.cardTitle?.[lang] ?? item.title[lang];

/** Route of a press release page in a language. */
export const newsRoute = (item, lang) => `${LANG_PREFIX[lang]}${item.path}/`;

/** Three related press releases: same category first, then the most recent. */
function similar(item, lang, ctx, href) {
  const i = IDX[lang];
  const others = ctx.news.filter((e) => e.path !== item.path);
  others.sort((a, b) => (a.category !== item.category) - (b.category !== item.category) || (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
  return others.slice(0, 3).map((e) => {
    const { full } = dateParts(e.date, lang, ctx.texts);
    // like the old build: the path to the language root followed by the full article path
    const up = href('/' + LANG_PREFIX[lang]);
    return `<a class="bx-pr-card" href="${up === './' ? '' : up}${e.path}/"><span class="bx-pr-card-m"><span>${ctx.categories[e.category].one[i]}</span> · `
      + `<time datetime="${e.date}">${full}</time></span><span class="bx-pr-card-t">${cardTitle(e, lang)}</span></a>`;
  }).join('');
}

/**
 * Body of a press release page (between the site header and footer).
 * ctx: { news, categories, texts, templates } — templates[`${lang}/news-article`] holds the theme wrapper with
 * {{article}} and {{share}}, the "share" buttons markup with {{xText}}.
 */
export function renderArticle(item, lang, ctx) {
  const i = IDX[lang];
  const T = ctx.texts;
  const route = newsRoute(item, lang);
  const href = (abs) => link(route, abs);
  const root = '/' + LANG_PREFIX[lang];
  const { full } = dateParts(item.date, lang, T);
  const place = `${T.CT.city[i]}, ${full}`;
  const crumbs = [
    `<a href="${href(root)}">${T.crumbs.home[i]}</a>`,
    `<a href="${href(root + 'noutati/')}">${T.crumbs.news[i]}</a>`,
    `<span aria-current="page">${item.crumb?.[lang] ?? item.title[lang]}</span>`,
  ].join(SEP);
  const kind = T.crumbs.kind[i];
  const meta = kind ? `<div class="bx-pr-meta"><span class="bx-pr-kind">${kind}</span></div>` : '';
  const xText = item.shareText?.[lang] ?? quotePlus(unescapeHtml(item.title[lang]));
  const share = ctx.templates[`${lang}/news-share`].replaceAll('{{xText}}', xText);
  // the PDF button appears when the PDF exists in public/ or the build can print it (ctx.pdfAvailable, site.mjs)
  const pdfFile = ctx.pdfAvailable ? (ctx.pdfAvailable(item, lang) ? pdfName(item) : null) : item.pdf;
  const pdf = pdfFile
    ? `<section class="bx-pr-box"><a class="bx-pr-pdf" href="${pdfFile}" target="_blank" rel="noopener" title="${T.CT.pdf[i]}">`
      + `${ICON_DOWNLOAD}<span>${T.CP.pdf_btn[i]}</span></a></section>`
    : '';
  const aside = `<aside class="bx-pr-aside" aria-label="${T.CP.info[i]}"><div class="bx-pr-card-box">${pdf}`
    + `<section class="bx-pr-box"><h2>${T.CT.share[i]}</h2><ul class="share-buttons-list bx-pr-share">${share}</ul></section>`
    + '</div></aside>';
  const about = `<section class="bx-pr-about" aria-labelledby="bx-pr-about-h"><h2 id="bx-pr-about-h">${T.CT.about_t[i]}</h2>`
    + `<p>${T.CT.about[i]}</p></section>`;
  const sim = `<section class="bx-pr-similar" aria-labelledby="bx-pr-sim-h"><div class="container">`
    + `<div class="bx-pr-similar-head"><h2 id="bx-pr-sim-h">${T.CP.similar[i]}</h2>`
    + `<a class="bx-pr-back" href="${href(root + 'noutati/')}">${ICON_BACK}<span>${T.CP.all[i]}</span></a></div>`
    + `<div class="bx-pr-cards">${similar(item, lang, ctx, href)}</div></div></section>`;
  const contact = `<section class="bx-pr-contact" aria-label="${T.CP.press[i]}"><div class="container">`
    + `<h2>${T.CP.press_q[i]}</h2><div class="bx-pr-contact-r"><div class="bx-pr-contact-l">`
    + `<a href="mailto:office@bimx.md">${ICON_MAIL}office@bimx.md</a><span aria-hidden="true">·</span>`
    + `<a href="tel:+37322897700">${ICON_PHONE}+373 22 89 77 00</a></div>`
    + `<p>${ICON_CLOCK}<span><strong>${T.CP.hours_t[i]}:</strong> ${T.CP.hours[i]}</span></p></div></div></section>`;
  // links in the text are written from the site root ("/assets/img/…"); on the page they are relative
  const rootPath = (u) => (u.startsWith('/') && !u.startsWith('//') ? href(u) : u);
  const body = item.body[lang]
    .replace(/(\s(?:href|src|data-src|poster)=)(["'])(\/(?!\/)[^"']*)\2/g, (_, a, q, abs) => a + q + href(abs) + q)
    .replace(/(\ssrcset=)(["'])([^"']*)\2/g, (_, a, q, v) => a + q + v.split(',').map((c) => c.replace(/^(\s*)(\S+)/, (m, sp, u) => sp + rootPath(u))).join(',') + q);
  const article = `<section class="bx-pr-head"><div class="container"><nav class="bx-pr-crumbs" aria-label="Breadcrumb">${crumbs}</nav>${meta}`
    + `<h1>${item.title[lang]}</h1><p class="bx-pr-lead">${item.summary[lang]}</p><p class="bx-pr-byline"><span>${place}</span></p></div></section>`
    + `<div class="container bx-pr-main"><article class="bx-pr-article"><div class="bx-pr-text">${body}</div>${about}</article>${aside}</div>`
    + `${sim}${contact}`;
  return ctx.templates[`${lang}/news-article`].replace('{{article}}', () => article);
}

/** Search engine description when news.json has none: the first real paragraph of the text, up to 160 characters. */
export function autoDescription(item, lang) {
  const text = (h) => unescapeHtml(h.replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim();
  const ps = [...item.body[lang].matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/g)].map((m) => text(m[1]));
  let d = ps.find((p) => p.length > 60) ?? text(item.summary[lang]);
  if (d.length > 160) d = d.slice(0, 157).replace(/\s+\S*$/, '') + '…';
  return escapeHtml(d);
}

/** Page fields of a press release (shell templates, title, description, sharing image). */
export function articlePage(item, lang, ctx) {
  const route = newsRoute(item, lang);
  const legacy = item.legacy ?? {};
  const page = {
    route, lang, inner: item.path + '/',
    parts: { ...ctx.defaults.parts, ...(legacy.parts?.[lang] ?? legacy.parts ?? {}) },
    title: item.pageTitle?.[lang] ?? `${item.title[lang]} – BIMx`,
    // goes into content="…": written as text in news.json, escaped here (entities in news.json are fine too)
    description: item.description?.[lang] !== undefined ? escapeHtml(unescapeHtml(item.description[lang])) : autoDescription(item, lang),
    bodyAttrs: ctx.defaults.bodyAttrs.replace('{{postId}}', legacy.postId ?? '0'),
    body: renderArticle(item, lang, ctx),
  };
  if (legacy.wpPost) page.wpPost = legacy.wpPost;
  if (legacy.wpContainer) page.wpContainer = legacy.wpContainer;
  if (item.photo) {
    // sharing image: the JPG copy of the photo (LinkedIn and some apps do not show WebP); alt is escaped by seo.mjs
    const src = item.photo.src.replace(/^\/+/, '');
    page.ogImage = { url: 'https://bimx.md/' + src.replace(/\.webp$/, '.jpg'), width: 1200, height: 705, alt: unescapeHtml(item.photo.alt[lang]) };
  }
  return page;
}

// ---------------------------------------------------------------- news lists (Noutăți & Comunicate)

// tabs: key → page inside the language. "toate" shows every section, newest first.
export const TABS = [['toate', 'noutati/'], ['bimx', 'category/anunturi-bimx/'], ['avize', 'category/avize-de-piata/'], ['emitenti', 'category/anunturi-ale-emitentilor/']];
const SOURCE = { bimx: 'bimx', avize: 'aviz', emitenti: 'emitent' };
const NEW_DAYS = 30; // the "New" label stays on the newest item at most this many days (replica.js hides it later)

const LIST_ARROW = '<svg class="bx-n-arr" width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.3 8h9.4M8 3.3 12.7 8 8 12.7" '
  + 'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_BUILDING = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/></svg>';
const ICON_CHART = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
  + 'stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/></svg>';
const CRUMB_SEP = '<li aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.25 10.5L8.75 7L5.25 3.5" '
  + 'stroke="white" stroke-opacity="0.6" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/></svg></li>';

/** Items shown on a tab, with their source ("bimx" / "aviz" / "emitent"). */
export function entries(tab, ctx) {
  const rows = ctx.news.filter((e) => tab === 'toate' || e.section === tab).map((e) => ({ e, src: SOURCE[e.section] }));
  return tab === 'toate' ? rows : rows; // ctx.news is already newest first
}

const tabLabel = (tab, i, T) => (tab === 'toate' ? T.title[i] : T[{ bimx: 'tab_bimx', avize: 'tab_avize', emitenti: 'tab_issuers' }[tab]][i]);

function itemHtml({ e, src }, lang, pos, showType, ctx, href) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const { full, day, abbr } = dateParts(e.date, lang, ctx.texts);
  const isNew = pos === 0 ? `<span class="bx-n-new" data-date="${e.date}" data-days="${NEW_DAYS}">${T.new[i]}</span>` : '';
  const kind = showType ? `<span class="bx-n-type">${T[{ aviz: 'type_aviz', emitent: 'type_emitent' }[src] ?? 'type_bimx'][i]}</span>` : '';
  return `<a class="bx-news-item" href="${href('/' + LANG_PREFIX[lang] + e.path + '/')}" data-source="${src}" data-cat="${e.category}" data-year="${e.date.slice(0, 4)}">`
    + `<time class="bx-n-date" datetime="${e.date}" title="${full}"><span class="bx-n-day">${day}</span><span class="bx-n-mon">${abbr}</span></time>`
    + '<span class="bx-n-body">'
    + `<span class="bx-n-meta">${kind}<span class="bx-n-cat">${ctx.categories[e.category].one[i]}</span>${isNew}</span>`
    + `<span class="bx-n-title" role="heading" aria-level="2">${cardTitle(e, lang)}</span>`
    + `<span class="bx-n-ex">${e.summary[lang]}</span>`
    + `</span>${LIST_ARROW}</a>`;
}

function emptyHtml(tab, lang, ctx, href) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const root = '/' + LANG_PREFIX[lang];
  const [icon, head, body, hint, second] = tab === 'avize'
    ? [ICON_CHART, T.avize_empty_h[i], T.avize_empty_p[i], '', [T.calendar[i], 'trading-calendar/']]
    : [ICON_BUILDING, T.empty_h[i], T.empty_p[i], T.empty_hint[i], [T.empty_listing[i], 'procesul-de-listare/']];
  return '<section class="bx-empty bx-news-empty" aria-labelledby="bx-empty-h">'
    + `<span class="bx-news-empty-icon">${icon}</span><h2 id="bx-empty-h">${head}</h2><p>${body}</p>${hint ? `<p class="bx-news-empty-hint">${hint}</p>` : ''}`
    + `<div class="bx-news-empty-actions"><a class="bx-btn-primary" href="${href(root + TABS[1][1])}">${T.empty_bimx[i]}</a>`
    + `<a class="bx-btn-secondary" href="${href(root + second[1])}">${second[0]}</a></div></section>`;
}

function catFilter(tab, lang, ctx) {
  if (tab !== 'bimx') return '';
  const i = IDX[lang];
  const T = ctx.texts.T;
  const opts = [`<option value="toate" selected>${T.cat_all[i]}</option>`];
  for (const [k, c] of Object.entries(ctx.categories)) {
    const n = ctx.news.filter((e) => e.section === 'bimx' && e.category === k).length;
    if (n) opts.push(`<option value="${k}">${c.many[i]} (${n})</option>`);
  }
  return `<label class="bx-news-year bx-news-cat"><span>${T.cat[i]}</span><select data-filter="cat">${opts.join('')}</select></label>`;
}

function yearFilter(tab, lang, ctx) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const years = [...new Set(entries(tab, ctx).map(({ e }) => e.date.slice(0, 4)))].sort().reverse();
  if (!years.length) return '';
  const opts = years.map((y, n) => `<option value="${y}"${n === 0 ? ' selected' : ''}>${y}</option>`).join('');
  return `<label class="bx-news-year"><span>${T.year[i]}</span><select data-filter="an" data-default="${years[0]}">`
    + `${opts}<option value="toate">${T.year_all[i]}</option></select></label>`;
}

function tabsHtml(tab, lang, ctx, href) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const labels = { toate: T.tab_all[i], bimx: T.tab_bimx[i], avize: T.tab_avize[i], emitenti: T.tab_issuers[i] };
  const root = '/' + LANG_PREFIX[lang];
  let nav = `<nav class="bx-news-tabs" aria-label="${T.tabs_label[i]}">`
    + TABS.map(([k, p]) => `<a class="bx-news-tab" href="${href(root + p)}"${k === tab ? ' aria-current="page"' : ''}>${labels[k]}</a>`).join('') + '</nav>';
  // on mobile the tabs become a select that navigates on change (replica.js)
  const opts = TABS.map(([k, p]) => `<option value="${href(root + p)}"${k === tab ? ' selected' : ''}>${labels[k]}</option>`).join('');
  nav += `<label class="bx-news-year bx-news-tabsel"><span class="bx-vh">${T.tabs_label[i]}</span><select data-nav="tab">${opts}</select></label>`;
  const filters = catFilter(tab, lang, ctx) + yearFilter(tab, lang, ctx);
  return `<div class="bx-news-tabbar">${nav}${filters ? `<div class="bx-news-filters">${filters}</div>` : ''}</div>`;
}

/** Breadcrumb, title, lead and tabs at the top of a news list page. */
export function listHero(tab, lang, route, ctx) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const href = (abs) => link(route, abs);
  const root = '/' + LANG_PREFIX[lang];
  const title = tabLabel(tab, i, T);
  const crumbs = [`<li><a href="${href(root)}">${ctx.texts.crumbs.home[i]}</a></li>`, CRUMB_SEP];
  if (tab === 'toate') crumbs.push(`<li><span aria-current="page">${T.title[i]}</span></li>`);
  else crumbs.push(`<li><a href="${href(root + TABS[0][1])}">${T.title[i]}</a></li>`, CRUMB_SEP, `<li><span aria-current="page">${title}</span></li>`);
  return `<ul class="breadcrumbs">${crumbs.join('')}</ul></nav>\n                <h1>${title}</h1>\n                <p>${T['lead_' + tab][i]}</p>${tabsHtml(tab, lang, ctx, href)}`;
}

/** The list (or the empty state) and the press contact of a news list page. */
export function listBody(tab, lang, route, ctx) {
  const i = IDX[lang];
  const T = ctx.texts.T;
  const href = (abs) => link(route, abs);
  const rows = entries(tab, ctx);
  // the type of publication is shown only on "toate", and only when several sources are mixed
  const showType = tab === 'toate' && new Set(rows.map((r) => r.src)).size > 1;
  const listing = rows.length
    ? `<div class="bx-news-list">${rows.map((r, n) => itemHtml(r, lang, n, showType, ctx, href)).join('')}</div><p class="bx-news-none" hidden>${T.none[i]}</p>`
    : emptyHtml(tab, lang, ctx, href);
  const press = `<section class="bx-news-press" aria-labelledby="bx-news-press-h"><div><h2 id="bx-news-press-h">${T.press_h[i]}</h2>`
    + `<p>${T.press_p[i]}</p></div><div class="bx-news-press-links"><a href="mailto:office@bimx.md">office@bimx.md</a>`
    + '<a href="tel:+37322897700">+373 22 89 77 00</a></div></section>';
  return `<div class="container bx-news">${listing}${press}</div>`;
}

/** Fill a news list page: markers {{newsHero}} and {{newsList}} in its body; noindex while the tab is empty. */
export function applyList(page, ctx) {
  const tab = page.newsTab;
  return {
    ...page,
    noindex: entries(tab, ctx).length === 0 || undefined,
    body: page.body.replace('{{newsHero}}', () => listHero(tab, page.lang, page.route, ctx)).replace('{{newsList}}', () => listBody(tab, page.lang, page.route, ctx)),
  };
}

// ---------------------------------------------------------------- news on the home page

const HOME_LIST = 5; // items in the list next to the main article

/**
 * The news block of the home page: the newest press release as the main article, the next ones in the list.
 * Markup: src/shell/<lang>/home-news.html and home-news-item.html (placeholders in double braces).
 */
export function homeNews(lang, route, ctx) {
  const href = (abs) => link(route, abs);
  const [main, ...rest] = ctx.news;
  const fillT = (tpl, vals) => tpl.replace(/\{\{(\w+)\}\}/g, (all, k) => (k in vals ? vals[k] : all));
  const vals = (e) => ({
    href: href('/' + LANG_PREFIX[lang] + e.path + '/'),
    cat: ctx.categories[e.category].one[IDX[lang]],
    date: dateParts(e.date, lang, ctx.texts).full,
    title: cardTitle(e, lang),
  });
  const list = rest.slice(0, HOME_LIST).map((e) => fillT(ctx.templates[`${lang}/home-news-item`], vals(e))).join('\n');
  return fillT(ctx.templates[`${lang}/home-news`], { ...vals(main), excerpt: main.homeExcerpt?.[lang] ?? main.summary[lang], list });
}

// ---------------------------------------------------------------- checks

const SECTIONS = ['bimx', 'avize', 'emitenti'];
const LANG_LIST = ['ro', 'en', 'uk', 'ru'];

/** Stop the build with a clear message when a news folder is incomplete. */
export function validateNews(items, categories) {
  const errors = [];
  const paths = new Set();
  for (const it of items) {
    const where = `src/content/news/${it.folder ?? it.path}`;
    const need = (cond, msg) => { if (!cond) errors.push(`${where}: ${msg}`); };
    need(typeof it.path === 'string' && /^[a-z0-9-]+(\/[a-z0-9-]+)*$/.test(it.path), '"path" must be an address like "2026/12/05/short-name" (lowercase, digits, -)');
    need(!/^(en|uk|ru)\//.test(it.path ?? ''), '"path" must not start with a language folder (en/, uk/, ru/): the build adds it');
    need(!paths.has(it.path), `"path" ${it.path} is used by another press release`);
    paths.add(it.path);
    need(/^\d{4}-\d{2}-\d{2}$/.test(it.date ?? ''), '"date" must look like "2026-12-05"');
    need(SECTIONS.includes(it.section), `"section" must be one of ${SECTIONS.join(', ')}`);
    need(it.category in categories, `"category" must be one of ${Object.keys(categories).join(', ')}`);
    for (const field of ['title', 'summary']) {
      for (const lang of LANG_LIST) need(typeof it[field]?.[lang] === 'string' && it[field][lang].trim(), `"${field}" has no ${lang.toUpperCase()} text`);
    }
    for (const lang of LANG_LIST) need(typeof it.body?.[lang] === 'string' && it.body[lang].trim(), `${lang}.html is missing or empty`);
    if (it.description) for (const lang of LANG_LIST) need(typeof it.description[lang] === 'string', `"description" has no ${lang.toUpperCase()} text (remove "description" to use the first paragraph)`);
    if (it.photo) {
      need(typeof it.photo.src === 'string' && /\.(webp|jpg|png)$/.test(it.photo.src), '"photo.src" must be an image path like "/assets/img/news/name.webp"');
      for (const lang of LANG_LIST) need(typeof it.photo.alt?.[lang] === 'string', `"photo.alt" has no ${lang.toUpperCase()} text`);
    }
  }
  if (errors.length) throw new Error('News data:\n  ' + errors.join('\n  '));
}
