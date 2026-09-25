"""Căile proiectului, configurația site-ului și datele Academy încărcate din src/academy/."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DIST = ROOT / "dist"

ACADEMY_SRC = SRC / "academy"
CONTENT = ACADEMY_SRC / "content"
MIRROR = SRC / "bimx-mirror"                 # ro/ – paginile bimx.md; i18n/en.json – traducerea; shared/ – resurse
ACADEMY_ASSETS = DIST / "academy" / "assets"

BIMX = "https://bimx.md"

# Limbile site-ului: româna (sursa, la rădăcină), apoi engleza, rusa și ucraineana, fiecare în folderul ei
# (/en/, /ru/, /uk/) – aceleași căi în toate limbile. Codul afișat în selector: UA pentru ucraineană (ISO: uk).
SITE_LANGS = ("ro", "en", "uk", "ru")          # și ordinea din selectorul de limbă
LANG_PREFIX = {lang: ("" if lang == "ro" else f"{lang}/") for lang in SITE_LANGS}
LOCALES = {"ro": ("ro-RO", "ro_RO"), "en": ("en-GB", "en_GB"), "ru": ("ru-RU", "ru_RU"), "uk": ("uk-UA", "uk_UA")}
LANG_NAMES = {"ro": "Română", "en": "English", "ru": "Русский", "uk": "Українська"}
LANG_CODES = {"ro": "RO", "en": "EN", "ru": "RU", "uk": "UA"}
CYRILLIC = ("ru", "uk")                                  # fontul cu chirilică și pluralul cu trei forme


def lang_of(parts):
    """Limba unei căi din dist/ (după primul segment: en/, ru/, uk/ sau nimic pentru română)."""
    return parts[0] if parts and parts[0] in SITE_LANGS[1:] else "ro"


def pick(lang, ro, en, ru, uk):
    """Valoarea în limba dată (pentru textele scurte scrise direct în cod)."""
    return {"ro": ro, "en": en, "ru": ru, "uk": uk}[lang]


LANGS = {
    lang: {"content": CONTENT / lang, "out": DIST / LANG_PREFIX[lang] / "academy",
           "template": ACADEMY_SRC / "templates" / f"index.{lang}.html"}
    for lang in SITE_LANGS
}

# Paginile bimx.md din meniul „BIMX ACADEMY”, înlocuite de secțiunile Academy.
ACADEMY_REDIRECTS = {
    "resurse-educationale": "#directii",
    "glosar": "#glosar",
    "formare": "#formare",
    "evenimente": "#evenimente",
    "publicatii": "#publicatii",
    "baza-cunostintelor": "#directii",
}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


# Textele interfeței (chei identice în ambele limbi) și catalogul primei pagini Academy.
T = {lang: _load(ACADEMY_SRC / "i18n" / f"{lang}.json") for lang in LANGS}
CATALOG = _load(ACADEMY_SRC / "catalog.json")
LEVELS = CATALOG["levels"]
LIVE = CATALOG["live_label"]
DIRECTION_META = CATALOG["directions"]
HOME_COURSES = CATALOG["home_courses"]
PUBLICATIONS = CATALOG["publications"]
