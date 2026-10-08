"""Imaginile de partajare (Open Graph, 1200 × 630), câte una pe limbă: src/site/img/og-bimx-<limbă>.png.

Se rulează manual, doar când se schimbă textele (python3 tools/og_images.py); build-ul folosește PNG-urile generate.
Randarea: Chrome headless (calea se poate da prin CHROME=), fonturile de pe Google Fonts (e nevoie de internet).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sitegen.config import SRC  # noqa: E402
from sitegen.pdf import find_chrome  # noqa: E402

# (numele bursei, titlul – ca în hero-ul primei pagini, rândul de jos)
TEXTS = {
    "ro": ("Bursa Internațională a Moldovei", "Intrăm în etapa de lansare",
           "Operator de piață licențiat de CNPF · Piața Reglementată și MTF"),
    "en": ("Moldova International Stock Exchange", "Entering the launch phase",
           "Market operator licensed by the CNPF · Regulated Market and MTF"),
    "uk": ("Міжнародна фондова біржа Молдови", "Ми вступаємо в етап запуску",
           "Оператор ринку з ліцензією НКФР · Регульований ринок і MTF"),
    "ru": ("Международная фондовая биржа Молдовы", "Мы вступаем в этап запуска",
           "Оператор рынка с лицензией НКФР · Регулируемый рынок и MTF"),
}
# Prompt (fontul site-ului) nu are chirilică: în rusă și ucraineană, Montserrat (ca pe site)
FONT = {"ro": "Prompt", "en": "Prompt", "uk": "Montserrat", "ru": "Montserrat"}

X_PATHS = ('<path fill="#fff" d="M0 0h11l29 34H29z"/><path fill="#fff" d="M40 0H29L0 34h11z"/>'
           '<path fill="#1DB0F0" d="M9 6h10l11 11-11 11H9l11-11z"/>')

TEMPLATE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<link href="{fonts}" rel="stylesheet">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
.c{{position:relative;width:1200px;height:630px;background:linear-gradient(120deg,#1A2266 0%,#232D80 60%,#2A3AA0 100%);color:#fff;overflow:hidden;font-family:{font},sans-serif}}
.ring{{position:absolute;right:-520px;top:-620px;width:1300px;height:1300px;border-radius:50%;border:150px solid rgba(30,177,241,.08);box-sizing:border-box}}
.logo{{position:absolute;left:80px;top:72px;display:flex;align-items:flex-end;gap:2px;font-family:Prompt,sans-serif}}
.logo span{{font-weight:700;font-size:64px;line-height:52px;letter-spacing:-.02em}}
.eb{{position:absolute;left:80px;top:210px;font-size:24px;font-weight:500;color:#7DD3FC}}
h1{{position:absolute;left:80px;top:250px;margin:0;font-size:{size}px;line-height:1.12;font-weight:700;letter-spacing:-.02em;max-width:660px}}
.foot{{position:absolute;left:80px;bottom:64px;display:flex;align-items:center;gap:12px;font-size:22px;color:rgba(255,255,255,.8)}}
.dot{{width:12px;height:12px;border-radius:50%;background:#F5B83D;flex:none}}
.x{{position:absolute;right:90px;top:170px;width:330px}}
</style></head><body><div class="c"><div class="ring"></div>
<div class="logo"><span>BIM</span><svg viewBox="0 0 40 34" width="44" height="38">{x}</svg></div>
<div class="eb">{name}</div>
<h1>{title}</h1>
<div class="foot"><span class="dot"></span>{foot}</div>
<svg class="x" viewBox="0 0 40 34">{x}</svg>
</div></body></html>
"""


def main():
    chrome = find_chrome()
    if not chrome:
        raise SystemExit("Chrome nu a fost găsit (setați CHROME=/cale/spre/chrome)")
    out_dir = SRC / "site" / "img"
    with tempfile.TemporaryDirectory() as tmp:
        for lang, (name, title, foot) in TEXTS.items():
            size = 72 if FONT[lang] == "Prompt" else 64      # Montserrat e mai lat
            page = Path(tmp) / f"og-{lang}.html"
            page.write_text(TEMPLATE.format(fonts=(SRC / "site" / "fonts" / "fonts.css").as_uri(), lang=lang, font=FONT[lang], size=size, name=name,
                                            title=title.replace(" в ", " в&nbsp;"), foot=foot, x=X_PATHS),
                            encoding="utf-8")                  # prepoziția „в” nu rămâne singură la capăt de rând
            out = out_dir / f"og-bimx-{lang}.png"
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            "--window-size=1200,630", "--virtual-time-budget=5000", f"--screenshot={out}", page.as_uri()],
                           check=True, capture_output=True, timeout=60)
            print(out.relative_to(SRC.parent))


if __name__ == "__main__":
    main()
