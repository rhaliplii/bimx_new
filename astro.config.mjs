// @ts-check
import { defineConfig } from 'astro/config';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeSearchIndex } from './src/lib/search.mjs';
import { writeMissingPdfs } from './src/lib/news-pdf.mjs';
import { writeMissingGuidePdfs } from './src/lib/pdf.mjs';
import { checkSite } from './src/lib/checks.mjs';

// After the build: the search index (src/lib/search.mjs), PDFs of new press releases and guides (news-pdf.mjs, pdf.mjs),
// the link checks (checks.mjs), and pages that are files rather than directories (e.g. academy/programe/x/lesson.html) are emitted by Astro as
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
        const [gMade, gMissing] = await writeMissingGuidePdfs(root);
        if (gMissing) console.log(`Academy guide PDFs: ${gMade} of ${gMissing} printed` + (gMade < gMissing ? ' (Chrome missing or failed: set CHROME=…)' : ''));
        // on GitHub Actions a missing PDF must not be published as a broken button (or delete a published PDF)
        if (process.env.CI && (made < missing || gMade < gMissing)) throw new Error('PDFs could not be printed (Chrome missing or failed)');
        const { problems, summary } = checkSite(root);
        console.log(summary);
        if (problems.length) throw new Error('Site check failed:\n  ' + problems.join('\n  '));
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
