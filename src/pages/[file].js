// Files at the site root built from the page list: sitemap.xml, robots.txt and the Apache .htaccess.
import { pages, redirects, shell } from '../lib/site.mjs';
import { TEST_COPY, htaccess, robotsTxt, sitemapXml } from '../lib/seo.mjs';

// the test copy (BIMX_MIRROR=1) has no sitemap
const FILES = {
  ...(TEST_COPY ? {} : { 'sitemap.xml': () => sitemapXml(pages, shell.seoIndex) }),
  'robots.txt': () => robotsTxt(),
  '.htaccess': () => htaccess(redirects),
};

export function getStaticPaths() {
  return Object.keys(FILES).map((file) => ({ params: { file } }));
}

export function GET({ params }) {
  return new Response(FILES[params.file]());
}
