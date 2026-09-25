"""Service worker: wat er wel en niet in de cache komt, dat GitHub ongemoeid blijft,
   openen in vliegtuigstand, en het opruimen van een oude cache bij een nieuwe versie.
   Start zelf een servertje op localhost. Gebruik: python3 gereedschap/swtest.py"""
import json, re
from playwright.sync_api import sync_playwright
from omgeving import FIXTURES, kopie_van_de_app, start_server

VB = (FIXTURES / 'voorbeeld.json').read_text()
MAP = kopie_van_de_app('/tmp/tenor-swtest')
POORT = 8765
VERSIE = (MAP / 'sw.js').read_text().split("VERSIE = '")[1].split("'")[0]
fouten = []


def ok(v, wat):
    print(('  ✓ ' if v else '  ✗ ') + wat)
    if not v:
        fouten.append(wat)


server = start_server(MAP, POORT)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/Brussels')
        ctx.add_init_script("""if (!sessionStorage.getItem('gezet')) { sessionStorage.setItem('gezet', '1');
          localStorage.setItem('tenor.instellingen', JSON.stringify({repo: 'gunther/tenor-data', token: 'github_pat_x', thema: 'dag'}));
          localStorage.setItem('tenor.kopie', JSON.stringify({tekst: %s, opgehaald: '2026-09-24T18:30:00+02:00'})); }""" % json.dumps(VB))
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: fouten.append(str(e)))
        api = []
        pg.on('request', lambda r: 'api.github.com' in r.url and api.append(r.url))
        pg.goto(f'http://localhost:{POORT}/')
        pg.wait_for_timeout(1500)
        actief = pg.evaluate("navigator.serviceWorker.controller !== null")
        if not actief:
            pg.reload(); pg.wait_for_timeout(800)
            actief = pg.evaluate("navigator.serviceWorker.controller !== null")
        ok(actief, 'service worker geregistreerd en actief')
        caches = pg.evaluate("caches.keys()")
        ok(caches == [f'tenor-app-{VERSIE}'], f'één cache, met versie in de naam: {caches}')
        inhoud = pg.evaluate(f"caches.open('tenor-app-{VERSIE}').then(c => c.keys()).then(k => k.map(r => new URL(r.url).pathname).sort())")
        # de verwachting komt uit sw.js zelf: haal_letters.py zet daar de lettertypes bij, een vaste lijst hier veroudert
        APP_IN_SW = re.findall(r"'(\./[^']*)'", (MAP / 'sw.js').read_text().split('const APP = [')[1].split('];')[0])
        verwacht = sorted({'/' if u == './' else '/' + u[2:] for u in APP_IN_SW})
        ok(inhoud == verwacht, f'de cache is precies de lijst uit sw.js: {inhoud}')
        # tweede toets, want de vorige legt sw.js alleen naast zichzelf: geen pad buiten de app, de iconen en de letters
        ok(all(p in ('/', '/index.html', '/manifest.webmanifest') or p.startswith('/iconen/') or p.startswith('/letters/')
               for p in inhoud), f'alleen /, index.html, manifest, /iconen/ en /letters/: {inhoud}')
        pg.wait_for_timeout(500)
        ok(len(api) >= 1, f'de app vroeg monitor.json op bij GitHub ({len(api)}×)')
        # De eerste opening hierboven ging met internet: api.github.com antwoordt dan 401 op het proeftoken
        # en de app opent Instellingen, niet de offline-regel. Het netwerk gaat dus pas nu weg, en met
        # set_offline en niet met een route: een route onderschept vóór de service worker, en de aanvraag
        # moet er juist langs gaan en daar onbeantwoord blijven — dat is wat deze regel toetst.
        api.clear()
        ctx.set_offline(True)
        pg.reload(); pg.wait_for_timeout(1200)
        ok(len(api) >= 1, f'de aanvraag gaat ook zonder netwerk langs de service worker naar GitHub ({len(api)}×)')
        ok(pg.locator('.kopie-regel').inner_text().startswith('offline · kopie van'),
           'zonder netwerk naar GitHub: offline-regel, geen nagebootste 200')
        alles = pg.evaluate("caches.keys().then(ns => Promise.all(ns.map(n => caches.open(n).then(c => c.keys())))).then(l => l.flat().map(r => r.url))")
        ok(not any('github' in u or 'monitor.json' in u for u in alles), 'geen enkel GitHub-antwoord in een cache')

        print('vliegtuigstand')
        pg.reload(); pg.wait_for_timeout(800)
        ok(pg.locator('.held').count() == 1, 'app opent offline vanuit de cache')
        ok(pg.locator('.kopie-regel').inner_text().startswith('offline · kopie van'), 'offline-regel onder Cadence')
        ctx.set_offline(False)

        print('nieuwe versie')
        sw = MAP / 'sw.js'
        sw.write_text(sw.read_text().replace(f"VERSIE = '{VERSIE}'", "VERSIE = '9.9.9'"))
        pg.evaluate("navigator.serviceWorker.getRegistration().then(r => r.update())")
        pg.wait_for_timeout(1500)
        caches = pg.evaluate("caches.keys()")
        ok(caches == ['tenor-app-9.9.9'], f'oude cache opgeruimd bij activate: {caches}')
        ctx.close(); b.close()
finally:
    server.terminate()

print('\nfouten:', fouten or 'geen')
