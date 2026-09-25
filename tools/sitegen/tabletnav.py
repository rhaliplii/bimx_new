"""Meniul de tip mobil (hamburger) și pe tabletă, 992–1199 px: între aceste lățimi meniul desktop nu încape.

Stilurile meniului mobil sunt scrise pentru ecrane ≤ 991 px, în tema bimx.md (main.css) și în src/site/site.css.
La build, regulile de antet și meniu din aceste blocuri se copiază, în aceeași ordine, într-un bloc pentru tabletă,
adăugat la sfârșitul site.css; orice schimbare a meniului mobil se aplică astfel automat și pe tabletă.
"""
import re

MOBILE = re.compile(r"@media[^{]*max-width:\s*991px[^{]*\{")
KEEP = ("header", ".burger", ".bx-lang", ".bx-menu", ".bx-prelaunch", ".modal_search_form")
TABLET = "@media (min-width: 992px) and (max-width: 1199px)"


def _blocks(css):
    """Conținutul fiecărui bloc @media (max-width: 991px) din foaia de stil."""
    out = []
    for m in MOBILE.finditer(css):
        depth, i = 1, m.end()
        while depth and i < len(css):
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        out.append(css[m.end():i - 1])
    return out


def _rules(block):
    """Regulile simple (selector { declarații }) dintr-un bloc; @-regulile imbricate se ignoră."""
    block = re.sub(r"/\*[\s\S]*?\*/", "", block)
    return [(sel.strip(), body.strip()) for sel, body in re.findall(r"([^{}@]+)\{([^{}]*)\}", block)]


def tablet_css(*sheets):
    rules = [f"  {sel} {{ {body} }}" for css in sheets for block in _blocks(css) for sel, body in _rules(block)
             if any(k in sel for k in KEEP)]
    if not rules:
        return ""
    return (f"\n\n/* ---------- generat la build (sitegen/tabletnav.py): meniul mobil și pe tabletă ---------- */\n"
            f"{TABLET} {{\n" + "\n".join(rules) + "\n}\n")
