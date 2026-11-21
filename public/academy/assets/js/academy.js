// Page language: UI messages follow <html lang>.
const EN_A = document.documentElement.lang === 'en';
const RU_A = (document.documentElement.lang || '').indexOf('ru') === 0;
const UK_A = (document.documentElement.lang || '').indexOf('uk') === 0;
// rusă și ucraineană: trei forme de plural („1 урок, 3 урока, 5 уроков” / „1 урок, 3 уроки, 5 уроків”)
const ruPlural = (n, one, few, many) => {
  const d = n % 10, h = n % 100;
  return d === 1 && h !== 11 ? one : (d >= 2 && d <= 4 && (h < 12 || h > 14)) ? few : many;
};

// BIMx Academy – progres, test și navigare pentru paginile de program și lecție.
(function () {
  const KEY = 'bimx-academy-progress';
  const body = document.body;
  const program = body.dataset.program;
  const lesson = body.dataset.lesson;
  const total = Number(body.dataset.total || 0);

  // Progress is a per-browser convenience: never let storage errors break the page.
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* ignore */ }
  }
  let progress = load();

  function doneCount() {
    return Object.keys(progress).filter(k => progress[k] && k.startsWith(program + '/')).length;
  }

  function render() {
    document.querySelectorAll('[data-lesson-id]').forEach(el => {
      el.classList.toggle('is-done', !!progress[el.dataset.lessonId]);
    });
    const done = doneCount();
    const pct = total ? Math.round(done / total * 100) : 0;

    const ring = document.querySelector('#progress-ring .value');
    if (ring) {
      const c = 2 * Math.PI * Number(ring.getAttribute('r'));
      ring.style.strokeDasharray = c;
      ring.style.strokeDashoffset = c * (1 - pct / 100);
    }
    const setText = (id, t) => { const el = document.getElementById(id); if (el) el.textContent = t; };
    setText('progress-pct', pct + '%');
    setText('progress-count', EN_A ? `${done} of ${total} lessons completed` : RU_A ? `Пройдено ${done} из ${total} ${ruPlural(total, 'урока', 'уроков', 'уроков')}` : UK_A ? `Пройдено ${done} з ${total} ${ruPlural(total, 'уроку', 'уроків', 'уроків')}` : `${done} din ${total} lecții finalizate`);
    setText('mini-count', `${done}/${total} ${EN_A ? 'lessons' : RU_A ? ruPlural(total, 'урок', 'урока', 'уроков') : UK_A ? ruPlural(total, 'урок', 'уроки', 'уроків') : 'lecții'}`);
    setText('mini-pct', pct + '%');
    const bar = document.querySelector('#mini-bar i');
    if (bar) bar.style.width = pct + '%';

    const start = document.getElementById('start-link');
    if (start && done > 0 && done < total) {
      const next = document.querySelector('.lesson_row:not(.is-done)');
      if (next) { start.href = next.getAttribute('href'); start.firstChild.textContent = EN_A ? 'Continue where you left off ' : RU_A ? 'Продолжить с того места, где вы остановились ' : UK_A ? 'Продовжити з того місця, де ви зупинилися ' : 'Continuă de unde ai rămas '; }
    }

    const btn = document.getElementById('complete-btn');
    if (btn && lesson) {
      const isDone = !!progress[program + '/' + lesson];
      btn.classList.toggle('is-done', isDone);
      btn.querySelector('span').textContent = isDone
        ? (EN_A ? 'Lesson completed' : RU_A ? 'Урок пройден' : UK_A ? 'Урок пройдено' : 'Lecție finalizată')
        : (EN_A ? 'Mark as completed' : RU_A ? 'Отметить как пройденный' : UK_A ? 'Позначити як пройдений' : 'Marchează ca finalizată');
    }
  }

  function setDone(value) {
    const id = program + '/' + lesson;
    if (value) progress[id] = true; else delete progress[id];
    save(progress);
    render();
  }

  const btn = document.getElementById('complete-btn');
  if (btn) btn.addEventListener('click', () => setDone(!progress[program + '/' + lesson]));

  const reset = document.getElementById('progress-reset');
  if (reset) reset.addEventListener('click', () => {
    Object.keys(progress).forEach(k => { if (k.startsWith(program + '/')) delete progress[k]; });
    save(progress);
    render();
  });

  // Mobile: lesson navigation collapses into <details>
  const nav = document.querySelector('.lesson_nav');
  if (nav) {
    const mq = window.matchMedia('(max-width: 900px)');
    const sync = () => { nav.open = !mq.matches; };
    sync();
    mq.addEventListener('change', sync);
    nav.querySelector('summary').addEventListener('click', e => { if (!mq.matches && !e.target.closest('a')) e.preventDefault(); });
  }

  // Quiz
  const quiz = document.getElementById('quiz');
  if (quiz) {
    const check = document.getElementById('quiz-check');
    const retry = document.getElementById('quiz-retry');
    const result = document.getElementById('quiz-result');
    const questions = [...quiz.querySelectorAll('.q')];

    check.addEventListener('click', () => {
      const unanswered = questions.filter(q => !q.querySelector('input:checked'));
      if (unanswered.length) {
        result.className = 'quiz_result';
        result.textContent = EN_A
          ? `You have ${unanswered.length === 1 ? 'one question' : unanswered.length + ' questions'} left unanswered.`
          : RU_A ? `Без ответа ${unanswered.length === 1 ? 'остался один вопрос' : 'осталось ' + unanswered.length + ' ' + ruPlural(unanswered.length, 'вопрос', 'вопроса', 'вопросов')}.`
          : UK_A ? `Без відповіді ${unanswered.length === 1 ? 'залишилося одне запитання' : 'залишилося ' + unanswered.length + ' ' + ruPlural(unanswered.length, 'запитання', 'запитання', 'запитань')}.`
          : `Mai ai ${unanswered.length === 1 ? 'o întrebare' : unanswered.length + ' întrebări'} fără răspuns.`;
        unanswered[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
      let score = 0;
      questions.forEach(q => {
        const answer = Number(q.dataset.answer);
        q.querySelectorAll('input').forEach((input, i) => {
          input.disabled = true;
          const label = input.closest('label');
          if (i === answer) label.classList.add('right');
          else if (input.checked) label.classList.add('wrong');
        });
        if (Number(q.querySelector('input:checked').value) === answer) score++;
        q.classList.add('checked');
      });
      const all = score === questions.length;
      result.className = 'quiz_result' + (all ? ' good' : '');
      result.textContent = all
        ? (EN_A ? `Excellent! ${score} of ${questions.length} answers correct.` : RU_A ? `Отлично! Правильных ответов: ${score} из ${questions.length}.` : UK_A ? `Чудово! Правильних відповідей: ${score} з ${questions.length}.` : `Excelent! ${score} din ${questions.length} răspunsuri corecte.`)
        : (EN_A ? `${score} of ${questions.length} answers correct. Read the explanations and try again.` : RU_A ? `Правильных ответов: ${score} из ${questions.length}. Прочитайте пояснения и попробуйте ещё раз.` : UK_A ? `Правильних відповідей: ${score} з ${questions.length}. Прочитайте пояснення та спробуйте ще раз.` : `${score} din ${questions.length} răspunsuri corecte. Citește explicațiile și încearcă din nou.`);
      check.hidden = true;
      retry.hidden = false;
      if (all && lesson && !progress[program + '/' + lesson]) setDone(true);
    });

    retry.addEventListener('click', () => {
      questions.forEach(q => {
        q.classList.remove('checked');
        q.querySelectorAll('label').forEach(l => l.classList.remove('right', 'wrong'));
        q.querySelectorAll('input').forEach(i => { i.disabled = false; i.checked = false; });
      });
      result.textContent = '';
      check.hidden = false;
      retry.hidden = true;
    });
  }

  // Table of contents scroll-spy
  const tocLinks = document.querySelectorAll('.toc a, .guide_toc a[href^="#"]');
  if (tocLinks.length) {
    const byId = new Map([...tocLinks].map(a => [a.getAttribute('href').slice(1), a]));
    const spy = new IntersectionObserver(entries => entries.forEach(en => {
      if (!en.isIntersecting) return;
      tocLinks.forEach(a => a.classList.remove('active'));
      const a = byId.get(en.target.id);
      if (a) a.classList.add('active');
    }), { rootMargin: '-20% 0px -70% 0px' });
    byId.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });
  }

  // Reading progress bar
  const readBar = document.querySelector('.read_progress i');
  const article = document.querySelector('.lesson_content');
  if (readBar && article) {
    const update = () => {
      const r = article.getBoundingClientRect();
      const span = r.height - window.innerHeight * 0.6;
      const pct = Math.min(100, Math.max(0, (-r.top + 120) / span * 100));
      readBar.style.width = pct + '%';
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
  }

  render();
})();
