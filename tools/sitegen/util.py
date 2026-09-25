"""Funcții mici, fără stare: escapare, pluraluri, durate, căi relative."""
import html
import os
import re
import unicodedata


def rich(text):
    """Escape text but keep the <strong>/<em> tags allowed in content."""
    out = html.escape(text, quote=False)
    for tag in ("strong", "em"):
        out = out.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return out


def esc(text):
    return html.escape(text)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def plural(n, forms):
    """„1 lecție / 5 lecții”; în rusă sunt trei forme: [one, few, many] („1 урок, 3 урока, 5 уроков”)."""
    if len(forms) == 3:
        one, few, many = forms
        if n % 10 == 1 and n % 100 != 11:
            word = one
        elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            word = few
        else:
            word = many
        return f"{n} {word}"
    one, many = forms
    return f"{n} {one if n == 1 else many}"


def lessons_of(program):
    return [(course, lesson) for course in program["courses"] for lesson in course["lessons"]]


def total_minutes(lessons):
    return sum(lesson["minutes"] for _, lesson in lessons)


def duration(minutes):
    h, m = divmod(minutes, 60)
    if not h:
        return f"{m} min"
    return f"{h} h {m} min" if m else f"{h} h"


def relto(target, from_dir):
    """Cale relativă (cu /) de la un director la un fișier sau director din site."""
    r = os.path.relpath(target, from_dir).replace(os.sep, "/")
    return "" if r == "." else r


def prefix(target, from_dir):
    r = relto(target, from_dir)
    return f"{r}/" if r else ""

