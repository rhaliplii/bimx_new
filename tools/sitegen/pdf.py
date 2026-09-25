"""PDF-urile ghidurilor Academy, generate la build cu Chrome headless din paginile ghidurilor.

Butonul din pagina ghidului devine un link de descărcare spre PDF. Dacă Chrome nu e disponibil (sau
generarea eșuează), butonul rămâne „Tipărește / salvează ca PDF” (window.print), deci build-ul nu depinde
de Chrome. Calea spre Chrome se poate da și prin variabila de mediu CHROME.
"""
import os
import re
import shutil
import subprocess
import tempfile
import time

from .config import LANGS, PUBLICATIONS, T

CANDIDATES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
BUTTON = re.compile(r'<button type="button" class="btn2" onclick="window\.print\(\)" data-pdf="([^"]+)">([\s\S]*?</svg>)\s*[^<]*</button>')


def find_chrome():
    for c in ([os.environ["CHROME"]] if os.environ.get("CHROME") else []) + list(CANDIDATES):
        path = shutil.which(c) or (c if os.path.isfile(c) else None)
        if path:
            return path
    return None


def print_pdf(chrome, html, pdf):
    """Tipărește pagina în PDF. Chrome headless poate rămâne deschis după scriere (ceasul din antet ține
    pagina activă), așa că procesul se oprește imediat ce fișierul PDF e complet."""
    if pdf.exists():
        pdf.unlink()
    with tempfile.TemporaryDirectory() as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run", "--hide-scrollbars",
               f"--user-data-dir={profile}", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
               f"--print-to-pdf={pdf}", html.as_uri()]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline, last = time.time() + 90, -1
        try:
            while time.time() < deadline and proc.poll() is None:
                time.sleep(0.5)
                if pdf.exists():
                    size = pdf.stat().st_size
                    if size == last and pdf.read_bytes()[-1024:].rstrip().endswith(b"%%EOF"):
                        break
                    last = size
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
    return pdf.exists() and pdf.stat().st_size > 10_000


def build_pdfs():
    """Generează PDF-urile și leagă butoanele de ele; întoarce (generate, total)."""
    chrome = find_chrome()
    made = total = 0
    for lang, cfg in LANGS.items():
        for pub in PUBLICATIONS:
            html = cfg["out"] / "publicatii" / f"{pub['slug']}.html"
            if not html.exists():
                continue
            total += 1
            pdf = html.with_suffix(".pdf")
            if not (chrome and print_pdf(chrome, html, pdf)):
                continue
            made += 1
            text = html.read_text(encoding="utf-8")
            text = BUTTON.sub(lambda m: f'<a class="btn2" href="{m.group(1)}" download>{m.group(2)}\n              '
                                        f'{T[lang]["download_pdf"]} <small>(PDF)</small></a>', text)
            html.write_text(text, encoding="utf-8")
    return made, total
