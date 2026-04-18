"""Render an HTML file to PNG via headless Chrome.

Usage (as module):
    from render_png import html_to_png
    html_to_png(html_string, "/tmp/out.png", width=1800)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chrome") or "",
]


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if path and os.path.exists(path):
            return path
    raise RuntimeError(
        "Chrome/Chromium not found. Install Chrome or adjust CHROME_CANDIDATES in render_png.py."
    )


def html_to_png(html: str, out_path: str, width: int = 1800, height: int = 1200) -> str:
    """Write `html` to a temp file, screenshot via Chrome headless, return out_path."""
    chrome = find_chrome()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html)
        html_path = f.name

    try:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            "--default-background-color=FFFFFFFF",
            f"--screenshot={out_path}",
            f"file://{html_path}",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0 or not os.path.exists(out_path):
            raise RuntimeError(
                f"Chrome screenshot failed (code={result.returncode})\n"
                f"stderr: {result.stderr}\nstdout: {result.stdout}"
            )
    finally:
        try:
            os.unlink(html_path)
        except OSError:
            pass

    return out_path


if __name__ == "__main__":
    # Tiny self-test
    sample = "<html><body style='padding:40px;font-family:sans-serif'><h1>render_png OK</h1></body></html>"
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/render_png_test.png"
    html_to_png(sample, out, width=800, height=400)
    print(f"Wrote {out}")
