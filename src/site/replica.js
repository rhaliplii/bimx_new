// Comportamentul care, pe bimx.md, depindea de server: formulare și partajare.
(function () {
  var HL = document.documentElement.lang || '';
  var EN = HL.indexOf('en') === 0, RU = HL.indexOf('ru') === 0, UK = HL.indexOf('uk') === 0;
  var MSG = EN ? 'This feature is currently unavailable.' : RU ? 'Эта функция пока недоступна.' : UK ? 'Ця функція поки що недоступна.'
    : 'Această funcție nu este disponibilă momentan.';

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
      var member = [].slice.call(document.querySelectorAll('.modal_overlay')).filter(function (m) { return getComputedStyle(m).display !== 'none'; })[0];   // overlay-ul e fixed: offsetParent e mereu null
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
      // numele și funcția lângă portret; biografia dedesubt, într-un bloc care pe desktop se derulează singur
      if (!d.querySelector('.bx-member-text')) {
        var head = document.createElement('div'), col = document.createElement('div');
        head.className = 'bx-member-head'; col.className = 'bx-member-text';
        [].slice.call(d.children).forEach(function (c) {
          if (c.classList.contains('close') || c.classList.contains('img_wrap')) return;
          (/^(H4|H3|SPAN)$/.test(c.tagName) && !col.children.length ? head : col).appendChild(c);
        });
        d.appendChild(head); d.appendChild(col);
      }
    });
    // toată cartela membrului e clicabilă (deschide biografia, ca „Detalii”)
    document.querySelectorAll('.team .member').forEach(function (m) {
      m.addEventListener('click', function (e) {
        if (e.target.closest('.modal_overlay, button, a')) return;
        var b = m.querySelector(':scope > .member_content button, button');
        if (b) b.click();
      });
    });
    // cât timp biografia e deschisă, pagina din spate nu se derulează
    var lockObs = new MutationObserver(function () {
      var open = [].slice.call(document.querySelectorAll('.team .modal_overlay')).some(function (o) { return getComputedStyle(o).display !== 'none'; });
      document.documentElement.style.overflow = open ? 'hidden' : '';
    });
    document.querySelectorAll('.team .modal_overlay').forEach(function (o) { lockObs.observe(o, { attributes: true, attributeFilter: ['style'] }); });
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
      if (box.hasAttribute('data-fixed')) {
        // stări fixe: doar eticheta etapei curente se schimbă din „Urmează” în „Deschis” la data ei; fără numărătoare
        items.forEach(function (li) {
          if (!li.classList.contains('is-next')) return;
          var d = dayOf(li.getAttribute('data-date')), st = li.querySelector('.bx-lt-status');
          st.textContent = box.getAttribute(d && d <= today ? 'data-open' : 'data-next');
        });
      } else states(items).forEach(function (k, i) {
        var li = items[i], st = li.querySelector('.bx-lt-status');
        li.classList.remove('is-done', 'is-next', 'is-planned'); li.classList.add('is-' + k);
        if (k === 'done') { st.innerHTML = CHECK + box.getAttribute('data-done'); return; }
        if (k === 'planned') { st.textContent = box.getAttribute('data-planned'); return; }
        var d = dayOf(li.getAttribute('data-date')), extra = '';
        if (d) {
          var n = Math.round((d - today) / 86400000);
          var few = box.getAttribute('data-few'), d10 = n % 10, d100 = n % 100;
          var form = !few ? (n === 1 ? 'data-one' : 'data-many')                      // rusă / ucraineană: „через 1 день / 3 дня / 5 дней”
            : (d10 === 1 && d100 !== 11) ? 'data-one' : (d10 >= 2 && d10 <= 4 && (d100 < 12 || d100 > 14)) ? 'data-few' : 'data-many';
          extra = n === 0 ? box.getAttribute('data-today') : box.getAttribute(form).replace('{n}', n);
        }
        st.innerHTML = box.getAttribute('data-next') + (extra ? '<span class="bx-lt-days">' + extra + '</span>' : '');
      });
      // mobil: progresul, „Etapa X din N”, lista pliată (ultima etapă finalizată + următoarea)
      var ks = box.hasAttribute('data-fixed')
        ? items.map(function (li) { return li.classList.contains('is-done') ? 'done' : li.classList.contains('is-next') ? 'next' : 'planned'; })
        : states(items);
      var nxt = ks.indexOf('next'), lastDone = ks.lastIndexOf('done');
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

    // Banda de sus: dacă mesajul nu încape (mobil), curge continuu spre stânga, ca o bandă de știri („Pre-lansare” rămâne fix)
    var strip = document.querySelector('.bx-strip'), move = strip && strip.querySelector('.bx-strip-move');
    if (move) {
      var item = move.querySelector('.bx-strip-item');
      var fit = function () {
        strip.classList.remove('is-marquee');
        [].slice.call(move.querySelectorAll('.bx-strip-clone')).forEach(function (c) { c.remove(); });
        if (item.scrollWidth <= strip.clientWidth + 1) return;
        var clone = item.cloneNode(true);                       // a doua copie: bucla fără gol vizibil
        clone.classList.add('bx-strip-clone'); clone.setAttribute('aria-hidden', 'true');
        move.appendChild(clone);
        var dist = item.getBoundingClientRect().width + parseFloat(getComputedStyle(item).paddingRight || 0);
        strip.style.setProperty('--bx-strip-dist', -dist + 'px');
        strip.style.setProperty('--bx-strip-time', Math.round(dist / 35) + 's');   // ~35 px/s
        strip.classList.add('is-marquee');
      };
      fit();
      var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(fit, 150); });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    }

    // Selectorul de limbă: lista se deschide la clic, se închide la clic în afară sau cu Escape
    document.querySelectorAll('.bx-lang').forEach(function (box) {
      var btn = box.querySelector('.bx-lang-btn'), menu = box.querySelector('.bx-lang-menu');
      if (!btn || !menu) return;
      var set = function (open) {
        menu.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) { var cur = menu.querySelector('a[aria-current]') || menu.querySelector('a'); if (cur) cur.focus(); }
      };
      btn.addEventListener('click', function (e) { e.stopPropagation(); set(menu.hidden); });
      document.addEventListener('click', function (e) { if (!box.contains(e.target)) set(false); });
      box.addEventListener('keydown', function (e) {
        var links = [].slice.call(menu.querySelectorAll('a')), i = links.indexOf(document.activeElement);
        if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); }
        else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && !menu.hidden) {
          e.preventDefault(); links[(i + (e.key === 'ArrowDown' ? 1 : links.length - 1)) % links.length].focus();
        }
      });
    });

    // Subsolul: pe mobil coloanele sunt pliate, pe desktop deschise
    var fcols = document.querySelectorAll('.bx-f-col');
    var fmq = window.matchMedia('(max-width: 768px)');
    var fsync = function () { fcols.forEach(function (d) { d.open = !fmq.matches; }); };
    fsync();
    if (fmq.addEventListener) fmq.addEventListener('change', fsync);

    // „Noutăți & Comunicate”: filtrele din pagină – categoria („Anunțuri BIMx”) și anul (toate paginile cu articole).
    // Filtrele stau în adresă (?cat=…&an=…), ca linkul să poată fi trimis.
    var news = document.querySelector('.bx-news');
    // eticheta „Nou”: doar cât timp cel mai recent articol are cel mult data-days zile (pagina e generată static)
    document.querySelectorAll('.bx-n-new').forEach(function (b) {
      var age = (Date.now() - new Date(b.getAttribute('data-date') + 'T00:00:00').getTime()) / 864e5;
      if (age > +b.getAttribute('data-days')) b.remove();
    });
    // pe mobil, taburile sunt un select: alegerea deschide pagina tabului
    var tabSel = document.querySelector('.bx-news-tabbar select[data-nav="tab"]');
    if (tabSel) tabSel.addEventListener('change', function () { location.href = tabSel.value; });
    var yearSel = document.querySelector('.bx-news-tabbar select[data-filter="an"]');         // în rândul taburilor, doar dacă există mai mulți ani
    var catSel = document.querySelector('.bx-news-tabbar select[data-filter="cat"]');          // doar la „Anunțuri BIMx”
    if (news && (yearSel || catSel)) {
      var items = [].slice.call(news.querySelectorAll('.bx-news-item'));
      var none = news.querySelector('.bx-news-none');
      var q = new URLSearchParams(location.search);
      var yearDef = yearSel ? yearSel.getAttribute('data-default') : 'toate';   // implicit: cel mai recent an
      var f = { cat: q.get('cat') || 'toate', an: q.get('an') || yearDef };
      if (!catSel || ![].some.call(catSel.options, function (o) { return o.value === f.cat; })) f.cat = 'toate';
      if (!yearSel || ![].some.call(yearSel.options, function (o) { return o.value === f.an; })) f.an = yearDef;
      var render = function (save) {
        if (catSel) catSel.value = f.cat;
        if (yearSel) yearSel.value = f.an;
        var n = 0;
        items.forEach(function (it) {
          var ok = (f.cat === 'toate' || it.getAttribute('data-cat') === f.cat) && (f.an === 'toate' || it.getAttribute('data-year') === f.an);
          it.hidden = !ok;
          if (ok) n++;
        });
        none.hidden = n > 0;
        if (save) {
          var p = new URLSearchParams();
          if (f.cat !== 'toate') p.set('cat', f.cat);
          if (f.an !== yearDef) p.set('an', f.an);
          history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p.toString() : '') + location.hash);
        }
      };
      if (catSel) catSel.addEventListener('change', function () { f.cat = catSel.value; render(true); });
      if (yearSel) yearSel.addEventListener('change', function () { f.an = yearSel.value; render(true); });
      render(false);
    }

    // Umbra antetului după derulare: apare după 12 px și dispare abia sub 4 px (histerezis), ca derularea elastică
    // a trackpadului lângă vârful paginii să nu o aprindă și stingă în buclă
    var hdr = document.querySelector('header.site-header');
    if (hdr) {
      var shadowOn = false, onScroll = function () {
        var y = Math.max(0, window.scrollY || window.pageYOffset || 0);
        var want = shadowOn ? y > 4 : y > 12;
        if (want !== shadowOn) { shadowOn = want; hdr.classList.toggle('bx-scrolled', want); }
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }

    // Meniul principal pe desktop: panoul se deschide la hover (cu o mică întârziere, ca trecerea mouse-ului peste meniu
    // să nu deschidă panouri) și se închide la ieșirea din meniu; clicul pe un element doar deschide (nu închide) panoul.
    // Pe ecranele tactile late (≥1200 px) atingerea deschide / închide panoul (tema), iar stările vizuale sunt aceleași.
    var wide = window.matchMedia('(min-width: 1200px)');
    var desk = window.matchMedia('(min-width: 1200px) and (hover: hover) and (pointer: fine)');
    var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
    var menu = document.getElementById('primary-menu-list');
    if (menu) {
      var tops = [].slice.call(menu.querySelectorAll(':scope > li.bx-dd'));
      var timer = null, stateTimer = null, shown = null;
      // panoul și bara cyan pornesc exact de la marginea de jos a antetului (acoperă linia de 1 px)
      var bar = document.querySelector('header.site-header .header_content');
      var ind = document.createElement('span'); ind.className = 'bx-nav-ind'; ind.setAttribute('aria-hidden', 'true');
      menu.appendChild(ind);
      var shade = document.createElement('div'); shade.className = 'bx-nav-backdrop'; shade.setAttribute('aria-hidden', 'true');
      document.body.appendChild(shade);
      var panelOf = function (li) { return li && li.querySelector(':scope > ul.sub-menu'); };
      var openLi = function () { return tops.filter(function (t) { var u = panelOf(t); return u && u.classList.contains('active'); })[0] || null; };
      // indicatorul comun: poziția și lățimea elementului, relativ la listă (transform: translateX + scaleX)
      var aim = function (li, jump) {
        if (!li) return;
        var m = menu.getBoundingClientRect(), r = li.getBoundingClientRect();
        if (jump) { ind.classList.add('jump'); }
        ind.style.setProperty('--bx-ind-x', (r.left - m.left) + 'px');
        ind.style.setProperty('--bx-ind-w', r.width);
        if (jump) { void ind.offsetWidth; ind.classList.remove('jump'); }
      };
      var place = function () {
        if (!wide.matches || !bar) return;
        var bottom = bar.getBoundingClientRect().bottom, mtop = menu.getBoundingClientRect().top;
        tops.forEach(function (li) { li.style.setProperty('--bx-dd-top', (bottom - li.getBoundingClientRect().top - 1) + 'px'); });
        ind.style.setProperty('--bx-ind-top', (bottom - mtop - 2) + 'px');
        document.documentElement.style.setProperty('--bx-hdr-bottom', Math.max(0, bottom) + 'px');
        if (shown) aim(shown, true);
      };
      place();
      window.addEventListener('resize', place);
      window.addEventListener('scroll', function () { if (shown) place(); }, { passive: true });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);
      // stările: prima deschidere (panoul alunecă, linkurile apar pe rând), trecere (doar conținutul se estompează), închidere
      var mark = function (cls, ms) {
        menu.classList.remove('bx-dd-opening', 'bx-dd-switching');
        clearTimeout(stateTimer);
        if (!cls) return;
        void menu.offsetWidth;   // repornește animația linkurilor și la treceri rapide între meniuri
        menu.classList.add.apply(menu.classList, cls.split(' '));
        stateTimer = setTimeout(function () { menu.classList.remove('bx-dd-opening', 'bx-dd-switching'); }, ms);
      };
      var stagger = function (li) {
        var items = [].slice.call(panelOf(li).querySelectorAll('li.not_click > ul.sub-menu > li, :scope > li.bx-dd-feature, :scope > li.bx-dd-foot'));
        items.forEach(function (it, k) { it.style.setProperty('--bx-d', Math.min(k * 25, 175) + 'ms'); });
      };
      var sync = function () {
        var li = openLi();
        if (li === shown) return;
        var prev = shown; shown = li;
        if (!wide.matches) { mark(null); return; }
        if (li && !prev) {
          place(); stagger(li); mark(calm.matches ? null : 'bx-dd-opening', 560);
          aim(li, true); void ind.offsetWidth;
          ind.classList.add('on'); shade.classList.add('on');
        } else if (li && prev) {
          stagger(li); mark(calm.matches ? null : 'bx-dd-opening bx-dd-switching', 480);
          aim(li, calm.matches);
        } else {
          mark(null);
          ind.classList.remove('on'); shade.classList.remove('on');
        }
      };
      tops.forEach(function (li) { var u = panelOf(li); if (u) new MutationObserver(sync).observe(u, { attributes: true, attributeFilter: ['class'] }); });
      var openOnly = function (li) {
        tops.forEach(function (t) {
          var u = panelOf(t);
          if (u) u.classList.toggle('active', t === li);
        });
      };
      var links = function (li) {
        return [].slice.call(panelOf(li).querySelectorAll('a')).filter(function (a) { return a.offsetParent !== null; });
      };
      tops.forEach(function (li) {
        var trig = li.querySelector(':scope > a');
        li.addEventListener('mouseenter', function () {
          if (!desk.matches) return;
          clearTimeout(timer);
          // dacă un panou e deja deschis, trecerea la alt element e imediată; altfel o mică întârziere de intenție
          if (shown === li) return;
          timer = setTimeout(function () { openOnly(li); }, shown ? 40 : 90);
        });
        trig.addEventListener('click', function (e) {
          if (!desk.matches) return;
          e.preventDefault(); e.stopImmediatePropagation();
          clearTimeout(timer);
          var u = panelOf(li);
          openOnly(u && u.classList.contains('active') && e.detail === 0 ? null : li);   // tastatura (Enter) comută; mouse-ul deschide
        }, true);
        // tastatura: Enter / Spațiu / ↓ pe element deschid panoul și mută focusul pe primul link; ←/→ între elemente
        trig.addEventListener('keydown', function (e) {
          if (!wide.matches) return;
          var k = tops.indexOf(li);
          if (e.key === 'ArrowDown' || e.key === ' ' || e.key === 'Enter') {
            e.preventDefault(); e.stopImmediatePropagation();
            clearTimeout(timer);
            if (e.key === 'Enter' && panelOf(li).classList.contains('active')) { openOnly(null); return; }
            openOnly(li);
            var first = links(li)[0];
            if (first) first.focus();
          } else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
            e.preventDefault();
            var next = tops[(k + (e.key === 'ArrowRight' ? 1 : -1) + tops.length) % tops.length];
            next.querySelector(':scope > a').focus();
            if (shown) openOnly(next);
          }
        });
        // în panou: ↑/↓ între linkuri (↑ de pe primul revine la element), Home / End
        panelOf(li).addEventListener('keydown', function (e) {
          if (['ArrowDown', 'ArrowUp', 'Home', 'End'].indexOf(e.key) < 0) return;
          var all = links(li), i = all.indexOf(document.activeElement);
          if (i < 0) return;
          e.preventDefault();
          if (e.key === 'Home') all[0].focus();
          else if (e.key === 'End') all[all.length - 1].focus();
          else if (e.key === 'ArrowDown') all[Math.min(i + 1, all.length - 1)].focus();
          else if (i === 0) trig.focus();
          else all[i - 1].focus();
        });
        // focusul de tastatură pe un element mută indicatorul, dacă un panou e deschis
        trig.addEventListener('focus', function () { if (shown && shown !== li && wide.matches) { clearTimeout(timer); openOnly(li); } });
      });
      // revenirea în meniu (inclusiv în panou) anulează închiderea programată
      menu.addEventListener('mouseenter', function () { if (desk.matches) clearTimeout(timer); });
      menu.addEventListener('mouseleave', function () {
        if (!desk.matches) return;
        clearTimeout(timer);
        timer = setTimeout(function () { openOnly(null); }, 280);
      });
      // focusul iese din meniu (Tab după ultimul link): panoul se închide
      menu.addEventListener('focusout', function (e) {
        if (wide.matches && e.relatedTarget && !menu.contains(e.relatedTarget)) openOnly(null);
      });
      // atingere / clic în afara meniului închide panoul
      document.addEventListener('pointerdown', function (e) {
        if (shown && wide.matches && !menu.contains(e.target)) openOnly(null);
      });
      var reset = function () { if (!wide.matches) { openOnly(null); ind.classList.remove('on'); shade.classList.remove('on'); shown = null; } else place(); };
      if (wide.addEventListener) wide.addEventListener('change', reset);
    }

    // Galeria foto: fotografia mărită (dialog), cu săgeți ←/→, Escape și descărcare
    var lb = document.querySelector('dialog.bx-lb');
    var shots = [].slice.call(document.querySelectorAll('.bx-photo'));
    if (lb && shots.length && lb.showModal) {
      var lbImg = lb.querySelector('img'), lbCap = lb.querySelector('figcaption'), lbCount = lb.querySelector('.bx-lb-count'),
          lbDl = lb.querySelector('.bx-lb-dl'), cur = 0, opener = null;
      var show = function (k) {
        cur = (k + shots.length) % shots.length;
        var s = shots[cur];
        lbImg.src = s.getAttribute('data-full'); lbImg.alt = s.getAttribute('data-alt');
        lbImg.width = +s.getAttribute('data-w'); lbImg.height = +s.getAttribute('data-h');
        lbCap.textContent = s.getAttribute('data-caption');
        lbCount.textContent = (cur + 1) + ' / ' + shots.length;
        lbDl.href = s.getAttribute('data-full');
      };
      shots.forEach(function (s, k) {
        s.addEventListener('click', function () { opener = s; show(k); lb.showModal(); });
      });
      lb.querySelector('.bx-lb-prev').addEventListener('click', function () { show(cur - 1); });
      lb.querySelector('.bx-lb-next').addEventListener('click', function () { show(cur + 1); });
      lb.querySelector('.bx-lb-close').addEventListener('click', function () { lb.close(); });
      lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });   // clic pe fundal
      lb.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); show(cur + 1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show(cur - 1); }
      });
      lb.addEventListener('close', function () { if (opener) opener.focus(); });
      if (shots.length < 2) lb.classList.add('single');
    }

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
