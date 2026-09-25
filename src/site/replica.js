// Comportamentul care, pe bimx.md, depindea de server: formulare și partajare.
(function () {
  var EN = (document.documentElement.lang || '').indexOf('en') === 0;
  var MSG = EN ? 'This feature is currently unavailable.' : 'Această funcție nu este disponibilă momentan.';

  // Formularele marcate la build (contactul) nu trimit date nicăieri.
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.hasAttribute || !form.hasAttribute('data-unavailable')) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    // UI-08: câmpurile obligatorii se validează înainte de mesaj
    if (form.classList.contains('bx-validate') && !form.checkValidity()) { form.reportValidity(); return; }
    var note = form.querySelector('.replica-note');
    if (!note) {
      note = document.createElement('p');
      note.className = 'replica-note';
      note.setAttribute('role', 'status');
      note.style.cssText = 'margin:8px 0 0;font-size:14px;color:#b42318';
      form.appendChild(note);
    }
    note.textContent = MSG;
  }, true);

  // Linkurile marcate la build afișează același mesaj, fără să părăsească pagina.
  var toast;
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[data-unavailable]');
    if (!link) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    if (!toast) {
      toast = document.createElement('div');
      toast.setAttribute('role', 'status');
      toast.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:100000;' +
        'background:#1A1F67;color:#fff;padding:12px 20px;border-radius:8px;font-size:15px;' +
        'box-shadow:0 8px 24px rgba(0,0,0,.2);transition:opacity .3s';
      document.body.appendChild(toast);
    }
    toast.textContent = MSG;
    toast.style.opacity = '1';
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { toast.style.opacity = '0'; }, 3000);
  }, true);

  // Partajarea folosește adresa paginii curente.
  function share() {
    var url = location.href.split('#')[0];
    document.querySelectorAll('[data-share-base]').forEach(function (a) {
      a.href = a.getAttribute('data-share-base') + encodeURIComponent(url) + (a.getAttribute('data-share-rest') || '');
    });
    document.querySelectorAll('[data-share-self]').forEach(function (b) {
      b.setAttribute('data-link', url);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', share);
  else share();

  // ---------------------------------------------------------------- accesibilitate (audit UI-04, UI-05, UI-16, UI-22)
  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  ready(function () {
    // DIV-urile cu role="button" (căutare, burger, închidere) se activează cu Enter și Space
    document.addEventListener('keydown', function (e) {
      var el = e.target;
      if ((e.key === 'Enter' || e.key === ' ') && el.getAttribute && el.getAttribute('role') === 'button' &&
          el.tagName !== 'BUTTON' && el.tagName !== 'A') {
        e.preventDefault();
        el.click();
      }
    });

    // titlurile de grup din panoul meniului („Dezvăluirea informației”, „Piață în timp real” …) sunt doar
    // etichete: clicul nu mai pornește handlerele temei (slideToggle / clasa active), care stricau panoul
    document.addEventListener('click', function (e) {
      var label = e.target.closest && e.target.closest('#primary-menu-list .not_click > a');
      if (label) { e.preventDefault(); e.stopImmediatePropagation(); }
    }, true);

    // aria-expanded sincronizat cu starea vizuală: meniuri, burger, căutare
    function watch(el, isOpen, target) {
      if (!el || !target) return;
      var sync = function () { el.setAttribute('aria-expanded', isOpen() ? 'true' : 'false'); };
      new MutationObserver(sync).observe(target, { attributes: true, attributeFilter: ['class', 'style'] });
      sync();
    }
    document.querySelectorAll('#primary-menu-list > li.menu-item-has-children > a[aria-haspopup]').forEach(function (a) {
      var sub = a.parentNode.querySelector(':scope > ul.sub-menu');
      watch(a, function () { return sub.classList.contains('active'); }, sub);
    });
    var burger = document.querySelector('.header_content .burger');
    watch(burger, function () { return burger.classList.contains('active'); }, burger);
    var search = document.querySelector('.header_content .search');
    var modal = document.querySelector('.modal_search_form');
    watch(search, function () { return modal.classList.contains('active'); }, modal);

    // Escape: închide submeniul (focus înapoi pe meniu), modalurile și avertizarea
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var open = document.querySelector('#primary-menu-list ul.sub-menu.active');
      if (open) {
        document.querySelectorAll('#primary-menu-list ul.sub-menu.active').forEach(function (u) { u.classList.remove('active'); });
        var top = open.closest('#primary-menu-list > li');
        if (top && top.firstElementChild) top.firstElementChild.focus();
        return;
      }
      var member = [].slice.call(document.querySelectorAll('.modal_overlay')).filter(function (m) { return m.offsetParent !== null; })[0];
      if (member) { var c = member.querySelector('.close'); if (c) c.click(); return; }
      var contact = document.querySelector('.contact_modal_overlay.active .close');
      if (contact) { contact.click(); return; }
      var popup = document.getElementById('ds-popup-1');
      if (popup && popup.classList.contains('ds-active')) {
        var ok = popup.querySelector('.ds-close-popup');
        if (ok) ok.click();
      }
    });

    // Biografiile din Consiliu: dialog, focus pe „Închide” la deschidere, înapoi pe „Detalii” la închidere
    document.querySelectorAll('.modal_content_member').forEach(function (d) {
      d.setAttribute('role', 'dialog');
      d.setAttribute('aria-modal', 'true');
      var name = d.querySelector('h4, h3');
      if (name) d.setAttribute('aria-label', name.textContent.trim());
    });
    var lastOpener = null;
    document.addEventListener('click', function (e) {
      var btn = e.target.closest && e.target.closest('.member button');
      if (btn) {
        lastOpener = btn;
        setTimeout(function () {
          var c = btn.closest('.member').querySelector('.modal_overlay .close');
          if (c) c.focus();
        }, 450);
      }
      // clic pe fundalul întunecat (în afara ferestrei) o închide
      if (e.target.classList && e.target.classList.contains('modal_overlay')) {
        var close = e.target.querySelector('.close');
        if (close) close.click();
      }
      if (e.target.closest && e.target.closest('.modal_overlay .close') && lastOpener) {
        var o = lastOpener; lastOpener = null;
        setTimeout(function () { o.focus(); }, 450);
      }
    });

    // Avertizarea despre datele demonstrative: focus pe „Am înțeles” când apare
    var popup = document.getElementById('ds-popup-1');
    if (popup) {
      var focused = false;
      new MutationObserver(function () {
        if (!focused && popup.classList.contains('ds-active')) {
          focused = true;
          var ok = popup.querySelector('.ds-close-popup');
          if (ok) setTimeout(function () { ok.focus(); }, 50);
        }
      }).observe(popup, { attributes: true, attributeFilter: ['class', 'style'] });
    }

    // Pagina de autentificare: afișează / ascunde parola
    document.querySelectorAll('.bx-pass-toggle').forEach(function (b) {
      b.addEventListener('click', function () {
        var input = document.getElementById(b.getAttribute('aria-controls'));
        var show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        b.setAttribute('aria-pressed', show ? 'true' : 'false');
        b.textContent = show ? b.getAttribute('data-hide') : b.getAttribute('data-show');
      });
    });

    // Meniul mobil începe exact sub antet (banda de stare de deasupra se derulează, deci poziția variază)
    var hc = document.querySelector('.header_content');
    var setTop = function () {
      if (hc) document.documentElement.style.setProperty('--bx-menu-top', Math.max(0, Math.round(hc.getBoundingClientRect().bottom)) + 'px');
    };
    setTop();
    window.addEventListener('scroll', setTop, { passive: true });
    window.addEventListener('resize', setTop);
    document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('.burger')) setTop(); }, true);

    // Stările din calendare se recalculează la fiecare vizită (site-ul e static): finalizat / urmează / planificat
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var dayOf = function (iso) { return iso ? new Date(iso + 'T00:00:00') : null; };
    var CHECK = '<svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 8.5l3 3 6-6.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var states = function (items) {
      var kinds = items.map(function (li) { var d = dayOf(li.getAttribute('data-date')); return d && d <= today ? 'done' : 'todo'; });
      var first = kinds.indexOf('todo');
      return kinds.map(function (k, i) { return k === 'done' ? 'done' : (i === first ? 'next' : 'planned'); });
    };
    // calendarul din hero
    document.querySelectorAll('.bx-lt').forEach(function (box) {
      var items = [].slice.call(box.querySelectorAll('.bx-lt-step'));
      states(items).forEach(function (k, i) {
        var li = items[i], st = li.querySelector('.bx-lt-status');
        li.classList.remove('is-done', 'is-next', 'is-planned'); li.classList.add('is-' + k);
        if (k === 'done') { st.innerHTML = CHECK + box.getAttribute('data-done'); return; }
        if (k === 'planned') { st.textContent = box.getAttribute('data-planned'); return; }
        var d = dayOf(li.getAttribute('data-date')), extra = '';
        if (d) {
          var n = Math.round((d - today) / 86400000);
          extra = n === 0 ? box.getAttribute('data-today') : n === 1 ? box.getAttribute('data-one') : box.getAttribute('data-many').replace('{n}', n);
        }
        st.innerHTML = box.getAttribute('data-next') + (extra ? '<span class="bx-lt-days">' + extra + '</span>' : '');
      });
      // mobil: progresul, „Etapa X din N”, lista pliată (ultima etapă finalizată + următoarea)
      var ks = states(items), nxt = ks.indexOf('next'), lastDone = ks.lastIndexOf('done');
      items.forEach(function (li, i) { li.classList.toggle('is-old', ks[i] === 'done' && i !== lastDone); });
      box.querySelectorAll('.bx-lt-prog span').forEach(function (s, i) { s.className = 'is-' + (ks[i] || 'planned'); });
      var of = box.querySelector('.bx-lt-of');
      if (of) of.textContent = of.getAttribute('data-tpl').replace('{i}', nxt < 0 ? items.length : nxt + 1).replace('{n}', items.length);
      var more = box.querySelector('.bx-lt-more');
      if (more) more.addEventListener('click', function () {
        var all = box.classList.toggle('is-all');
        more.setAttribute('aria-expanded', all ? 'true' : 'false');
        more.textContent = more.getAttribute(all ? 'data-less' : 'data-all');
      });
    });
    // pagina calendarului
    document.querySelectorAll('.bx-timeline[data-done]').forEach(function (ol) {
      var items = [].slice.call(ol.querySelectorAll('.bx-step'));
      var ks = states(items);
      ks.forEach(function (k, i) {
        var li = items[i];
        li.classList.remove('is-done', 'is-next', 'is-planned', 'seg-done'); li.classList.add('is-' + k);
        if (k === 'done' && ks[i + 1] === 'done') li.classList.add('seg-done');
        var st = li.querySelector('.bx-step-state'); if (st) st.textContent = ol.getAttribute('data-' + k);
      });
    });
    // eticheta „Se deschide 28.09” → „Deschis” după dată
    document.querySelectorAll('.bx-part-badge[data-date]').forEach(function (b) {
      var d = dayOf(b.getAttribute('data-date'));
      if (d && d <= today) { b.textContent = b.getAttribute('data-after'); b.classList.add('is-open'); }
    });

    // Hero „X”: reflexie de lumină o singură dată la încărcare, apoi înclinare discretă (≤ 2,5°) după mouse
    var art = document.querySelector('.bx-home-art-img');
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (art && !still) {
      var tilt = art.querySelector('.bx-tilt'), sheen = art.querySelector('.bx-sheen'), img = art.querySelector('img');
      var start = function () {
        // masca reflexiei = forma X-ului; pe file:// browserul blochează imaginea ca mască, deci reflexia trece fără mască
        if (location.protocol !== 'file:') sheen.style.setProperty('--bx-mask', 'url("' + img.currentSrc + '")');
        else sheen.classList.add('no-mask');
        sheen.classList.add('run');
      };
      if (img.complete) start(); else img.addEventListener('load', start, { once: true });
      if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        var hero = document.querySelector('.bx-home-hero'), raf = 0, MAX = 3;
        hero.addEventListener('mousemove', function (e) {
          cancelAnimationFrame(raf);
          raf = requestAnimationFrame(function () {
            var r = hero.getBoundingClientRect();
            var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
            tilt.style.transform = 'rotateY(' + (x * 2 * MAX).toFixed(2) + 'deg) rotateX(' + (-y * 2 * MAX).toFixed(2) + 'deg) ' +
              'translate3d(' + (x * 10).toFixed(1) + 'px,' + (y * 8).toFixed(1) + 'px,0)';
          });
        });
        hero.addEventListener('mouseleave', function () { tilt.style.transform = ''; });
      }
    }

    // Subsolul: pe mobil coloanele sunt pliate, pe desktop deschise
    var fcols = document.querySelectorAll('.bx-f-col');
    var fmq = window.matchMedia('(max-width: 768px)');
    var fsync = function () { fcols.forEach(function (d) { d.open = !fmq.matches; }); };
    fsync();
    if (fmq.addEventListener) fmq.addEventListener('change', fsync);

    // Tickerul: pauză / pornire
    document.querySelectorAll('.bx-ticker-toggle').forEach(function (b) {
      b.addEventListener('click', function () {
        var wrap = b.closest('.bx-ticker');
        var paused = wrap.classList.toggle('paused');
        b.setAttribute('aria-pressed', paused ? 'true' : 'false');
        b.textContent = paused ? b.getAttribute('data-play') : b.getAttribute('data-pause');
      });
    });
  });
})();
