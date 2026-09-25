# Site BIMx + BIMx Academy

Site static: copia bimx.md și BIMx Academy, în română și în engleză. Totul se generează din `src/` în `dist/`.

Cerințe: Python 3.9+ (doar biblioteca standard) și `make`.

```
make check     # validează lecțiile, construiește dist/ și verifică linkurile
make serve     # construiește și pornește http://localhost:8000/
```

## Structura

```
src/
  academy/
    content/ro/*.json, content/en/*.json   lecțiile (aceleași fișiere și slug-uri în ambele limbi)
    i18n/ro.json, i18n/en.json             textele interfeței
    catalog.json                           direcții, cursuri, publicații de pe prima pagină
    templates/index.ro.html, index.en.html prima pagină (secțiunile BUILD se generează)
    assets/                                css, js, imagini Academy
  bimx-mirror/
    ro/                                    paginile bimx.md (sursa ambelor limbi)
    i18n/en.json                           traducerea EN: text RO → text EN
    data/market.json                       datele de piață demonstrative (ticker, top-uri, grafic)
    shared/                                wp-content, wp-includes (comune ambelor limbi)
  site/replica.js                          formulare, partajare și accesibilitate (tastatură, Escape, aria-expanded)
  site/site.css                            corecturile de stil peste tema bimx.md (audit UI/UX)
  site/search.js                           căutarea din antet (index generat la build)
tools/
  build.py                                 punctul de intrare al build-ului
  sitegen/                                 codul build-ului (config, mirror, translate, shell, academy, detach, fixes, pdf, search, util, icons)
  validate.py                              verifică lecțiile și că fiecare text bimx.md are traducere EN
  check_links.py                           verifică linkurile locale din dist/ și că nimic nu trimite spre bimx.md
  mirror_bimx.py                           descarcă din nou bimx.md în src/bimx-mirror/
docs/                                      audituri și corespondență — doar local, exclus din git
dist/                                      rezultatul build-ului — generat, nu se editează
```

## Ce e în `dist/`

| Adresă | Ce este |
|---|---|
| `index.html`, `identitate/`, `prezentare-generala/` … | bimx.md (RO) |
| `en/index.html`, `en/identitate/` … | bimx.md (EN) — aceleași pagini, traduse |
| `academy/`, `en/academy/` | BIMx Academy (RO / EN) |

Butoanele RO/EN duc la aceeași pagină în cealaltă limbă. Meniul „BIMX ACADEMY” din bimx.md duce în Academy, iar paginile bimx.md înlocuite de Academy (`glosar/`, `formare/`, `publicatii/` …) redirecționează spre secțiunile corespunzătoare.

## Cum se actualizează

| Ce | Unde |
|---|---|
| O lecție | `src/academy/content/{ro,en}/NN-<program>.json` — apoi `make validate` |
| Un text din interfață | `src/academy/i18n/{ro,en}.json` |
| Cursurile / ghidurile de pe prima pagină | `src/academy/catalog.json` |
| Conținutul fix al primei pagini Academy | `src/academy/templates/index.{ro,en}.html` |
| Stiluri, scripturi, imagini Academy | `src/academy/assets/` |
| Traducerea EN a unei pagini bimx.md | `src/bimx-mirror/i18n/en.json` — apoi `make validate` |
| Copia bimx.md | `make mirror` (descarcă din nou tot de pe bimx.md), apoi `make validate` arată textele noi de tradus |

Deploy: la fiecare push pe `main`, `.github/workflows/pages.yml` rulează `make check` și publică `dist/` pe GitHub Pages (https://rhaliplii.github.io/bimx/). Setare necesară o singură dată: Settings → Pages → Source: „GitHub Actions”. `dist/` merge pe orice server static: toate linkurile sunt relative, deci site-ul funcționează și dintr-un subdirector.

## Versiunea engleză

bimx.md nu are versiune engleză (doar o pagină provizorie `/en/home/`), așa că fiecare pagină EN se generează din pagina RO: `tools/sitegen/translate.py` extrage textul fiecărui bloc (paragraf, titlu, link, celulă, atribute `alt`/`title`/`placeholder`), iar build-ul îl înlocuiește cu traducerea din `src/bimx-mirror/i18n/en.json`. Tag-urile din interiorul unui text apar în catalog ca marcaje `{1}`, `{2}` … și trebuie păstrate în traducere. Secțiunea `js` a catalogului traduce textele din scripturile temei.

Un text fără traducere rămâne în română în pagina EN; `make validate` le listează. Documentele PDF rămân în română.

## Independent de bimx.md

Niciun link, buton, formular sau resursă din `dist/` nu trimite spre bimx.md (pasul `sitegen/detach.py`; `make check` pică dacă apare vreunul):

- linkurile spre pagini copiate devin locale; linkurile rupte și pe bimx.md au echivalent local în `LINK_ALIASES` (ex. `/calendar` → `trading-calendar/`);
- „Intra in cont” / „Log In” au fost scoase: autentificarea există doar pe serverul bimx.md;
- formularul de contact validează câmpurile obligatorii, dar nu trimite date: afișează „Această funcție nu este disponibilă momentan.”; newsletterul MailPoet e înlocuit de linkuri spre LinkedIn și Facebook;
- căutarea din antet funcționează local: la build, `tools/sitegen/search.py` indexează conținutul principal al paginilor (RO și EN, fără antet, subsol, secțiuni ascunse și pagini „În curând”) în `dist/assets/search/{ro,en}.js`, iar `src/site/search.js` caută în browser, fără diacritice, cu rezultatele pe măsură ce scrii;
- butoanele de partajare (Facebook, X, LinkedIn, copiere link) folosesc adresa paginii curente.
- tickerul folosește datele demonstrative din `src/bimx-mirror/data/market.json` (ca pe bimx.md, unde sunt tot simulate) și apare doar pe prima pagină și pe paginile de piață, marcat „Date demonstrative”.

Adresele de email @bimx.md și mențiunile „bimx.md” din textul lecțiilor rămân.

## Corecturile din auditul UI/UX

Paginile bimx.md vin neschimbate din `src/bimx-mirror/`, iar corecturile se aplică la build, ca un nou `make mirror` să nu le piardă:

- `tools/sitegen/fixes.py` — antet (pre-lansare în loc de „Market Open”, fără login, butoane accesibile), subsol (adresă, rețele sociale, fără pagini goale), breadcrumbs, prima pagină (butoane cu destinații reale, iconițe SVG, fără secțiunile de piață ascunse), Centrul de descărcare, paginile „În curând” transformate în pagini reale (Calendarul de tranzacționare, Statut, Organigrama, Situații financiare), redirecționări pentru rutele duplicate, skip-link, meta description, ierarhia titlurilor (`aria-level`), corpul de text mai mare în CSS-ul temei;
- `src/site/site.css` — stilurile corecturilor și tokenurile comune `--bx-*` (folosite și de Academy);
- `tools/sitegen/pdf.py` — PDF-urile ghidurilor Academy, generate cu Chrome headless (dacă Chrome lipsește, butonul tipărește pagina; calea se poate da prin `CHROME=`).

Fiecare corectură e etichetată în cod cu numărul problemei din audit (UI-xx).

## Limitări

Formularele și autentificarea au nevoie de un server și nu funcționează în site-ul static. Câteva imagini din CSS-urile temei (slick, lightbox) lipsesc și de pe bimx.md; `check_links.py` le raportează doar ca avertisment.
