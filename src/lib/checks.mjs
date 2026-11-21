// Checks of the built site (ported from tools/check_links.py); the build fails when one of them finds a problem:
//   - every local link, image, script and url() leads to an existing file;
//   - no page links to https://bimx.md in its content: links stay relative, so the site works on the staging copy too
//     (the official address is allowed in <head>: canonical, hreflang, sharing tags, organisation data);
//   - nothing refers to the old GitHub preview copy (rhaliplii.github.io/bimx_new);
//   - every address in sitemap.xml is a page of the site.
import fs from 'node:fs';
import path from 'node:path';

const ATTR = /\s(?:href|src|srcset|data-src)=(["'])([^"']*)\1/g;
const CSS_URL = /url\(\s*['"]?([^'")]+)/g;
// CSS files of the WordPress theme that ask for images bimx.md never had: only a warning
const KNOWN_BROKEN = new Set(['wp-content/themes/victor-child/assets/css/lightbox.css', 'wp-content/themes/victor-child/assets/css/slick-theme.css']);
const ORIGIN = /(?:https?:(?:\\?\/){2}|https?%3A%2F%2F|(?<![\w@.])\/\/)(?:www\.)?bimx\.md[^"'\s<>)]*/gi;
const DECLARED = /<link rel="(?:canonical|alternate)"[^>]*>|<meta (?:property="og:[^"]*"|name="twitter:[^"]*")[^>]*>|<script type="application\/ld\+json">[\s\S]*?<\/script>/g;
const EXTERNAL = ['#', 'http:', 'https:', '//', 'mailto:', 'tel:', 'javascript:', 'data:', '{'];
const MIRROR = /rhaliplii|bimx_new/gi;
const TEXT = ['.html', '.css', '.js', '.json', '.xml', '.txt', '.htaccess'];

function* targets(text, css) {
  const found = [...text.matchAll(CSS_URL)].map((m) => ({ val: m[1], srcset: false }));
  if (!css) found.push(...[...text.matchAll(ATTR)].map((m) => ({ val: m[2], srcset: m[0].trimStart().startsWith('srcset') })));
  for (const { val, srcset } of found) {
    for (const part of srcset ? val.split(',') : [val]) {
      const url = part.trim().split(' ')[0];
      if (url && !EXTERNAL.some((e) => url.startsWith(e))) yield url;
    }
  }
}

export function checkSite(dist) {
  const files = [];
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).forEach((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : files.push(path.join(d, e.name))));
  walk(dist);
  const broken = new Map(), origin = new Map(), mirror = new Map(), rootLinks = new Map();
  const add = (map, k, v) => (map.get(k) ?? map.set(k, new Set()).get(k)).add(v);
  let checked = 0;
  for (const f of files) {
    const rel = path.relative(dist, f).split(path.sep).join('/');
    const ext = path.extname(f) || path.basename(f);
    if (!TEXT.includes(ext)) continue;
    const text = fs.readFileSync(f, 'utf8');
    for (const m of text.matchAll(MIRROR)) add(mirror, rel, m[0]);
    if (ext !== '.html' && ext !== '.css') continue;
    for (const m of text.replace(DECLARED, '').matchAll(ORIGIN)) add(origin, rel, m[0]);
    for (const url of targets(text, ext === '.css')) {
      let p;
      try { p = decodeURIComponent(url.split('#')[0].split('?')[0]); } catch { p = url; }
      if (!p) continue;
      // addresses from the root ("/assets/…") are allowed only in 404.html, which is served at any address;
      // elsewhere they break the copies of the site in a sub-folder (GitHub Pages preview)
      if (p.startsWith('/') && rel !== '404.html' && !KNOWN_BROKEN.has(rel)) add(rootLinks, rel, url);
      let target = p.startsWith('/') ? path.join(dist, p) : path.resolve(path.dirname(f), p);
      if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, 'index.html');
      checked++;
      if (!fs.existsSync(target)) add(broken, rel, url);
    }
  }
  const known = [...broken.keys()].filter((k) => KNOWN_BROKEN.has(k));
  const knownCount = known.reduce((n, k) => n + broken.get(k).size, 0);
  known.forEach((k) => broken.delete(k));
  const sitemap = path.join(dist, 'sitemap.xml');
  const locs = fs.existsSync(sitemap) ? [...fs.readFileSync(sitemap, 'utf8').matchAll(/<loc>https:\/\/bimx\.md\/([^<]*)<\/loc>/g)].map((m) => m[1]) : [];
  const missing = locs.filter((loc) => !fs.existsSync(path.join(dist, decodeURIComponent(loc), loc === '' || loc.endsWith('/') ? 'index.html' : '')));

  const problems = [];
  for (const [page, urls] of broken) problems.push(`${page}: broken link${urls.size > 1 ? 's' : ''} ${[...urls].join(', ')}`);
  for (const [page, urls] of origin) problems.push(`${page}: links to bimx.md instead of a relative link: ${[...urls].join(', ')}`);
  for (const [page, urls] of mirror) problems.push(`${page}: refers to the GitHub preview copy (${[...urls].join(', ')})`);
  for (const [page, urls] of rootLinks) problems.push(`${page}: link from the site root instead of a relative link: ${[...urls].join(', ')}`);
  for (const loc of missing) problems.push(`sitemap.xml: no page for ${loc}`);
  const summary = `links: ${checked} checked, ${[...broken.values()].reduce((n, s) => n + s.size, 0)} broken`
    + (knownCount ? `; ${knownCount} images missing in the WordPress theme CSS (known, as on the old site)` : '')
    + (locs.length ? `; sitemap.xml: ${locs.length} addresses` : '');
  return { problems, summary };
}
