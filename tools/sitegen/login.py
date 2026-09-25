"""Pagina „Intră în cont” (autentificare/ și en/autentificare/) și butonul din antet care duce la ea.

Site-ul e static: nu există un server de autentificare. Formularul arată cum va arăta accesul în portalul
participanților, validează câmpurile, dar nu trimite nimic (replica.js afișează un mesaj). Pagina spune clar
că portalul nu e încă activ și indică pașii reali: admiterea ca membru, atestarea agenților, admiterea emitenților.
Pagina se construiește din pagina „Politica cookie” (aceeași adâncime, antet și subsol deja corectate).
"""
import re

from .config import DIST

SLUG = "autentificare"
TEMPLATE = "politica-cookie"

T = {
    "ro": {
        "button": "Intrați în cont", "title": "Intrați în cont", "crumb": "Intrați în cont", "home": "Acasă",
        "lead": "Portalul participanților BIMx, pentru membrii bursei, agenții de bursă atestați și emitenții admiși la tranzacționare.",
        "notice_h": "Portalul nu este încă activ",
        "notice": "Conturile se creează după admiterea primilor membri și emitenți (admiterea începe pe 28 septembrie 2026). "
                  "Până atunci, autentificarea nu funcționează și datele introduse nu sunt trimise.",
        "form_h": "Autentificare", "user": "E-mail sau nume de utilizator", "password": "Parolă", "show": "Afișați parola",
        "hide": "Ascundeți parola", "remember": "Păstrați autentificarea pe acest dispozitiv", "submit": "Intrați în cont",
        "forgot": "Ați uitat parola?", "forgot_p": "Scrieți-ne la {mail}.",
        "who_h": "Cine primește acces",
        "who": [("Membrii bursei", "Societățile de investiții licențiate de CNPF și admise ca membri BIMx.", "lista-societatilor/index.html"),
                ("Agenții de bursă atestați", "Persoanele desemnate de membri, după procedura de atestare.", "atestarea-brokerilor/index.html"),
                ("Emitenții", "Companiile și autoritățile ale căror instrumente sunt admise la tranzacționare.", "procesul-de-listare/index.html")],
        "arena": "Tranzacționarea se face pe platforma ARENA, cu codul de utilizator și parola primite de fiecare agent de bursă atestat.",
        "no_account": "Nu aveți cont?", "no_account_p": "Accesul se acordă după admitere. Pentru întrebări, scrieți la {mail}.",
        "desc": "Autentificare în portalul participanților BIMx: membri, agenți de bursă atestați și emitenți.",
    },
    "en": {
        "button": "Log in", "title": "Log in", "crumb": "Log in", "home": "Home",
        "lead": "The BIMx participant portal, for exchange members, certified exchange traders and issuers admitted to trading.",
        "notice_h": "The portal is not active yet",
        "notice": "Accounts are created once the first members and issuers are admitted (admission opens on 28 September 2026). "
                  "Until then, login does not work and the details you enter are not sent.",
        "form_h": "Sign in", "user": "Email or username", "password": "Password", "show": "Show password",
        "hide": "Hide password", "remember": "Remember me on this device", "submit": "Log in",
        "forgot": "Forgot your password?", "forgot_p": "Write to us at {mail}.",
        "who_h": "Who gets access",
        "who": [("Exchange members", "Investment firms licensed by the CNPF and admitted as BIMx members.", "lista-societatilor/index.html"),
                ("Certified exchange traders", "People appointed by members, after the certification procedure.", "atestarea-brokerilor/index.html"),
                ("Issuers", "Companies and authorities whose instruments are admitted to trading.", "procesul-de-listare/index.html")],
        "arena": "Trading takes place on the ARENA platform, using the user code and password each certified exchange trader receives.",
        "no_account": "No account?", "no_account_p": "Access is granted after admission. For questions, write to {mail}.",
        "desc": "Log in to the BIMx participant portal: members, certified exchange traders and issuers.",
    },
}

MAIL = '<a href="mailto:office@bimx.md">office@bimx.md</a>'
SEP = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M5.25 10.5L8.75 7L5.25 3.5" '
       'stroke="white" stroke-opacity="0.6" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_LOCK = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>')
ICON_INFO = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
             'aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>')
ARROW = ('<svg width="16" height="16" viewBox="0 0 17 17" fill="none" aria-hidden="true"><path d="M3.5 8.4h9.8M8.4 3.5l4.9 4.9-4.9 4.9" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def header_button(text, pg):
    """Butonul „Intră în cont” din antet și elementul din meniul mobil duc la pagina de autentificare."""
    t = T[pg.lang]
    href = pg.link(f"{SLUG}/index.html")
    current = ' aria-current="page"' if pg.key == SLUG else ""
    text = re.sub(r'\s*<a href="#" data-unavailable\s+class="btn1">[^<]*</a>',
                  f'\n                    <a href="{href}" class="btn1 bx-login"{current}>{t["button"]}</a>', text, count=1)
    # meniul mobil (hide_desktop): „Log In” → pagina de autentificare; în subsol dispare (e deja în antet)
    text = re.sub(r'(<li id="menu-item-252"[^>]*>)<a href="#" data-unavailable>[^<]*</a>',
                  rf'\1<a href="{href}">{t["button"]}</a>', text, count=1)
    return text


def page_main(pg):
    t = T[pg.lang]
    who = "".join(f'<li><a href="{pg.link(href)}"><strong>{h}</strong><span>{p}</span>{ARROW}</a></li>' for h, p, href in t["who"])
    return f'''
<div class="container_fluid"><div class="second_main_section"><div class="container"><div class="secont_main_section_content">
<nav aria-label="Breadcrumb"><ul class="breadcrumbs"><li><a href="{pg.link("index.html")}">{t["home"]}</a></li><li aria-hidden="true">{SEP}</li>
<li><span aria-current="page">{t["crumb"]}</span></li></ul></nav>
<h1 class="page_title">{t["title"]}</h1><div class="page_description"><p>{t["lead"]}</p></div>
</div></div></div></div>
<div class="container"><div class="bx-login-page">
  <section class="bx-login-card" aria-labelledby="bx-login-h">
    <div class="bx-login-notice" role="note">{ICON_INFO}<div><strong>{t["notice_h"]}</strong><p>{t["notice"]}</p></div></div>
    <h2 id="bx-login-h">{ICON_LOCK}{t["form_h"]}</h2>
    <form class="bx-login-form bx-validate" action="#" method="post" data-unavailable novalidate>
      <label for="bx-user">{t["user"]}</label>
      <input id="bx-user" name="username" type="text" autocomplete="username" required>
      <label for="bx-pass">{t["password"]}</label>
      <div class="bx-pass-wrap">
        <input id="bx-pass" name="password" type="password" autocomplete="current-password" required>
        <button type="button" class="bx-pass-toggle" aria-controls="bx-pass" aria-pressed="false" data-show="{t["show"]}" data-hide="{t["hide"]}">{t["show"]}</button>
      </div>
      <label class="bx-check"><input type="checkbox" name="remember"> {t["remember"]}</label>
      <button type="submit" class="bx-btn bx-btn-primary bx-login-submit">{t["submit"]}</button>
    </form>
    <p class="bx-login-help"><strong>{t["forgot"]}</strong> {t["forgot_p"].format(mail=MAIL)}</p>
  </section>
  <aside class="bx-login-side" aria-labelledby="bx-who-h">
    <h2 id="bx-who-h">{t["who_h"]}</h2>
    <ul class="bx-who">{who}</ul>
    <p class="bx-login-arena">{t["arena"]}</p>
    <div class="bx-login-noacc"><strong>{t["no_account"]}</strong><p>{t["no_account_p"].format(mail=MAIL)}</p></div>
  </aside>
</div></div>
'''


def build_login_pages(page_cls):
    """Scrie autentificare/index.html (RO și EN) pornind de la pagina-șablon; întoarce numărul de pagini."""
    made = 0
    for lang in ("ro", "en"):
        prefix = "en/" if lang == "en" else ""
        src = DIST / f"{prefix}{TEMPLATE}" / "index.html"
        if not src.exists():
            continue
        dest = DIST / f"{prefix}{SLUG}" / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        # comutatorul de limbă și linkurile canonice spre aceeași pagină în cealaltă limbă
        text = text.replace(f"{TEMPLATE}/index.html", f"{SLUG}/index.html")
        dest.write_text(text, encoding="utf-8")
        pg = page_cls(dest)
        t = T[lang]
        m0 = re.search(r"<main\b[^>]*>", text)
        m1 = text.find("</main>")
        text = text[:m0.end()] + page_main(pg) + text[m1:]
        text = re.sub(r"<title>[^<]*</title>", f"<title>{t['title']} – BIMx</title>", text, count=1)
        text = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{t["desc"]}">', text, count=1)
        text = re.sub(r'(class="btn1 bx-login")', r'\1 aria-current="page"', text, count=1)
        dest.write_text(text, encoding="utf-8")
        made += 1
    return made
