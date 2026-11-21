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
  const xText = item.shareText?.[lang] ?? quotePlus(item.title[lang]);
  const share = ctx.templates[`${lang}/news-share`].replaceAll('{{xText}}', xText);
  const pdf = item.pdf
    ? `<section class="bx-pr-box"><a class="bx-pr-pdf" href="${item.pdf}" target="_blank" rel="noopener" title="${T.CT.pdf[i]}">`
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
  const body = item.body[lang].replace(/(\s(?:href|src)=")(\/(?!\/)[^"]*)(")/g, (_, a, abs, b) => a + href(abs) + b);
  const article = `<section class="bx-pr-head"><div class="container"><nav class="bx-pr-crumbs" aria-label="Breadcrumb">${crumbs}</nav>${meta}`
    + `<h1>${item.title[lang]}</h1><p class="bx-pr-lead">${item.summary[lang]}</p><p class="bx-pr-byline"><span>${place}</span></p></div></section>`
    + `<div class="container bx-pr-main"><article class="bx-pr-article"><div class="bx-pr-text">${body}</div>${about}</article>${aside}</div>`
    + `${sim}${contact}`;
  return ctx.templates[`${lang}/news-article`].replace('{{article}}', () => article);
}

/** Page fields of a press release (shell templates, title, description, sharing image). */
export function articlePage(item, lang, ctx) {
  const route = newsRoute(item, lang);
  const legacy = item.legacy ?? {};
  const page = {
    route, lang, inner: item.path + '/',
    parts: { ...ctx.defaults.parts, ...(legacy.parts?.[lang] ?? legacy.parts ?? {}) },
    title: item.pageTitle?.[lang] ?? `${item.title[lang]} – BIMx`,
    description: item.description[lang],
    bodyAttrs: ctx.defaults.bodyAttrs.replace('{{postId}}', legacy.postId ?? '0'),
    body: renderArticle(item, lang, ctx),
  };
  if (legacy.wpPost) page.wpPost = legacy.wpPost;
  if (legacy.wpContainer) page.wpContainer = legacy.wpContainer;
  if (item.photo) {
    page.ogImage = { url: 'https://bimx.md/' + item.photo.src.replace(/\.webp$/, '.jpg'), width: 1200, height: 705, alt: item.photo.alt[lang] };
  }
  return page;
}
