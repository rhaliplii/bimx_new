// Relative links between pages of the static site, matching the URLs of the previous generator.
//
// A page "route" is its path inside dist/ without the leading slash:
//   ""                         → index.html (RO home)
//   "identitate/"              → identitate/index.html
//   "en/identitate/"           → en/identitate/index.html
//   "academy/programe/a/b.html"
//   "404.html"
// Targets are absolute site paths ("/identitate/", "/wp-content/x.png", "/en/").

export const LANGS = ['ro', 'en', 'uk', 'ru'];
export const LANG_PREFIX = { ro: '', en: 'en/', uk: 'uk/', ru: 'ru/' };

/** Directory of a route, always ending with "/" ("" for the root). */
export function routeDir(route) {
  if (route === '' || route.endsWith('/')) return route;
  const i = route.lastIndexOf('/');
  return i < 0 ? '' : route.slice(0, i + 1);
}

/** Output file of a route inside dist/. */
export function routeFile(route) {
  return route === '' || route.endsWith('/') ? `${route}index.html` : route;
}

/** Language of a route and the route inside that language. */
export function splitLang(route) {
  for (const lang of LANGS.slice(1)) {
    if (route === lang + '/' || route.startsWith(lang + '/')) return { lang, inner: route.slice(lang.length + 1) };
  }
  return { lang: 'ro', inner: route };
}

/**
 * Relative URL from the page at `route` to the absolute target ("/x/y/", "/a.png?v=1#top").
 * Same directory → "./", a file in the same directory → "b.html".
 */
export function rel(route, target) {
  const m = /^([^?#]*)([?#].*)?$/.exec(target);
  const path = m[1];
  const tail = m[2] || '';
  const from = routeDir(route).split('/').filter(Boolean);
  const isDir = path.endsWith('/');
  const to = path.split('/').filter(Boolean);
  let i = 0;
  while (i < from.length && i < to.length - (isDir ? 0 : 1) && from[i] === to[i]) i++;
  const up = from.length - i;
  const rest = to.slice(i);
  let out = '../'.repeat(up) + rest.join('/');
  if (isDir) {
    if (rest.length) out += '/';
    else if (!up) out = './';
  }
  if (out === '' && !isDir) out = './';
  return out + tail;
}

/** Absolute target for a relative URL found on the page at `route`; null when it is not a site link. */
export function resolve(route, url) {
  if (/^(?:[a-z][a-z0-9+.-]*:|\/\/|#|\{\{)/i.test(url) || url === '') return null;
  const m = /^([^?#]*)([?#].*)?$/.exec(url);
  const path = m[1];
  const tail = m[2] || '';
  const parts = routeDir(route).split('/').filter(Boolean);
  if (path.startsWith('/')) parts.length = 0;
  const segs = path.split('/');
  for (let k = 0; k < segs.length; k++) {
    const s = segs[k];
    if (s === '' || s === '.') continue;
    if (s === '..') {
      if (!parts.length) return null;
      parts.pop();
    } else parts.push(s);
  }
  const isDir = path === '' || path === '.' || path.endsWith('/') || path === '..' || path.endsWith('/.') || path.endsWith('/..');
  return '/' + parts.join('/') + (isDir && parts.length ? '/' : '') + tail;
}

/** 404.html is served at any address, so its links start from the site root. */
export function absoluteLinks(route) {
  return splitLang(route).inner === '404.html';
}

/** Link from a page to an absolute site path. */
export function link(route, target) {
  return absoluteLinks(route) ? target : rel(route, target);
}
