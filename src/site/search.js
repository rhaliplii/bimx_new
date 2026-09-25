// Căutarea din antet (modalul .modal_search_form), fără server: indexul paginilor se generează la build
// (tools/sitegen/search.py → assets/search/{ro,en}.js) și se încarcă la prima căutare.
(function () {
  var me = document.currentScript;
  var ROOT = (me && me.getAttribute('data-root')) || '';
  var LANG = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0 ? 'en' : 'ro';
  var T = LANG === 'en'
    ? { loading: 'Searching…', none: 'No results for', one: 'result for', many: 'results for', error: 'Search is unavailable right now.', hint: 'Type at least 2 characters.' }
    : { loading: 'Se caută…', none: 'Niciun rezultat pentru', one: 'rezultat pentru', many: 'rezultate pentru', error: 'Căutarea nu este disponibilă momentan.', hint: 'Scrieți cel puțin 2 caractere.' };
  var MAX_RESULTS = 20;

  var modal = document.querySelector('.modal_search_form');
  var form = modal && modal.querySelector('.search-form-custom');
  var input = form && form.querySelector('.search-field');
  if (!form || !input) return;

  // ---------------------------------------------------------------- stiluri
  var css = document.createElement('style');
  css.textContent = [
    '.modal_search_form.bx-has-results{height:auto;min-height:100%;align-items:flex-start;padding-bottom:44px;max-height:100vh;overflow:auto}',
    '.modal_search_form .container{flex-direction:column;align-items:stretch}',
    '.bx-search-results{width:100%;margin-top:14px;font-family:inherit}',
    '.bx-search-results .bx-sr-status{font-size:14px;color:#6A7181;margin:0 0 10px 4px}',
    '.bx-search-results ol{list-style:none;margin:0;padding:0;display:grid;gap:8px}',
    '.bx-search-results a{display:block;padding:12px 16px;border:1px solid #E5E7EB;border-radius:12px;text-decoration:none;color:#1A2266;background:#fff;transition:border-color .2s,background .2s}',
    '.bx-search-results a:hover,.bx-search-results a:focus-visible{border-color:#1EB1F1;background:#F5FBFE;outline:none}',
    '.bx-search-results .bx-sr-sec{display:block;font-size:12px;font-weight:600;letter-spacing:.03em;color:#1DB0F0;margin-bottom:2px}',
    '.bx-search-results .bx-sr-title{display:block;font-size:16px;font-weight:600;line-height:1.35}',
    '.bx-search-results .bx-sr-snip{display:block;font-size:14px;line-height:1.5;color:#4A5065;margin-top:4px}',
    '.bx-search-results mark{background:#FFF1B8;color:inherit;border-radius:3px;padding:0 1px}'
  ].join('');
  document.head.appendChild(css);

  var box = document.createElement('div');
  box.className = 'bx-search-results';
  box.setAttribute('aria-live', 'polite');
  form.parentNode.insertBefore(box, form.nextSibling);
  input.setAttribute('aria-label', input.getAttribute('placeholder') || 'Search');
  input.setAttribute('autocomplete', 'off');

  // ---------------------------------------------------------------- index
  var index = null, loading = null;
  function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = ROOT + 'assets/search/' + LANG + '.js';
      s.onload = function () {
        var data = (window.BIMX_SEARCH || {})[LANG] || [];
        index = data.map(function (d) { return { d: d, t: norm(d.t), h: norm(d.h), x: norm(d.x), s: norm(d.s) }; });
        resolve(index);
      };
      s.onerror = function () { loading = null; reject(new Error('index')); };
      document.head.appendChild(s);
    });
    return loading;
  }

  function count(hay, needle) {
    var n = 0, i = hay.indexOf(needle);
    while (i !== -1 && n < 50) { n++; i = hay.indexOf(needle, i + needle.length); }
    return n;
  }

  function search(q) {
    var nq = norm(q).trim();
    var terms = nq.split(/[^a-z0-9]+/).filter(function (w) { return w.length >= 2 || /\d/.test(w); });
    if (!terms.length) return [];
    var out = [];
    index.forEach(function (p) {
      var all = p.t + ' ' + p.s + ' ' + p.h + ' ' + p.x;
      for (var i = 0; i < terms.length; i++) if (all.indexOf(terms[i]) === -1) return;
      var score = 0;
      terms.forEach(function (w) {
        if (p.t.indexOf(w) !== -1) score += 30;
        if (p.h.indexOf(w) !== -1) score += 8;
        if (p.s.indexOf(w) !== -1) score += 4;
        score += Math.min(count(p.x, w), 12);
      });
      if (terms.length > 1 && (p.t.indexOf(nq) !== -1 || p.x.indexOf(nq) !== -1)) score += 25;
      out.push({ p: p, score: score });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    return out.slice(0, MAX_RESULTS).map(function (r) { r.terms = terms; return r; });
  }

  // ---------------------------------------------------------------- afișare
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function highlight(orig, terms) {
    // textul normalizat are aceeași lungime ca originalul (diacriticele românești se descompun în literă + semn)
    var n = norm(orig), marks = [];
    terms.forEach(function (w) {
      var i = n.indexOf(w);
      while (i !== -1) { marks.push([i, i + w.length]); i = n.indexOf(w, i + w.length); }
    });
    if (!marks.length || n.length !== orig.length) return esc(orig);
    marks.sort(function (a, b) { return a[0] - b[0]; });
    var html = '', pos = 0;
    marks.forEach(function (m) {
      if (m[0] < pos) return;
      html += esc(orig.slice(pos, m[0])) + '<mark>' + esc(orig.slice(m[0], m[1])) + '</mark>';
      pos = m[1];
    });
    return html + esc(orig.slice(pos));
  }
  function snippet(p, terms) {
    var at = -1;
    for (var i = 0; i < terms.length && at === -1; i++) at = p.x.indexOf(terms[i]);
    var text = p.d.x;
    if (at === -1) return text.slice(0, 180) + (text.length > 180 ? '…' : '');
    var start = Math.max(0, at - 70), end = Math.min(text.length, at + 150);
    while (start > 0 && text[start - 1] !== ' ') start--;
    while (end < text.length && text[end] !== ' ') end++;
    return (start > 0 ? '…' : '') + text.slice(start, end).trim() + (end < text.length ? '…' : '');
  }
  function render(q, results) {
    var quoted = LANG === 'en' ? '“' + esc(q) + '”' : '„' + esc(q) + '”';
    if (!results.length) {
      box.innerHTML = '<p class="bx-sr-status">' + T.none + ' ' + quoted + '.</p>';
    } else {
      box.innerHTML = '<p class="bx-sr-status">' + results.length + (results.length >= MAX_RESULTS ? '+' : '') + ' ' +
        (results.length === 1 ? T.one : T.many) + ' ' + quoted + '</p><ol>' +
        results.map(function (r) {
          var d = r.p.d;
          return '<li><a href="' + esc(ROOT + d.u) + '"><span class="bx-sr-sec">' + esc(d.s) + '</span>' +
            '<span class="bx-sr-title">' + highlight(d.t, r.terms) + '</span>' +
            '<span class="bx-sr-snip">' + highlight(snippet(r.p, r.terms), r.terms) + '</span></a></li>';
        }).join('') + '</ol>';
    }
    modal.classList.add('bx-has-results');
  }
  function clear() { box.innerHTML = ''; modal.classList.remove('bx-has-results'); }

  var timer = null, lastQ = '';
  function run(immediate) {
    var q = input.value.trim();
    clearTimeout(timer);
    if (q.length < 2) {
      if (immediate && q.length) { box.innerHTML = '<p class="bx-sr-status">' + T.hint + '</p>'; modal.classList.add('bx-has-results'); }
      else clear();
      return;
    }
    timer = setTimeout(function () {
      if (q === lastQ && box.innerHTML) return;
      lastQ = q;
      if (!index) { box.innerHTML = '<p class="bx-sr-status">' + T.loading + '</p>'; modal.classList.add('bx-has-results'); }
      load().then(function () { if (input.value.trim() === q) render(q, search(q)); })
            .catch(function () { box.innerHTML = '<p class="bx-sr-status">' + T.error + '</p>'; });
    }, immediate ? 0 : 160);
  }

  // ---------------------------------------------------------------- evenimente
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    lastQ = '';
    run(true);
  }, true);
  input.addEventListener('input', function () { run(false); });
  input.removeAttribute('required');

  // la deschiderea modalului: focus în câmp și încărcarea indexului în avans
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.header_content .search')) {
      setTimeout(function () { input.focus(); }, 120);
      load().catch(function () {});
    }
    if (e.target.closest && e.target.closest('.modal_search_form .close')) {
      setTimeout(function () { clear(); }, 300);
    }
  });

  // dialogul: clic pe fundal închide; „/” deschide; pagina din spate nu se derulează cât dialogul e deschis
  function closeSearch() {
    modal.classList.remove('active');
    clear();
    var opener = document.querySelector('.header_content .search');
    if (opener && opener.focus) opener.focus();
  }
  modal.addEventListener('click', function (e) { if (e.target === modal) closeSearch(); });
  new MutationObserver(function () {
    document.body.classList.toggle('bx-search-open', modal.classList.contains('active'));
  }).observe(modal, { attributes: true, attributeFilter: ['class'] });
  document.addEventListener('keydown', function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || '';
    if (e.key === '/' && !modal.classList.contains('active') && !/INPUT|TEXTAREA|SELECT/.test(tag)) {
      e.preventDefault();
      var opener = document.querySelector('.header_content .search');
      if (opener) opener.click();
      setTimeout(function () { input.focus(); }, 60);
    }
  });
  var hint = document.createElement('p');
  hint.className = 'bx-search-hint';
  hint.textContent = LANG === 'en' ? 'Press Esc to close · / to search from any page' : 'Apăsați Esc pentru a închide · / pentru a căuta de pe orice pagină';
  form.parentNode.insertBefore(hint, box);

  // tastatură: săgeți între rezultate, Escape închide
  modal.addEventListener('keydown', function (e) {
    var links = [].slice.call(box.querySelectorAll('a'));
    var i = links.indexOf(document.activeElement);
    if (e.key === 'ArrowDown' && links.length) {
      e.preventDefault();
      (links[i + 1] || links[0]).focus();
    } else if (e.key === 'ArrowUp' && links.length) {
      e.preventDefault();
      if (i <= 0) input.focus(); else links[i - 1].focus();
    } else if (e.key === 'Escape') {
      closeSearch();
    }
  });
})();
