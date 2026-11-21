# bimx.md on Astro

The bimx.md site (4 languages: RO at the root, `/en/`, `/uk/`, `/ru/`) and BIMx Academy, built as a static site with
[Astro](https://astro.build). The output in `dist/` is plain HTML/CSS/JS for the existing Hostinger hosting.

```
npm install
npm run dev        # http://localhost:4321/ — live preview while editing
npm run build      # dist/ — the site to publish (Chrome is used to print PDFs of new press releases)
```

## Where to change what

| What | Where |
|---|---|
| **A new press release** | a new folder in `src/content/news/` (see below) |
| Text of a press release | `src/content/news/<date>-<name>/ro.html`, `en.html`, `uk.html`, `ru.html` |
| News categories | `src/content/news/categories.json` |
| Texts of the news pages (tabs, labels, “About BIMx”) | `src/data/news-texts.json` |
| An Academy lesson, course or guide | `src/content/academy/content/<lang>/*.json`, `catalog.json`, `i18n/<lang>.json` |
| The main menu | `src/lib/menu.mjs` (labels in 4 languages + menu structure) |
| Header, footer, `<head>` of the pages | `src/shell/<lang>/*.html` (one template per language; see below) |
| Content of a regular page | `src/content/pages/<lang>/<page>/index.html` |
| Styles and scripts | `public/assets/css/site.css`, `public/assets/js/*.js`, `public/wp-content/…` (WordPress theme) |
| Images, PDFs, downloads | `public/` (published as they are, at the same address) |
| Old addresses that redirect | `src/data/redirect-pages.json` |

## Adding a press release

1. Create `src/content/news/2026-12-05-short-name/news.json`:

   ```json
   {
     "path": "2026/12/05/short-name",
     "date": "2026-12-05",
     "section": "bimx",
     "category": "listare",
     "title":   { "ro": "…", "en": "…", "uk": "…", "ru": "…" },
     "summary": { "ro": "…", "en": "…", "uk": "…", "ru": "…" }
   }
   ```

   - `path` is the page address (`https://bimx.md/2026/12/05/short-name/`).
   - `section`: `bimx` (BIMx announcements), `avize` (market notices) or `emitenti` (issuer announcements).
   - `category`: one of the keys in `categories.json` (`parteneriat`, `evenimente`, `admitere`, `licenta`, `actionari`, `listare`).
   - `summary`: one or two sentences, shown under the title and in the lists.
   - Optional: `description` (for search engines; otherwise the first paragraph), `cardTitle` (shorter title for lists and
     the home page), `crumb` (breadcrumb), `homeExcerpt` (text on the home page), `photo`.

2. Add the text in four files next to it: `ro.html`, `en.html`, `uk.html`, `ru.html` — paragraphs, lists, tables in HTML.
   Links and images inside the site are written from the root: `<a href="/procesul-de-listare/">`, `<img src="/assets/img/news/x.webp">`.

3. `npm run build`. The press release gets its page in 4 languages, appears first on the home page, in the news lists
   and filters, in “related press releases”, in the sitemap and in the site search, and its PDF is printed.

If the build stops with an error, it says which file and field is wrong (for example a missing translation).

## How the site is built

- **Every page = shell + body.** The parts shared by all pages (head, header, footer, scripts) are templates in
  `src/shell/<lang>/` with placeholders: `{{u:/path/}}` (link to a page, written relative on output), `{{alt:en}}`
  (same page in another language), `{{menu}}`, `{{title}}`… The page body and fields (title, description) are in
  `src/content/pages/` or are generated (news, Academy). `src/lib/shell.mjs` puts them together.
- **Generated from data:** press releases, news lists, the news on the home page (`src/lib/news.mjs`), Academy pages
  (`src/lib/academy.mjs`), the menu (`src/lib/menu.mjs`), SEO tags, `sitemap.xml`, `robots.txt`, `.htaccess`
  (`src/lib/seo.mjs`), redirect pages, the search index and the `?v=` versions of CSS/JS files (after the build:
  `src/lib/search.mjs`), PDFs of new press releases (`src/lib/news-pdf.mjs`).
- **Links stay relative** (`../identitate/`), so the site also works from a sub-folder or a test copy.

## Checking against the old site

During the migration from the Python generator (`../tools/`), the Astro build was compared file by file with the
old output: `npm run build && node scripts/compare.mjs <old-dist>`. All 774 files are identical.
`scripts/import-baseline.mjs` and `scripts/extract-news.mjs` were one-off import scripts; do not run them again
(they would overwrite edited content).

Known issues kept from the old site (to fix separately): the og:url of two RO Academy pages is broken by the
“broker → agent de bursă” rename (`seoRaw` in `academy.mjs`); the RO Academy home has the card title “Agenți de bursă și
agenți de bursă”; the description of the press release of 30.10.2026 starts with a lowercase fragment.
