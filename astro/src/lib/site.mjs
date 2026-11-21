// Loads the site sources for the Astro build: page bodies with their fields, shell templates and menus.
// BIMx Academy pages are not files in src/content/pages: they are generated from src/content/academy (academy.mjs).
import { splitLang } from './links.mjs';
import { seoIndex } from './seo.mjs';
import { academyPages } from './academy.mjs';

const pageFiles = import.meta.glob('/src/content/pages/**/*.html', { query: '?raw', import: 'default', eager: true });
const shellFiles = import.meta.glob('/src/shell/**/*.html', { query: '?raw', import: 'default', eager: true });
const menuFiles = import.meta.glob('/src/shell/*/menu.json', { import: 'default', eager: true });
import redirectList from '../data/redirect-pages.json';

/** Front matter: one `key: <JSON>` per line between --- lines, then the page body. */
export function parsePage(raw) {
  const m = /^---\n([\s\S]*?)\n---\n/.exec(raw);
  if (!m) throw new Error('Page without front matter');
  const fields = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(': ');
    fields[line.slice(0, i)] = JSON.parse(line.slice(i + 2));
  }
  return { ...fields, body: raw.slice(m[0].length) };
}

export const pages = [
  ...Object.values(pageFiles).map((raw) => {
    const p = parsePage(raw);
    return { ...p, ...splitLang(p.route) };
  }),
  ...academyPages(),
];

export const shell = {
  templates: Object.fromEntries(Object.entries(shellFiles).map(([f, t]) => [f.replace('/src/shell/', '').replace(/\.html$/, ''), t])),
  menu: Object.fromEntries(Object.entries(menuFiles).map(([f, m]) => [f.split('/')[3], m])),
};

shell.seoIndex = seoIndex(pages);

export const redirects = redirectList;
