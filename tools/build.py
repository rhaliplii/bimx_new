#!/usr/bin/env python3
"""Construiește site-ul complet în dist/: copia bimx.md + BIMx Academy, în română, engleză și rusă.

Rulare:  python3 tools/build.py   (sau: make build)

Surse (src/):
  bimx-mirror/ro                    – paginile bimx.md (reîmprospătare: tools/mirror_bimx.py)
  bimx-mirror/i18n/en.json          – traducerea EN a paginilor bimx.md (catalog RO → EN)
  bimx-mirror/shared                – wp-content și wp-includes, comune ambelor limbi
  academy/content/{ro,en}/*.json    – lecțiile Academy, cu aceleași slug-uri în ambele limbi
  academy/templates/index.{ro,en}.html – prima pagină Academy (secțiunile dintre marcajele BUILD se generează)
  academy/i18n/{ro,en}.json         – textele interfeței Academy
  academy/catalog.json              – direcții, cursuri, publicații de pe prima pagină
  academy/assets/                   – stilurile, scripturile și imaginile Academy
  site/replica.js                   – formulare și partajare fără serverul bimx.md
  site/search.js                    – căutarea din antet (indexul se generează la build)
  site/site.css                     – corecturile de stil peste tema bimx.md (audit UI/UX)

Rezultat (dist/):
  index.html, <pagină>/            – bimx.md în română
  en/index.html, en/<pagină>/      – bimx.md în engleză (aceleași căi ca în română)
  academy/, en/academy/            – BIMx Academy (programe/, publicatii/, assets/)
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sitegen.academy import build, load_programs  # noqa: E402
from sitegen.detach import detach  # noqa: E402
from sitegen.fixes import apply_fixes  # noqa: E402
from sitegen.pdf import build_pdfs  # noqa: E402
from sitegen.search import build_search  # noqa: E402
from sitegen.config import ACADEMY_ASSETS, ACADEMY_SRC, DIST, LANGS, PUBLICATIONS, ROOT, SITE_LANGS  # noqa: E402
from sitegen.mirror import build_snapshot, localize_links  # noqa: E402
from sitegen.shell import write_scoped_css  # noqa: E402


def main():
    programs = {lang: load_programs(lang) for lang in SITE_LANGS}
    if not programs["ro"]:
        raise SystemExit("Nu există lecții în src/academy/content/ro/")
    ro_slugs = [p["slug"] for p in programs["ro"]]
    for lang in SITE_LANGS[1:]:
        slugs = [p["slug"] for p in programs[lang]]
        if slugs != ro_slugs:
            missing = sorted(set(ro_slugs) - set(slugs))
            raise SystemExit(f"content/{lang}/ nu corespunde cu content/ro/ (lipsesc: {missing})")
    if DIST.exists():
        shutil.rmtree(DIST)
    pages, missing = build_snapshot()
    print(f"bimx.md: {pages} pagini ({' + '.join(l.upper() for l in SITE_LANGS)}) din src/bimx-mirror/")
    for lang, keys in missing.items():
        if keys:
            print(f"  Atenție: {len(keys)} texte fără traducere {lang.upper()} (rămân în română) – rulați tools/validate.py")
    shutil.copytree(ACADEMY_SRC / "assets", ACADEMY_ASSETS, ignore=shutil.ignore_patterns(".DS_Store"))
    write_scoped_css()
    for lang in SITE_LANGS:
        count = build(lang, programs[lang])
        localize_links(LANGS[lang]["out"], lang)
        print(f"Academy [{lang}]: {len(programs[lang])} programe, {count} lecții, {len(PUBLICATIONS)} ghiduri.")
    print(f"Decuplare de bimx.md: {detach()} pagini ajustate.")
    print(f"Corecturi din auditul UI/UX: {apply_fixes()} pagini ajustate.")
    made, total = build_pdfs()
    print(f"PDF-uri pentru ghiduri: {made} din {total}" + ("" if made == total else " (fără Chrome: butonul tipărește pagina)"))
    counts, injected = build_search()
    print("Căutare: " + ", ".join(f"{counts[l]} pagini {l.upper()}" for l in SITE_LANGS) + f" în index; scriptul adăugat pe {injected} pagini.")
    print(f"Gata. Deschideți {(DIST / 'index.html').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
