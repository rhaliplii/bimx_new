"""Versiunea fișierelor proprii (CSS, JS) în adresă: assets/js/replica.js → assets/js/replica.js?v=<hash conținut>.

Fără ea, un browser care a păstrat în cache un replica.js vechi îl poate folosi cu pagini noi (de ex. calendarul
lansării cu stările calculate după vechea logică). Hash-ul se schimbă doar când se schimbă fișierul.
Temele WordPress (wp-content, wp-includes) au deja ?ver=… și rămân neschimbate.
"""
import hashlib
import os
import re
from pathlib import Path

from .config import DIST

ASSET = re.compile(r'(\s(?:src|href)=")([^"?#:]+\.(?:js|css))(")')


def cachebust():
    hashes = {}

    def version(path):
        if path not in hashes:
            hashes[path] = hashlib.md5(path.read_bytes()).hexdigest()[:10] if path.is_file() else None
        return hashes[path]

    changed = 0
    for f in DIST.rglob("*.html"):
        text = f.read_text(encoding="utf-8", errors="replace")

        def add(m):
            target = Path(os.path.normpath(f.parent / m.group(2)))
            try:
                rel = target.relative_to(DIST)
            except ValueError:
                return m.group(0)
            if rel.parts[0] in ("wp-content", "wp-includes"):
                return m.group(0)
            v = version(target)
            return f"{m.group(1)}{m.group(2)}?v={v}{m.group(3)}" if v else m.group(0)

        new = ASSET.sub(add, text)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed += 1
    return changed, sum(1 for v in hashes.values() if v)
