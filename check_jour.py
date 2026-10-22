import os
os.environ.setdefault("LD_LIBRARY_PATH", "/workspace/libs/usr/lib/x86_64-linux-gnu:/workspace/libs/lib/x86_64-linux-gnu")
os.environ.setdefault("FONTCONFIG_FILE", "/workspace/libs/etc/fonts/fonts.conf")
os.environ.setdefault("XDG_DATA_HOME", "/workspace/libs/usr/share")
from playwright.sync_api import sync_playwright

pages = {
    "coran": "/workspace/copier/coran/index.html",
    "arabe": "/workspace/copier/arabe/index.html",
}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 420, "height": 900})
    for nom, path in pages.items():
        p = ctx.new_page()
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.goto(f"file://{path}", wait_until="load")
        p.wait_for_timeout(1500)
        txt = p.inner_text("body")
        print("=" * 30, nom)
        print("ERREURS JS:", errs or "aucune")
        print(txt[:700].replace("\n\n", "\n"))
        p.screenshot(path=f"/tmp/page_{nom}.png", full_page=False)
        p.close()
    b.close()
