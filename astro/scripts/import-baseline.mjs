// One-off import of the site built by the previous Python generator (baseline dist/) into the Astro sources.
//
//   node scripts/import-baseline.mjs <baseline-dist>
//
// Every page is split into shell parts (head, header, footer, scripts) and its own body. Shell parts become
// templates per language (src/shell/<lang>/), the body and page fields go to src/content/pages/<lang>/.
// The script checks that every page renders back from the templates byte for byte.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { resolve, link as rel, splitLang } from '../src/lib/links.mjs';
import { renderPage, altTarget } from '../src/lib/shell.mjs';
import { renderRedirect } from '../src/lib/redirects.mjs';
import { seoBlock, seoIndex, isIndexable } from '../src/lib/seo.mjs';

const BASE = path.resolve(process.argv[2] || '../../baseline-dist');
const OUT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SHELL_DIR = path.join(OUT, 'src/shell');
const PAGES_DIR = path.join(OUT, 'src/content/pages');

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });
}

const PAGE = /^([\s\S]*?<head>)([\s\S]*?)<\/head>([\s\S]*?)<body([^>]*)>([\s\S]*?)(<header id="masthead"[\s\S]*?<\/header>)([\s\S]*?)(<footer id="colophon"[\s\S]*?<\/footer>)([\s\S]*)$/;
const URL_ATTR = /(\s(?:href|src|action|data-src|poster)=)(["'])([^"']*)\2/g;
const SEO_START = /<meta property="og:|<meta name="twitter:|<link rel="canonical"|<link rel="alternate" hreflang|<meta name="robots"|<script type="application\/ld\+json">/;

function tokenizeUrls(route, s) {
  s = s.replace(URL_ATTR, (all, attr, q, url) => {
    const abs = resolve(route, url);
    if (abs === null || rel(route, abs) !== url) return all;
    return `${attr}${q}{{u:${abs}}}${q}`;
  });
  s = s.replace(/(\ssrcset=)(["'])([^"']*)\2/g, (all, attr, q, val) => {
    const parts = val.split(',').map((c) => {
      const m = /^(\s*)(\S+)(.*)$/.exec(c);
      const abs = resolve(route, m[2]);
      return abs !== null && rel(route, abs) === m[2] ? `${m[1]}{{u:${abs}}}${m[3]}` : c;
    });
    return `${attr}${q}${parts.join(',')}${q}`;
  });
  s = s.replace(/(<meta name="msapplication-TileImage" content=")([^"]*)(")/g, (all, a, url, b) => {
    const abs = resolve(route, url);
    return abs !== null && rel(route, abs) === url ? `${a}{{u:${abs}}}${b}` : all;
  });
  return s;
}

function tokenizeAlt(page, s) {
  return s.replace(/href="([^"]*)"( lang="(ro|en|uk|ru)" hreflang="\3")/g, (all, url, rest, lang) =>
    rel(page.route, altTarget(page, lang)) === url ? `href="{{alt:${lang}}}"${rest}` : all);
}

function tokenizeWp(page, s) {
  s = s.replace(/(wpcf7-f\d+)-p(\d+)(-o1)/g, (all, a, id, b) => { page.wpPost = id; return `${a}{{wpPost}}${b}`; });
  s = s.replace(/(name="_wpcf7_container_post" value=")(\d+)(")/g, (all, a, id, b) => {
    if (id !== '0') page.wpContainer = id;
    return `${a}{{wpContainer}}${b}`;
  });
  return s;
}

const menus = {};
function tokenizeHeader(page, s) {
  const start = s.indexOf('<li id="menu-item-407"');
  const end = s.indexOf('<li class="hide_desktop bx-menu-apply');
  if (start >= 0 && end > start) {
    const old = s.slice(start, end);
    const toggle = /<button class="sub-menu-toggle"[\s\S]*?<\/button>/.exec(old)[0];
    const back = /class="back_to_main_menu[^"]*"><a [^>]*>([^<]*)<\/a>/.exec(old)[1];
    const m = (menus[page.lang] ??= { toggle, back });
    if (m.toggle !== toggle || m.back !== back) throw new Error(`Menu toggle/back differ on ${page.route}`);
    s = s.slice(0, start) + '{{menu}}' + s.slice(end);
  }
  s = s.replace(/(class="custom-logo-link" rel="home") aria-current="page"/, '$1{{home}}');
  return tokenizeUrls(page.route, tokenizeAlt(page, s));
}

function tokenizeHead(page, s) {
  s = s.replace(/<title>([\s\S]*?)<\/title>/, (all, t) => { page.title = t; return '<title>{{title}}</title>'; });
  s = s.replace(/<meta name="description" content="([^"]*)">/, (all, d) => { page.description = d; return '<meta name="description" content="{{description}}">'; });
  const i = s.search(SEO_START);
  if (i >= 0) {
    page.seo = s.slice(i);
    s = s.slice(0, i) + '{{seo}}';
  }
  return tokenizeUrls(page.route, s);
}

function category(inner) {
  if (inner === '') return 'home';
  if (inner === '404.html') return '404';
  if (inner.startsWith('academy/')) return 'academy';
  if (inner.startsWith('2026/')) return 'news';
  if (inner.startsWith('category/') || inner === 'noutati/') return 'news-list';
  return 'page';
}

// ---- import ----
const files = walk(BASE).filter((f) => f.endsWith('.html')).sort();
const pages = [];
const redirects = [];
const clusters = {}; // `${lang}/${seg}` → Map(text → name)
const templates = {};

for (const file of files) {
  const relFile = path.relative(BASE, file).split(path.sep).join('/');
  const route = relFile === 'index.html' ? '' : relFile.endsWith('/index.html') ? relFile.slice(0, -'index.html'.length) : relFile;
  const { lang, inner } = splitLang(route);
  const html = fs.readFileSync(file, 'utf8');
  const refresh = /<meta http-equiv="refresh" content="0; url=([^"]*)">/.exec(html);
  if (refresh) {
    const to = resolve(route, refresh[1]);
    const entry = { route, to };
    if (renderRedirect(route, to) !== html) {
      const url = refresh[1];
      let tpl = html.split(`url=${url}"`).join('url={{to}}"').split(`href="${url}"`).join('href="{{to}}"');
      tpl = tpl.replace(/(<link rel="canonical" href=")[^"]*(")/, '$1{{canonical}}$2');
      tpl = tokenizeUrls(route, tpl);
      const key = `${lang}/redirect`;
      if (templates[key] !== undefined && templates[key] !== tpl) throw new Error(`Second redirect template variant: ${relFile}`);
      templates[key] = tpl;
      if (renderRedirect(route, to, tpl) !== html) throw new Error(`Redirect page does not round-trip: ${relFile}`);
      entry.template = 'redirect';
    }
    redirects.push(entry);
    continue;
  }
  const m = PAGE.exec(html);
  if (!m) throw new Error(`Unexpected page structure: ${relFile}`);
  const page = { route, lang, inner, file: relFile, parts: {} };
  const segs = {
    open: tokenizeUrls(route, m[1]),
    head: tokenizeHead(page, m[2]),
    mid: tokenizeUrls(route, m[3]),
    pre: tokenizeUrls(route, m[5]),
    header: tokenizeHeader(page, m[6]),
    footer: tokenizeWp(page, tokenizeUrls(route, tokenizeAlt(page, m[8]))),
    tail: tokenizeUrls(route, m[9]),
  };
  page.bodyAttrs = m[4];
  page.body = m[7];
  for (const [seg, text] of Object.entries(segs)) {
    const key = `${lang}/${seg}`;
    const map = (clusters[key] ??= new Map());
    if (!map.has(text)) {
      const base = `${seg}-${category(inner)}`;
      let name = base;
      for (let n = 2; [...map.values()].includes(name); n++) name = `${base}-${n}`;
      map.set(text, name);
      templates[`${lang}/${name}`] = text;
    }
    page.parts[seg] = map.get(text);
  }
  pages.push(page);
}

// single-variant templates drop the category suffix
for (const [key, map] of Object.entries(clusters)) {
  if (map.size !== 1) continue;
  const [lang, seg] = key.split('/');
  const [text, name] = [...map.entries()][0];
  delete templates[`${lang}/${name}`];
  templates[`${lang}/${seg}`] = text;
  map.set(text, seg);
  for (const p of pages) if (p.lang === lang && p.parts[seg] === name) p.parts[seg] = seg;
}

// SEO: derive the page fields from the old tags; keep the raw tags only where the generator cannot reproduce them
for (const p of pages) {
  const robots = /<meta name="robots" content="([^"]*)">/.exec(p.seo ?? '');
  if (robots && robots[1].includes('noindex') && isIndexable(p)) p.noindex = true;
}
const index = seoIndex(pages);
let rawSeo = 0;
for (const p of pages) {
  const raw = p.seo ?? '';
  delete p.seo;
  if (seoBlock(p, index) === raw) continue;
  const img = /og:image" content="([^"]*)">\n<meta property="og:image:width" content="(\d+)">\n<meta property="og:image:height" content="(\d+)">\n<meta property="og:image:alt" content="([^"]*)">/.exec(raw);
  if (img) {
    p.ogImage = { url: img[1], width: Number(img[2]), height: Number(img[3]), alt: img[4].replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&') };
    if (seoBlock(p, index) === raw) continue;
    delete p.ogImage;
  }
  p.seoRaw = raw;
  rawSeo++;
  if (rawSeo <= 3 && p.inner !== '404.html') {
    const got = seoBlock({ ...p, seoRaw: undefined }, index);
    let k = 0; while (got[k] === raw[k]) k++;
    console.error(`SEO differs: ${p.route} @${k}\n  got: ${JSON.stringify(got.slice(k - 60, k + 100))}\n  exp: ${JSON.stringify(raw.slice(k - 60, k + 100))}`);
  }
}
console.log(`SEO tags kept as they are on ${rawSeo} pages`);

// round trip
const shell = { templates, menu: menus, seoIndex: index };
let bad = 0;
for (const p of pages) {
  const out = renderPage(p, shell);
  const orig = fs.readFileSync(path.join(BASE, p.file), 'utf8');
  if (out !== orig) {
    let k = 0;
    while (out[k] === orig[k]) k++;
    if (bad++ < 5) console.error(`Round trip differs: ${p.file} @${k}\n  got: ${JSON.stringify(out.slice(k - 40, k + 80))}\n  exp: ${JSON.stringify(orig.slice(k - 40, k + 80))}`);
  }
}
if (bad) throw new Error(`${bad} pages do not round-trip`);

// write
fs.rmSync(SHELL_DIR, { recursive: true, force: true });
fs.rmSync(PAGES_DIR, { recursive: true, force: true });
for (const [key, text] of Object.entries(templates)) {
  const f = path.join(SHELL_DIR, `${key}.html`);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, text);
}
for (const [lang, m] of Object.entries(menus)) fs.writeFileSync(path.join(SHELL_DIR, lang, 'menu.json'), JSON.stringify(m, null, 2) + '\n');

const FIELDS = ['route', 'parts', 'title', 'description', 'noindex', 'ogImage', 'wpPost', 'wpContainer', 'bodyAttrs', 'seoRaw'];
for (const p of pages) {
  const f = path.join(PAGES_DIR, p.lang, p.inner === '' || p.inner.endsWith('/') ? `${p.inner}index.html` : p.inner);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  const front = FIELDS.filter((k) => p[k] !== undefined).map((k) => `${k}: ${JSON.stringify(p[k])}`).join('\n');
  fs.writeFileSync(f, `---\n${front}\n---\n${p.body}`);
}
fs.mkdirSync(path.join(OUT, 'src/data'), { recursive: true });
fs.writeFileSync(path.join(OUT, 'src/data/redirect-pages.json'),
  JSON.stringify(redirects, null, 2) + '\n');

const counts = Object.fromEntries(Object.entries(clusters).map(([k, m]) => [k, m.size]));
console.log(`${pages.length} pages, ${redirects.length} redirect pages, ${Object.keys(templates).length} shell templates`);
console.log(JSON.stringify(counts));
