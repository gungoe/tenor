"""Loopt de vier gebaren en de navigatie door: strijk bij openen, detail heen en terug,
   het grootboek gefilterd, en het aflezen van de grafiek. Meldt fouten uit de console.
   Gebruik: python3 gereedschap/beweging.py"""
from playwright.sync_api import sync_playwright
from omgeving import kijkbestanden, url, WERKMAP
kijkbestanden(('voorbeeld',))
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/Brussels')
    pg = ctx.new_page(); fouten = []
    pg.on('console', lambda m: m.type == 'error' and fouten.append(m.text)); pg.on('pageerror', lambda e: fouten.append(str(e)))
    pg.goto(url(WERKMAP / 'voorbeeld.html'))
    pg.wait_for_timeout(350); pg.screenshot(path=str(WERKMAP / 'beweging-350.png'), clip={'x':0,'y':0,'width':390,'height':620})
    pg.wait_for_timeout(1600)
    # tabwissel, detail, terug, filter
    pg.click('[data-tab="portefeuille"]'); pg.click('[data-ticker="ENR.DE"]'); pg.wait_for_timeout(300)
    assert pg.inner_text('.detail-naam .titel') == 'Siemens Energy'
    pg.click('[data-filter="ENR.DE"]'); pg.wait_for_timeout(300)
    print('grootboek-onderregel:', pg.inner_text('.onderregel'))
    pg.click('[data-tab="grootboek"]'); print('na tweede tik:', pg.inner_text('.onderregel'))
    pg.click('[data-ticker="SAP.DE"][data-herkomst="grootboek"]'); print('terug-label:', pg.inner_text('.terug'))
    pg.click('[data-terug]'); print('terug op:', pg.inner_text('.titel'))
    # grafiek aflezen op Stand
    pg.click('[data-tab="stand"]'); g = pg.locator('[data-grafiek]').bounding_box()
    pg.mouse.move(g['x'] + 80, g['y'] + 40); pg.mouse.down(); print('aflezing:', pg.inner_text('.aflezing')); pg.mouse.up()
    print('fouten:', fouten)
    b.close()
