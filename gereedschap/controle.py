"""Opmaakcontrole: elk scherm in dag en avond, met elke fixture, in vier maten:
   390 x 844 en 440 x 956 staand, en 844 x 390 liggend, één keer met de uitsparing links
   (--veilig-links: 59px) en één keer rechts (--veilig-rechts: 59px), telkens met --veilig-onder: 21px.
   Meldt alles wat buiten de marge of de kolom valt, tekst in de nagebootste uitsparing, een tabbalk die
   niet onderaan in de kolom staat, koppen die niet meescrollen (of wel, bij een hoog venster), wat afbreekt
   en tikdoelen kleiner dan 44 px; controleert Portefeuille in elk van de drie sorteringen (CASH als laatste,
   de grenslijn bij RANG), de grootboekrij met breukdeel, het instaplabel en de metaregel op Detail,
   en legt van elk scherm twee afdrukken in gereedschap/werkmap/.
   Daarna de draaiproef: wisselen tussen 390 x 844 en 844 x 390 bewaart scherm en scrollpositie
   en start geen animatie.
   Gebruik: python3 gereedschap/controle.py [voorbeeld,rest,oud] [dag,avond] [staand,staand440,liggend-links,liggend-rechts]"""
import json, sys
from playwright.sync_api import sync_playwright
from omgeving import kijkbestanden, url, FIXTURES, WERKMAP
CHECK = """
() => {
  const W = innerWidth, fouten = [];
  const kol = document.getElementById('app').getBoundingClientRect();   // de zijmarge van 22 px geldt binnen de kolom
  if (document.documentElement.scrollWidth > W) fouten.push('pagina breder dan scherm: ' + document.documentElement.scrollWidth);
  const sel = '.rij-rechts,.balkwaarde,.onderregel,.cadence,.strook-waarde,.kolom-waarde,.ticker,.rendement,.gewicht,.tag,.titel,.held,.label,.as-onder span,.rij-sub,.zin,.leeg,.reden,.naam,.merk-woord,.rangnummer,.grenslijn,.beschrijving,.klein';
  document.querySelectorAll(sel).forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || el.closest('.voorbeeld-label')) return;
    if (r.right > kol.right - 22 + 0.5 && !el.closest('.tabbalk')) fouten.push('buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,40) + '" right=' + r.right.toFixed(1));
    if (r.left < kol.left + 22 - 0.5 && !el.closest('.tabbalk')) fouten.push('links buiten marge ' + el.className + ' "' + el.textContent.trim().slice(0,30) + '" left=' + r.left.toFixed(1));
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
  // de metaregel op één lijn, zonder afkappen (3 en 9)
  const meta = document.querySelector('.detail-meta');
  if (meta) {
    const lh = parseFloat(getComputedStyle(meta).lineHeight);
    if (meta.getBoundingClientRect().height > lh * 1.5) fouten.push('metaregel afgebroken: "' + meta.textContent + '"');
    if (meta.scrollWidth > meta.clientWidth + 1) fouten.push('metaregel afgekapt: "' + meta.textContent + '"');
  }
  return fouten;
}
"""
# De kolom (4.5 en 8): hoogstens 440 px, gecentreerd binnen de veilige zone, staand over het hele scherm;
# alles erin; geen tekst in de nagebootste uitsparing; de tabbalk onderaan en even breed als de kolom;
# 's avonds het middelpunt van de spot op dezelfde plek tegenover de kolom als staand.
KOLOM = """
(z) => {
  const W = innerWidth, H = innerHeight, fouten = [];
  const app = document.getElementById('app'), kol = app.getBoundingClientRect();
  const binnenL = z.links, binnenR = W - z.rechts;
  if (kol.width > 440.5) fouten.push('kolom breder dan 440 px: ' + kol.width.toFixed(1));
  if (Math.abs((kol.left - binnenL) - (binnenR - kol.right)) > 1) fouten.push(`kolom niet gecentreerd binnen de veilige zone: ${kol.left.toFixed(1)}–${kol.right.toFixed(1)}`);
  if (binnenR - binnenL <= 440 && Math.abs(kol.width - (binnenR - binnenL)) > 1) fouten.push('staand vult de kolom het scherm niet: ' + kol.width.toFixed(1));
  app.querySelectorAll('*').forEach(el => {
    if (el.closest('.spot') || (el.closest('svg') && el.tagName !== 'svg')) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    if (r.left < kol.left - 0.5 || r.right > kol.right + 0.5) fouten.push('buiten de kolom: ' + (el.className.baseVal ?? el.className) + ' "' + el.textContent.trim().slice(0, 30) + '"');
  });
  // tekst: alleen wat zichtbaar is (binnen het scrollende scherm of het venster)
  const scherm = document.getElementById('scherm').getBoundingClientRect();
  const loper = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = loper.nextNode(); n; n = loper.nextNode()) {
    if (!n.textContent.trim() || !n.parentElement || n.parentElement.closest('script,style,.spot')) continue;
    const rng = document.createRange(); rng.selectNodeContents(n);
    const clip = n.parentElement.closest('#scherm') ? scherm : { left: 0, top: 0, right: W, bottom: H };
    for (const r of rng.getClientRects()) {
      const l = Math.max(r.left, clip.left), t = Math.max(r.top, clip.top), rr = Math.min(r.right, clip.right), b = Math.min(r.bottom, clip.bottom);
      if (rr - l <= 0 || b - t <= 0) continue;
      if (l < z.links - 0.5 || rr > W - z.rechts + 0.5 || b > H - z.onder + 0.5 || t < z.boven - 0.5)
        fouten.push('tekst in de uitsparing: "' + n.textContent.trim().slice(0, 30) + '"');
    }
  }
  const tb = document.getElementById('tabbalk');
  if (!tb.hidden) {
    const r = tb.getBoundingClientRect();
    if (Math.abs(r.bottom - H) > 1) fouten.push('tabbalk niet onderaan: ' + r.bottom.toFixed(1));
    if (Math.abs(r.left - kol.left) > 1 || Math.abs(r.right - kol.right) > 1) fouten.push('tabbalk niet even breed als de kolom');
    tb.querySelectorAll('.tab').forEach(t => { if (t.getBoundingClientRect().bottom > H - z.onder + 0.5) fouten.push('tab in de veilige zone onderaan'); });
  }
  const spot = app.querySelector('.spot');
  if (getComputedStyle(spot).display !== 'none') {
    const r = spot.getBoundingClientRect(), mx = (r.left + r.right) / 2 - kol.left, my = (r.top + r.bottom) / 2 - kol.top;
    if (Math.abs(mx + 60) > 1 || Math.abs(my + 60) > 1) fouten.push(`spot niet linksboven buiten de kolom: ${mx.toFixed(0)}, ${my.toFixed(0)}`);
  }
  return [...new Set(fouten)];
}
"""
# De koppen (4.5): bij een venster van minstens 600 px blijft de vaste kop staan, lager scrolt hij mee;
# de koppen die nergens vast staan, scrollen altijd mee.
KOPPEN = """
(hoog) => {
  const fouten = [], sch = document.getElementById('scherm');
  const koppen = [...sch.querySelectorAll('.vast, .titel-rij')].filter(k => !k.parentElement.closest('.vast'));
  const ruimte = sch.scrollHeight - sch.clientHeight;
  if (!koppen.length || ruimte < 1) return fouten;
  const n = Math.min(120, ruimte), voor = koppen.map(k => k.getBoundingClientRect().top);
  sch.scrollTop = n;
  koppen.forEach((k, i) => {
    const verschoven = voor[i] - k.getBoundingClientRect().top, vast = k.classList.contains('vast');
    if (vast && hoog) { if (Math.abs(verschoven) > 0.5) fouten.push('vaste kop scrolt mee bij een venster van minstens 600 px'); }
    else if (Math.abs(verschoven - n) > 0.5) fouten.push((vast ? 'vaste kop' : 'kop') + ' scrolt niet mee: ' + verschoven.toFixed(1) + ' van ' + n);
  });
  sch.scrollTop = 0;
  return fouten;
}
"""
# naam, breedte, hoogte, veilige zones (zoals de variabelen van 8 ze nabootsen)
MATEN = {
    'staand': (390, 844, {}),
    'staand440': (440, 956, {}),
    'liggend-links': (844, 390, {'links': 59, 'onder': 21}),
    'liggend-rechts': (844, 390, {'rechts': 59, 'onder': 21}),
}
# naam, tab, sortering, detail, extra javascript vóór het tekenen
schermen = [
    ('stand', 'stand', None, None, ''), ('portefeuille', 'portefeuille', 'gewicht', None, ''),
    ('portefeuille-instap', 'portefeuille', 'instap', None, ''), ('portefeuille-rang', 'portefeuille', 'rang', None, ''),
    ('vandaag', 'vandaag', None, None, ''), ('grootboek', 'grootboek', None, None, ''),
    ('detail', 'portefeuille', None, 'ENR.DE', ''),
    # instap midden in de 200 dagen, zodat de streep een label krijgt
    ('detail-instap', 'portefeuille', None, 'SAP.DE', "const p = s.monitor.posities.find(x => x.ticker === 'SAP.DE'); p.instap = s.monitor.handelsdagen[120];"),
    ('instellingen', 'stand', None, None, ''), ('gefilterd', 'grootboek', None, None, ''),
    # het breedtegeval van hoofdstuk 3, alleen in rest.json: ESSITY-B.ST · Cyclische consumptie · 8 van 8
    ('detail-breed', 'portefeuille', None, 'ESSITY-B.ST', ''),
]
fixturen = (sys.argv[1] if len(sys.argv) > 1 else 'voorbeeld,rest,oud').split(',')
themas = (sys.argv[2] if len(sys.argv) > 2 else 'dag,avond').split(',')
maten = (sys.argv[3] if len(sys.argv) > 3 else ','.join(MATEN)).split(',')
kijkbestanden()
tickers = {fix: {x['ticker'] for x in json.loads((FIXTURES / f'{fix}.json').read_text())['posities']} for fix in fixturen}
alle = []


def zet_zones(pg, zones):
    """Bootst de uitsparing na via de variabelen van 8; in Chromium is env() altijd 0."""
    if zones:
        pg.evaluate("z => Object.entries(z).forEach(([k, v]) => document.documentElement.style.setProperty('--veilig-' + k, v + 'px'))", zones)


with sync_playwright() as p:
    b = p.chromium.launch()
    for maat in maten:
        breed, hoog, zones = MATEN[maat]
        z = {'boven': 0, 'rechts': 0, 'onder': 0, 'links': 0, **zones}
        achter = '' if maat == 'staand' else '-' + maat
        for fix in fixturen:
            for thema in themas:
                for naam, tab, sortering, detail, extra in schermen:
                    if detail and detail not in tickers[fix]:
                        continue
                    ctx = b.new_context(viewport={'width': breed, 'height': hoog}, device_scale_factor=1, reduced_motion='reduce', color_scheme='light', timezone_id='Europe/Brussels', locale='nl-BE')
                    pg = ctx.new_page()
                    pg.on('pageerror', lambda e: alle.append(f'{maat} {fix} {thema} {naam}: paginafout {e}'))
                    pg.goto(url(WERKMAP / f'{fix}.html'))
                    zet_zones(pg, zones)
                    pg.evaluate(f"""() => {{ Thema.zet('{thema}'); const s = Schermen.staat;
                       {f"Instellingen.bewaar({{ sortering: '{sortering}' }});" if sortering else ''}
                       {extra}
                       s.tab = '{tab}'; s.detail = {json.dumps({'ticker': detail, 'herkomst': 'portefeuille'}) if detail else 'null'};
                       s.modus = '{'instellingen' if naam == 'instellingen' else 'app'}'; s.filter = {"'ENR.DE'" if naam == 'gefilterd' else 'null'};
                       {"s.melding = 'token'; s.test = {soort: 'niet-gevonden'};" if naam == 'instellingen' else ''}
                       Schermen.teken(); }}""")
                    fouten = pg.evaluate(CHECK) + pg.evaluate(KOLOM, z) + pg.evaluate(KOPPEN, hoog >= 600)
                    if sortering: fouten += pg.evaluate(PORTEFEUILLE, sortering)
                    if naam == 'grootboek': fouten += pg.evaluate(GROOTBOEK)
                    if detail: fouten += pg.evaluate(DETAIL, naam == 'detail-instap')
                    pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}{achter}.png'))
                    pg.add_style_tag(content='.app{height:auto!important;overflow:visible!important}.scherm{overflow:visible!important}')
                    pg.screenshot(path=str(WERKMAP / f'{fix}-{thema}-{naam}{achter}-heel.png'), full_page=True)
                    print(maat, fix, thema, naam, 'OK' if not fouten else fouten)
                    alle += [f'{maat} {fix} {thema} {naam}: {f}' for f in fouten]
                    ctx.close()

    # Draaien is geen gebeurtenis (8): het open scherm en de scrollpositie blijven, er wordt niet opnieuw
    # getekend (het schermvlak is hetzelfde element) en er start geen animatie. Zonder reduced_motion,
    # anders zou er nooit een animatie te zien zijn.
    bron = (WERKMAP / 'echt.html').read_text()
    for woord in ('orientationchange', "addEventListener('resize'", 'screen.orientation'):
        if woord in bron:
            alle.append(f'draaien: de app reageert op {woord}')
    LEES = """() => { const s = Schermen.staat, sch = document.getElementById('scherm');
      return { scherm: [s.modus, s.tab, s.detail && s.detail.ticker, s.filter].join('|'), scroll: sch.scrollTop,
               zelfde: !!document.querySelector('.schermvlak[data-gemerkt]'),
               animaties: document.getAnimations().filter(a => a.playState === 'running' && a.effect.getTiming().iterations !== Infinity)
                 .map(a => a.animationName || a.transitionProperty || 'animatie') }; }"""
    for thema in [t for t in themas]:
        for naam, kies, scroll in (('portefeuille', "[data-tab='portefeuille']", 400), ('grootboek', "[data-tab='grootboek']", 300),
                                   ('detail', "[data-ticker='ENR.DE']", 250), ('stand', "[data-tab='stand']", 200)):
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, color_scheme='light', timezone_id='Europe/Brussels', locale='nl-BE')
            pg = ctx.new_page()
            pg.on('pageerror', lambda e: alle.append(f'draaien {thema} {naam}: paginafout {e}'))
            pg.goto(url(WERKMAP / 'voorbeeld.html'))
            pg.evaluate(f"Thema.zet('{thema}')")
            pg.wait_for_timeout(2600)                                   # de strijk bij openen is voorbij
            if naam == 'detail':
                pg.click("[data-tab='portefeuille']"); pg.wait_for_timeout(1600)
            pg.click(kies); pg.wait_for_timeout(1800)                  # inzet (of de schuif naar Detail) is voorbij
            pg.evaluate(f"""() => {{ document.querySelector('.schermvlak').dataset.gemerkt = '';
                                     document.getElementById('scherm').scrollTop = {scroll}; }}""")
            voor = pg.evaluate(LEES)
            fout = []
            if voor['animaties']:
                fout.append(f"vóór het draaien lopen er nog animaties: {voor['animaties']}")
            for stap, (w, h) in enumerate(((844, 390), (390, 844), (844, 390))):
                pg.set_viewport_size({'width': w, 'height': h})
                pg.wait_for_timeout(120)
                na = pg.evaluate(LEES)
                wat = f'{w}x{h} (draai {stap + 1})'
                if na['scherm'] != voor['scherm']: fout.append(f"{wat}: ander scherm: {na['scherm']} in plaats van {voor['scherm']}")
                if abs(na['scroll'] - voor['scroll']) > 1: fout.append(f"{wat}: scrollpositie {na['scroll']} in plaats van {voor['scroll']}")
                if not na['zelfde']: fout.append(f'{wat}: het scherm is opnieuw getekend')
                if na['animaties']: fout.append(f"{wat}: animatie gestart: {na['animaties']}")
            pg.screenshot(path=str(WERKMAP / f'draaien-{thema}-{naam}.png'))
            print('draaien', thema, naam, f"scroll {voor['scroll']}", 'OK' if not fout else fout)
            alle += [f'draaien {thema} {naam}: {f}' for f in fout]
            ctx.close()
    b.close()
print('\nfouten:', alle or 'geen')
