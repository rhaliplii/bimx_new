// @ts-check
import { defineConfig } from 'astro/config';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeSearchIndex } from './src/lib/search.mjs';
import { writeMissingPdfs } from './src/lib/news-pdf.mjs';

// After the build: the search index (src/lib/search.mjs), PDFs of new press releases (src/lib/news-pdf.mjs), and pages that are files rather than directories (e.g. academy/programe/x/lesson.html) are emitted by Astro as
// lesson.html/index.html; move them to their real address after the build.
function filePages() {
  return {
    name: 'bimx-file-pages',
    hooks: {
      'astro:build:done': async ({ dir }) => {
        const root = fileURLToPath(dir);
        const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).forEach((e) => {
          const p = path.join(d, e.name);
          if (!e.isDirectory()) return;
          if (e.name.endsWith('.html')) {
            const tmp = p + '.tmp';
            fs.renameSync(path.join(p, 'index.html'), tmp);
            fs.rmSync(p, { recursive: true });
            fs.renameSync(tmp, p);
          } else walk(p);
        });
        walk(root);
        const counts = writeSearchIndex(root);
        console.log(`search index: ${Object.entries(counts).map(([l, n]) => `${n} ${l.toUpperCase()}`).join(', ')}`);
        const texts = JSON.parse(fs.readFileSync('src/data/news-texts.json', 'utf8'));
        const [made, missing] = await writeMissingPdfs(root, texts);
        if (missing) console.log(`press release PDFs: ${made} of ${missing} printed` + (made < missing ? ' (Chrome missing or failed: set CHROME=…)' : ''));
      },
    },
  };
}

// Static site for bimx.md. Pages keep the exact URLs of the previous generator (directory-style, relative links).
export default defineConfig({
  site: 'https://bimx.md',
  output: 'static',
  trailingSlash: 'ignore',
  compressHTML: false,
  build: { format: 'directory', inlineStylesheets: 'never' },
  devToolbar: { enabled: false },
  integrations: [filePages()],
});
