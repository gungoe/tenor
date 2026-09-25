"""Uitrol achter de HTTP-cache van GitHub Pages (max-age=600): installeert de huidige versie,
   verhoogt daarna VERSIE in index.html en sw.js naar 9.9.9, en opent drie keer.
   'nieuw' hoort 0.5.0 -> 9.9.9 -> 9.9.9 te geven, 'oud' (zonder de twee cacheregels) blijft hangen.
   Gebruik: python3 gereedschap/uitrol.py nieuw 8802"""
import sys, time, pathlib, shutil, subprocess
from playwright.sync_api import sync_playwright
from omgeving import kopie_van_de_app, start_server
variant = sys.argv[1] if len(sys.argv) > 1 else 'nieuw'
poort = int(sys.argv[2]) if len(sys.argv) > 2 else 8802
map_ = kopie_van_de_app(f'/tmp/tenor-uitrol-{variant}')
sw = map_ / 'sw.js'
if variant == 'oud':   # de regels van vóór de review
    s = sw.read_text()
    s = s.replace("cache.addAll(APP.map(u => new Request(u, { cache: 'reload' })))", "cache.addAll(APP)")
    s = s.replace("fetch(verzoek.mode === 'navigate' ? './index.html' : verzoek, { cache: 'no-cache' })", "fetch(verzoek)")
    sw.write_text(s)
server = start_server(map_, poort)
def versie(pg): return pg.evaluate("document.documentElement.innerHTML.match(/const VERSIE = '([\\d.]+)'/)[1]")
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context()
        pg = ctx.new_page(); pg.goto(f'http://localhost:{poort}/'); pg.wait_for_timeout(1500)
        pg.goto(f'http://localhost:{poort}/'); pg.wait_for_timeout(800)            # nu door de service worker
        gezien = [versie(pg)]
        time.sleep(1.2)
        for f in ('index.html', 'sw.js'):
            pad = map_ / f
            tekst = pad.read_text()
            oud_nr = tekst.split("VERSIE = '")[1].split("'")[0]
            pad.write_text(tekst.replace(f"VERSIE = '{oud_nr}'", "VERSIE = '9.9.9'"))
        for opening in range(3):                                                  # openen na de push
            pg.close(); pg = ctx.new_page(); pg.goto(f'http://localhost:{poort}/'); pg.wait_for_timeout(1500)
            gezien.append(versie(pg))
        print(variant, '· vóór de push:', gezien[0], '· openingen na de push:', ' → '.join(gezien[1:]),
              '· caches:', pg.evaluate('caches.keys()'))
        b.close()
finally:
    server.terminate()
