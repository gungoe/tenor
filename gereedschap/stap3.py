"""Doorloop van de app met nagebootste GitHub-antwoorden: eerste installatie, kopie en
   vernieuwen, geweigerd token, offline, laadscherm, lange druk, trek om te vernieuwen,
   gefilterd grootboek, oude en mislukte run. Gebruik: python3 gereedschap/stap3.py"""
import json, time
from playwright.sync_api import sync_playwright
from omgeving import kijkbestanden, url, FIXTURES, WERKMAP
kijkbestanden()
VB = (FIXTURES / 'voorbeeld.json').read_text()
REST = (FIXTURES / 'rest.json').read_text()
URL = 'https://api.github.com/repos/gunther/tenor-data/contents/monitor.json'
fouten = []
def ok(voorwaarde, wat):
    print(('  ✓ ' if voorwaarde else '  ✗ ') + wat)
    if not voorwaarde: fouten.append(wat)

with sync_playwright() as p:
    b = p.chromium.launch()
    def nieuw(opslag=None, route=None, vertraging=0):
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/Brussels', has_touch=True)
        if vertraging:
            ctx.add_init_script(f"window.fetch = (f => (...a) => new Promise(r => setTimeout(r, {vertraging})).then(() => f(...a)))(window.fetch);")
        if opslag:
            ctx.add_init_script(f"for (const [k, v] of Object.entries({json.dumps(opslag)})) localStorage.setItem(k, v);")
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: fouten.append('paginafout: ' + str(e)))
        if route: pg.route(URL, route)
        return ctx, pg
    ins = json.dumps({'repo': 'gunther/tenor-data', 'token': 'github_pat_x', 'thema': 'dag'})
    kopie = json.dumps({'tekst': VB, 'opgehaald': '2026-09-10T18:30:00+02:00'})
    antwoord = lambda tekst, status=200: (lambda route: route.fulfill(status=status, body=tekst, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}))
    gezien = {}
    def teller(route):
        gezien['auth'] = route.request.headers.get('authorization'); gezien['accept'] = route.request.headers.get('accept')
        route.fulfill(status=200, body=VB, headers={'Access-Control-Allow-Origin': '*'})

    print('eerste keer, zonder token')
    ctx, pg = nieuw(route=teller); pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(300)
    ok(pg.inner_text('.titel') == 'Instellingen', 'instellingenscherm')
    ok(pg.locator('.terug').count() == 0 and pg.locator('#kop .merk').count() == 1, 'merk, geen terugpijl zonder gegevens')
    ok(pg.locator('#tabbalk').is_hidden(), 'geen tabbalk')
    pg.fill('[data-veld="repo"]', 'gunther/tenor-data'); pg.fill('[data-veld="token"]', 'github_pat_x')
    pg.click('[data-actie="test"]'); pg.wait_for_timeout(400)
    ok('Het token werkt.' in pg.inner_text('.scherm'), 'token testen: werkt')
    ok(gezien.get('auth') == 'Bearer github_pat_x' and gezien.get('accept') == 'application/vnd.github.raw+json', 'headers juist')
    ok(pg.inner_text('.terug-label') == 'STAND', 'terugpijl verschijnt na geslaagde test')
    pg.click('[data-sluit-instellingen]'); pg.wait_for_timeout(400)
    ok(pg.locator('.held').count() == 1 and pg.locator('.titel').count() == 0, 'Stand zonder kop, met held')
    ok('koersen van do 10 sep · 593 namen · volgende' in pg.inner_text('.scherm'), 'Cadence-sub met koersdatum')
    bewaard = json.loads(pg.evaluate("localStorage.getItem('tenor.instellingen')"))
    ok(bewaard['token'] == 'github_pat_x', 'instellingen bewaard onder tenor.instellingen')
    ok(pg.evaluate("!!localStorage.getItem('tenor.kopie')"), 'kopie bewaard')
    ctx.close()

    print('openen met kopie en token; nieuwe stand komt binnen')
    ctx, pg = nieuw({'tenor.instellingen': ins, 'tenor.kopie': kopie}, antwoord(REST), vertraging=700)
    pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(150)
    ok(pg.locator('.held').count() == 1 and '0,3' in pg.inner_text('.held'), 'kopie meteen zichtbaar')
    pg.wait_for_timeout(1200)
    ok('3,5' in pg.inner_text('.held'), 'stil bijgewerkt naar de nieuwe stand')
    ok(pg.evaluate("document.documentElement.hasAttribute('data-rust')"), 'Rest dimt de zaal')
    ok(pg.evaluate("document.querySelector('meta[name=theme-color]').content") == '#EFE9DA', 'statusbalk volgt de gedimde zaal')
    ctx.close()

    print('token ongeldig')
    ctx, pg = nieuw({'tenor.instellingen': ins, 'tenor.kopie': kopie}, antwoord('{}', 401))
    pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(500)
    ok(pg.inner_text('.melding') == 'Het leestoken werkt niet.', 'melding in Instellingen')
    ok(pg.eval_on_selector('.melding', 'e => getComputedStyle(e).color') == 'rgb(138, 59, 43)', 'melding in Brick')
    pg.click('[data-sluit-instellingen]'); pg.wait_for_timeout(400)
    ok(pg.locator('.held').count() == 1, 'terug naar de kopie, zonder opnieuw het geweigerde token te proberen')
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(300)
    ok(pg.locator('.held').count() == 1, 'terugkeer naar de voorgrond zeurt niet opnieuw')
    ctx.close()

    print('offline met kopie')
    ctx, pg = nieuw({'tenor.instellingen': ins, 'tenor.kopie': kopie}, lambda r: r.abort())
    pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(500)
    ok(pg.inner_text('.kopie-regel') == 'offline · kopie van do 10 sep 18:30', 'offline-regel op Stand')
    pg.click('[data-tab="vandaag"]'); ok(pg.locator('.kopie-regel').count() == 1, 'offline-regel op Vandaag')
    ctx.close()

    print('eerste keer met token, zonder kopie')
    ctx, pg = nieuw({'tenor.instellingen': ins}, antwoord(VB), vertraging=1000)
    pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(300)
    ok(pg.inner_text('.laden') == 'Tenor haalt de stand op.', 'laadscherm met merk')
    pg.screenshot(path=str(WERKMAP / 'laden.png'))
    pg.wait_for_timeout(1400)
    ok(pg.locator('.held').count() == 1, 'daarna Stand')
    print('lange druk op het merk')
    box = pg.locator('#kop .merk').bounding_box()
    pg.mouse.move(box['x'] + 10, box['y'] + 10); pg.mouse.down(); pg.wait_for_timeout(300); pg.mouse.up(); pg.wait_for_timeout(400)
    ok(pg.locator('.held').count() == 1, 'korte druk doet niets')
    pg.mouse.down(); pg.wait_for_timeout(700); pg.mouse.up(); pg.wait_for_timeout(200)
    ok(pg.inner_text('.titel') == 'Instellingen', 'lange druk (600 ms) opent Instellingen')
    pg.click('[data-thema-keuze="avond"]')
    ok(pg.evaluate("document.documentElement.dataset.thema") == 'avond' and json.loads(pg.evaluate("localStorage.getItem('tenor.instellingen')"))['thema'] == 'avond', 'thema Avond gekozen en bewaard')
    ok(pg.evaluate("document.querySelector('meta[name=theme-color]').content") == '#131215', 'statusbalk Stage')
    pg.click('[data-thema-keuze="dag"]'); pg.click('[data-sluit-instellingen]'); pg.wait_for_timeout(1400)

    print('trek om te vernieuwen')
    pg.click('[data-tab="portefeuille"]'); pg.wait_for_timeout(200)
    pg.unroute(URL); pg.route(URL, antwoord(REST))
    trek = lambda afstand: pg.evaluate("""(afstand) => {
      const el = document.getElementById('scherm');
      const t = y => new Touch({ identifier: 1, target: el, clientX: 200, clientY: y });
      el.dispatchEvent(new TouchEvent('touchstart', { touches: [t(200)], bubbles: true, cancelable: true }));
      el.dispatchEvent(new TouchEvent('touchmove', { touches: [t(200 + afstand / 2)], bubbles: true, cancelable: true }));
      const half = getComputedStyle(document.querySelector('#kop .merk-onder')).transform;
      el.dispatchEvent(new TouchEvent('touchmove', { touches: [t(200 + afstand)], bubbles: true, cancelable: true }));
      el.dispatchEvent(new TouchEvent('touchend', { touches: [], bubbles: true, cancelable: true }));
      return half;
    }""", afstand)
    half = trek(40); pg.wait_for_timeout(500)
    ok(half.startswith('matrix(0.3'), f'merk strijkt mee met de vinger ({half})')
    eerste = pg.locator('.rendement').first.inner_text(); ok(pg.locator('.tag-afroombaar').count() == 0, f'onder de drempel: niets opgehaald (eerste rendement {eerste})')
    trek(80); pg.wait_for_timeout(1600)
    ok(pg.locator('.tag-afroombaar').count() == 1, 'boven 64 px: vernieuwd (nieuwe stand zichtbaar)')
    ok(pg.locator('.rij.cash').count() == 1 and pg.inner_text('.rij.cash').replace('\\xa0',' ').endswith('10.290'), 'cash als laatste rij')
    ok(pg.inner_text('.onderregel') == '30 posities', 'onderregel alleen posities')

    print('grootboek gefilterd')
    pg.click('[data-ticker="ENR.DE"]'); pg.wait_for_timeout(300)
    g = pg.locator('[data-grafiek]').bounding_box(); pg.mouse.move(g['x'] + g['width'] - 2, g['y'] + 30); pg.mouse.down()
    ok(pg.inner_text('.aflezing').startswith('do 10 sep ·'), 'aflezing met datum uit handelsdagen: ' + pg.inner_text('.aflezing'))
    pg.mouse.up()
    ok('van 31-08' in pg.inner_text('.scherm'), 'rangorde uit rangorde_datum')
    pg.click('[data-filter="ENR.DE"]'); pg.wait_for_timeout(300)
    ok(pg.inner_text('.terug-label') == 'GROOTBOEK' and pg.inner_text('.onderregel').startswith('2 transacties · ENR.DE'), 'terugpijl en gefilterde onderregel')
    pg.click('[data-filter-weg]'); pg.wait_for_timeout(300)
    ok(pg.locator('#kop .merk').count() == 1 and 'ENR.DE' not in pg.inner_text('.onderregel'), 'pijl haalt de filter weg')
    ctx.close()

    print('hartslag oud en fout, tandwiel zonder token')
    ctx, pg = nieuw(); pg.goto(url(WERKMAP / 'oud.html')); pg.wait_for_timeout(300)
    ok(pg.inner_text('.zin') == 'De laatste run is vijf dagen oud. De cijfers hieronder zijn van do 10 sep 2026.', 'app-zin bij oude run')
    ok(pg.locator('.tandwiel').count() == 1, 'tandwiel op Stand zonder token')
    pg.click('.tandwiel'); ok(pg.inner_text('.titel') == 'Instellingen', 'tandwiel opent Instellingen')
    ctx.close()
    fout = json.loads(VB); fout['hartslag']['status'] = 'fout'; fout['hartslag']['run'] = 'Yahoo gaf geen koersen; de run stopte.'
    ctx, pg = nieuw({'tenor.instellingen': ins, 'tenor.kopie': json.dumps({'tekst': json.dumps(fout), 'opgehaald': '2026-09-10T18:30:00+02:00'})}, lambda r: r.abort())
    pg.goto(url(WERKMAP / 'echt.html')); pg.wait_for_timeout(400)
    ok(pg.inner_text('.cadence') == 'CADENCE · FOUT' and pg.inner_text('.zin-extra.alarm') == 'Yahoo gaf geen koersen; de run stopte.', 'fout: label en runtekst onder de zin')
    ctx.close()
    b.close()
print('\nfouten:', fouten or 'geen')
