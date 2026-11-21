// Printing pages to PDF with Chrome headless (press releases, Academy guides). Chrome is found on the PATH, in the usual
// macOS locations, or through the CHROME environment variable. Without Chrome the build still works, it just prints nothing.
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const CANDIDATES = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium'];

export function findChrome() {
  for (const c of [process.env.CHROME, ...CANDIDATES].filter(Boolean)) {
    if (c.includes('/')) { if (fs.existsSync(c)) return c; continue; }
    try { return execFileSync('which', [c], { encoding: 'utf8' }).trim() || null; } catch { /* not installed */ }
  }
  return null;
}

/** Print an HTML file to PDF; resolves to true when a real PDF was written. */
export function printPdf(chrome, htmlFile, pdfFile) {
  return new Promise((resolve) => {
    const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bimx-chrome-'));
    const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-sandbox', '--no-first-run', '--hide-scrollbars', `--user-data-dir=${profile}`,
      '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=8000', `--print-to-pdf=${pdfFile}`,
      pathToFileURL(htmlFile).href], { stdio: 'ignore' });
    const timer = setTimeout(() => proc.kill(), 90_000);
    proc.on('exit', () => {
      clearTimeout(timer);
      fs.rmSync(profile, { recursive: true, force: true });
      resolve(fs.existsSync(pdfFile) && fs.statSync(pdfFile).size > 10_000);
    });
  });
}


/** Academy guides: print academy/publicatii/<guide>.pdf from the built guide page when the PDF is not in public/. */
export async function writeMissingGuidePdfs(distDir, root = process.cwd()) {
  const catalog = JSON.parse(fs.readFileSync(path.join(root, 'src/content/academy/catalog.json'), 'utf8'));
  const jobs = [];
  for (const prefix of ['', 'en/', 'uk/', 'ru/']) {
    for (const pub of catalog.publications) {
      const rel = `${prefix}academy/publicatii/${pub.slug}.pdf`;
      if (!fs.existsSync(path.join(root, 'public', rel))) jobs.push([path.join(distDir, rel.replace(/\.pdf$/, '.html')), path.join(distDir, rel)]);
    }
  }
  if (!jobs.length) return [0, 0];
  const chrome = findChrome();
  if (!chrome) return [0, jobs.length];
  let made = 0;
  for (const [html, pdf] of jobs) if (fs.existsSync(html) && (await printPdf(chrome, html, pdf))) made++;
  return [made, jobs.length];
}
