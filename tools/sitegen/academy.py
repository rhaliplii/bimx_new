"""Paginile Academy: programe, lecții, ghiduri și prima pagină."""
import json
import re

from .config import (ACADEMY_ASSETS, DIRECTION_META, HOME_COURSES, LANGS, LEVELS, LIVE, LOCALES, PUBLICATIONS, ROOT, SITE_LANGS, T)
from .icons import (ARROW, ARROW_LEFT, CALLOUT_ICONS, CHECK, CRUMB, ICON_BAR, ICON_BOOK, ICON_CLOCK, ICON_LAYERS,
                    ICON_USER)
from .shell import shell_parts
from .util import duration, esc, lessons_of, plural, prefix, relto, rich, slugify, total_minutes


class Ctx:
    """Limba și poziția paginii curente: de aici rezultă toate căile relative."""

    def __init__(self, lang, rel):
        self.lang = lang
        self.t = T[lang]
        self.rel = rel                                        # calea paginii, relativă la Academy în limba ei
        here = (LANGS[lang]["out"] / rel).parent
        self.p = prefix(LANGS[lang]["out"], here)             # până la rădăcina Academy a limbii
        self.a = prefix(ACADEMY_ASSETS.parent, here)          # până la folderul care conține assets/
        self.home = f"{self.p}index.html"
        self._here = here

    def switch(self):
        """Linkurile către aceeași pagină în fiecare limbă (ordinea din SITE_LANGS)."""
        return tuple(relto(LANGS[lang]["out"] / self.rel, self._here) for lang in SITE_LANGS)



def page(ctx, title, description, body_attrs, main, read_progress=False):
    attrs = " ".join(f'data-{k}="{esc(str(v))}"' for k, v in body_attrs.items())
    links = ctx.switch()
    a = ctx.a
    sh = shell_parts(ctx.lang, ctx._here, links)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{lang}" href="{href}">' for lang, href in zip(SITE_LANGS, links))
    progress = '<div class="read_progress" aria-hidden="true"><i></i></div>' if read_progress else ""
    return f"""<!DOCTYPE html>
<html lang="{ctx.lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{alternates}
<link rel="icon" href="https://bimx.md/wp-content/uploads/2026/07/Favicon.png">
{sh["head"]}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{a}assets/css/main.css">
<link rel="stylesheet" href="{a}assets/css/academy.css">
{sh["scripts"]}
</head>
<body class="bx-academy-page" {attrs}>

{sh["header"]}

<main id="top" class="bx-academy">
{progress}
{main}
</main>

{sh["footer"]}

<script src="{a}assets/js/main.js"></script>
<script src="{a}assets/js/academy.js"></script>
</body>
</html>
"""


def breadcrumbs(items):
    parts = []
    for label, href in items:
        if href:
            parts.append(f'<li><a href="{href}">{esc(label)}</a>{CRUMB}</li>')
        else:
            parts.append(f"<li><span>{esc(label)}</span></li>")
    return '<ul class="breadcrumbs">' + "".join(parts) + "</ul>"



# ---------------------------------------------------------------- blocks

def render_block(b, t):
    kind = b["type"]
    if kind == "p":
        return f"<p>{rich(b['text'])}</p>"
    if kind == "list":
        return '<ul class="bullets">' + "".join(f"<li>{rich(i)}</li>" for i in b["items"]) + "</ul>"
    if kind == "steps":
        return '<ol class="steps_list">' + "".join(
            f"<li><div><b>{rich(i['title'])}</b><span>{rich(i['text'])}</span></div></li>" for i in b["items"]
        ) + "</ol>"
    if kind == "callout":
        variant = b.get("variant", "tip")
        if variant not in CALLOUT_ICONS:
            variant = "tip"
        label, icon = t["callouts"][variant], CALLOUT_ICONS[variant]
        title = f"<h5>{rich(b['title'])}</h5>" if b.get("title") else ""
        return (
            f'<aside class="callout {variant}"><div class="ci">{icon}</div>'
            f'<div><span class="ct">{label}</span>{title}<p>{rich(b["text"])}</p></div></aside>'
        )
    if kind == "table":
        head = "".join(f"<th>{rich(h)}</th>" for h in b["headers"])
        rows = "".join("<tr>" + "".join(f"<td>{rich(c)}</td>" for c in row) + "</tr>" for row in b["rows"])
        return f'<div class="table_wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    if kind == "formula":
        note = f'<div class="fn">{rich(b["note"])}</div>' if b.get("note") else ""
        return (
            f'<div class="formula"><div class="fl">{rich(b.get("label", "Formula"))}</div>'
            f'<div class="fe">{rich(b["expr"])}</div>{note}</div>'
        )
    raise ValueError(f"Tip de bloc necunoscut: {kind}")


# ---------------------------------------------------------------- program page

def status_icon():
    return f'<span class="check_mark" aria-hidden="true">{CHECK}</span>'


def program_page(lang, program, programs):
    slug = program["slug"]
    ctx = Ctx(lang, f"programe/{slug}/index.html")
    t, home = ctx.t, ctx.home
    lessons = lessons_of(program)
    first = lessons[0][1]
    minutes = total_minutes(lessons)

    course_blocks = []
    n = 0
    for course in program["courses"]:
        rows = []
        for lesson in course["lessons"]:
            n += 1
            rows.append(
                f'<li><a class="lesson_row" href="{lesson["slug"]}.html" data-lesson-id="{slug}/{lesson["slug"]}">'
                f'<span class="n">{n:02d}</span>'
                f'<span><h4>{esc(lesson["title"])}</h4><p>{rich(lesson["summary"])}</p></span>'
                f'<span class="min">{lesson["minutes"]} min</span>{status_icon()}</a></li>'
            )
        course_min = total_minutes([(course, l) for l in course["lessons"]])
        course_blocks.append(f"""<div class="course_block" id="{course['code']}">
          <div class="cb_head">
            <div><span class="code">{esc(course['code'])}</span><h3>{esc(course['title'])}</h3><p>{rich(course['description'])}</p></div>
            <div class="count"><b>{plural(len(course['lessons']), t['lesson'])}</b>{duration(course_min)}</div>
          </div>
          <ol class="lesson_list">{''.join(rows)}</ol>
        </div>""")

    others = []
    for other in programs:
        if other["slug"] == slug:
            continue
        cnt = len(lessons_of(other))
        others.append(
            f'<a href="../{other["slug"]}/index.html"><span class="num">{t["track"]} {other["num"]}</span>'
            f'<h4>{esc(other["title"])}</h4><p>{esc(other["short"])}</p>'
            f'<span class="link_arrow">{plural(cnt, t["lesson"])} {ARROW}</span></a>'
        )

    outcomes = "".join(f"<li>{rich(o)}</li>" for o in program["outcomes"])
    crumb_label, crumb_href = t["home_crumb"]
    main = f"""
  <div class="second_main_section compact">
    <div class="container">
      <div class="hero_grid">
        <div>
          {breadcrumbs([(crumb_label, crumb_href), ("BIMx Academy", home), (t["tracks"], home + "#directii"), (program["title"], None)])}
          <span class="label">{t["track"]} {program['num']} · {esc(program['level'])}</span>
          <h1>{esc(program['title'])}</h1>
          <p class="lead">{rich(program['intro'])}</p>
          <div class="meta_row">
            <span>{ICON_LAYERS}{plural(len(program['courses']), t['course'])}</span>
            <span>{ICON_BOOK}{plural(len(lessons), t['lesson'])}</span>
            <span>{ICON_CLOCK}{duration(minutes)} {t['reading']}</span>
            <span>{ICON_USER}{esc(program['audience'])}</span>
          </div>
          <div class="hero_buttons">
            <a href="{first['slug']}.html" class="btn1" id="start-link">{t['start_first']} {ARROW}</a>
            <a href="#programa" class="btn2">{t['see_syllabus']}</a>
          </div>
        </div>
        <aside class="hero_card">
          <div class="progress_card">
            <div class="ring" id="progress-ring">
              <svg width="120" height="120" viewBox="0 0 120 120"><circle class="track" cx="60" cy="60" r="52" fill="none" stroke-width="10"/><circle class="value" cx="60" cy="60" r="52" fill="none" stroke-width="10" stroke-linecap="round" style="stroke-dasharray:327;stroke-dashoffset:327"/></svg>
              <b id="progress-pct">0%</b>
            </div>
            <div>
              <h3>{t['your_progress']}</h3>
              <p id="progress-count">0 {t['of_done'].format(n=len(lessons))}</p>
              <button type="button" class="btn2" id="progress-reset">{t['reset']}</button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="program_layout">
      <div>
        <h2 class="sub_title">{t['learn']}</h2>
        <ul class="outcomes">{outcomes}</ul>

        <h2 class="sub_title" id="programa" style="scroll-margin-top:110px">{t['syllabus']}</h2>
        {''.join(course_blocks)}
      </div>

      <aside class="side_card">
        <h3>{t['about_program']}</h3>
        <dl class="info_list">
          <div><dt>{t['level']}</dt><dd>{esc(program['level'])}</dd></div>
          <div><dt>{t['audience']}</dt><dd>{esc(program['audience'])}</dd></div>
          <div><dt>{t['courses']}</dt><dd>{len(program['courses'])}</dd></div>
          <div><dt>{t['lessons']}</dt><dd>{len(lessons)}</dd></div>
          <div><dt>{t['est']}</dt><dd>{duration(minutes)}</dd></div>
          <div><dt>{t['format']}</dt><dd>{t['format_val']}</dd></div>
        </dl>
        <p class="note"><strong>{t['req']}</strong> {rich(program['prerequisites'])}</p>
        <a href="{first['slug']}.html" class="btn1">{t['start_program']} {ARROW}</a>
      </aside>
    </div>
  </div>

  <section class="block_section" style="padding-top:72px;padding-bottom:0">
    <div class="container">
      <div class="head"><div><span class="label light">{t['keep_learning']}</span><h2>{t['other_tracks']}</h2></div></div>
      <div class="other_programs">{''.join(others)}</div>
    </div>
  </section>
"""
    return page(ctx, f"{program['title']} – BIMx Academy", program["short"],
                {"program": slug, "total": len(lessons)}, main)


# ---------------------------------------------------------------- lesson page

def lesson_page(lang, program, index):
    slug = program["slug"]
    lessons = lessons_of(program)
    course, lesson = lessons[index]
    ctx = Ctx(lang, f"programe/{slug}/{lesson['slug']}.html")
    t, home = ctx.t, ctx.home
    total = len(lessons)

    groups = []
    for c in program["courses"]:
        links = []
        for l in c["lessons"]:
            current = " current" if l["slug"] == lesson["slug"] else ""
            aria = ' aria-current="page"' if current else ""
            links.append(
                f'<a href="{l["slug"]}.html" class="{current.strip()}" data-lesson-id="{slug}/{l["slug"]}"{aria}>'
                f'{status_icon()}<span>{esc(l["title"])}</span></a>'
            )
        groups.append(f'<div class="group"><span>{esc(c["code"])} · {esc(c["title"])}</span>{"".join(links)}</div>')

    sections, toc = [], []
    used = set()
    for s in lesson["sections"]:
        sid = slugify(s["heading"]) or "sectiune"
        while sid in used:
            sid += "-2"
        used.add(sid)
        toc.append(f'<a href="#{sid}">{esc(s["heading"])}</a>')
        blocks = "".join(render_block(b, t) for b in s["blocks"])
        sections.append(f'<section id="{sid}"><h2>{rich(s["heading"])}</h2>{blocks}</section>')
    toc.append(f'<a href="#de-retinut">{t["takeaways"]}</a>')
    toc.append(f'<a href="#quiz">{t["quiz"]}</a>')

    takeaways = "".join(f"<li>{rich(x)}</li>" for x in lesson["takeaways"])

    questions = []
    for qi, q in enumerate(lesson["quiz"]):
        opts = "".join(
            f'<label><input type="radio" name="q{qi}" value="{oi}"><span>{rich(o)}</span></label>'
            for oi, o in enumerate(q["options"])
        )
        questions.append(
            f'<div class="q" data-answer="{q["answer"]}"><fieldset>'
            f'<legend><small>{t["q_of"].format(i=qi + 1, n=len(lesson["quiz"]))}</small>{rich(q["q"])}</legend>'
            f'<div class="opts">{opts}</div></fieldset>'
            f'<p class="expl"><strong>{t["explanation"]}</strong> {rich(q["explanation"])}</p></div>'
        )

    if index > 0:
        pl = lessons[index - 1][1]
        prev_link = f'<a href="{pl["slug"]}.html" class="prev"><span>{ARROW_LEFT} {t["prev"]}</span><b>{esc(pl["title"])}</b></a>'
    else:
        prev_link = f'<a href="index.html" class="prev"><span>{ARROW_LEFT} {t["back_program"]}</span><b>{esc(program["title"])}</b></a>'
    if index < total - 1:
        nl = lessons[index + 1][1]
        next_link = f'<a href="{nl["slug"]}.html" class="next"><span>{t["next"]} {ARROW}</span><b>{esc(nl["title"])}</b></a>'
    else:
        next_link = f'<a href="index.html" class="next"><span>{t["the_end"]} {ARROW}</span><b>{t["back_syllabus"]}</b></a>'

    crumb_label, crumb_href = t["home_crumb"]
    main = f"""
  <div class="second_main_section compact">
    <div class="container" style="position:relative;z-index:1">
      {breadcrumbs([(crumb_label, crumb_href), ("BIMx Academy", home), (program["title"], "index.html"), (t["lesson_n"].format(i=index + 1), None)])}
      <span class="label">{esc(course['code'])} · {t['lesson_of'].format(i=index + 1, n=total)}</span>
      <h1>{esc(lesson['title'])}</h1>
      <p class="lead">{rich(lesson['summary'])}</p>
      <div class="meta_row" style="margin-bottom:0">
        <span>{ICON_CLOCK}{lesson['minutes']} {t['min_reading']}</span>
        <span>{ICON_BAR}{esc(program['level'])}</span>
        <span>{ICON_LAYERS}{esc(course['title'])}</span>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="lesson_layout">
      <details class="lesson_nav" open>
        <summary>
          <span class="ln_title">{t['program_content']}</span>
          <span class="ln_program">{esc(program['title'])}</span>
          <div class="mini_bar" id="mini-bar"><i></i></div>
          <div class="mini_label"><span id="mini-count">0/{total} {t['lesson'][1]}</span><span id="mini-pct">0%</span></div>
        </summary>
        <a href="index.html" class="ln_back">{ARROW_LEFT} {t['back_program']}</a>
        {''.join(groups)}
      </details>

      <article class="lesson_content">
        {''.join(sections)}

        <div class="takeaways" id="de-retinut" style="scroll-margin-top:110px">
          <h2>{t['takeaways']}</h2>
          <ul>{takeaways}</ul>
        </div>

        <div class="quiz" id="quiz">
          <h2>{t['quiz']}</h2>
          <p class="quiz_sub">{t['quiz_sub']}</p>
          {''.join(questions)}
          <div class="quiz_actions">
            <span class="quiz_result" id="quiz-result" role="status" aria-live="polite"></span>
            <div>
              <button type="button" class="btn1" id="quiz-check">{t['check']}</button>
              <button type="button" class="btn3" id="quiz-retry" hidden>{t['retry']}</button>
            </div>
          </div>
        </div>

        <div class="complete_bar">
          <p><b>{t['done_q']}</b>{t['done_p']}</p>
          <button type="button" class="btn1 complete_btn" id="complete-btn">{CHECK.replace('<svg ', '<svg width="16" height="16" ')}<span>{t['mark_done']}</span></button>
        </div>

        <nav class="pager" aria-label="{t['pager']}">{prev_link}{next_link}</nav>

        <p class="disclaimer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>
          <span>{t['disclaimer']}</span>
        </p>
      </article>

      <aside class="toc" aria-label="{t['on_page']}">
        <h4>{t['on_page']}</h4>
        {''.join(toc)}
      </aside>
    </div>
  </div>
"""
    return page(ctx, f"{lesson['title']} – {program['title']} – BIMx Academy", lesson["summary"],
                {"program": slug, "lesson": lesson["slug"], "total": total}, main, read_progress=True)


# ---------------------------------------------------------------- publications

def publication_source(pub, programs):
    program = next(p for p in programs if p["slug"] == pub["program"])
    if pub.get("course"):
        course = next(c for c in program["courses"] if c["code"] == pub["course"])
        return program, course["description"], [(course, l) for l in course["lessons"]]
    return program, program["intro"], lessons_of(program)


def publication_page(lang, pub, programs):
    ctx = Ctx(lang, f"publicatii/{pub['slug']}.html")
    t, home, a = ctx.t, ctx.home, ctx.a
    title, short = pub[lang]["title"], pub[lang]["short"]
    program, intro, lessons = publication_source(pub, programs)
    minutes = total_minutes(lessons)
    program_href = f"{ctx.p}programe/{program['slug']}/index.html" + (f"#{pub['course']}" if pub.get("course") else "")

    toc, chapters = [], []
    for n, (course, lesson) in enumerate(lessons, 1):
        cid = f"capitolul-{n}"
        toc.append(f'<a href="#{cid}"><span>{n:02d}</span>{esc(lesson["title"])}</a>')
        sections = []
        for s in lesson["sections"]:
            blocks = "".join(render_block(b, t) for b in s["blocks"])
            sections.append(f'<h3>{rich(s["heading"])}</h3>{blocks}')
        takeaways = "".join(f"<li>{rich(x)}</li>" for x in lesson["takeaways"])
        chapters.append(f"""<section class="chapter" id="{cid}">
          <span class="chapter_num">{t['chapter_of'].format(i=n, n=len(lessons))}</span>
          <h2>{esc(lesson['title'])}</h2>
          <p class="chapter_lead">{rich(lesson['summary'])}</p>
          {''.join(sections)}
          <div class="takeaways"><h2>{t['takeaways']}</h2><ul>{takeaways}</ul></div>
        </section>""")

    crumb_label, crumb_href = t["home_crumb"]
    main = f"""
  <div class="second_main_section compact guide_hero">
    <div class="container">
      <div class="hero_grid">
        <div>
          {breadcrumbs([(crumb_label, crumb_href), ("BIMx Academy", home), (t["publications"], home + "#publicatii"), (title, None)])}
          <span class="label">{t['guide']} · {esc(program['level'])}</span>
          <h1>{esc(title)}</h1>
          <p class="lead">{rich(intro)}</p>
          <div class="meta_row">
            <span>{ICON_BOOK}{plural(len(lessons), t['chapter'])}</span>
            <span>{ICON_CLOCK}{duration(minutes)} {t['reading']}</span>
            <span>{ICON_USER}{esc(program['audience'])}</span>
          </div>
          <div class="hero_buttons">
            <a href="#capitolul-1" class="btn1">{t['start_reading']} {ARROW}</a>
            <button type="button" class="btn2" onclick="window.print()" data-pdf="{pub['slug']}.pdf">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>
              {t['print_pdf']}
            </button>
          </div>
        </div>
        <div class="guide_cover"><img src="{a}assets/img/publicatii/{pub['slug']}.svg" alt="{esc(t['cover_alt'].format(t=title))}"></div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="guide_layout">
      <nav class="guide_toc" aria-label="{t['toc']}">
        <h4>{t['toc']}</h4>
        {''.join(toc)}
        <a href="{program_href}" class="btn3">{t['interactive']} {ARROW}</a>
      </nav>

      <article class="lesson_content guide_content">
        {''.join(chapters)}

        <aside class="guide_cta">
          <div>
            <span class="label light">{t['practice']}</span>
            <h3>{t['practice_h']}</h3>
            <p>{t['practice_p']}</p>
          </div>
          <a href="{program_href}" class="btn1">{t['go_course']} {ARROW}</a>
        </aside>

        <p class="disclaimer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>
          <span>{t['disclaimer']}</span>
        </p>
      </article>
    </div>
  </div>
"""
    return page(ctx, t["guide_title"].format(t=title), short, {"guide": pub["slug"]}, main, read_progress=True)


# ---------------------------------------------------------------- homepage

def replace_marker(text, name, content, where):
    pattern = re.compile(rf"(<!-- BUILD:{name}:START -->)(.*?)(<!-- BUILD:{name}:END -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"Marcajul BUILD:{name} lipsește din {where}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def update_home(lang, programs):
    template = LANGS[lang]["template"]
    if not template.exists():
        raise SystemExit(f"Lipsește {template.relative_to(ROOT)}")
    index = LANGS[lang]["out"] / "index.html"
    t = T[lang]
    a = prefix(ACADEMY_ASSETS.parent, LANGS[lang]["out"])
    text = template.read_text(encoding="utf-8")
    where = str(template.relative_to(ROOT))

    blocks = []
    for prog in programs:
        meta = DIRECTION_META.get(prog["slug"], {"tags": {lang: [prog["level"]]}, "icon": ""})
        tags = "".join(f'<span class="tag">{esc(x)}</span>' for x in meta["tags"][lang])
        cnt = len(lessons_of(prog))
        blocks.append(f"""        <a class="block reveal" href="programe/{prog['slug']}/index.html">
          <span class="num">{prog['num']}</span>
          <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{meta['icon']}</svg></div>
          <h3>{esc(prog['title'])}</h3>
          <p>{esc(prog['short'])}</p>
          <div class="meta">{tags}</div>
          <span class="link_arrow">{plural(cnt, t['lesson'])} · {t['view_track']} {ARROW}</span>
        </a>""")
    text = replace_marker(text, "directions", "\n".join(blocks), where)

    by_code = {}
    for prog in programs:
        for course in prog["courses"]:
            by_code[course["code"]] = (prog, course)

    cards = []
    for item in HOME_COURSES:
        code, level = item["code"], item["level"]
        if code not in by_code:
            continue
        desc, fmt, live = item[lang]["description"], item[lang]["format"], item[lang].get("live")
        prog, course = by_code[code]
        n = len(course["lessons"])
        mins = total_minutes([(course, l) for l in course["lessons"]])
        foot_label = (f'<span class="soon live">{LIVE[lang]}</span>' if live
                      else f'<span class="soon">{t["track"]} {prog["num"]}</span>')
        cards.append(f"""        <a class="course reveal" data-level="{level}" href="programe/{prog['slug']}/index.html#{code}">
          <div class="cover"><img src="{a}assets/img/cursuri/{code.lower()}.svg" alt="" loading="lazy"><span class="level {level}">{LEVELS[level][lang]}</span><span class="code">{code}</span></div>
          <div class="body">
            <h3>{esc(course['title'])}</h3>
            <p>{esc(desc)}</p>
            <div class="facts">
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/></svg>{plural(n, t['lesson'])}</span>
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>{duration(mins)}</span>
              <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8"/></svg>{fmt}</span>
            </div>
          </div>
          <div class="foot">{foot_label}<span class="link_arrow">{t['view_lessons']} {ARROW}</span></div>
        </a>""")
    text = replace_marker(text, "courses", "\n".join(cards), where)

    pubs = []
    for pub in PUBLICATIONS:
        _, _, lessons = publication_source(pub, programs)
        title, short = pub[lang]["title"], pub[lang]["short"]
        pubs.append(f"""        <a class="pub reveal" href="publicatii/{pub['slug']}.html">
          <div class="doc"><img src="{a}assets/img/publicatii/{pub['slug']}.svg" alt="" loading="lazy"><span class="fmt">PDF · {plural(len(lessons), t['chapter'])}</span></div>
          <div class="inner">
            <h3>{esc(title)}</h3>
            <p>{esc(short)}</p>
            <span class="link_arrow">{t['read_guide']} {ARROW}</span>
          </div>
        </a>""")
    text = replace_marker(text, "publications", "\n".join(pubs), where)

    total_lessons = sum(len(lessons_of(prog)) for prog in programs)
    levels = {c["level"] for c in HOME_COURSES if c["code"] in by_code}
    values = [len(programs), len(levels), len(by_code), total_lessons]
    text = replace_marker(
        text, "stats",
        "\n".join(f'            <div class="stat"><strong>{n}</strong><span>{label}</span></div>' for n, label in zip(values, t["stats"])),
        where,
    )
    text = apply_shell_to_home(text, lang, index.parent)
    index.write_text(text, encoding="utf-8")


def apply_shell_to_home(text, lang, here):
    sh = shell_parts(lang, here, tuple(relto(LANGS[x]["out"] / "index.html", here) for x in SITE_LANGS))
    for name in ("header", "footer"):
        marker = f"<!-- BUILD:bimx-{name} -->"
        if marker not in text:
            raise SystemExit(f"Marcajul {marker} lipsește din șablonul Academy [{lang}]")
        text = text.replace(marker, sh[name], 1)
    css = re.search(r'<link rel="stylesheet" href="[^"]*assets/css/main\.css">', text).group(0)
    academy_css = css.replace("main.css", "academy.css")
    text = text.replace(css, f"{sh['head']}\n{css}\n{academy_css}\n{sh['scripts']}", 1)
    text = text.replace('<main id="top">', '<main id="top" class="bx-academy">', 1)
    text = re.sub(r"<body>", '<body class="bx-academy-page">', text, count=1)
    return text


# ---------------------------------------------------------------- main

def load_programs(lang):
    folder = LANGS[lang]["content"]
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(folder.glob("*.json"))]


def build(lang, programs):
    out = LANGS[lang]["out"]
    count = 0
    for program in programs:
        folder = out / "programe" / program["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(program_page(lang, program, programs), encoding="utf-8")
        for i, (_, lesson) in enumerate(lessons_of(program)):
            (folder / f"{lesson['slug']}.html").write_text(lesson_page(lang, program, i), encoding="utf-8")
            count += 1
        print(f"  [{lang}] {program['num']} {program['title']}: {len(lessons_of(program))} lessons")

    guides = out / "publicatii"
    guides.mkdir(parents=True, exist_ok=True)
    for pub in PUBLICATIONS:
        (guides / f"{pub['slug']}.html").write_text(publication_page(lang, pub, programs), encoding="utf-8")

    update_home(lang, programs)
    return count


