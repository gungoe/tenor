"""Opmaakcontrole: elk scherm op 390 x 844, in dag en avond, met elke fixture.
   Meldt alles wat buiten de marge valt, afbreekt of een tikdoel kleiner dan 44 px is,
   en legt van elk scherm twee afdrukken in gereedschap/werkmap/.
   Gebruik: python3 gereedschap/controle.py [voorbeeld,rest,oud] [dag,avond]"""
import json, sys
from playwright.sync_api import sync_playwright
from omgeving import kijkbestanden, url, WERKMAP
CHECK = """
() => {
  const W = innerWidth, fouten = [];
  if (document.documentElement.scrollWidth > W) fouten.push('pagina breder dan scherm: ' + document.documentElement.scrollWidth);
  const sel = '.rij-rechts,.balkwaarde,.onderregel,.cadence,.strook-waarde,.kolom-waarde,.ticker,.rendement,.gewicht,.tag,.titel,.held,.label,.as-onder span,.rij-sub,.zin,.leeg,.reden,.naam,.merk-woord';
  document.querySelectorAll(sel).forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || el.closest('.voorbeeld-label')) return;
    if (r.right > W - 22 + 0.5 && !el.closest('.tabbalk')) fouten.push('buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '" right=' + r.right.toFixed(1));
    if (r.left < 22 - 0.5 && !el.closest('.tabbalk')) fouten.push('links buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,30) + '" left=' + r.left.toFixed(1));
    if (el.scrollWidth > el.clientWidth + 1 && !el.classList.contains('naam')) fouten.push('afgekapt ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '"');
    const cs = getComputedStyle(el);
    if (cs.whiteSpace === 'nowrap' && !el.querySelector('.klein')) { const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize)*1.4; if (r.height > lh * 1.9) fouten.push('afgebroken ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '"'); }
  });
  document.querySelectorAll('button').forEach(b => { const r = b.getBoundingClientRect(); if (r.width && (r.height < 44 || r.width < 44)) fouten.push('tikdoel ' + b.className + ' ' + r.width.toFixed(0) + 'x' + r.height.toFixed(0)); });
  return [...new Set(fouten)];
}
"""
schermen = [('stand', {}), ('portefeuille', {}), ('vandaag', {}), ('grootboek', {}), ('detail', {}), ('instellingen', {}), ('gefilterd', {})]
fixturen = (sys.argv[1] if len(sys.argv) > 1 else 'voorbeeld,rest,oud').split(',')
themas = (sys.argv[2] if len(sys.argv) > 2 else 'dag,avond').split(',')
kijkbestanden()
with sync_playwright() as p:
    b = p.chromium.launch()
    for fix in fixturen:
        for thema in themas:
            for naam, _ in schermen:
                ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, reduced_motion='reduce', color_scheme='light', timezone_id='Europe/Brussels', locale='nl-BE')
                pg = ctx.new_page()
                pg.goto(url(WERKMAP / f'{fix}.html'))
                tab = {'detail': 'portefeuille', 'instellingen': 'stand', 'gefilterd': 'grootboek'}.get(naam, naam)
                pg.evaluate(f"""() => {{ Thema.zet('{thema}'); const s = Schermen.staat;
                   s.tab = '{tab}'; s.detail = {json.dumps({'ticker': 'ENR.DE', 'herkomst': 'portefeuille'}) if naam == 'detail' else 'null'};
                   s.modus = '{'instellingen' if naam == 'instellingen' else 'app'}'; s.filter = {"'ENR.DE'" if naam == 'gefilterd' else 'null'};
                   {"s.melding = 'token'; s.test = {soort: 'niet-gevonden'};" if naam == 'instellingen' else ''}
                   Schermen.teken(); }}""")
                fouten = pg.evaluate(CHECK)
                pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}.png'))
                pg.add_style_tag(content='.app{height:auto!important;overflow:visible!important}.scherm{overflow:visible!important}')
                pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}-heel.png'), full_page=True)
                print(fix, thema, naam, 'OK' if not fouten else fouten)
                ctx.close()
    b.close()
