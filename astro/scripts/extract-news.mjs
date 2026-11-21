// One-off: turn the press release pages imported from the old site into news data (src/content/news/).
//
//   node scripts/extract-news.mjs /tmp/mig/news-py.json
//
// news-py.json is a dump of the Python data (news.NEWS, CATS, T, MONTHS, home.NEWS_EDIT / NEWS_EXCERPT, communique.T / P).
// The script checks that every press release page renders back exactly from the new data, then deletes the snapshots.
import fs from 'node:fs';
import path from 'node:path';
import { LANGS, LANG_PREFIX, resolve, link } from '../src/lib/links.mjs';
import { articlePage, renderArticle, IDX } from '../src/lib/news.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const PY = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const PAGES = path.join(ROOT, 'src/content/pages');
const NEWS_DIR = path.join(ROOT, 'src/content/news');
const SHELL = path.join(ROOT, 'src/shell');

function readPage(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const m = /^---\n([\s\S]*?)\n---\n/.exec(raw);
  const f = {};
  for (const line of m[1].split('\n')) { const i = line.indexOf(': '); f[line.slice(0, i)] = JSON.parse(line.slice(i + 2)); }
  return { ...f, body: raw.slice(m[0].length) };
}
const one = (re, s, what) => { const m = re.exec(s); if (!m) throw new Error(`not found: ${what}`); return m; };
const same = (a, b, what) => { if (a !== undefined && a !== b) throw new Error(`${what} differs: ${JSON.stringify(a).slice(0, 200)} vs ${JSON.stringify(b).slice(0, 200)}`); return b; };

const templates = {};
const crumbs = { home: [], news: [], kind: [] };
const items = [];
const snapshots = [];

PY.NEWS.forEach((entry, order) => {
  const [p, date, category, key, summaries, photo] = entry;
  const item = { path: p, date, section: 'bimx', category, order, title: {}, cardTitle: {}, crumb: {}, summary: {}, description: {}, body: {}, legacy: {} };
  const parts = {}, postIds = {}, wpPost = {}, wpContainer = {}, shareText = {}, pageTitle = {};
  for (const lang of LANGS) {
    const i = IDX[lang];
    const file = path.join(PAGES, lang, p, 'index.html');
    const pg = readPage(file);
    snapshots.push({ file, pg, lang, item });
    const b = pg.body;
    const start = b.indexOf('<div class="single_anunturi_bimx bx-pr">');
    const headAt = b.indexOf('<section class="bx-pr-head">');
    const end = b.indexOf('</section>', b.indexOf('<section class="bx-pr-contact"')) + '</section>'.length;
    const block = b.slice(headAt, end);
    const wrapper = b.slice(0, headAt) + '{{article}}' + b.slice(end);
    templates[`${lang}/news-article`] = same(templates[`${lang}/news-article`], wrapper, `wrapper ${lang}`);

    const nav = one(/<nav class="bx-pr-crumbs" aria-label="Breadcrumb">([\s\S]*?)<\/nav>/, block, 'crumbs')[1];
    const links = [...nav.matchAll(/<a href="([^"]*)">([\s\S]*?)<\/a>/g)];
    crumbs.home[i] = same(crumbs.home[i], links[0][2], 'home crumb');
    crumbs.news[i] = same(crumbs.news[i], links[1][2], 'news crumb');
    item.crumb[lang] = one(/<span aria-current="page">([\s\S]*?)<\/span>/, nav, 'current')[1];
    const kind = /<span class="bx-pr-kind">([^<]*)<\/span>/.exec(block);
    crumbs.kind[i] = same(crumbs.kind[i], kind ? kind[1] : '', 'kind');
    item.title[lang] = one(/<h1>([\s\S]*?)<\/h1>/, block, 'h1')[1];
    item.summary[lang] = same(summaries[i], one(/<p class="bx-pr-lead">([\s\S]*?)<\/p>/, block, 'lead')[1], 'lead');
    item.cardTitle[lang] = PY.NEWS_EDIT[key][i][1];
    const route = `${LANG_PREFIX[lang]}${p}/`;
    let body = one(/<div class="bx-pr-text">([\s\S]*?)<\/div><section class="bx-pr-about"/, block, 'body')[1];
    // links inside the text: relative → from the site root ("/assets/…"), turned back into relative ones at build time
    body = body.replace(/(\s(?:href|src)=")([^"]*)(")/g, (all, a, url, c) => {
      const abs = resolve(route, url);
      return abs !== null && link(route, abs) === url ? a + abs + c : all;
    });
    item.body[lang] = body;
    const pdf = /<a class="bx-pr-pdf" href="([^"]*)"/.exec(block);
    item.pdf = same(item.pdf, pdf ? pdf[1] : null, 'pdf');
    const share = one(/<ul class="share-buttons-list bx-pr-share">([\s\S]*?)<\/ul>/, block, 'share')[1];
    const xText = one(/&text=([^"]*)"/, share, 'x text')[1];
    shareText[lang] = xText;
    templates[`${lang}/news-share`] = same(templates[`${lang}/news-share`], share.split(xText).join('{{xText}}'), `share ${lang}`);
    item.description[lang] = pg.description;
    pageTitle[lang] = pg.title;
    parts[lang] = pg.parts;
    postIds[lang] = one(/postid-(\d+)/, pg.bodyAttrs, 'postid')[1];
    wpPost[lang] = pg.wpPost;
    wpContainer[lang] = pg.wpContainer;
    if (photo) item.photo = { src: photo[0], alt: Object.fromEntries(LANGS.map((l) => [l, photo[1][IDX[l]]])), caption: Object.fromEntries(LANGS.map((l) => [l, photo[2][IDX[l]]])) };
  }
  const allSame = (o) => new Set(Object.values(o).map((v) => JSON.stringify(v))).size === 1;
  if (!allSame(postIds) || !allSame(wpPost) || !allSame(wpContainer)) throw new Error(`legacy ids differ per language: ${p}`);
  item.legacy = { postId: postIds.ro, wpPost: wpPost.ro, wpContainer: wpContainer.ro, parts: allSame(parts) ? parts.ro : parts };
  if (Object.entries(pageTitle).some(([l, t]) => t !== `${item.title[l]} &#8211; BIMx`)) item.pageTitle = pageTitle;
  if (Object.entries(shareText).some(([l, t]) => t !== quote(item.title[l]))) item.shareText = shareText;
  items.push(item);
});

function quote(s) {
  return Array.from(new TextEncoder().encode(s), (b) => {
    const c = String.fromCharCode(b);
    return /[A-Za-z0-9_.~-]/.test(c) ? c : c === ' ' ? '+' : '%' + b.toString(16).toUpperCase().padStart(2, '0');
  }).join('');
}

// defaults: the most common shell parts and the body class of a single post
const count = {};
for (const it of items) { const k = JSON.stringify(it.legacy.parts); count[k] = (count[k] || 0) + 1; }
const defaultParts = JSON.parse(Object.entries(count).sort((a, b) => b[1] - a[1])[0][0]);
const bodyAttrs = snapshots[0].pg.bodyAttrs.replace(/postid-\d+/, 'postid-{{postId}}');
for (const s of snapshots) same(bodyAttrs, s.pg.bodyAttrs.replace(/postid-\d+/, 'postid-{{postId}}'), 'bodyAttrs');
for (const it of items) if (JSON.stringify(it.legacy.parts) === JSON.stringify(defaultParts)) delete it.legacy.parts;

const categories = Object.fromEntries(Object.entries(PY.CATS).map(([k, [one, many]]) => [k, { one, many }]));
const texts = { MONTHS: PY.MONTHS, T: PY.T, CT: PY.CT, CP: PY.CP, crumbs };
const ctx = { news: items, categories, texts, templates, defaults: { parts: defaultParts, bodyAttrs } };

// verify
let bad = 0;
for (const { pg, lang, item } of snapshots) {
  const page = articlePage(item, lang, ctx);
  for (const k of ['route', 'title', 'description', 'bodyAttrs', 'wpPost', 'wpContainer', 'body']) {
    if (page[k] !== pg[k]) {
      bad++;
      const a = String(page[k]), b = String(pg[k]);
      let x = 0; while (a[x] === b[x]) x++;
      console.error(`${lang} ${item.path} ${k} @${x}\n  got: ${JSON.stringify(a.slice(x - 50, x + 80))}\n  exp: ${JSON.stringify(b.slice(x - 50, x + 80))}`);
      break;
    }
  }
  if (JSON.stringify(page.parts) !== JSON.stringify(pg.parts)) { bad++; console.error('parts', lang, item.path); }
  if (JSON.stringify(page.ogImage) !== JSON.stringify(pg.ogImage)) { bad++; console.error('ogImage', lang, item.path, page.ogImage, pg.ogImage); }
}
if (bad) throw new Error(`${bad} press release pages differ`);

// write
fs.rmSync(NEWS_DIR, { recursive: true, force: true });
fs.mkdirSync(NEWS_DIR, { recursive: true });
fs.writeFileSync(path.join(NEWS_DIR, 'categories.json'), JSON.stringify(categories, null, 2) + '\n');
for (const it of items) {
  const short = PY.NEWS.find((e) => e[0] === it.path)[3];
  const dir = path.join(NEWS_DIR, `${it.date}-${short}`);
  fs.mkdirSync(dir, { recursive: true });
  const { body, ...data } = it;
  fs.writeFileSync(path.join(dir, 'news.json'), JSON.stringify(data, null, 2) + '\n');
  for (const lang of LANGS) fs.writeFileSync(path.join(dir, `${lang}.html`), body[lang]);
}
fs.mkdirSync(path.join(ROOT, 'src/data'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'src/data/news-texts.json'), JSON.stringify(texts, null, 1) + '\n');
fs.writeFileSync(path.join(ROOT, 'src/data/news-defaults.json'), JSON.stringify(ctx.defaults, null, 2) + '\n');
for (const [k, v] of Object.entries(templates)) fs.writeFileSync(path.join(SHELL, `${k}.html`), v);
for (const { file } of snapshots) fs.rmSync(path.dirname(file), { recursive: true });
console.log(`${items.length} press releases × ${LANGS.length} languages extracted and verified`);
