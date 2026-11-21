// Old addresses kept as small redirect pages (on the server they are also 301 redirects in .htaccess).
// Most use the plain page below; the redirects created for BIMx Academy also load the site scripts, from a
// template in src/shell/<lang>/redirect.html with {{to}}, {{canonical}} and {{u:/path}} placeholders.
import { link, splitLang } from './links.mjs';

export const LOCALE = { ro: 'ro-RO', en: 'en-GB', uk: 'uk-UA', ru: 'ru-RU' };
export const SITE_URL = 'https://bimx.md';

/** Redirect page for `route` pointing to the absolute site path `to` (may carry a #fragment). */
export function renderRedirect(route, to, template) {
  const url = link(route, to);
  const canonical = SITE_URL + to.split('#')[0];
  if (template) {
    return template.replace(/\{\{(?:u:([^}]*)|(to|canonical))\}\}/g, (_, abs, f) => (abs ? link(route, abs) : f === 'to' ? url : canonical));
  }
  return `<!doctype html>\n<html lang="${LOCALE[splitLang(route).lang]}"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=${url}">`
    + `<title>BIMx</title><link rel="canonical" href="${canonical}"></head><body><a href="${url}">BIMx</a></body></html>\n`;
}
