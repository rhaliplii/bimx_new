"""Sistemul de iconițe al paginilor bimx.md (BIMx Academy are setul ei și nu e atinsă).

O singură bibliotecă: grilă 24 × 24, contur 1,75 (1,9 la 16 px), capete și colțuri rotunjite, fără umpluturi, culoarea
din CSS (currentColor). Fiecare concept are simbolul lui; același simbol apare doar pentru același concept (de ex. calendarul
pentru toate blocurile „Stare”, balanța pentru toate regulile pieței).

Iconițele se atribuie pe pagină și în ordinea din pagină (identică în RO și EN):
- CARDS: iconițele din cardurile cu placă (.icon) → placă 48 px cu simbol 24 px;
- CHECKS: marcatorii listelor de verificare (.item > .icon) → bifă 20 px, fără placă;
- LABELS: iconițele din etichetele de secțiune (<h6>) → 16 px.
"""
import re

P = {
    # instituții și piață
    "landmark": '<path d="M3 21h18M5 21V10M9.5 21V10M14.5 21V10M19 21V10M2.5 10 12 4l9.5 6"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8.5 7.5h1M14.5 7.5h1M8.5 11.5h1M14.5 11.5h1M8.5 15.5h1M14.5 15.5h1M10 21v-3h4v3"/>',
    "office": '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16M16 9h2a2 2 0 0 1 2 2v10M2 21h20M8 7h4M8 11h4M8 15h4"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
    "building-plus": '<path d="M3 21h12M5 21V10l6-4.5L17 10v3M9 21v-4h4v4M19 15v6M16 18h6"/>',
    "merge": '<circle cx="6" cy="5.5" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="M6 8v13M6 9.5c0 5 4 9 9.5 9"/>',
    "server": '<rect x="3" y="3.5" width="18" height="7" rx="1.5"/><rect x="3" y="13.5" width="18" height="7" rx="1.5"/><path d="M7 7h.01M7 17h.01M11 7h6M11 17h6"/>',
    "monitor": '<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M8 21h8M12 17v4M6.5 13l3-3 3 2 4.5-4.5"/>',
    "trending": '<path d="M3 17l6-6 4 4 8-8M14.5 7H21v6.5"/>',
    "bar-chart": '<path d="M3 3v18h18M8 17v-5M13 17V8M18 17v-9"/>',
    "line-chart": '<path d="M3 3v18h18M7 14l4-4 3 3 5-6"/>',
    "candles": '<path d="M8 3v4M8 15v6M16 3v8M16 17v4"/><rect x="5.5" y="7" width="5" height="8" rx="1"/><rect x="13.5" y="11" width="5" height="6" rx="1"/>',
    "pie": '<path d="M21 12A9 9 0 1 1 12 3v9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
    "branch": '<circle cx="6" cy="18.5" r="2.5"/><circle cx="6" cy="5.5" r="2.5"/><circle cx="18" cy="8" r="2.5"/><path d="M6 8v8M18 10.5c0 4-4 5.5-9.5 7"/>',
    "file-stack": '<path d="M15.5 3H7a2 2 0 0 0-2 2v11"/><rect x="8" y="7" width="12" height="14" rx="2"/><path d="M11 12h6M11 16h4"/>',
    "ticket-percent": '<path d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2.5a2.5 2.5 0 0 0 0 5V17a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2.5a2.5 2.5 0 0 0 0-5z"/><path d="M9 15l6-6M9.5 9.5h.01M14.5 14.5h.01"/>',
    "banknote": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>',
    # date și documente
    "calendar": '<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4M8 14h.01M12 14h.01M16 14h.01M8 17.5h.01M12 17.5h.01"/>',
    "cycle": '<path d="M20.5 12A8.5 8.5 0 0 1 6 18M3.5 12A8.5 8.5 0 0 1 18 6"/><path d="M18 2.5V6h-3.5M6 21.5V18h3.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "sunset": '<path d="M3 18h18M7 18a5 5 0 0 1 10 0M12 3v6M9 6.5l3 3 3-3M4.5 11.5l1.5 1.5M19.5 11.5 18 13M3 21.5h18"/>',
    "id-card": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><circle cx="8.5" cy="11" r="2"/><path d="M5.5 16a3 3 0 0 1 6 0M14.5 10h4M14.5 14h2.5"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M8 13h8"/>',
    "file-chart": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8.5 17v-2M12 17v-4M15.5 17v-6"/>',
    "newspaper": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h4M7 16h4"/><rect x="13" y="12" width="4" height="4" rx=".5"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    "file-text": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
    # reglementare și încredere
    "scale": '<path d="M12 3v18M7 21h10M4 7h16M12 3l-1 4M6 7l-3 7a3 3 0 0 0 6 0zM18 7l-3 7a3 3 0 0 0 6 0z"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="M8.5 13.9 7 22l5-3 5 3-1.5-8.1"/>',
    "clipboard-check": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 13l2 2 4-4"/>',
    "shield-check": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "flag": '<path d="M5 21V4M5 4h13l-2.5 4.5L18 13H5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "gem": '<path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20M12 21 8.5 9 12 3l3.5 6z"/>',
    # oameni
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6 6 0 0 1 3.5 5.5"/>',
    "handshake": '<path d="M11 17l2 2a1.5 1.5 0 0 0 2-2M13 15l2.5 2.5a1.5 1.5 0 0 0 2-2L14 12M3 11l4-4 4 1 3-1 7 5-2.5 2.5M3 11l6 6a1.5 1.5 0 0 0 2-2M7 7l-4 4"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.2a4.3 4.3 0 0 1 7.5 2.6C19.5 15.4 12 20 12 20z"/>',
    "accessibility": '<circle cx="12" cy="4.5" r="1.8"/><path d="M5 8.5l7 1.5 7-1.5M12 10v4.5M9 21l3-6.5 3 6.5"/>',
    "shapes": '<circle cx="7.5" cy="7.5" r="4"/><rect x="13" y="13" width="8" height="8" rx="1"/><path d="M17 3l4 7h-8z"/><path d="M4 14h5v5.5"/>',
    "lightbulb": '<path d="M9 18h6M10 21.5h4M8.5 14.5A6 6 0 1 1 15.5 14.5c-.8.7-1.5 1.7-1.5 2.5v1h-4v-1c0-.8-.7-1.8-1.5-2.5z"/>',
    "gauge": '<path d="M4 18a9 9 0 1 1 16 0"/><path d="M12 14l4-5M12 14h.01"/>',
    "layers": '<path d="M12 2.5l10 5-10 5-10-5z"/><path d="M2 12l10 5 10-5M2 16.5l10 5 10-5"/>',
    "log-in": '<path d="M14 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M9.5 16.5 14 12 9.5 7.5M14 12H3"/>',
    "refresh": '<path d="M20.5 4v5.5H15M3.5 20v-5.5H9"/><path d="M19.4 9A8 8 0 0 0 5.7 6.4L3.5 8.8M4.6 15a8 8 0 0 0 13.7 2.6l2.2-2.4"/>',
    "arrows-lr": '<path d="M17 3.5l4 4-4 4M21 7.5H7.5M7 12.5l-4 4 4 4M3 16.5h13.5"/>',
    # natură și sustenabilitate
    "leaf": '<path d="M5 20c0-9 5.5-15 15-16-.5 10-6.5 15.5-15 16z"/><path d="M5 20l8.5-8.5"/>',
    "sprout": '<path d="M12 21v-8M12 13C12 8.5 9 5.5 4 5.5c0 4.5 3 7.5 8 7.5zM12 15c0-4.5 3-7.5 8-7.5 0 4.5-3 7.5-8 7.5z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.3 4.3l1.4 1.4M18.3 18.3l1.4 1.4M2.5 12h2M19.5 12h2M4.3 19.7l1.4-1.4M18.3 5.7l1.4-1.4"/>',
    "store": '<path d="M3.5 9 5 4h14l1.5 5M3.5 9h17v1.5a2.8 2.8 0 0 1-5.7 0 2.8 2.8 0 0 1-5.6 0 2.8 2.8 0 0 1-5.7 0zM5 13v8h14v-8M10 21v-5h4v5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "plane": '<path d="M2.5 13.5 21 5l-5 15.5-4.5-6.5z"/><path d="M11.5 14 21 5"/>',
    # contact
    "phone": '<path d="M21.5 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.6 4.2 2 2 0 0 1 3.6 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.7a2 2 0 0 1-.5 2.1L7.5 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.5 2.7.6a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m3 6.5 9 6.5 9-6.5"/>',
    "map-pin": '<path d="M12 21.5s-7-6.2-7-11.5a7 7 0 0 1 14 0c0 5.3-7 11.5-7 11.5z"/><circle cx="12" cy="10" r="2.5"/>',
    "send": '<path d="M21.5 2.5 11 13M21.5 2.5 15 21.5l-4-8.5-8.5-4z"/>',
    "download": '<path d="M12 3v12M7 10l5 5 5-5M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16 9.5"/>',
}


def svg(name, size=24):
    sw = "1.9" if size <= 16 else "1.75"
    return (f'<svg class="bx-i" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{P[name]}</svg>')


# Cardurile cu placă, în ordinea din pagină (cheia = primul segment al căii, fără en/).
CARDS = {
    "index.html": ["trending", "office", "monitor"],
    "accesibilitate-incluziune-si-diversitate": ["accessibility", "heart", "shapes"],
    "actiuni": ["merge", "building-plus", "calendar"],
    "compensare-si-decontare": ["cycle"],
    "contacte": ["phone", "mail", "map-pin", "clock"],
    "costuri": ["log-in", "refresh", "arrows-lr", "users", "layers"],
    "cotatii-in-timp-real": ["globe", "monitor", "sunset", "calendar"],
    "fise-detaliate": ["id-card", "bar-chart", "line-chart", "office", "folder", "calendar"],
    "fondatori": ["target", "branch", "plane", "trending", "flag", "store"],
    "identitate": ["banknote", "candles", "flag", "sprout", "shield-check", "eye", "scale", "accessibility", "lightbulb", "gauge"],
    "indicii-bursei": ["calendar"],
    "model-operational": ["check", "check", "check", "check"],
    "obligatiuni": ["landmark", "building", "briefcase", "leaf", "sun", "calendar"],
    "prezentare-generala": ["landmark", "pie", "server", "file-stack"],
    "procesul-de-listare": ["calendar"],
    "program-de-tranzactionare": ["calendar"],
    "rapoarte": ["file-chart", "newspaper", "book", "calendar"],
    "regulamente-si-acte-normative": ["scale", "scale", "award", "clipboard-check"],
    "valori-mobiliare": ["trending", "ticket-percent", "calendar"],
}
# Blocurile .item cu iconiță proprie (Procesul de listare: „Rolul brokerilor”, „Ghidul complet”)
ITEMS = {"procesul-de-listare": ["users", "book"]}
ITEM_ICON = re.compile(r'(<div class="item">\s*)<svg width="48"[\s\S]*?</svg>')
DOC_ICON = re.compile(r'(<li>\s*)<svg width="40"[\s\S]*?</svg>(\s*)(<a href="[^"]*"|<span class="bx-doc-soon")')

# Pe Fondatori, prima iconiță e eticheta listei („Obiectivele Guvernului”), nu un card.
SMALL_FIRST = {"fondatori"}
CHECK_PAGES = {"model-operational"}

# Etichetele de secțiune (<h6> cu iconiță), după textul RO; varianta EN se ia după poziție.
LABELS = {
    "Contact pentru clarificări": "mail", "Trimite un mesaj": "send", "Date instituționale": "landmark",
    "Adrese dedicate": "mail", "Structura acționariatului": "pie", "Parteneriat public-privat": "handshake",
    "Viziunea": "compass", "Misiunea": "target", "Valorile BIMx": "gem", "Guvernanță": "scale",
    "Participanți": "users", "Documente oficiale": "file-text", "Certificare": "award",
}
LABELS_EN = {
    "Contact for enquiries": "mail", "Send a message": "send", "Corporate details": "landmark",
    "Dedicated addresses": "mail", "Shareholder structure": "pie", "Public-private partnership": "handshake",
    "Vision": "compass", "Mission": "target", "BIMx values": "gem", "Governance": "scale",
    "Participants": "users", "Official documents": "file-text", "Certification": "award",
}

ICON_BLOCK = re.compile(r'<div class="icon(?: bx-icon)?">\s*(?:<svg[\s\S]*?</svg>|<img [^>]*>)(\s*</div>)?')
H6_ICON = re.compile(r'(<h6[^>]*>)\s*<svg[\s\S]*?</svg>\s*([^<]*)')


_CATALOG_LABELS = {}


def labels_from_catalog(lang):
    """Etichetele (h6) în altă limbă: traducerea din catalogul i18n/<lang>.json a etichetelor RO."""
    if lang not in _CATALOG_LABELS:
        import json
        from .config import MIRROR
        f = MIRROR / "i18n" / f"{lang}.json"
        cat = json.loads(f.read_text(encoding="utf-8"))["text"] if f.exists() else {}
        _CATALOG_LABELS[lang] = {cat[k].strip(): v for k, v in LABELS.items() if k in cat}
    return _CATALOG_LABELS[lang]


def apply_icons(text, key, lang):
    """Înlocuiește iconițele din <main> cu setul unitar; întoarce (text, câte au fost înlocuite)."""
    m0, m1 = text.find("<main"), text.find("</main>")
    if m0 < 0 or m1 < 0:
        return text, 0
    main = text[m0:m1]
    names = CARDS.get(key)
    count = 0
    if names:
        it = iter(names)
        first = [True]

        def card(m):
            nonlocal count
            block = m.group(0)
            vb = re.search(r'viewBox="0 0 (\d+)', block)
            if vb and int(vb.group(1)) > 100:          # logo-urile partenerilor
                return block
            name = next(it, None)
            if not name:
                return block
            count += 1
            if key in SMALL_FIRST and first[0]:
                first[0] = False
                return f'<div class="icon bx-ic-label">{svg(name, 16)}' + (m.group(1) or "")
            first[0] = False
            if key in CHECK_PAGES:
                return f'<div class="icon bx-ic-check">{svg(name, 20)}' + (m.group(1) or "")
            if m.group(1) is None:                      # iconița și titlul în același bloc (Regulamente)
                return f'<div class="icon bx-ic-row"><span class="bx-ic-plate">{svg(name)}</span>'
            return f'<div class="icon bx-ic">{svg(name)}</div>'
        main = ICON_BLOCK.sub(card, main)

    if key in ITEMS:
        it2 = iter(ITEMS[key])

        def item(m):
            nonlocal count
            name = next(it2, None)
            if not name:
                return m.group(0)
            count += 1
            return f'{m.group(1)}<span class="bx-ic-plate">{svg(name)}</span>'
        main = ITEM_ICON.sub(item, main)
    if key == "centru-de-descarcare":           # rândurile de documente: descărcare (disponibil) sau document (în curând)
        def doc(m):
            nonlocal count
            count += 1
            soon = "bx-doc-soon" in m.group(3)
            return (f'{m.group(1)}<span class="bx-ic-plate bx-ic-sm{" is-muted" if soon else ""}">'
                    f'{svg("file-text" if soon else "download", 20)}</span>{m.group(2)}{m.group(3)}')
        main = DOC_ICON.sub(doc, main)

    table = {"ro": LABELS, "en": LABELS_EN}.get(lang) or labels_from_catalog(lang)

    def label(m):
        nonlocal count
        name = table.get(m.group(2).strip())
        if not name:
            return m.group(0)
        count += 1
        return f'{m.group(1)}<span class="bx-ic-h6">{svg(name, 16)}</span>{m.group(2)}'
    main = H6_ICON.sub(label, main)
    return text[:m0] + main + text[m1:], count
