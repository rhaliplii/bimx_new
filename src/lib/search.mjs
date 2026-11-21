// Site search index: for each language, assets/search/<lang>.js with the title, section, headings and main text of
// every page (without header, footer, menus, hidden sections and quizzes). The site is static, so assets/js/search.js
// searches these files in the browser. Built after the pages, from the finished HTML. Ported from tools/sitegen/search.py,
// including the behaviour of Python's HTMLParser that the old index relied on.
import fs from 'node:fs';
import path from 'node:path';

const MAX_TEXT = 12000; // characters of text per page
const SKIP_TAGS = new Set(['script', 'style', 'svg', 'noscript', 'form', 'nav', 'select', 'button', 'template', 'iframe']);
const SKIP_CLASSES = new Set(['market_overview', 'market_gainers', 'bimx-ticker-wrap', 'breadcrumbs', 'modal_search_form', 'ds-popup',
  'ds-popup-wrapper', 'quiz', 'lesson_nav', 'toc', 'guide_toc', 'pager', 'complete_bar', 'disclaimer',
  'section_nav_wrap', 'read_progress', 'share', 'share-list', 'contact_modal_overlay', 'numbers']);
const BREAK_TAGS = new Set(['p', 'li', 'br', 'div', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'dt', 'dd', 'section', 'article']);
const PLACEHOLDER = /^\s*(În curând|Coming soon)\s*$/;
const LANGS = ['ro', 'en', 'uk', 'ru'];

const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
function unescape(s) {
  return s.replace(/&(#[xX][0-9a-fA-F]+|#\d+|[a-zA-Z][a-zA-Z0-9]*);?/g, (all, e) => {
    if (e[0] === '#') {
      const n = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return String.fromCodePoint(n);
    }
    return NAMED[e] ?? all;
  });
}

// Python's str.split() whitespace
const WS = /[\s\u001c-\u001f\u0085]+/g;
const squash = (s) => s.split(WS).filter(Boolean).join(' ');

/** Minimal tokenizer with the semantics of Python's html.parser (tags, comments, raw text in script/style). */
function* tokens(html) {
  const ATTR = /\s*([^\s/>"'=]+)(?:\s*=\s*('[^']*'|"[^"]*"|[^\s>]*))?/y;
  let i = 0, data = '';
  const flush = function* () { if (data) { yield { type: 'data', text: unescape(data) }; data = ''; } };
  while (i < html.length) {
    const lt = html.indexOf('<', i);
    if (lt < 0) { data += html.slice(i); break; }
    data += html.slice(i, lt);
    i = lt;
    if (html.startsWith('<!--', i)) {
      const end = html.indexOf('-->', i + 4);
      yield* flush();
      i = end < 0 ? html.length : end + 3;
    } else if (/^<\/[a-zA-Z]/.test(html.slice(i, i + 3))) {
      const m = /^<\/\s*([a-zA-Z][^\s>]*)[^>]*>/.exec(html.slice(i, i + 200));
      if (!m) { data += '<'; i++; continue; }
      yield* flush();
      yield { type: 'end', tag: m[1].toLowerCase() };
      i += m[0].length;
    } else if (/^<[a-zA-Z]/.test(html.slice(i, i + 2))) {
      const m = /^<([a-zA-Z][^\t\n\r\f />\x00]*)/.exec(html.slice(i, i + 100));
      const tag = m[1].toLowerCase();
      let j = i + m[0].length;
      const attrs = {};
      for (;;) {
        ATTR.lastIndex = j;
        const a = ATTR.exec(html);
        if (!a || a[0] === '') break;
        let v = a[2];
        if (v !== undefined && (v[0] === '"' || v[0] === "'")) v = v.slice(1, -1);
        const name = a[1].toLowerCase();
        if (!(name in attrs)) attrs[name] = v === undefined ? null : unescape(v);
        j = ATTR.lastIndex;
      }
      const close = html.indexOf('>', j);
      const selfClosing = html[close - 1] === '/';
      yield* flush();
      yield { type: 'start', tag, attrs };
      i = close + 1;
      if (selfClosing) yield { type: 'end', tag };
      else if (tag === 'script' || tag === 'style') {
        const re = new RegExp(`</${tag}\\s*>`, 'ig');
        re.lastIndex = i;
        const e = re.exec(html);
        const end = e ? e.index : html.length;
        if (end > i) yield { type: 'data', text: html.slice(i, end) };
        if (e) { yield { type: 'end', tag }; i = end + e[0].length; } else i = html.length;
      }
    } else if (html.startsWith('<!', i) || html.startsWith('<?', i)) {
      const end = html.indexOf('>', i);
      yield* flush();
      i = end < 0 ? html.length : end + 1;
    } else { data += '<'; i++; }
  }
  yield* flush();
}

function extract(html) {
  let inMain = 0, skip = null, curHead = null, inCrumbs = false, crumbDepth = 0;
  const parts = [], heads = [], h1 = [], crumbs = [];
  for (const t of tokens(html)) {
    if (t.type === 'start') {
      const cls = new Set((t.attrs.class || '').split(WS).filter(Boolean));
      if (cls.has('breadcrumbs')) { inCrumbs = true; crumbDepth = 0; }
      if (inCrumbs) crumbDepth += t.tag === 'ul' ? 1 : 0;
      if (t.tag === 'main') inMain++;
      if (skip) { if (t.tag === skip[0]) skip[1]++; continue; }
      const hidden = (t.attrs.style || '').replace(/ /g, '').includes('display:none') || 'hidden' in t.attrs;
      if (inMain && (SKIP_TAGS.has(t.tag) || [...cls].some((c) => SKIP_CLASSES.has(c)) || hidden)) { skip = [t.tag, 1]; continue; }
      if (['h1', 'h2', 'h3'].includes(t.tag) && inMain) curHead = [t.tag, []];
      if (BREAK_TAGS.has(t.tag)) parts.push(' ');
    } else if (t.type === 'end') {
      if (inCrumbs && t.tag === 'ul') { crumbDepth--; if (crumbDepth <= 0) inCrumbs = false; }
      if (t.tag === 'main') inMain = Math.max(0, inMain - 1);
      if (skip) { if (t.tag === skip[0]) { skip[1]--; if (skip[1] === 0) skip = null; } continue; }
      if (curHead && t.tag === curHead[0]) {
        const text = squash(curHead[1].join(''));
        if (text) (t.tag === 'h1' ? h1 : heads).push(text);
        curHead = null;
      }
    } else {
      if (inCrumbs && t.text.trim()) crumbs.push(t.text.trim());
      if (!inMain || skip) continue;
      parts.push(t.text);
      if (curHead) curHead[1].push(t.text);
    }
  }
  return { parts, heads, h1, crumbs };
}

function entry(route, html) {
  if (html.slice(0, 500).includes('http-equiv="refresh"')) return null;
  const p = extract(html);
  const body = squash(p.parts.join('')).normalize('NFC');
  let title = p.h1.length ? p.h1[0] : unescape(/<title>([\s\S]*?)<\/title>/.exec(html)[1]);
  title = title.trim().replace(/\s+[–-]\s+(BIMx Academy|Ghid BIMx Academy|BIMx Academy guide|BIMx)$/, '');
  if (PLACEHOLDER.test(title) || PLACEHOLDER.test(body) || body.split(' ').filter(Boolean).length < 12) return null;
  const fix = { 'Despre Noi': 'Despre noi', 'Piaţă': 'Piață', 'Ştiri': 'Știri' };
  const crumbs = p.crumbs.slice(1, -1).filter((c) => !['Acasă', 'Home', 'Главная'].includes(c));
  const section = crumbs.map((c) => fix[c] ?? c).join(' › ') || (route.includes('academy/') ? 'BIMx Academy' : 'BIMx');
  const cut = (s, n) => Array.from(s).slice(0, n).join('');
  return { u: route === '' ? './' : route, t: title.normalize('NFC'), s: section, h: cut([...new Set(p.heads)].join(' · '), 600), x: cut(body, MAX_TEXT) };
}

/** Write dist/assets/search/<lang>.js from the built pages. */
export function writeSearchIndex(distDir) {
  const files = [];
  const walk = (d, rel = []) => fs.readdirSync(d, { withFileTypes: true }).forEach((e) => {
    if (e.isDirectory()) { if (!(rel.length === 0 && ['assets', 'wp-content', 'wp-includes'].includes(e.name))) walk(path.join(d, e.name), [...rel, e.name]); }
    else if (e.name.endsWith('.html')) files.push([...rel, e.name]);
  });
  walk(distDir);
  // like Python's sorted(Path.rglob()): compare path parts, not whole strings
  files.sort((a, b) => { for (let k = 0; k < Math.min(a.length, b.length); k++) if (a[k] !== b[k]) return a[k] < b[k] ? -1 : 1; return a.length - b.length; });
  const pages = Object.fromEntries(LANGS.map((l) => [l, []]));
  for (const parts of files) {
    const rel = parts.join('/');
    if (rel === '404.html') continue; // the old build wrote 404.html after the index
    const route = rel === 'index.html' ? '' : rel.endsWith('/index.html') ? rel.slice(0, -'index.html'.length) : rel;
    const e = entry(route, fs.readFileSync(path.join(distDir, rel), 'utf8'));
    if (!e) continue;
    const lang = LANGS.includes(parts[0]) && parts.length > 1 ? parts[0] : 'ro';
    pages[lang].push(e);
  }
  const dir = path.join(distDir, 'assets/search');
  fs.mkdirSync(dir, { recursive: true });
  for (const [lang, entries] of Object.entries(pages)) {
    fs.writeFileSync(path.join(dir, `${lang}.js`), `window.BIMX_SEARCH = window.BIMX_SEARCH || {};\nwindow.BIMX_SEARCH.${lang} = ${JSON.stringify(entries)};\n`);
  }
  return Object.fromEntries(Object.entries(pages).map(([l, e]) => [l, e.length]));
}
