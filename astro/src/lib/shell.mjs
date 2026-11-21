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
import { LANG_PREFIX, link } from './links.mjs';
import { buildMenu } from './menu.mjs';
import { seoBlock } from './seo.mjs';

export function altTarget(page, lang) {
  return '/' + LANG_PREFIX[lang] + page.inner;
}

const FIELD = /\{\{(u|alt):([^}]*)\}\}|\{\{(home|menu|title|description|seo|bodyAttrs|wpPost|wpContainer)\}\}/g;

/** Fill the placeholders of a shell template for a page. */
export function fill(template, page, ctx) {
  return template.replace(FIELD, (_, kind, arg, field) => {
    if (kind === 'u') return link(page.route, arg);
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
