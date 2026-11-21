// Compares the Astro build (dist/) with the site built by the previous generator.
//
//   node scripts/compare.mjs [baseline-dist] [--show N]
//
// HTML is compared byte for byte; pages that differ are compared again after parsing and re-serializing both
// sides (attribute quotes, whitespace between tags, ?v= cache hashes ignored) and reported with the first difference.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { parse, serialize } from 'parse5';

const args = process.argv.slice(2);
const showIdx = args.indexOf('--show');
const SHOW = showIdx >= 0 ? Number(args.splice(showIdx, 2)[1]) : 10;
const BASE = path.resolve(args[0] || '../../baseline-dist');
const DIST = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../dist');

const walk = (dir, root = dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(dir, e.name);
  return e.isDirectory() ? walk(p, root) : [path.relative(root, p).split(path.sep).join('/')];
});
const hash = (f) => crypto.createHash('sha1').update(fs.readFileSync(f)).digest('hex');
const normalize = (html) => serialize(parse(html.replace(/\?v=[0-9a-f]{6,}/g, '?v=H')))
  .replace(/>\s+</g, '><').replace(/\s+/g, ' ');

const a = new Set(walk(BASE).filter((f) => !f.endsWith('.DS_Store')));
const b = new Set(walk(DIST).filter((f) => !f.endsWith('.DS_Store')));
const missing = [...a].filter((f) => !b.has(f));
const extra = [...b].filter((f) => !a.has(f));
let same = 0, normSame = 0;
const diffs = [];
for (const f of [...a].filter((f) => b.has(f)).sort()) {
  const fa = path.join(BASE, f), fb = path.join(DIST, f);
  if (hash(fa) === hash(fb)) { same++; continue; }
  if (/\.(html|xml|txt|htaccess)$/.test(f) || f.endsWith('.htaccess')) {
    const na = normalize(fs.readFileSync(fa, 'utf8')), nb = normalize(fs.readFileSync(fb, 'utf8'));
    if (na === nb) { normSame++; continue; }
    let k = 0;
    while (na[k] === nb[k]) k++;
    diffs.push({ f, at: k, exp: na.slice(Math.max(0, k - 60), k + 120), got: nb.slice(Math.max(0, k - 60), k + 120) });
  } else diffs.push({ f, binary: true });
}
console.log(`files: baseline ${a.size}, astro ${b.size}; identical ${same}, equal after normalizing ${normSame}, different ${diffs.length}, missing ${missing.length}, extra ${extra.length}`);
if (missing.length) console.log('missing:', missing.slice(0, SHOW).join(' '), missing.length > SHOW ? `… +${missing.length - SHOW}` : '');
if (extra.length) console.log('extra:', extra.slice(0, SHOW).join(' '), extra.length > SHOW ? `… +${extra.length - SHOW}` : '');
for (const d of diffs.slice(0, SHOW)) {
  if (d.binary) console.log(`differs (binary): ${d.f}`);
  else console.log(`differs: ${d.f} @${d.at}\n  baseline: ${JSON.stringify(d.exp)}\n  astro:    ${JSON.stringify(d.got)}`);
}
if (diffs.length > SHOW) console.log(`… +${diffs.length - SHOW} more`);
process.exitCode = diffs.length || missing.length || extra.length ? 1 : 0;
