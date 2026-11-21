// Publish the current main on bimx.md: create the next release tag (vYYYY.MM.DD, then .2, .3 … the same day) on
// origin/main and push it. The Deploy workflow then builds that commit and publishes it.
//
//   npm run release            # tag origin/main
//   npm run release -- --dry   # only show what would be tagged
import { execFileSync } from 'node:child_process';

const git = (...args) => execFileSync('git', args, { encoding: 'utf8' }).trim();
const dry = process.argv.includes('--dry');

git('fetch', '--tags', 'origin', 'main');
const commit = git('rev-parse', 'origin/main');
const subject = git('log', '-1', '--format=%s', commit);
const already = git('tag', '--points-at', commit).split('\n').filter((t) => /^v\d{4}\.\d{2}\.\d{2}/.test(t));
if (already.length) {
  console.log(`origin/main (${commit.slice(0, 7)}) is already released as ${already.join(', ')}.`);
  console.log('To publish it again (e.g. after a failed deploy), re-run the Deploy workflow for that tag on GitHub.');
  process.exit(0);
}
const d = new Date();
const day = `v${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
const taken = new Set(git('tag', '--list', `${day}*`).split('\n').filter(Boolean));
let tag = day;
for (let n = 2; taken.has(tag); n++) tag = `${day}.${n}`;

console.log(`${dry ? 'Would tag' : 'Tagging'} ${commit.slice(0, 7)} "${subject}" as ${tag}`);
if (dry) process.exit(0);
git('tag', '-a', tag, commit, '-m', `Release ${tag}: ${subject}`);
git('push', 'origin', tag);
console.log(`Pushed ${tag}. Follow the publication in GitHub → Actions → Deploy.`);
