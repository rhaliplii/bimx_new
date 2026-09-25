"""Prima pagină bimx.md (RO și EN), restructurată din conținutul original al paginii.

Conținutul rămâne cel de pe bimx.md: hero-ul „Eveniment viitor”, știrile și „Pentru cine este BIMx?”. Se schimbă
compoziția: hero-ul prezintă BIMx (titlul și descrierea din pagina „Identitate”), evenimentul original devine un modul
mic cu dată, vizualul e semnul „x” din logo ca nod al fluxurilor pieței, iar la bază stă calendarul scurt (aceleași date
ca pe pagina calendarului, din comunicările oficiale BIMx).
"""
import datetime
import re

TODAY = datetime.date.today()

# Aceleași etape ca pe pagina „Calendarul de tranzacționare” (fixes.CALENDAR), în formă scurtă.
MILESTONES = [
    (datetime.date(2026, 8, 21), ("21 august 2026", "Licența de operator de piață obținută de la CNPF"), ("21 August 2026", "Market operator licence obtained from the CNPF")),
    (datetime.date(2026, 9, 28), ("28 septembrie 2026", "Începe admiterea brokerilor și a emitenților"),
                                 ("28 September 2026", "Admission of brokers and issuers opens")),
    (datetime.date(2026, 10, 1), ("1 octombrie 2026", "Platforma ARENA, sistemul de tranzacționare BIMx, intră în producție"), ("1 October 2026", "ARENA, the BIMx trading system, goes live")),
    (None, ("Până la sfârșitul anului 2026", "Prima listare și prima ședință de tranzacționare"), ("By the end of 2026", "First listing and first trading session")),
]
ICON_MAIL = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m3 6.5 9 6.5 9-6.5"/></svg>')
ICON_PHONE = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><path d="M21.5 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.6 4.2 2 2 0 0 1 3.6 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.7a2 2 0 0 1-.5 2.1L7.5 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.5 2.7.6a2 2 0 0 1 1.7 2z"/></svg>')
TL_LABELS = {
    "ro": {"title": "Calendarul lansării", "full": "Vizualizați calendarul complet", "done": "Finalizat", "next": "Urmează",
           "planned": "Planificat", "day": "în 1 zi", "days": "în {n} zile", "today": "astăzi"},
    "en": {"title": "Launch calendar", "full": "View the full calendar", "done": "Completed", "next": "Next",
           "planned": "Planned", "day": "in 1 day", "days": "in {n} days", "today": "today"},
}
LABELS = {"ro": {"calendar": "Calendar", "full": "Vizualizați calendarul"},
          "en": {"calendar": "Calendar", "full": "View calendar"}}
ARROW = ('<svg width="16" height="16" viewBox="0 0 17 17" fill="none" aria-hidden="true"><path d="M3.5 8.4h9.8M8.4 3.5l4.9 4.9-4.9 4.9" '
         'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def milestone_state(date):
    if date is None:
        return "planned"
    return "done" if date <= TODAY else "upcoming"


# ---------------------------------------------------------------- vizualul: semnul „x” BIMx ca nod al pieței

INTRO = {  # eticheta din subsolul original; titlul și descrierea formulate de BIMx (25.09.2026)
    "ro": ("Bursa Internațională a Moldovei (BIMx)", "Lansăm noua bursă a Moldovei",
           "O piață reglementată care oferă capital pentru companii și oportunități pentru investitori.",
           ("Prezentare generală", "prezentare-generala/index.html")),
    "en": ("Moldova International Stock Exchange (BIMx)", "Launching Moldova's new stock exchange",
           "A regulated market that provides capital for companies and opportunities for investors.",
           ("Overview", "prezentare-generala/index.html")),
}
NEXT_CTA = {"ro": ("Pregătiți dosarul de admitere", "atestarea-brokerilor/index.html"),
            "en": ("Prepare your admission file", "atestarea-brokerilor/index.html")}
# „Cum doriți să participați?” – înlocuiește blocul „Pentru cine este BIMx?” (text stabilit de BIMx, 25.09.2026)
PATHS = {
    "ro": ("Cum doriți să participați?", [
        ("Emitenți", "Listați compania", "Criterii de admitere, costuri și calendarul primei listări.",
         "Verificați etapele", "procesul-de-listare/index.html", None),
        ("Brokeri și intermediari", "Deveniți membru BIMx", "Documente necesare, conectare tehnică la ARENA și termene.",
         "Aplicați pentru admitere", "atestarea-brokerilor/index.html", "Se deschide 28.09"),
        ("Investitori", "Investiți la BIMx", "Cum puteți cumpăra acțiuni și obligațiuni prin brokeri licențiați.",
         "Ghidul investitorului", "academy/publicatii/ghidul-investitorului-incepator.html", None)]),
    "en": ("How would you like to take part?", [
        ("Issuers", "List your company", "Admission criteria, costs and the timeline for the first listing.",
         "Review the steps", "procesul-de-listare/index.html", None),
        ("Brokers and intermediaries", "Become a BIMx member", "Required documents, technical connection to ARENA and deadlines.",
         "Apply for admission", "atestarea-brokerilor/index.html", "Opens 28.09"),
        ("Investors", "Invest on BIMx", "How you can buy shares and bonds through licensed brokers.",
         "Investor guide", "academy/publicatii/ghidul-investitorului-incepator.html", None)]),
}


OPEN_LABEL = {"ro": "Deschis", "en": "Open"}


def paths_section(pg):
    title, cards = PATHS[pg.lang]
    out = []
    for who, h, desc, cta, href, badge in cards:
        badge_html = (f'<span class="bx-part-badge" data-date="2026-09-28" data-after="{OPEN_LABEL[pg.lang]}">{badge}</span>'
                      if badge else "")
        out.append(f'<article class="bx-part{" is-featured" if badge else ""}"><p class="bx-part-who">{who}{badge_html}</p>'
                   f'<h3>{h}</h3><p class="bx-part-desc">{desc}</p>'
                   f'<a class="bx-part-cta" href="{pg.link(href)}">{cta}{ARROW}</a></article>')
    return (f'<div class="bx-participate" role="region" aria-labelledby="bx-part-h"><div class="container">'
            f'<h2 id="bx-part-h">{title}</h2><div class="bx-part-grid">{"".join(out)}</div></div></div>')


# Știrile de pe prima pagină: titlu și categorie reale pentru fiecare articol (după adresă), în RO și EN
NEWS_EDIT = {
    "comunicat-de-presa": (("Licență", "BIMx a obținut licența de operator de piață de la CNPF"),
                           ("Licence", "BIMx obtains its market operator licence from the CNPF")),
    "in-atentia-actionarilor": (("Acționari", "Hotărârile adunării generale extraordinare a acționarilor din 21 august 2026"),
                                ("Shareholders", "Resolutions of the extraordinary general meeting of shareholders of 21 August 2026")),
    "bimx-depune-dosarul": (("Licență", "BIMx depune dosarul pentru obținerea licenței de operator de piață"),
                            ("Licence", "BIMx submits its application for a market operator licence")),
    "comunicat-informativ-11-iunie": (("Acționari", "Acționarii aprobă depunerea dosarului de licențiere la CNPF"),
                                      ("Shareholders", "Shareholders approve filing the licence application with the CNPF")),
    "comunicat-informativ-28-mai": (("Acționari", "Acționarii confirmă auditorul pentru exercițiul 2025–2026"),
                                    ("Shareholders", "Shareholders confirm the auditor for the 2025–2026 financial year")),
    "comunicat-informativ-02-aprilie": (("Acționari", "Acționarii aprobă contractul SaaS pentru platforma ARENA"),
                                        ("Shareholders", "Shareholders approve the SaaS contract for the ARENA platform")),
}


def news_edit(href, lang):
    for k, v in NEWS_EDIT.items():
        if k in href:
            return v[0 if lang == "ro" else 1]
    return None


# rândul de încredere de sub hero (text stabilit de BIMx, 25.09.2026): (nume, rol, pagina, rolul e un link)
TRUST_TITLE = {"ro": "Reglementat și susținut de", "en": "Regulated and backed by"}
EXT = ' target="_blank" rel="noopener"'
CNPF_REGISTER = "https://www.cnpf.md/ro/registrele-actelor-permisive-6412.html"   # registrele actelor permisive CNPF
TRUST = {
    "ro": [("CNPF", "Autoritate de supraveghere", None, False),
           ("Bursa de Valori București", "Acționar strategic", None, False),
           ("Agenția Proprietății Publice", "Acționar, 20%", None, False),
           ("Bănci și companii de asigurări", "Structura acționariatului", "fondatori/index.html", True)],
    "en": [("CNPF", "Supervisory authority", None, False),
           ("Bucharest Stock Exchange", "Strategic shareholder", None, False),
           ("Public Property Agency", "Shareholder, 20%", None, False),
           ("Banks and insurance companies", "Shareholder structure", "fondatori/index.html", True)],
}


def x_mark():
    """SVG: semnul „x” din logo (X navy + săgeata albastră), mărit, în centrul unei rețele de fluxuri.

    Fluxurile intră din stânga, se strâng în X și ies spre dreapta: piața ca punct de întâlnire. Geometria X-ului
    urmează logo-ul (două brațe diagonale, săgeata ">" în centru)."""
    W, H, cx, cy = 640, 440, 320, 220
    left = [(40, 60), (22, 140), (48, 220), (22, 300), (40, 380)]
    right = [(600, 60), (618, 140), (592, 220), (618, 300), (600, 380)]
    parts = []
    for i, (x, y) in enumerate(left):
        parts.append(f'<path class="flow flow-in" d="M{x} {y}C{x + 150} {y} {cx - 150} {cy + (y - cy) * .18:.0f} {cx - 64} {cy + (y - cy) * .1:.0f}" style="animation-delay:{i * .35:.2f}s"/>')
        parts.append(f'<circle class="end end-in" cx="{x}" cy="{y}" r="5"/>')
    for i, (x, y) in enumerate(right):
        parts.append(f'<path class="flow flow-out" d="M{cx + 64} {cy + (y - cy) * .1:.0f}C{cx + 150} {cy + (y - cy) * .18:.0f} {x - 150} {y} {x} {y}" style="animation-delay:{i * .35 + .2:.2f}s"/>')
        parts.append(f'<circle class="end end-out" cx="{x}" cy="{y}" r="5"/>')
    # X-ul: două brațe (ca în logo), săgeata albastră în centru
    s = 118
    arm = 34
    parts.append(f'<g class="xmark" transform="translate({cx} {cy})">'
                 f'<path class="x-arm" d="M{-s} {-s}h{arm * 1.6:.0f}L{s} {s}h{-arm * 1.6:.0f}Z"/>'
                 f'<path class="x-arm" d="M{s} {-s}h{-arm * 1.6:.0f}L{-s} {s}h{arm * 1.6:.0f}Z"/>'
                 f'<path class="x-chev" d="M{-58} {-58}H{-8}L{50} 0L{-8} 58H{-58}L0 0Z"/></g>')
    grid = "".join(f'<circle class="grid" cx="{gx}" cy="{gy}" r="1.2"/>' for gx in range(20, W, 40) for gy in range(20, H, 40))
    return (f'<svg class="bx-xmark" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
            f'<defs><radialGradient id="bx-x-glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#1DB0F0" stop-opacity=".14"/>'
            f'<stop offset="1" stop-color="#1DB0F0" stop-opacity="0"/></radialGradient></defs>{grid}'
            f'<circle cx="{cx}" cy="{cy}" r="200" fill="url(#bx-x-glow)"/>' + "".join(parts) + "</svg>")


# ---------------------------------------------------------------- restructurarea primei pagini

def restructure_home(text, pg):
    lab = LABELS[pg.lang]
    m = re.search(r'<div class="container_fluid">\s*<div class="main_section"[^>]*>([\s\S]*?)</div>\s*</div>\s*</div>\s*</div>', text)
    if not m:
        return text
    hero = m.group(1)
    meta = re.search(r'<div class="section_meta">([\s\S]*?)</div>', hero)
    h1 = re.search(r"<h1>([\s\S]*?)</h1>", hero)
    p = re.search(r"<p>([\s\S]*?)</p>", hero)
    buttons = re.search(r'<div class="buttons">([\s\S]*)$', hero)   # închiderea lui .buttons e în potrivirea exterioară
    if not (h1 and p and buttons):
        return text
    lines = [x.strip() for x in re.split(r"<br\s*/?>", p.group(1)) if x.strip()]
    lead, detail = lines[0], (lines[1] if len(lines) > 1 else "")

    states = [milestone_state(date) for date, _, _ in MILESTONES]
    next_i = next((i for i, st in enumerate(states) if st != "done"), None)
    cta_label, cta_path = NEXT_CTA[pg.lang]
    head, _, last = cta_label.rpartition(" ")     # săgeata rămâne lipită de ultimul cuvânt
    L = TL_LABELS[pg.lang]
    steps = []
    check = ('<svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 8.5l3 3 6-6.5" '
             'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    for i, ((date, ro, en), st) in enumerate(zip(MILESTONES, states)):
        d, title = ro if pg.lang == "ro" else en
        kind = "done" if st == "done" else ("next" if i == next_i else "planned")
        if kind == "done":
            status = f'{check}{L["done"]}'
        elif kind == "next":
            iso = date.isoformat() if date else ""
            status = f'{L["next"]}<span class="bx-lt-days" data-date="{iso}" data-one="{L["day"]}" data-many="{L["days"]}" data-today="{L["today"]}"></span>'
        else:
            status = L["planned"]
        cta_html = (f'<a class="bx-tl-cta" href="{pg.link(cta_path)}">{head} <span class="bx-nowrap">{last}{ARROW}</span></a>'
                    if kind == "next" else "")
        steps.append(f'<li class="bx-lt-step is-{kind}" data-date="{date.isoformat() if date else ""}"><span class="bx-lt-bar" aria-hidden="true"></span>'
                     f'<p class="bx-lt-status">{status}</p><time>{d}</time><p class="bx-lt-title">{title}</p>{cta_html}</li>')
    eyebrow, title, desc, (cta, cta_href) = INTRO[pg.lang]
    trust = "".join(
        f'<li><strong>{name}</strong>'
        + (f'<a class="bx-trust-link" href="{h if h.startswith("http") else pg.link(h)}"'
           f'{EXT if h.startswith("http") else ""}>{role}{ARROW}</a>' if more else f'<span>{role}</span>')
        + '</li>' for name, role, h, more in TRUST[pg.lang])

    new_hero = f'''<div class="container_fluid">
<section class="bx-home-hero" aria-labelledby="bx-home-title">
  <div class="container bx-home-hero-grid">
    <div class="bx-home-hero-copy">
      <p class="bx-home-eyebrow">{eyebrow}</p>
      <h1 id="bx-home-title">{title}</h1>
      <p class="bx-home-lead">{desc}</p>
      <div class="bx-home-actions"><a class="bx-home-cta" href="{pg.link(cta_href)}">{cta}{ARROW}</a></div>
    </div>
    <div class="bx-home-art">{x_mark()}</div>
  </div>
  <div class="container">
    <div class="bx-lt" role="region" aria-labelledby="bx-lt-h" data-done="{L["done"]}" data-next="{L["next"]}" data-planned="{L["planned"]}"
         data-one="{L["day"]}" data-many="{L["days"]}" data-today="{L["today"]}">
      <div class="bx-lt-head"><h2 id="bx-lt-h">{L["title"]}</h2>
        <a href="{pg.link("trading-calendar/index.html")}">{L["full"]}{ARROW}</a></div>
      <ol>{"".join(steps)}</ol>
    </div>
  </div>
</section>
<section class="bx-trust" aria-label="{"Cadrul BIMx" if pg.lang == "ro" else "The BIMx framework"}">
  <div class="container bx-trust-inner"><p class="bx-trust-title">{TRUST_TITLE[pg.lang]}</p><ul class="bx-trust-row">{trust}</ul></div>
</section>
'''   # containerul „container_fluid” original rămâne deschis și se închide după stilul tickerului, ca în bimx.md
    text = text[:m.start()] + new_hero + text[m.end():]
    # „Pentru cine este BIMx?” → „Cum doriți să participați?”
    who = re.search(r'<div class="container_fluid">\s*<div class="for_who_is">[\s\S]*?(?=<!--<div class="container_fluid">-->|</main>)', text)
    if who:   # cardurile (căile de conversie) stau imediat sub hero, înaintea rândului de încredere
        text = text[:who.start()] + text[who.end():]
        # în interiorul hero-ului (fundalul navy), după calendar
        text = text.replace('</section>\n<section class="bx-trust"', paths_section(pg) + '\n</section>\n<section class="bx-trust"', 1)
    # știrile și anunțurile: ultima secțiune, înainte de subsol (compactă, fără imaginea mare – vezi site.css)
    news = re.search(r'<div class="container">\s*<div class="home_posts">[\s\S]*?(?=<!--<div class="container_fluid">-->|</main>)', text)
    if news:
        block = news.group(0)
        text = text[:news.start()] + text[news.end():]
        block = re.sub(r'\s*<a class="more-link"[\s\S]*?</a>', "", block)          # „Citește mai mult” din mijlocul rezumatului
        # articolul principal: titlul real, categoria reală, rezumatul fără titlu și fără „24.08.2026, Chișinău –”
        mp = re.search(r'<div class="main_post">[\s\S]*?<a href="([^"]*)" class="read-more">', block)
        if mp and news_edit(mp.group(1), pg.lang):
            cat, head = news_edit(mp.group(1), pg.lang)
            block = re.sub(r'(<div class="post-category[^"]*">)[^<]*(</div>\s*<h2>)[^<]*(</h2>)', rf'\g<1>{cat}\g<2>{head}\3', block, count=1)
            block = re.sub(r'(<div class="post-excerpt">\s*<p>)[\s\S]*?\d{2}\.\d{2}\.\d{4},\s*Chișinău\s*[–-]\s*', r"\1", block, count=1)
        # lista: titluri și categorii reale
        def item(m):
            ed = news_edit(m.group(1), pg.lang)
            if not ed:
                return m.group(0)
            it = m.group(0)
            it = re.sub(r'(<div class="post-category">)\s*[^<]*(</div>)', rf"\g<1>{ed[0]}\2", it, count=1)
            return re.sub(r'(<h3[^>]*>)[\s\S]*?(</h3>)', rf"\g<1>{ed[1]}\2", it, count=1)
        block = re.sub(r'<a href="([^"]*)" class="list-item[^"]*">[\s\S]*?</a>', item, block)
        block = re.sub(r"(<h[23][^>]*>)\s*(COMUNICAT INFORMATIV|INFORMATION NOTICE)", lambda x: x.group(1) + x.group(2).capitalize(), block)
        block = re.sub(r"(<h2>)\s*(COMUNICAT DE PRESĂ|PRESS RELEASE)\s*(</h2>)", lambda x: x.group(1) + x.group(2).capitalize() + x.group(3), block)
        end = text.find("</main>")
        text = text[:end] + '<section class="bx-home-news">' + block + "</section>\n" + text[end:]
    # contactul pentru admitere, deasupra subsolului (adresa generală BIMx)
    q, mail_l = ("Întrebări despre admitere?", "Scrieți-ne") if pg.lang == "ro" else ("Questions about admission?", "Write to us")
    contact = (f'<section class="bx-home-contact" aria-label="{q}"><div class="container bx-home-contact-inner">'
               f'<p><strong>{q}</strong></p><p class="bx-home-contact-links">'
               f'<a href="mailto:office@bimx.md">{ICON_MAIL}office@bimx.md</a>'
               f'<span aria-hidden="true">·</span><a href="tel:+37322897700">{ICON_PHONE}+373 22 89 77 00</a></p></div></section>\n')
    end = text.find("</main>")
    text = text[:end] + contact + text[end:]
    return text
