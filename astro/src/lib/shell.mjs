// Page shell: the parts every page shares (head, header, footer, scripts), stored as HTML templates per language
// in src/shell/<lang>/ with a few placeholders:
//
//   {{u:/abs/path}}   relative link from the current page to an absolute site path
//   {{alt:xx}}        the same page in language xx (language switchers)
//   {{home}}          aria-current="page" on the logo of the home page
//   {{menu}}          main menu (src/lib/menu.mjs)
//   {{title}} {{description}} {{seo}} {{wpPost}} {{wpContainer}}   page fields
//
// The same functions are used by the import script (round-trip check) and by the Astro page.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { LANG_PREFIX, link } from './links.mjs';
import { buildMenu } from './menu.mjs';
import { seoBlock } from './seo.mjs';

// Own CSS and JS files carry their content hash in the address (site.css?v=…), so browsers never mix an old cached
// file with new pages. The hash is recomputed from public/ at build time.
const PUBLIC = path.resolve(process.cwd(), 'public');
const versions = new Map();
function versioned(abs) {
  const m = /^([^?#]+\.(?:css|js))\?v=[0-9a-f]+$/.exec(abs);
  if (!m) return abs;
  if (!versions.has(m[1])) {
    const file = path.join(PUBLIC, m[1]);
    versions.set(m[1], fs.existsSync(file) ? crypto.createHash('md5').update(fs.readFileSync(file)).digest('hex').slice(0, 10) : null);
  }
  const v = versions.get(m[1]);
  return v ? `${m[1]}?v=${v}` : abs;
}

export function altTarget(page, lang) {
  return '/' + LANG_PREFIX[lang] + page.inner;
}

const FIELD = /\{\{(u|alt):([^}]*)\}\}|\{\{(home|menu|title|description|seo|bodyAttrs|wpPost|wpContainer)\}\}/g;

/** Fill the placeholders of a shell template for a page. */
export function fill(template, page, ctx) {
  return template.replace(FIELD, (_, kind, arg, field) => {
    if (kind === 'u') return link(page.route, versioned(arg));
    if (kind === 'alt') return link(page.route, altTarget(page, arg));
    switch (field) {
      // 404.html is built from the home page and keeps its logo state
      case 'home': return page.inner === '' || page.inner === '404.html' ? ' aria-current="page"' : '';
      case 'menu': return buildMenu(page, ctx.menu);
      case 'seo': return seoBlock(page, ctx.seoIndex);
      case 'wpPost': return page.wpPost ? `-p${page.wpPost}` : '';
      case 'wpContainer': return page.wpContainer || '0';
      default: return page[field] ?? '';
    }
  });
}

/** Whole HTML document of a page. */
export function renderPage(page, shell) {
  const t = (seg) => {
    const tpl = shell.templates[`${page.lang}/${page.parts[seg]}`];
    if (tpl === undefined) throw new Error(`Missing shell template ${page.lang}/${page.parts[seg]} for ${page.route}`);
    return fill(tpl, page, { menu: shell.menu[page.lang], seoIndex: shell.seoIndex });
  };
  return t('open') + t('head') + '</head>' + t('mid') + '<body' + page.bodyAttrs + '>' + t('pre')
    + t('header') + page.body + t('footer') + t('tail');
}
