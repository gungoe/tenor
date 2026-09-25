"""Opmaakcontrole: elk scherm op 390 x 844, in dag en avond, met elke fixture.
   Meldt alles wat buiten de marge valt, afbreekt of een tikdoel kleiner dan 44 px is,
   controleert Portefeuille in elk van de drie sorteringen (CASH als laatste, de grenslijn bij RANG),
   de grootboekrij met breukdeel en het instaplabel op Detail,
   en legt van elk scherm twee afdrukken in gereedschap/werkmap/.
   Gebruik: python3 gereedschap/controle.py [voorbeeld,rest,oud] [dag,avond]"""
import json, sys
from playwright.sync_api import sync_playwright
from omgeving import kijkbestanden, url, WERKMAP
CHECK = """
() => {
  const W = innerWidth, fouten = [];
  if (document.documentElement.scrollWidth > W) fouten.push('pagina breder dan scherm: ' + document.documentElement.scrollWidth);
  const sel = '.rij-rechts,.balkwaarde,.onderregel,.cadence,.strook-waarde,.kolom-waarde,.ticker,.rendement,.gewicht,.tag,.titel,.held,.label,.as-onder span,.rij-sub,.zin,.leeg,.reden,.naam,.merk-woord,.rangnummer,.grenslijn,.beschrijving,.klein';
  document.querySelectorAll(sel).forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || el.closest('.voorbeeld-label')) return;
    if (r.right > W - 22 + 0.5 && !el.closest('.tabbalk')) fouten.push('buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '" right=' + r.right.toFixed(1));
    if (r.left < 22 - 0.5 && !el.closest('.tabbalk')) fouten.push('links buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,30) + '" left=' + r.left.toFixed(1));
    if (el.scrollWidth > el.clientWidth + 1 && !el.classList.contains('naam')) fouten.push('afgekapt ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '"');
    const cs = getComputedStyle(el);
    if (cs.whiteSpace === 'nowrap' && !el.querySelector('.klein')) { const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize)*1.4; if (r.height > lh * 1.9) fouten.push('afgebroken ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '"'); }
  });
  // de beschrijving hoogstens twee regels
  document.querySelectorAll('.beschrijving').forEach(el => { if (el.scrollHeight > el.clientHeight + 1) fouten.push('beschrijving langer dan twee regels'); });
  document.querySelectorAll('button').forEach(b => { const r = b.getBoundingClientRect(); if (r.width && (r.height < 44 || r.width < 44)) fouten.push('tikdoel ' + b.className + ' ' + r.width.toFixed(0) + 'x' + r.height.toFixed(0)); });
  // 4.5: geen gewichtsbalken op Portefeuille en Detail
  if (document.querySelector('.gewichtspoor, .balkgrid')) fouten.push('gewichtsbalk gevonden');
  return [...new Set(fouten)];
}
"""
# Portefeuille: de volgorde van de rijen, CASH als laatste, de grenslijn alleen bij RANG, het actieve label
PORTEFEUILLE = """
(sortering) => {
  const fouten = [], d = Schermen.staat.monitor;
  const actief = [...document.querySelectorAll('[data-sortering][aria-pressed="true"]')].map(b => b.dataset.sortering);
  if (actief.join() !== sortering) fouten.push('actief label ' + actief + ', verwacht ' + sortering);
  const rijen = [...document.querySelector('.rijen.portefeuille').children];
  const laatste = rijen[rijen.length - 1];
  if (!laatste.classList.contains('cash')) fouten.push('laatste rij is geen CASH');
  const open = d.vandaag.open_plaatsen;
  const verwacht = open > 0 ? `CASH · ${open} ${open === 1 ? 'PLAATS' : 'PLAATSEN'} OPEN` : 'CASH';
  if (laatste.querySelector('.label').innerText !== verwacht) fouten.push('cashlabel ' + laatste.querySelector('.label').innerText);
  const volgorde = rijen.filter(r => r.dataset.ticker).map(r => r.dataset.ticker);
  const veld = { gewicht: 'gewicht', instap: 'rendement', rang: 'rang' }[sortering];
  const waarden = volgorde.map(t => d.posities.find(p => p.ticker === t)[veld]);
  for (let i = 1; i < waarden.length; i++) {
    const a = waarden[i - 1], b = waarden[i];
    if (sortering === 'rang' ? a > b : a < b) fouten.push(`volgorde ${volgorde[i - 1]} vóór ${volgorde[i]}`);
    if (a === b && volgorde[i - 1] > volgorde[i]) fouten.push(`gelijk maar niet op ticker: ${volgorde[i - 1]}, ${volgorde[i]}`);
  }
  const grens = rijen.findIndex(r => r.classList.contains('grenslijn'));
  const buiten = d.posities.some(p => p.in_top60 === false);
  if (sortering === 'rang' && buiten) {
    if (grens < 0) fouten.push('geen grenslijn bij RANG');
    else {
      if (rijen[grens].innerText !== 'BUITEN DE TOP-60 · SMA200 BESLIST') fouten.push('grenslijn: ' + rijen[grens].innerText);
      const voor = rijen.slice(0, grens).filter(r => r.dataset.ticker).map(r => d.posities.find(p => p.ticker === r.dataset.ticker));
      const na = rijen.slice(grens).filter(r => r.dataset.ticker).map(r => d.posities.find(p => p.ticker === r.dataset.ticker));
      if (voor.some(p => p.in_top60 === false) || !na.length || na[0].in_top60 !== false) fouten.push('grenslijn op de verkeerde plaats');
      if (getComputedStyle(rijen[grens]).color !== getComputedStyle(document.querySelector('.label')).color) fouten.push('grenslijn niet in Mute');
    }
    if (!document.querySelector('.rangnummer')) fouten.push('geen rangnummer bij RANG');
    if (!document.querySelector('.onderregel').innerText.startsWith('rangorde ')) fouten.push('onderregel bij RANG: ' + document.querySelector('.onderregel').innerText);
  } else if (grens >= 0) fouten.push('grenslijn buiten RANG of zonder positie buiten de top-60');
  if (sortering !== 'rang' && document.querySelector('.rangnummer')) fouten.push('rangnummer buiten RANG');
  return fouten;
}
"""
# Grootboek: een rij met breukdeel draait de twee regels om; een dividendrij toont het netto
GROOTBOEK = """
() => {
  const fouten = [], d = Schermen.staat.monitor;
  const breuk = d.grootboek.find(r => typeof r.aantal === 'number' && !Number.isInteger(r.aantal));
  if (breuk) {
    const rij = [...document.querySelectorAll('.dag .rij')].find(r => r.querySelector('.ticker').innerText === breuk.ticker);
    const rechts = rij.querySelector('.rij-rechts'), klein = rechts.querySelector('.klein');
    const boven = rechts.firstChild.textContent.trim();
    if (!/^€\\u00a0[\\d.]+$/.test(boven)) fouten.push('breukdeel: bovenaan hoort alleen het bedrag, niet "' + boven + '"');
    if (!/^[\\d.]+,\\d{1,4} × [\\d.]+,\\d\\d · kosten/.test(klein.innerText)) fouten.push('breukdeel: onderregel "' + klein.innerText + '"');
  }
  const div = d.grootboek.find(r => r.kant === 'DIVIDEND' && typeof r.bruto === 'number');
  const divRijen = [...document.querySelectorAll('.tag-dividend')].map(t => t.closest('.rij'));
  if (div && !divRijen.some(r => r.querySelector('.ticker').innerText === div.ticker && r.innerText.includes('ingehouden'))) fouten.push('dividendrij met bruto zonder "ingehouden"');
  const zonder = d.grootboek.find(r => r.kant === 'DIVIDEND' && typeof r.bruto !== 'number');
  if (zonder && !divRijen.some(r => r.querySelector('.ticker').innerText === zonder.ticker && r.innerText.includes('netto · op ex-datum'))) fouten.push('dividendrij zonder bruto zonder "netto · op ex-datum"');
  return fouten;
}
"""
# Detail: de woorden bij de SMA-lijn, geen gewichtsbalk, de instapstreep en het label
DETAIL = """
(metLabel) => {
  const fouten = [];
  const p = Schermen.staat.monitor.posities.find(x => x.ticker === Schermen.staat.detail.ticker);
  const sma = document.querySelector('.sma-label');
  if (typeof p.koers_vs_sma200 === 'number' && !(sma && /^KOERS (GELIJK AAN|[\\d,]+% (BOVEN|ONDER)) SMA200$/.test(sma.textContent))) fouten.push('SMA-label: ' + (sma && sma.textContent));
  const streep = document.querySelector('.instapstreep'), label = document.querySelector('.instap-label');
  if (metLabel && !(streep && label)) fouten.push('instapstreep of -label ontbreekt');
  if (label) {
    const l = label.getBoundingClientRect();
    for (const s of document.querySelectorAll('.as-onder > span:not(.instap-label)')) {
      const r = s.getBoundingClientRect();
      if (l.left < r.right + 39 && l.right > r.left - 39) fouten.push('instaplabel te dicht bij "' + s.innerText + '"');
    }
  }
  return fouten;
}
"""
# naam, tab, sortering, detail, extra javascript vóór het tekenen
schermen = [
    ('stand', 'stand', None, None, ''), ('portefeuille', 'portefeuille', 'gewicht', None, ''),
    ('portefeuille-instap', 'portefeuille', 'instap', None, ''), ('portefeuille-rang', 'portefeuille', 'rang', None, ''),
    ('vandaag', 'vandaag', None, None, ''), ('grootboek', 'grootboek', None, None, ''),
    ('detail', 'portefeuille', None, 'ENR.DE', ''),
    # instap midden in de 200 dagen, zodat de streep een label krijgt
    ('detail-instap', 'portefeuille', None, 'SAP.DE', "const p = s.monitor.posities.find(x => x.ticker === 'SAP.DE'); p.instap = s.monitor.handelsdagen[120];"),
    ('instellingen', 'stand', None, None, ''), ('gefilterd', 'grootboek', None, None, ''),
]
fixturen = (sys.argv[1] if len(sys.argv) > 1 else 'voorbeeld,rest,oud').split(',')
themas = (sys.argv[2] if len(sys.argv) > 2 else 'dag,avond').split(',')
kijkbestanden()
alle = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for fix in fixturen:
        for thema in themas:
            for naam, tab, sortering, detail, extra in schermen:
                ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, reduced_motion='reduce', color_scheme='light', timezone_id='Europe/Brussels', locale='nl-BE')
                pg = ctx.new_page()
                pg.on('pageerror', lambda e: alle.append(f'{fix} {thema} {naam}: paginafout {e}'))
                pg.goto(url(WERKMAP / f'{fix}.html'))
                pg.evaluate(f"""() => {{ Thema.zet('{thema}'); const s = Schermen.staat;
                   {f"Instellingen.bewaar({{ sortering: '{sortering}' }});" if sortering else ''}
                   {extra}
                   s.tab = '{tab}'; s.detail = {json.dumps({'ticker': detail, 'herkomst': 'portefeuille'}) if detail else 'null'};
                   s.modus = '{'instellingen' if naam == 'instellingen' else 'app'}'; s.filter = {"'ENR.DE'" if naam == 'gefilterd' else 'null'};
                   {"s.melding = 'token'; s.test = {soort: 'niet-gevonden'};" if naam == 'instellingen' else ''}
                   Schermen.teken(); }}""")
                fouten = pg.evaluate(CHECK)
                if sortering: fouten += pg.evaluate(PORTEFEUILLE, sortering)
                if naam == 'grootboek': fouten += pg.evaluate(GROOTBOEK)
                if detail: fouten += pg.evaluate(DETAIL, naam == 'detail-instap')
                pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}.png'))
                pg.add_style_tag(content='.app{height:auto!important;overflow:visible!important}.scherm{overflow:visible!important}')
                pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}-heel.png'), full_page=True)
                print(fix, thema, naam, 'OK' if not fouten else fouten)
                alle += [f'{fix} {thema} {naam}: {f}' for f in fouten]
                ctx.close()
    b.close()
print('\nfouten:', alle or 'geen')
