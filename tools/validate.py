#!/usr/bin/env python3
"""Verifică structura fișierelor din content/ înainte de build."""
import json, re, sys
from pathlib import Path

BLOCKS = {"p": ["text"], "list": ["items"], "steps": ["items"], "callout": ["variant", "text"], "table": ["headers", "rows"], "formula": ["expr"]}
errors = []
CONTENT = Path(__file__).resolve().parent.parent / "src" / "academy" / "content"
for f in [x for lang in ("ro", "en", "ru", "uk") for x in sorted((CONTENT / lang).glob("*.json"))]:
    d = json.loads(f.read_text(encoding="utf-8"))
    for k in ["slug", "num", "title", "short", "level", "audience", "intro", "outcomes", "prerequisites", "courses"]:
        if k not in d: errors.append(f"{f.name}: lipsește {k}")
    slugs = set()
    words = 0
    for c in d["courses"]:
        for l in c["lessons"]:
            where = f"{f.name} › {l.get('slug')}"
            if not re.fullmatch(r"[a-z0-9-]+", l["slug"]) or l["slug"] in slugs or l["slug"] == "index":
                errors.append(f"{where}: slug invalid/duplicat")
            slugs.add(l["slug"])
            kinds = set()
            text = []
            for s in l["sections"]:
                for b in s["blocks"]:
                    t = b.get("type")
                    if t not in BLOCKS: errors.append(f"{where}: bloc necunoscut {t}"); continue
                    for req in BLOCKS[t]:
                        if req not in b: errors.append(f"{where}: {t} fără {req}")
                    kinds.add(t if t != "callout" else "callout:" + b.get("variant", ""))
                    text.append(json.dumps(b, ensure_ascii=False))
                    if t == "table" and any(len(r) != len(b["headers"]) for r in b["rows"]):
                        errors.append(f"{where}: rând de tabel cu număr greșit de coloane")
            for need in ["callout:definition", "callout:example"]:
                if need not in kinds: errors.append(f"{where}: lipsește {need}")
            if len(l["quiz"]) != 3: errors.append(f"{where}: quiz are {len(l['quiz'])} întrebări")
            for q in l["quiz"]:
                if not 0 <= q["answer"] < len(q["options"]): errors.append(f"{where}: răspuns în afara opțiunilor")
            bad = re.findall(r"<(?!/?(?:strong|em)>)[^>]*>", " ".join(text))
            if bad: errors.append(f"{where}: tag-uri nepermise {set(bad)}")
            if f.parent.name == "ro" and re.search(r"[şţŞŢ]", " ".join(text)): errors.append(f"{where}: diacritice cu sedilă (ş/ţ) în loc de virgulă")
            words += len(re.sub(r"<[^>]+>", " ", " ".join(text)).split())
    n = sum(len(c["lessons"]) for c in d["courses"])
    answers = [q["answer"] for c in d["courses"] for l in c["lessons"] for q in l["quiz"]]
    print(f"{f.parent.name}/{f.name}: {n} lecții, ~{words // max(n,1)} cuvinte/lecție, răspunsuri corecte pe poziții {sorted(set(answers))}")

# Traducerile EN, RU și UK ale paginilor bimx.md: fiecare text al paginilor RO are traducere, cu aceleași marcaje {n}.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sitegen import translate  # noqa: E402

MIRROR = Path(__file__).resolve().parent.parent / "src" / "bimx-mirror"
needed = {}
for page in sorted((MIRROR / "ro").rglob("*.html")):
    for key in translate.extract(page.read_text(encoding="utf-8")):
        needed.setdefault(key, page.relative_to(MIRROR / "ro"))
for lang in ("en", "ru", "uk"):
    catalog = json.loads((MIRROR / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))["text"]
    for key, page in needed.items():
        if key not in catalog:
            errors.append(f"i18n/{lang}.json: lipsește traducerea pentru „{key[:80]}” ({page})")
        elif not translate.check_placeholders(key, catalog[key]):
            errors.append(f"i18n/{lang}.json: marcajele {{n}} diferă în „{key[:80]}”")
        elif lang == "uk" and re.search(r"[ЫыЭэЪъЁё]", catalog[key]):
            errors.append(f"i18n/uk.json: litere rusești (ы/э/ъ/ё) în traducerea pentru „{key[:80]}”")
    unused = len(set(catalog) - set(needed))
    print(f"bimx.md {lang.upper()}: {len(needed)} texte, {len(needed) - sum(k not in catalog for k in needed)} traduse"
          + (f", {unused} traduceri nefolosite (pot fi șterse)" if unused else ""))
print("\n".join(errors) or "OK – fără erori")
sys.exit(1 if errors else 0)
