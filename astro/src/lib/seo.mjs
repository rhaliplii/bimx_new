// SEO for https://bimx.md/: sharing tags (Open Graph, Twitter), canonical, hreflang, robots, the organisation data
// on the home page, sitemap.xml, robots.txt and .htaccess. Ported from tools/sitegen/seo.py and fixes.fix_og.
//
// A page is indexable unless it is still "in preparation" (class="bx-prep" in the body), is the login page, or
// has `noindex: true` in its fields. Indexable pages are listed in sitemap.xml and linked with hreflang.
import { LANGS, LANG_PREFIX } from './links.mjs';

export const SITE_URL = 'https://bimx.md/';
const LOCALE_OG = { ro: 'ro_RO', en: 'en_GB', uk: 'uk_UA', ru: 'ru_RU' };
const LOCALE = { ro: 'ro-RO', en: 'en-GB', uk: 'uk-UA', ru: 'ru-RU' };
const NOINDEX_KEYS = ['autentificare'];
const LINKEDIN = 'https://linkedin.com/company/moldova-international-stock-exchange-bursa-internationala-a-moldovei';
const FACEBOOK = 'https://www.facebook.com/BIMx.MD/';

const HOME_TITLE = {
  ro: 'Bursa Internațională a Moldovei (BIMx)', en: 'Moldova International Stock Exchange (BIMx)',
  ru: 'Международная фондовая биржа Молдовы (BIMx)', uk: 'Міжнародна фондова біржа Молдови (BIMx)',
};
const IMAGE_ALT = {
  ro: 'BIMx – Bursa Internațională a Moldovei', en: 'BIMx – Moldova International Stock Exchange',
  ru: 'BIMx — Международная фондовая биржа Молдовы', uk: 'BIMx — Міжнародна фондова біржа Молдови',
};

const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: '\u00a0', ndash: '–', mdash: '—', laquo: '«', raquo: '»', hellip: '…', rsquo: '’', lsquo: '‘', rdquo: '”', ldquo: '“', bdquo: '„' };
export function unescapeHtml(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (all, e) => {
    if (e[0] === '#') return String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
    return NAMED[e] ?? all;
  });
}
/** Python html.escape(quote=True). */
export function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
}

export function isIndexable(page) {
  if (page.noindex) return false;
  if (page.body.includes('class="bx-prep"')) return false;
  return !NOINDEX_KEYS.includes(page.inner.split('/')[0]);
}

/** Public address of a page route. */
export const urlOf = (route) => SITE_URL + route;

/** Index of the pages by route, used for hreflang and the sitemap. */
export function seoIndex(pages) {
  const indexable = new Set(pages.filter((p) => p.inner !== '404.html' && isIndexable(p)).map((p) => p.route));
  return { indexable };
}

/** hreflang: indexable variants of the same page (at least two), plus x-default = Romanian. */
export function alternates(page, index) {
  const alts = [];
  for (const x of LANGS) {
    const other = LANG_PREFIX[x] + page.inner;
    if (index.indexable.has(other)) alts.push([x, urlOf(other)]);
  }
  if (alts.length < 2) return [];
  const ro = alts.find(([x]) => x === 'ro');
  if (ro) alts.push(['x-default', ro[1]]);
  return alts;
}

function organization(page, ogTitle) {
  const name = unescapeHtml(ogTitle).replace(/ \(BIMx\)$/, '');
  const org = SITE_URL + '#organization';
  const data = {
    '@context': 'https://schema.org', '@graph': [
      {
        '@type': 'Organization', '@id': org, name, alternateName: 'BIMx', url: SITE_URL,
        logo: SITE_URL + 'assets/img/bimx-logo.svg', email: 'office@bimx.md',
        address: { '@type': 'PostalAddress', streetAddress: 'str. Vlaicu Pârcălab 63', postalCode: 'MD-2012', addressLocality: 'Chișinău', addressCountry: 'MD' },
        sameAs: [LINKEDIN, FACEBOOK],
      },
      { '@type': 'WebSite', '@id': SITE_URL + '#website', name: 'BIMx', url: SITE_URL, inLanguage: LOCALE[page.lang], publisher: { '@id': org } },
    ],
  };
  // Python json.dumps(ensure_ascii=False, separators=(",", ":")) escapes "/" only inside "</"
  return '<script type="application/ld+json">' + JSON.stringify(data).replace(/<\//g, '<\\/') + '</script>';
}

/** Tags at the end of <head>: sharing, canonical, hreflang, robots and (home page) organisation data. */
export function seoBlock(page, index) {
  if (page.seoRaw !== undefined) return page.seoRaw;
  const home = page.inner === '';
  const title = home ? HOME_TITLE[page.lang] : unescapeHtml(page.title ?? 'BIMx').trim();
  const desc = page.description !== undefined ? unescapeHtml(page.description) : '';
  const url = urlOf(page.route);
  const img = page.ogImage ?? { url: `${SITE_URL}assets/img/og-bimx-${page.lang}.png`, width: 1200, height: 630, alt: IMAGE_ALT[page.lang] };
  const e = escapeHtml;
  const tags = [
    '<meta property="og:type" content="website">',
    '<meta property="og:site_name" content="BIMx">',
    `<meta property="og:title" content="${e(title)}">`,
    `<meta property="og:description" content="${e(desc)}">`,
    `<meta property="og:url" content="${e(url)}">`,
    `<meta property="og:locale" content="${LOCALE_OG[page.lang]}">`,
    ...LANGS.filter((x) => x !== page.lang).map((x) => `<meta property="og:locale:alternate" content="${LOCALE_OG[x]}">`),
    `<meta property="og:image" content="${img.url}">`,
    `<meta property="og:image:width" content="${img.width}">`,
    `<meta property="og:image:height" content="${img.height}">`,
    `<meta property="og:image:alt" content="${e(img.alt)}">`,
    '<meta name="twitter:card" content="summary_large_image">',
    `<meta name="twitter:title" content="${e(title)}">`,
    `<meta name="twitter:description" content="${e(desc)}">`,
    `<meta name="twitter:image" content="${img.url}">`,
    `<link rel="canonical" href="${url}">`,
  ];
  const indexable = index.indexable.has(page.route);
  if (indexable) tags.push(...alternates(page, index).map(([x, u]) => `<link rel="alternate" hreflang="${x}" href="${u}">`));
  tags.push(`<meta name="robots" content="${indexable ? 'max-image-preview:large' : 'noindex, follow'}">`);
  if (home) tags.push(organization(page, e(title)));
  return tags.join('\n') + '\n';
}

// ---- files at the site root ----

const xmlEscape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');

export function sitemapXml(pages, index) {
  const order = Object.fromEntries(LANGS.map((x, i) => [x, i]));
  const rows = pages.filter((p) => index.indexable.has(p.route))
    .map((p) => ({ p, loc: urlOf(p.route) }))
    .sort((a, b) => order[a.p.lang] - order[b.p.lang] || (a.loc < b.loc ? -1 : a.loc > b.loc ? 1 : 0))
    .map(({ p, loc }) => {
      const links = alternates(p, index).map(([x, u]) => `\n    <xhtml:link rel="alternate" hreflang="${x}" href="${xmlEscape(u)}"/>`).join('');
      return `  <url>\n    <loc>${xmlEscape(loc)}</loc>${links}\n  </url>`;
    });
  return '<?xml version="1.0" encoding="UTF-8"?>\n'
    + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + rows.join('\n') + '\n</urlset>\n';
}

export function robotsTxt() {
  return `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}sitemap.xml\n`;
}

const apache = (s) => s.replace(/([.^$*+?()[\]{}|\\-])/g, '\\$1');

/** 301 for the old addresses, "…/index.html" → "…/", old WordPress sitemaps → sitemap.xml, the 404 page. */
export function htaccess(redirects) {
  const rows = redirects.map((r) => {
    const [path, frag] = r.to.split('#');
    return [r.route, path.slice(1), frag || ''];
  }).sort((a, b) => (a.join('\u0000') < b.join('\u0000') ? -1 : 1));
  const rules = rows.map(([src, dst, frag]) =>
    `RewriteRule ^${apache(src.replace(/\/$/, ''))}(?:/(?:index\\.html)?)?$ /${dst}${frag ? '#' + frag : ''} [R=301,L,NE]`);
  return '# bimx.md – site static generat de tools/build.py (sitegen/seo.py). Nu se editează pe server.\n'
    + '# HTTPS și www → bimx.md sunt setate în panoul găzduirii, nu aici.\n'
    + 'DirectoryIndex index.html\n'
    + 'ErrorDocument 404 /404.html\n\n'
    + '<IfModule mod_rewrite.c>\n'
    + 'RewriteEngine On\n'
    + 'RewriteBase /\n\n'
    + '# rutele vechi, unite cu alte pagini (aceleași ca paginile cu redirecționare meta din dist/)\n'
    + rules.join('\n') + '\n\n'
    + '# sitemap-urile vechi WordPress\n'
    + 'RewriteRule ^(?:wp-sitemap[^/]*|sitemap_index)\\.xml$ /sitemap.xml [R=301,L]\n\n'
    + '# o singură adresă pe pagină: /pagina/index.html → /pagina/\n'
    + 'RewriteCond %{THE_REQUEST} \\s/+((?:[^?\\s]*/)?)index\\.html[?\\s]\n'
    + 'RewriteRule ^ /%1 [R=301,L,NE]\n'
    + '</IfModule>\n';
}
