# bimx.md — notes for Claude

Static site of the Moldova International Stock Exchange (BIMx) and BIMx Academy, built with Astro. Four languages:
Romanian at the root (the original), `/en/`, `/uk/`, `/ru/` (translated). Output `dist/` = plain files for Hostinger.
Read `README.md` for the structure; this file lists the rules.

## Commands

- `npm run dev` — preview at http://localhost:4321/
- `npm run build` — builds `dist/` and runs every check (news and Academy data, links, sitemap). **Run it before every
  commit**; a failing build names the file and the problem.
- `npm run release` — publishes the current `origin/main` on bimx.md (creates the tag `vYYYY.MM.DD`). Only when the
  user asks to publish. Pushing to `main` publishes only on the password-protected staging copy.

## Common tasks

- **New press release:** a folder `src/content/news/<YYYY-MM-DD>-<short-name>/` with `news.json` and `ro.html`, `en.html`,
  `uk.html`, `ru.html` (see README "Adding a press release" and an existing folder). Required: `path`, `date`, `section`,
  `category`, `title` and `summary` in all four languages, and the four text files. Links inside the text are written
  from the site root (`/procesul-de-listare/`), never `https://bimx.md/…` (the build rejects those).
  The PDF is printed by the build; nothing to do.
- **Change a published press release:** edit its files. If the text changed, delete its PDFs from
  `public/<lang prefix>2026/…/<name>/BIMx-*.pdf` so they are printed again.
- **Academy lesson:** `src/content/academy/content/<lang>/NN-*.json` — same slugs and order in every language; lesson text
  allows only `<strong>` and `<em>`; each lesson has a definition and an example callout and a 3-question quiz.
- **Menu:** `src/lib/menu.mjs`. **Header/footer/head:** `src/shell/<lang>/*.html` (change all four languages).
- **Regular page:** `src/content/pages/<lang>/<page>/index.html` — one file per language; change all four.

## Rules

- Never edit `dist/`. Static files (images, PDFs, CSS, JS) live in `public/` at their published address.
- Every visible text exists in RO, EN, UK and RU. Romanian uses comma-below letters (ș, ț), not cedillas (ş, ţ).
  Ukrainian text must not contain Russian letters (ы, э, ъ, ё).
- On Romanian pages the term is "agent de bursă", not "broker".
- Keep page addresses stable: a renamed page needs an entry in `src/data/redirect-pages.json` (it also becomes a 301
  in `.htaccess`).
- Links between pages stay relative (the build writes them); templates use `{{u:/path/}}`, news texts use `/path/`.
- `scripts/compare.mjs <other-dist>` compares two builds file by file: use it to prove that a refactoring does not
  change the pages.
- Commit messages: what changed for the visitor, in the language the user writes in.
