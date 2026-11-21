// PDF of a press release: the institutional version (no photos), printed with Chrome headless after the build.
// Header with logo and licence, place and date, type, title, text and "About BIMx"; a footer with the company details
// and "Page X of Y" on every page. Ported from tools/sitegen/communique.py.
//
// PDFs already in public/ (the published ones) are kept as they are; the build prints only the missing ones, i.e. for
// new press releases. After changing the text of a published press release, delete its PDF from public/ to reprint it.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { LANGS, LANG_PREFIX } from './links.mjs';
import { IDX, dateParts, pdfName, sortNews } from './news.mjs';
import { findChrome, printPdf } from './pdf.mjs';

export { findChrome };

const ROOT = process.cwd();
/** Read the news folders straight from disk (the Astro build uses import.meta.glob instead). */
export function loadNews() {
  const dir = path.join(ROOT, 'src/content/news');
  return sortNews(fs.readdirSync(dir).filter((d) => fs.existsSync(path.join(dir, d, 'news.json'))).map((d) => {
    const data = JSON.parse(fs.readFileSync(path.join(dir, d, 'news.json'), 'utf8'));
    return { ...data, body: Object.fromEntries(LANGS.map((l) => [l, fs.readFileSync(path.join(dir, d, `${l}.html`), 'utf8')])) };
  }));
}

const dataUri = (svg) => 'data:image/svg+xml,' + encodeURIComponent(svg).replace(/[!'()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());

/** The text for the PDF: without photos and style attributes; links become full addresses. */
function printBody(html, pageUrl) {
  let b = html.replace(/<figure(?![^>]*wp-block-table)[\s\S]*?<\/figure>|<img[^>]*>|<!--[\s\S]*?-->/g, '');
  b = b.replace(/\s(?:class|style|id|data-[a-z-]+)="[^"]*"/g, '');
  return b.replace(/href="([^"]*)"/g, (all, href) => (/^(?:[a-z]+:|#)/.test(href) ? all : `href="${new URL(href, pageUrl).href}"`));
}

export function printHtml(item, lang, texts) {
  const i = IDX[lang];
  const T = texts.CT;
  const pageUrl = `https://bimx.md/${LANG_PREFIX[lang]}${item.path}/`;
  const logo = fs.readFileSync(path.join(ROOT, 'public/assets/img/bimx-logo.svg'), 'utf8');
  const small = dataUri(logo.replace(/(<svg\b[^>]*?)\s(width|height)="[^"]*"/, '$1').replace(/(<svg\b[^>]*?)\s(width|height)="[^"]*"/, '$1').replace('<svg', '<svg width="66" height="19"'));
  const kind = texts.crumbs.kind[i];
  const place = `${T.city[i]}, ${dateParts(item.date, lang, texts).full}`;
  const cssStr = (s) => s.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\\\\A/g, '\\A');
  const foot = [T.company_sa[i], T.address[i], 'T: +373 22 89 77 00 · E: office@bimx.md · W: bimx.md', T.ids[i]].join('\\A');
  const vals = { foot: cssStr(foot), social: dataUri(fs.readFileSync(path.join(ROOT, 'src/print/social.svg'), 'utf8')), page: T.page[i], logo_small: small,
    running: cssStr(kind ? `${kind} · ${place}` : place) };
  const css = fs.readFileSync(path.join(ROOT, 'src/print/news.css'), 'utf8').replace(/\{\{(\w+)\}\}/g, (a, k) => vals[k] ?? a);
  const fonts = pathToFileURL(path.join(ROOT, 'public/assets/fonts/fonts.css')).href;
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>${item.title[lang]}</title>`
    + `<link href="${fonts}" rel="stylesheet"><style>${css}</style></head><body>`
    + `<header class="head"><img src="${dataUri(logo)}" alt="BIMx"><div>${T.company[i]}\n${T.licence[i].replace('\\A', '\n')}</div></header>`
    + `<div class="meta"><div class="place">${place}</div>${kind ? `<div class="kind">${kind}</div>` : ''}</div>`
    + `<h1>${item.title[lang]}</h1><div class="text">${printBody(item.body[lang], pageUrl)}</div>`
    + `<section class="about"><h2>${T.about_t[i]}</h2><p>${T.about[i]}</p></section></body></html>`;
}

/** Print the PDFs that are not in public/ yet into dist/. Returns [printed, missing]. */
export async function writeMissingPdfs(distDir, texts) {
  const jobs = [];
  for (const item of loadNews()) {
    for (const lang of LANGS) {
      const rel = `${LANG_PREFIX[lang]}${item.path}/${pdfName(item)}`;
      if (!fs.existsSync(path.join(ROOT, 'public', rel))) jobs.push({ item, lang, out: path.join(distDir, rel) });
    }
  }
  if (!jobs.length) return [0, 0];
  const chrome = findChrome();
  if (!chrome) return [0, jobs.length];
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'bimx-pdf-'));
  let made = 0;
  for (const { item, lang, out } of jobs) {
    const html = path.join(tmp, `${lang}-${item.path.replace(/\//g, '-')}.html`);
    fs.writeFileSync(html, printHtml(item, lang, texts));
    fs.mkdirSync(path.dirname(out), { recursive: true });
    if (await printPdf(chrome, html, out)) made++;
  }
  fs.rmSync(tmp, { recursive: true, force: true });
  return [made, jobs.length];
}
