// Loads the site sources for the Astro build: page bodies with their fields, shell templates and menus.
// BIMx Academy pages are not files in src/content/pages: they are generated from src/content/academy (academy.mjs).
// Press releases are generated from src/content/news (news.mjs).
import { LANGS, LANG_PREFIX, splitLang } from './links.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { seoIndex } from './seo.mjs';
import { findChrome } from './news-pdf.mjs';
import { academyPages } from './academy.mjs';
import { applyList, articlePage, homeNews, pdfName, sortNews, validateNews } from './news.mjs';
import newsTexts from '../data/news-texts.json';
import newsDefaults from '../data/news-defaults.json';
import categories from '../content/news/categories.json';

const pageFiles = import.meta.glob('/src/content/pages/**/*.html', { query: '?raw', import: 'default', eager: true });
const shellFiles = import.meta.glob('/src/shell/**/*.html', { query: '?raw', import: 'default', eager: true });
const menuFiles = import.meta.glob('/src/shell/*/menu.json', { import: 'default', eager: true });
import redirectList from '../data/redirect-pages.json';

const newsData = import.meta.glob('/src/content/news/*/news.json', { import: 'default', eager: true });
const newsBodies = import.meta.glob('/src/content/news/*/*.html', { query: '?raw', import: 'default', eager: true });

/** Front matter: one `key: <JSON>` per line between --- lines, then the page body. */
export function parsePage(raw) {
  const m = /^---\n([\s\S]*?)\n---\n/.exec(raw);
  if (!m) throw new Error('Page without front matter');
  const fields = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(': ');
    fields[line.slice(0, i)] = JSON.parse(line.slice(i + 2));
  }
  return { ...fields, body: raw.slice(m[0].length) };
}

const contentPages = Object.values(pageFiles).map((raw) => {
  const p = parsePage(raw);
  return { ...p, ...splitLang(p.route) };
});

export const shell = {
  templates: Object.fromEntries(Object.entries(shellFiles).map(([f, t]) => [f.replace('/src/shell/', '').replace(/\.html$/, ''), t])),
  menu: Object.fromEntries(Object.entries(menuFiles).map(([f, m]) => [f.split('/')[3], m])),
};

// News: one folder per press release (src/content/news/<date>-<name>/news.json + <lang>.html)
export const news = sortNews(Object.entries(newsData).map(([file, data]) => {
  const dir = file.replace(/\/news\.json$/, '');
  const body = Object.fromEntries(LANGS.map((lang) => [lang, newsBodies[`${dir}/${lang}.html`]]));
  return { ...data, body, folder: dir.split('/').pop() };
}));
validateNews(news, categories);
// a press release PDF is either published in public/ or printed after the build (needs Chrome; src/lib/news-pdf.mjs)
const canPrint = Boolean(findChrome());
const pdfAvailable = (item, lang) => canPrint || fs.existsSync(path.resolve('public', LANG_PREFIX[lang] + item.path, pdfName(item)));
export const newsCtx = { news, categories, texts: newsTexts, templates: shell.templates, defaults: newsDefaults, pdfAvailable };
const newsPages = news.flatMap((item) => LANGS.map((lang) => articlePage(item, lang, newsCtx)));

// pages that show news: the news lists ({{newsHero}}, {{newsList}}) and the home pages ({{homeNews}})
const withNews = (p) => {
  if (p.newsTab) return applyList(p, newsCtx);
  if (p.body.includes('{{homeNews}}')) return { ...p, body: p.body.replace('{{homeNews}}', () => homeNews(p.lang, p.route, newsCtx)) };
  return p;
};
export const pages = [...contentPages.map(withNews), ...newsPages, ...academyPages()];

// Every address is built once: a press release, a page or an old address that redirects must not share a route
// (Astro would keep only one of them and the build would still pass).
{
  const seen = new Map();
  const problems = [];
  const where = (p) => (p.path ? `src/content/news/${p.folder}` : p.redirect ? 'src/data/redirect-pages.json' : p.academy ? 'Academy' : `src/content/pages/${p.lang}/${p.inner || 'index.html'}`);
  for (const p of [...pages.map((x) => ({ ...x, folder: news.find((n) => x.inner === n.path + '/')?.folder, path: news.some((n) => x.inner === n.path + '/') })),
    ...redirectList.map((r) => ({ route: r.route, redirect: true }))]) {
    const key = p.route.replace(/index\.html$/, '');
    if (seen.has(key)) problems.push(`/${key} is built twice: ${seen.get(key)} and ${where(p)}`);
    else seen.set(key, where(p));
  }
  for (const item of news) {
    if (item.photo && !fs.existsSync(path.resolve('public', item.photo.src.replace(/^\/+/, '')))) problems.push(`src/content/news/${item.folder}: photo ${item.photo.src} is not in public/`);
    if (item.photo && /\.webp$/.test(item.photo.src) && !fs.existsSync(path.resolve('public', item.photo.src.replace(/^\/+/, '').replace(/\.webp$/, '.jpg'))))
      problems.push(`src/content/news/${item.folder}: the JPG copy of ${item.photo.src} (used for sharing) is not in public/`);
  }
  if (problems.length) throw new Error('Addresses:\n  ' + problems.join('\n  '));
}
shell.seoIndex = seoIndex(pages);

export const redirects = redirectList;
