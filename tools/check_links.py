#!/usr/bin/env python3
"""Verifică dist/: fiecare link local duce la un fișier existent și nicio pagină nu trimite spre bimx.md.

Adresele de email @bimx.md, mențiunile „bimx.md” din text și adresele oficiale din <head> (canonical, hreflang,
Open Graph) sunt permise.
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

DIST = Path(__file__).resolve().parent.parent / "dist"
ATTR = re.compile(r'\s(?:href|src|srcset|data-src)=(["\'])([^"\']*)\1')
CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)")
# CSS-uri ale temei bimx.md care cer imagini/fonturi pe care nici bimx.md nu le servește: doar avertisment.
KNOWN_BROKEN = {
    "wp-content/themes/victor-child/assets/css/lightbox.css",
    "wp-content/themes/victor-child/assets/css/slick-theme.css",
}
# URL spre bimx.md: absolut, fără protocol, escapat în JSON sau codificat într-un parametru (share).
ORIGIN = re.compile(r"(?:https?:(?:\\?/){2}|https?%3A%2F%2F|(?<![\w@.])//)(?:www\.)?bimx\.md[^\"'\s<>)]*", re.I)
# Excepție: adresele oficiale din <head> (canonical, hreflang, Open Graph / Twitter) trimit intenționat absolut la bimx.md,
# ca motoarele de căutare și rețelele sociale să indice site-ul oficial (config.SITE_URL), nu copia de test.
DECLARED = re.compile(r'<link rel="(?:canonical|alternate)"[^>]*>|<meta (?:property="og:[^"]*"|name="twitter:[^"]*")[^>]*>')
EXTERNAL = ("#", "http:", "https:", "//", "mailto:", "tel:", "javascript:", "data:", "{")


def targets(text, css):
    # în HTML se verifică și url() din style="…" și <style>, nu doar atributele
    matches = list(CSS_URL.finditer(text)) + ([] if css else list(ATTR.finditer(text)))
    for m in matches:
        val = m.group(1) if m.re is CSS_URL else m.group(2)
        for part in val.split(",") if "srcset" in m.group(0)[:8] else [val]:
            url = part.strip().split(" ")[0]
            if url and not url.startswith(EXTERNAL):
                yield url


def main():
    if not DIST.exists():
        raise SystemExit("Lipsește dist/ (rulați tools/build.py)")
    broken, checked, origin = {}, 0, {}
    for f in sorted(DIST.rglob("*")):
        if f.suffix not in (".html", ".css"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in ORIGIN.finditer(DECLARED.sub("", text)):
            origin.setdefault(str(f.relative_to(DIST)), set()).add(m.group(0))
        for url in targets(text, f.suffix == ".css"):
            path = unquote(url.split("#")[0].split("?")[0])
            if not path:
                continue
            target = Path(os.path.normpath(f.parent / path))
            if target.is_dir():
                target = target / "index.html"
            checked += 1
            if not target.exists():
                broken.setdefault(str(f.relative_to(DIST)), set()).add(url)
    known = {k: v for k, v in broken.items() if k in KNOWN_BROKEN}
    broken = {k: v for k, v in broken.items() if k not in KNOWN_BROKEN}
    for page, urls in sorted(broken.items()):
        print(f"{page}:")
        for url in sorted(urls):
            print(f"    {url}")
    if known:
        print(f"Avertisment: {sum(len(u) for u in known.values())} resurse lipsă în CSS-urile temei ({', '.join(sorted(known))}).")
    for page, urls in sorted(origin.items()):
        print(f"{page}: trimite spre bimx.md")
        for url in sorted(urls):
            print(f"    {url}")
    total = sum(len(u) for u in broken.values())
    print(f"{checked} linkuri verificate, {total} rupte în {len(broken)} fișiere.")
    print(f"Referințe spre bimx.md: {sum(len(u) for u in origin.values())} în {len(origin)} fișiere.")
    sys.exit(1 if broken or origin else 0)


if __name__ == "__main__":
    main()
