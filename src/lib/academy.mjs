// BIMx Academy pages, generated from the Academy data (ported from tools/sitegen/academy.py).
//
// Where to change what (all under src/content/academy/):
//   content/<lang>/NN-<program>.json   a program: its courses, lessons (sections, takeaways, quiz)
//   catalog.json                       Academy home: direction icons and tags, the course cards, the guides
//                                      ("publications": a guide = a whole program or one course of it)
//   i18n/<lang>.json                   interface texts (buttons, labels, plural forms)
//   templates/index.<lang>.html        Academy home page; the parts between <!-- BUILD:x:START/END --> are generated
// Styles, scripts, images and the guide PDFs are static files in public/academy/ and public/<lang>/academy/.
//
// Routes: academy/ (home), academy/programe/<program>/ (program), academy/programe/<program>/<lesson>.html,
// academy/publicatii/<guide>.html; the same under en/, uk/, ru/. Every language has the same programs and
// lessons (same slugs, same order) as the Romanian content.
//
// Lesson block types ("p", "list", "steps", "callout", "table", "formula"): renderBlock(). Lesson and guide text is
// escaped; only <strong> and <em> are allowed in it. On every page, as on the rest of the site: heading levels get
// aria-level where a level is skipped, and the Romanian pages say "agent de bursă" instead of "broker".
//
// The pages are page objects like the ones in src/content/pages (route, parts, title, description, bodyAttrs, body):
// the shared shell (head, header, footer, scripts) comes from src/shell/<lang>/.
import { LANGS, LANG_PREFIX, link, splitLang } from './links.mjs';
import { escapeHtml as esc, unescapeHtml } from './seo.mjs';

// ---------------------------------------------------------------- data

/** Academy data from src/content/academy/ (read by Vite at build time). */
function academySources() {
  const programFiles = import.meta.glob('/src/content/academy/content/*/*.json', { import: 'default', eager: true });
  const i18nFiles = import.meta.glob('/src/content/academy/i18n/*.json', { import: 'default', eager: true });
  const templateFiles = import.meta.glob('/src/content/academy/templates/index.*.html', { query: '?raw', import: 'default', eager: true });
  const catalog = import.meta.glob('/src/content/academy/catalog.json', { import: 'default', eager: true })['/src/content/academy/catalog.json'];
  const programs = {};
  // programs in file name order (01-…, 02-…): the order of the directions everywhere
  for (const file of Object.keys(programFiles).sort()) (programs[file.split('/')[5]] ??= []).push(programFiles[file]);
  const byLang = (files) => Object.fromEntries(Object.entries(files).map(([f, v]) => [f.split('/').pop().split('.').at(-2), v]));
  return { programs, catalog, i18n: byLang(i18nFiles), templates: byLang(templateFiles) };
}

// ---------------------------------------------------------------- small helpers

/** Text from the lesson files: escaped, but <strong> and <em> stay as tags. */
function rich(text) {
  let out = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  for (const tag of ['strong', 'em']) out = out.split(`&lt;${tag}&gt;`).join(`<${tag}>`).split(`&lt;/${tag}&gt;`).join(`</${tag}>`);
  return out;
}

/** Section anchors: "Ce este o acțiune?" → "ce-este-o-actiune". */
function slugify(text) {
  return text.normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

/** "1 lecție / 5 lecții"; Russian and Ukrainian have three forms [one, few, many]. */
function plural(n, forms) {
  if (forms.length === 3) {
    const [one, few, many] = forms;
    const word = n % 10 === 1 && n % 100 !== 11 ? one : n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14) ? few : many;
    return `${n} ${word}`;
  }
  return `${n} ${n === 1 ? forms[0] : forms[1]}`;
}

const lessonsOf = (program) => program.courses.flatMap((course) => course.lessons.map((lesson) => [course, lesson]));
const totalMinutes = (lessons) => lessons.reduce((sum, [, lesson]) => sum + lesson.minutes, 0);
const pad2 = (n) => String(n).padStart(2, '0');
const format = (s, values) => s.replace(/\{(\w+)\}/g, (_, k) => values[k]);

function duration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (!h) return `${m} min`;
  return m ? `${h} h ${m} min` : `${h} h`;
}

/**
 * A https://bimx.md/... address as a site path in the page's language ("https://bimx.md/fondatori/" → "/en/fondatori/").
 * Used for the "Home" crumb (i18n home_crumb) and the bimx.md links in the home templates. The target page must
 * exist on this site (the old generator kept the bimx.md address when it did not); query and fragment are dropped.
 */
function localPath(lang, url) {
  let path = url.slice('https://bimx.md'.length).split('#')[0].split('?')[0];
  if (['/en', '/en/', '/en/home/'].includes(path)) path = '/en/';
  const prefixed = LANGS.slice(1).some((x) => path.startsWith(`/${x}/`));
  if (lang !== 'ro' && !prefixed) path = `/${lang}${path}`;
  else if (lang !== 'ro' && lang !== 'en' && path.startsWith('/en/')) path = `/${lang}/${path.slice(4)}`;
  return path;
}

// ---------------------------------------------------------------- icons

const ARROW = '<svg width="16" height="16" viewBox="0 0 17 17" fill="none"><path d="M3.5 8.4h9.8M8.4 3.5l4.9 4.9-4.9 4.9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ARROW_LEFT = '<svg width="16" height="16" viewBox="0 0 17 17" fill="none"><path d="M13.3 8.4H3.5M8.4 3.5L3.5 8.4l4.9 4.9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const CRUMB = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.25 10.5L8.75 7L5.25 3.5" stroke="white" stroke-opacity=".6" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const CHECK = '<svg viewBox="0 0 16 16" fill="none"><path d="M4 8.3l2.6 2.6L12 5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_CLOCK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';
const ICON_BOOK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20V3H6.5A2.5 2.5 0 004 5.5v14z"/><path d="M4 19.5A2.5 2.5 0 006.5 22H20v-5"/></svg>';
const ICON_LAYERS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l10 5-10 5L2 7l10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>';
const ICON_USER = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/></svg>';
const ICON_BAR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 20v-6M12 20V10M18 20V4"/></svg>';
const ICON_INFO = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>';
const ICON_DOWNLOAD = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>';

const CALLOUT_ICONS = {
  definition: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20V3H6.5A2.5 2.5 0 004 5.5v14z"/></svg>',
  example: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M9 6h6M9 11h.01M12 11h.01M15 11h.01M9 15h.01M12 15h.01M15 15h.01M9 18h6"/></svg>',
  tip: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 00-4 12.7V17h8v-2.3A7 7 0 0012 2z"/></svg>',
  warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>',
};

const statusIcon = () => `<span class="check_mark" aria-hidden="true">${CHECK}</span>`;

// ---------------------------------------------------------------- page context

/** The page being generated: its route and language; `u()` links from it to an absolute site path. */
function context(src, lang, inner) {
  const route = LANG_PREFIX[lang] + 'academy/' + inner;
  const academy = '/' + LANG_PREFIX[lang] + 'academy/';
  const t = src.i18n[lang];
  const u = (target) => link(route, target);
  return {
    src, lang, route, t, u,
    academy,                                              // "/en/academy/"
    home: u(academy),                                     // link to the Academy home
    asset: (path) => u('/academy/assets/' + path),        // Academy assets are shared by all languages
    crumbHome: [t.home_crumb[0], u(localPath(lang, t.home_crumb[1]))],
  };
}

function breadcrumbs(items) {
  return '<ul class="breadcrumbs">' + items.map(([label, href]) => (href
    ? `<li><a href="${href}">${esc(label)}</a>${CRUMB}</li>`
    : `<li><span>${esc(label)}</span></li>`)).join('') + '</ul>';
}

/** Body of an Academy page (between the site header and footer); read_progress = the reading bar at the top. */
function frame(main, readProgress = false) {
  const progress = readProgress ? '<div class="read_progress" aria-hidden="true"><i></i></div>' : '';
  return `\n\n<main id="top" class="bx-academy">\n${progress}\n${main}\n</main>\n\n`;
}

const bodyData = (data) => ' class="bx-academy-page" ' + Object.entries(data).map(([k, v]) => `data-${k}="${esc(String(v))}"`).join(' ');

// ---------------------------------------------------------------- lesson blocks

/** One content block of a lesson section ("type" in the lesson JSON). */
function renderBlock(b, t) {
  switch (b.type) {
    case 'p':
      return `<p>${rich(b.text)}</p>`;
    case 'list':
      return '<ul class="bullets">' + b.items.map((i) => `<li>${rich(i)}</li>`).join('') + '</ul>';
    case 'steps':
      return '<ol class="steps_list">' + b.items.map((i) => `<li><div><b>${rich(i.title)}</b><span>${rich(i.text)}</span></div></li>`).join('') + '</ol>';
    case 'callout': {
      const variant = CALLOUT_ICONS[b.variant ?? 'tip'] ? (b.variant ?? 'tip') : 'tip';
      const title = b.title ? `<h5>${rich(b.title)}</h5>` : '';
      return `<aside class="callout ${variant}"><div class="ci">${CALLOUT_ICONS[variant]}</div>`
        + `<div><span class="ct">${t.callouts[variant]}</span>${title}<p>${rich(b.text)}</p></div></aside>`;
    }
    case 'table': {
      const head = b.headers.map((h) => `<th>${rich(h)}</th>`).join('');
      const rows = b.rows.map((row) => '<tr>' + row.map((c) => `<td>${rich(c)}</td>`).join('') + '</tr>').join('');
      return `<div class="table_wrap"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
    }
    case 'formula': {
      const note = b.note ? `<div class="fn">${rich(b.note)}</div>` : '';
      return `<div class="formula"><div class="fl">${rich(b.label ?? 'Formula')}</div><div class="fe">${rich(b.expr)}</div>${note}</div>`;
    }
    default:
      throw new Error(`Unknown lesson block type: ${b.type}`);
  }
}

// ---------------------------------------------------------------- program page

function programPage(src, lang, program, programs) {
  const slug = program.slug;
  const c = context(src, lang, `programe/${slug}/`);
  const { t, home } = c;
  const lessons = lessonsOf(program);
  const first = lessons[0][1];
  const minutes = totalMinutes(lessons);

  let n = 0;
  const courseBlocks = program.courses.map((course) => {
    const rows = course.lessons.map((lesson) => {
      n++;
      return `<li><a class="lesson_row" href="${lesson.slug}.html" data-lesson-id="${slug}/${lesson.slug}">`
        + `<span class="n">${pad2(n)}</span>`
        + `<span><h4>${esc(lesson.title)}</h4><p>${rich(lesson.summary)}</p></span>`
        + `<span class="min">${lesson.minutes} min</span>${statusIcon()}</a></li>`;
    });
    const courseMin = totalMinutes(course.lessons.map((l) => [course, l]));
    return `<div class="course_block" id="${course.code}">
          <div class="cb_head">
            <div><span class="code">${esc(course.code)}</span><h3>${esc(course.title)}</h3><p>${rich(course.description)}</p></div>
            <div class="count"><b>${plural(course.lessons.length, t.lesson)}</b>${duration(courseMin)}</div>
          </div>
          <ol class="lesson_list">${rows.join('')}</ol>
        </div>`;
  });

  const others = programs.filter((p) => p.slug !== slug).map((other) =>
    `<a href="${c.u(`${c.academy}programe/${other.slug}/`)}"><span class="num">${t.track} ${other.num}</span>`
    + `<h4>${esc(other.title)}</h4><p>${esc(other.short)}</p>`
    + `<span class="link_arrow">${plural(lessonsOf(other).length, t.lesson)} ${ARROW}</span></a>`);

  const outcomes = program.outcomes.map((o) => `<li>${rich(o)}</li>`).join('');
  const main = `
  <div class="second_main_section compact">
    <div class="container">
      <div class="hero_grid">
        <div>
          ${breadcrumbs([c.crumbHome, ['BIMx Academy', home], [t.tracks, home + '#directii'], [program.title, null]])}
          <span class="label">${t.track} ${program.num} · ${esc(program.level)}</span>
          <h1>${esc(program.title)}</h1>
          <p class="lead">${rich(program.intro)}</p>
          <div class="meta_row">
            <span>${ICON_LAYERS}${plural(program.courses.length, t.course)}</span>
            <span>${ICON_BOOK}${plural(lessons.length, t.lesson)}</span>
            <span>${ICON_CLOCK}${duration(minutes)} ${t.reading}</span>
            <span>${ICON_USER}${esc(program.audience)}</span>
          </div>
          <div class="hero_buttons">
            <a href="${first.slug}.html" class="btn1" id="start-link">${t.start_first} ${ARROW}</a>
            <a href="#programa" class="btn2">${t.see_syllabus}</a>
          </div>
        </div>
        <aside class="hero_card">
          <div class="progress_card">
            <div class="ring" id="progress-ring">
              <svg width="120" height="120" viewBox="0 0 120 120"><circle class="track" cx="60" cy="60" r="52" fill="none" stroke-width="10"/><circle class="value" cx="60" cy="60" r="52" fill="none" stroke-width="10" stroke-linecap="round" style="stroke-dasharray:327;stroke-dashoffset:327"/></svg>
              <b id="progress-pct">0%</b>
            </div>
            <div>
              <h3>${t.your_progress}</h3>
              <p id="progress-count">0 ${format(t.of_done, { n: lessons.length })}</p>
              <button type="button" class="btn2" id="progress-reset">${t.reset}</button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="program_layout">
      <div>
        <h2 class="sub_title">${t.learn}</h2>
        <ul class="outcomes">${outcomes}</ul>

        <h2 class="sub_title" id="programa" style="scroll-margin-top:110px">${t.syllabus}</h2>
        ${courseBlocks.join('')}
      </div>

      <aside class="side_card">
        <h3>${t.about_program}</h3>
        <dl class="info_list">
          <div><dt>${t.level}</dt><dd>${esc(program.level)}</dd></div>
          <div><dt>${t.audience}</dt><dd>${esc(program.audience)}</dd></div>
          <div><dt>${t.courses}</dt><dd>${program.courses.length}</dd></div>
          <div><dt>${t.lessons}</dt><dd>${lessons.length}</dd></div>
          <div><dt>${t.est}</dt><dd>${duration(minutes)}</dd></div>
          <div><dt>${t.format}</dt><dd>${t.format_val}</dd></div>
        </dl>
        <p class="note"><strong>${t.req}</strong> ${rich(program.prerequisites)}</p>
        <a href="${first.slug}.html" class="btn1">${t.start_program} ${ARROW}</a>
      </aside>
    </div>
  </div>

  <section class="block_section" style="padding-top:72px;padding-bottom:0">
    <div class="container">
      <div class="head"><div><span class="label light">${t.keep_learning}</span><h2>${t.other_tracks}</h2></div></div>
      <div class="other_programs">${others.join('')}</div>
    </div>
  </section>
`;
  return {
    route: c.route, kind: 'program',
    title: `${program.title} – BIMx Academy`, description: program.short,
    bodyAttrs: bodyData({ program: slug, total: lessons.length }),
    body: frame(main),
  };
}

// ---------------------------------------------------------------- lesson page

function lessonPage(src, lang, program, index) {
  const slug = program.slug;
  const lessons = lessonsOf(program);
  const [course, lesson] = lessons[index];
  const c = context(src, lang, `programe/${slug}/${lesson.slug}.html`);
  const { t, home } = c;
  const total = lessons.length;
  const programHref = c.u(`${c.academy}programe/${slug}/`);

  // left column: all lessons of the program, grouped by course
  const groups = program.courses.map((crs) => {
    const links = crs.lessons.map((l) => {
      const current = l.slug === lesson.slug;
      return `<a href="${l.slug}.html" class="${current ? 'current' : ''}" data-lesson-id="${slug}/${l.slug}"${current ? ' aria-current="page"' : ''}>`
        + `${statusIcon()}<span>${esc(l.title)}</span></a>`;
    });
    return `<div class="group"><span>${esc(crs.code)} · ${esc(crs.title)}</span>${links.join('')}</div>`;
  });

  // sections with anchors (from the heading), and the "on this page" list
  const sections = [];
  const toc = [];
  const used = new Set();
  for (const s of lesson.sections) {
    let sid = slugify(s.heading) || 'sectiune';
    while (used.has(sid)) sid += '-2';
    used.add(sid);
    toc.push(`<a href="#${sid}">${esc(s.heading)}</a>`);
    sections.push(`<section id="${sid}"><h2>${rich(s.heading)}</h2>${s.blocks.map((b) => renderBlock(b, t)).join('')}</section>`);
  }
  toc.push(`<a href="#de-retinut">${t.takeaways}</a>`, `<a href="#quiz">${t.quiz}</a>`);

  const takeaways = lesson.takeaways.map((x) => `<li>${rich(x)}</li>`).join('');
  const questions = lesson.quiz.map((q, qi) => {
    const opts = q.options.map((o, oi) => `<label><input type="radio" name="q${qi}" value="${oi}"><span>${rich(o)}</span></label>`).join('');
    return `<div class="q" data-answer="${q.answer}"><fieldset>`
      + `<legend><small>${format(t.q_of, { i: qi + 1, n: lesson.quiz.length })}</small>${rich(q.q)}</legend>`
      + `<div class="opts">${opts}</div></fieldset>`
      + `<p class="expl"><strong>${t.explanation}</strong> ${rich(q.explanation)}</p></div>`;
  });

  const prev = index > 0 ? lessons[index - 1][1] : null;
  const next = index < total - 1 ? lessons[index + 1][1] : null;
  const prevLink = prev
    ? `<a href="${prev.slug}.html" class="prev"><span>${ARROW_LEFT} ${t.prev}</span><b>${esc(prev.title)}</b></a>`
    : `<a href="${programHref}" class="prev"><span>${ARROW_LEFT} ${t.back_program}</span><b>${esc(program.title)}</b></a>`;
  const nextLink = next
    ? `<a href="${next.slug}.html" class="next"><span>${t.next} ${ARROW}</span><b>${esc(next.title)}</b></a>`
    : `<a href="${programHref}" class="next"><span>${t.the_end} ${ARROW}</span><b>${t.back_syllabus}</b></a>`;

  const main = `
  <div class="second_main_section compact">
    <div class="container" style="position:relative;z-index:1">
      ${breadcrumbs([c.crumbHome, ['BIMx Academy', home], [program.title, programHref], [format(t.lesson_n, { i: index + 1 }), null]])}
      <span class="label">${esc(course.code)} · ${format(t.lesson_of, { i: index + 1, n: total })}</span>
      <h1>${esc(lesson.title)}</h1>
      <p class="lead">${rich(lesson.summary)}</p>
      <div class="meta_row" style="margin-bottom:0">
        <span>${ICON_CLOCK}${lesson.minutes} ${t.min_reading}</span>
        <span>${ICON_BAR}${esc(program.level)}</span>
        <span>${ICON_LAYERS}${esc(course.title)}</span>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="lesson_layout">
      <details class="lesson_nav" open>
        <summary>
          <span class="ln_title">${t.program_content}</span>
          <span class="ln_program">${esc(program.title)}</span>
          <div class="mini_bar" id="mini-bar"><i></i></div>
          <div class="mini_label"><span id="mini-count">0/${total} ${t.lesson[1]}</span><span id="mini-pct">0%</span></div>
        </summary>
        <a href="${programHref}" class="ln_back">${ARROW_LEFT} ${t.back_program}</a>
        ${groups.join('')}
      </details>

      <article class="lesson_content">
        ${sections.join('')}

        <div class="takeaways" id="de-retinut" style="scroll-margin-top:110px">
          <h2>${t.takeaways}</h2>
          <ul>${takeaways}</ul>
        </div>

        <div class="quiz" id="quiz">
          <h2>${t.quiz}</h2>
          <p class="quiz_sub">${t.quiz_sub}</p>
          ${questions.join('')}
          <div class="quiz_actions">
            <span class="quiz_result" id="quiz-result" role="status" aria-live="polite"></span>
            <div>
              <button type="button" class="btn1" id="quiz-check">${t.check}</button>
              <button type="button" class="btn3" id="quiz-retry" hidden>${t.retry}</button>
            </div>
          </div>
        </div>

        <div class="complete_bar">
          <p><b>${t.done_q}</b>${t.done_p}</p>
          <button type="button" class="btn1 complete_btn" id="complete-btn">${CHECK.replace('<svg ', '<svg width="16" height="16" ')}<span>${t.mark_done}</span></button>
        </div>

        <nav class="pager" aria-label="${t.pager}">${prevLink}${nextLink}</nav>

        <p class="disclaimer">
          ${ICON_INFO}
          <span>${t.disclaimer}</span>
        </p>
      </article>

      <aside class="toc" aria-label="${t.on_page}">
        <h4>${t.on_page}</h4>
        ${toc.join('')}
      </aside>
    </div>
  </div>
`;
  return {
    route: c.route, kind: 'lesson',
    title: `${lesson.title} – ${program.title} – BIMx Academy`, description: lesson.summary,
    bodyAttrs: bodyData({ program: slug, lesson: lesson.slug, total }),
    body: frame(main, true),
  };
}

// ---------------------------------------------------------------- guides (publications)

/** A guide is a whole program, or one course of it ("course" in catalog.json). */
function guideSource(pub, programs) {
  const program = programs.find((p) => p.slug === pub.program);
  if (pub.course) {
    const course = program.courses.find((x) => x.code === pub.course);
    return { program, intro: course.description, lessons: course.lessons.map((l) => [course, l]) };
  }
  return { program, intro: program.intro, lessons: lessonsOf(program) };
}

function guidePage(src, lang, pub, programs) {
  const c = context(src, lang, `publicatii/${pub.slug}.html`);
  const { t, home } = c;
  const { title, short } = pub[lang];
  const { program, intro, lessons } = guideSource(pub, programs);
  const minutes = totalMinutes(lessons);
  const programHref = c.u(`${c.academy}programe/${program.slug}/`) + (pub.course ? `#${pub.course}` : '');

  const toc = [];
  const chapters = lessons.map(([, lesson], i) => {
    const n = i + 1;
    const cid = `capitolul-${n}`;
    toc.push(`<a href="#${cid}"><span>${pad2(n)}</span>${esc(lesson.title)}</a>`);
    const sections = lesson.sections.map((s) => `<h3>${rich(s.heading)}</h3>${s.blocks.map((b) => renderBlock(b, t)).join('')}`);
    const takeaways = lesson.takeaways.map((x) => `<li>${rich(x)}</li>`).join('');
    return `<section class="chapter" id="${cid}">
          <span class="chapter_num">${format(t.chapter_of, { i: n, n: lessons.length })}</span>
          <h2>${esc(lesson.title)}</h2>
          <p class="chapter_lead">${rich(lesson.summary)}</p>
          ${sections.join('')}
          <div class="takeaways"><h2>${t.takeaways}</h2><ul>${takeaways}</ul></div>
        </section>`;
  });

  // the PDF of the guide is a static file next to the page (public/<lang>/academy/publicatii/<guide>.pdf)
  const main = `
  <div class="second_main_section compact guide_hero">
    <div class="container">
      <div class="hero_grid">
        <div>
          ${breadcrumbs([c.crumbHome, ['BIMx Academy', home], [t.publications, home + '#publicatii'], [title, null]])}
          <span class="label">${t.guide} · ${esc(program.level)}</span>
          <h1>${esc(title)}</h1>
          <p class="lead">${rich(intro)}</p>
          <div class="meta_row">
            <span>${ICON_BOOK}${plural(lessons.length, t.chapter)}</span>
            <span>${ICON_CLOCK}${duration(minutes)} ${t.reading}</span>
            <span>${ICON_USER}${esc(program.audience)}</span>
          </div>
          <div class="hero_buttons">
            <a href="#capitolul-1" class="btn1">${t.start_reading} ${ARROW}</a>
            <a class="btn2" href="${pub.slug}.pdf" download>
              ${ICON_DOWNLOAD}
              ${t.download_pdf} <small>(PDF)</small></a>
          </div>
        </div>
        <div class="guide_cover"><img src="${c.asset(`img/publicatii/${pub.slug}.svg`)}" alt="${esc(format(t.cover_alt, { t: title }))}"></div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="guide_layout">
      <nav class="guide_toc" aria-label="${t.toc}">
        <h4>${t.toc}</h4>
        ${toc.join('')}
        <a href="${programHref}" class="btn3">${t.interactive} ${ARROW}</a>
      </nav>

      <article class="lesson_content guide_content">
        ${chapters.join('')}

        <aside class="guide_cta">
          <div>
            <span class="label light">${t.practice}</span>
            <h3>${t.practice_h}</h3>
            <p>${t.practice_p}</p>
          </div>
          <a href="${programHref}" class="btn1">${t.go_course} ${ARROW}</a>
        </aside>

        <p class="disclaimer">
          ${ICON_INFO}
          <span>${t.disclaimer}</span>
        </p>
      </article>
    </div>
  </div>
`;
  return {
    route: c.route, kind: 'guide',
    title: format(t.guide_title, { t: title }), description: short,
    bodyAttrs: bodyData({ guide: pub.slug }),
    body: frame(main, true),
  };
}

// ---------------------------------------------------------------- Academy home

function replaceMarker(text, name, content, lang) {
  const re = new RegExp(`(<!-- BUILD:${name}:START -->)([\\s\\S]*?)(<!-- BUILD:${name}:END -->)`, 'g');
  if (!re.test(text)) throw new Error(`Marker BUILD:${name} missing in templates/index.${lang}.html`);
  return text.replace(re, (_, a, __, b) => `${a}\n${content}\n${b}`);
}

/** Links written by hand in the home template: bimx.md addresses become local pages, "…/index.html" becomes "…/". */
function templateLinks(c, html) {
  html = html.replace(/(\s(?:href|src))=(["'])(https:\/\/bimx\.md[^"']*)\2/g, (all, attr, q, url) =>
    (url.startsWith('https://bimx.md/') ? `${attr}=${q}${c.u(localPath(c.lang, url))}${q}` : all));
  return html.replace(/(\shref=")(?!\/\/)([^"#?:]*\/)?index\.html(?=[#?"])/g, (_, a, dir) => a + (dir || './'));
}

function homePage(src, lang, programs) {
  const c = context(src, lang, '');
  const { t, u, academy } = c;
  const { catalog } = src;
  let text = src.templates[lang];

  const directions = programs.map((prog) => {
    const meta = catalog.directions[prog.slug] ?? { tags: { [lang]: [prog.level] }, icon: '' };
    const tags = meta.tags[lang].map((x) => `<span class="tag">${esc(x)}</span>`).join('');
    return `        <a class="block reveal" href="${u(`${academy}programe/${prog.slug}/`)}">
          <span class="num">${prog.num}</span>
          <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${meta.icon}</svg></div>
          <h3>${esc(prog.title)}</h3>
          <p>${esc(prog.short)}</p>
          <div class="meta">${tags}</div>
          <span class="link_arrow">${plural(lessonsOf(prog).length, t.lesson)} · ${t.view_track} ${ARROW}</span>
        </a>`;
  });
  text = replaceMarker(text, 'directions', directions.join('\n'), lang);

  const byCode = new Map();
  for (const prog of programs) for (const course of prog.courses) byCode.set(course.code, [prog, course]);

  // course cards: the order and texts come from catalog.json ("home_courses"); unknown codes are skipped
  const cards = catalog.home_courses.filter((item) => byCode.has(item.code)).map((item) => {
    const { code, level } = item;
    const { description, format: fmt, live } = item[lang];
    const [prog, course] = byCode.get(code);
    const mins = totalMinutes(course.lessons.map((l) => [course, l]));
    const foot = live ? `<span class="soon live">${catalog.live_label[lang]}</span>` : `<span class="soon">${t.track} ${prog.num}</span>`;
    return `        <a class="course reveal" data-level="${level}" href="${u(`${academy}programe/${prog.slug}/#${code}`)}">
          <div class="cover"><img src="${c.asset(`img/cursuri/${code.toLowerCase()}.svg`)}" alt="" loading="lazy"><span class="level ${level}">${catalog.levels[level][lang]}</span><span class="code">${code}</span></div>
          <div class="body">
            <h3>${esc(course.title)}</h3>
            <p>${esc(description)}</p>
            <div class="facts">
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/></svg>${plural(course.lessons.length, t.lesson)}</span>
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>${duration(mins)}</span>
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8"/></svg>${fmt}</span>
            </div>
          </div>
          <div class="foot">${foot}<span class="link_arrow">${t.view_lessons} ${ARROW}</span></div>
        </a>`;
  });
  text = replaceMarker(text, 'courses', cards.join('\n'), lang);

  const pubs = catalog.publications.map((pub) => {
    const { lessons } = guideSource(pub, programs);
    return `        <a class="pub reveal" href="${u(`${academy}publicatii/${pub.slug}.html`)}">
          <div class="doc"><img src="${c.asset(`img/publicatii/${pub.slug}.svg`)}" alt="" loading="lazy"><span class="fmt">PDF · ${plural(lessons.length, t.chapter)}</span></div>
          <div class="inner">
            <h3>${esc(pub[lang].title)}</h3>
            <p>${esc(pub[lang].short)}</p>
            <span class="link_arrow">${t.read_guide} ${ARROW}</span>
          </div>
        </a>`;
  });
  text = replaceMarker(text, 'publications', pubs.join('\n'), lang);

  const levels = new Set(catalog.home_courses.filter((x) => byCode.has(x.code)).map((x) => x.level));
  const values = [programs.length, levels.size, byCode.size, programs.reduce((s, p) => s + lessonsOf(p).length, 0)];
  text = replaceMarker(text, 'stats',
    values.map((n, i) => `            <div class="stat"><strong>${n}</strong><span>${t.stats[i]}</span></div>`).join('\n'), lang);

  // the page: <title> and description from the template head, the body between the header and footer markers
  // (the rest of the template head is replaced by the shared shell)
  const field = (re) => { const m = re.exec(text); if (!m) throw new Error(`templates/index.${lang}.html: ${re} not found`); return m[1]; };
  const [HEADER, FOOTER] = ['<!-- BUILD:bimx-header -->', '<!-- BUILD:bimx-footer -->'];
  const start = text.indexOf(HEADER);
  const end = text.indexOf(FOOTER);
  if (start < 0 || end < start) throw new Error(`templates/index.${lang}.html: ${HEADER} / ${FOOTER} markers missing`);
  const body = text.slice(start + HEADER.length, end).replace('<main id="top">', '<main id="top" class="bx-academy">');
  return {
    route: c.route, kind: 'home',
    title: field(/<title>([\s\S]*?)<\/title>/), description: field(/<meta name="description" content="([^"]*)">/),
    bodyAttrs: ' class="bx-academy-page"',
    body: templateLinks(c, body),
  };
}

// ---------------------------------------------------------------- site-wide text rules (ported from fixes.py)

/**
 * Headings without skipped levels for assistive technology: the visual tag stays, aria-level gets the logical
 * level (fixes.fix_headings). The page header has no headings, so the body starts the count.
 */
function fixHeadings(html) {
  const strip = (s) => unescapeHtml(s.replace(/<[^>]+>/g, ' ')).trim();
  let prev = 0;
  let seenH1 = false;
  return html.replace(/<h([1-6])\b([^>]*)>([\s\S]*?)<\/h\1>/g, (all, lvl, attrs, inner) => {
    const level = Number(lvl);
    if (!strip(inner)) return all;
    let want = level;
    if (level === 1) { want = seenH1 ? 2 : 1; seenH1 = true; }
    if (prev) want = Math.min(want, prev + 1);
    prev = want;
    return want !== level && !attrs.includes('aria-level') ? `<h${level}${attrs} aria-level="${want}">${inner}</h${level}>` : all;
  });
}

// Romanian only: "broker" → "agent de bursă" in all visible text and in alt/title/content/aria-label/placeholder
// (requested by BIMx; fixes.fix_broker_ro). Addresses (href, src) keep the word.
const BROKER_RO = { brokerilor: 'agenților de bursă', brokerului: 'agentului de bursă', brokerii: 'agenții de bursă', brokerul: 'agentul de bursă', brokeri: 'agenți de bursă', broker: 'agent de bursă' };
const BROKER_KEEP = ['prin intermediul brokerului', 'Brokeri și intermediari'];   // phrases where "broker" stays
// word boundaries as in Python (letters of any alphabet count as word characters)
const BROKER = /(?<![\p{L}\p{N}_])([Bb])(roker(?:ilor|ului|ii|ul|i)?)(?![\p{L}\p{N}_])/gu;

function brokerWords(s) {
  return s.replace(BROKER, (_, b, rest) => {
    const word = BROKER_RO['b' + rest];
    return b === 'B' ? word[0].toUpperCase() + word.slice(1) : word;
  });
}

/** Runs `rename` with the BROKER_KEEP phrases set aside. */
function keepPhrases(text, rename) {
  BROKER_KEEP.forEach((phrase, i) => { text = text.split(phrase).join(`\u0000${i}\u0000`); });
  text = rename(text);
  BROKER_KEEP.forEach((phrase, i) => { text = text.split(`\u0000${i}\u0000`).join(phrase); });
  return text;
}

/** The rename in plain text (page title, description). */
const renameBrokerText = (text) => keepPhrases(text, brokerWords);

/** The rename in HTML: text between tags and the listed attributes. */
const renameBrokerHtml = (html) => keepPhrases(html, (h) => h
  .replace(/>([^<]+)</g, (_, s) => '>' + brokerWords(s) + '<')
  .replace(/(\s(?:alt|title|content|aria-label|placeholder|data-all|data-less)=")([^"]*)"/g, (_, a, s) => a + brokerWords(s) + '"'));

// ---------------------------------------------------------------- checks (ported from tools/validate.py)

const BLOCK_FIELDS = { p: ['text'], list: ['items'], steps: ['items'], callout: ['variant', 'text'], table: ['headers', 'rows'], formula: ['expr'] };
const PROGRAM_FIELDS = ['slug', 'num', 'title', 'short', 'level', 'audience', 'intro', 'outcomes', 'prerequisites', 'courses'];

/** Stop the build with a clear list when a lesson file is incomplete or malformed. */
export function validateAcademy(src) {
  const errors = [];
  for (const [lang, programs] of Object.entries(src.programs)) {
    for (const d of programs) {
      const file = `src/content/academy/content/${lang}/${d.num ?? '?'}-${d.slug ?? '?'}.json`;
      for (const k of PROGRAM_FIELDS) if (!(k in d)) errors.push(`${file}: missing "${k}"`);
      const slugs = new Set();
      for (const c of d.courses ?? []) {
        for (const l of c.lessons ?? []) {
          const where = `${file} › ${l.slug}`;
          if (!/^[a-z0-9-]+$/.test(l.slug ?? '') || slugs.has(l.slug) || l.slug === 'index') errors.push(`${where}: invalid or duplicate lesson slug`);
          slugs.add(l.slug);
          const kinds = new Set();
          const text = [];
          for (const sec of l.sections ?? []) {
            for (const b of sec.blocks ?? []) {
              if (!(b.type in BLOCK_FIELDS)) { errors.push(`${where}: unknown block type "${b.type}"`); continue; }
              for (const f of BLOCK_FIELDS[b.type]) if (!(f in b)) errors.push(`${where}: "${b.type}" block without "${f}"`);
              kinds.add(b.type === 'callout' ? `callout:${b.variant ?? ''}` : b.type);
              text.push(JSON.stringify(b));
              if (b.type === 'table' && (b.rows ?? []).some((r) => r.length !== b.headers.length)) errors.push(`${where}: table row with the wrong number of columns`);
            }
          }
          for (const need of ['callout:definition', 'callout:example']) if (!kinds.has(need)) errors.push(`${where}: missing a ${need.replace(':', ' ')} block`);
          if ((l.quiz ?? []).length !== 3) errors.push(`${where}: the quiz has ${(l.quiz ?? []).length} questions instead of 3`);
          for (const q of l.quiz ?? []) if (!(q.answer >= 0 && q.answer < q.options.length)) errors.push(`${where}: quiz answer outside the options`);
          const bad = text.join(' ').match(/<(?!\/?(?:strong|em)>)[^>]*>/g);
          if (bad) errors.push(`${where}: tags not allowed in lesson text: ${[...new Set(bad)].join(' ')}`);
          if (lang === 'ro' && /[şţŞŢ]/.test(text.join(' '))) errors.push(`${where}: cedilla letters (ş/ţ) instead of comma letters (ș/ț)`);
        }
      }
    }
  }
  if (errors.length) throw new Error('Academy data:\n  ' + errors.join('\n  '));
}

// ---------------------------------------------------------------- all Academy pages

/** Shell templates of an Academy page (src/shell/<lang>/). */
function shellParts(lang, kind) {
  return {
    open: 'open-academy', head: 'head-academy', mid: 'mid-academy', pre: 'pre-academy',
    header: lang === 'ro' ? 'header-academy' : 'header-news',      // the RO header marks "BIMx Academy" as current
    footer: 'footer-academy',
    tail: kind === 'home' ? 'tail-academy' : 'tail-academy-2',
  };
}

/** Every Academy page in every language, as page objects for the shell (see site.mjs). */
export function academyPages(src = academySources()) {
  validateAcademy(src);
  const roSlugs = src.programs.ro.map((p) => p.slug).join();
  const pages = [];
  for (const lang of LANGS) {
    const programs = src.programs[lang] ?? [];
    if (programs.map((p) => p.slug).join() !== roSlugs) throw new Error(`content/${lang}/ does not have the same programs as content/ro/`);
    pages.push(homePage(src, lang, programs));
    for (const program of programs) {
      pages.push(programPage(src, lang, program, programs));
      lessonsOf(program).forEach((_, i) => pages.push(lessonPage(src, lang, program, i)));
    }
    for (const pub of src.catalog.publications) pages.push(guidePage(src, lang, pub, programs));
  }

  const out = pages.map(({ kind, ...p }) => {
    const page = { ...p, ...splitLang(p.route), parts: shellParts(splitLang(p.route).lang, kind) };
    if (kind !== 'home') {                   // the home page takes both, already escaped, from its template
      page.title = esc(page.title);
      page.description = esc(page.description);
    }
    page.body = fixHeadings(page.body);
    if (page.lang === 'ro') {
      // the rename applies to <title> text and to the description's content="…", as on the rest of the site
      page.title = renameBrokerText(page.title);
      page.description = renameBrokerText(page.description);
      page.body = renameBrokerHtml(page.body);
    }
    return page;
  });

  return out;
}
