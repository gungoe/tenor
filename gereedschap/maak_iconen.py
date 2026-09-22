# Het app-icoon: één vorm (4.1), vier materialen (4.2). SVG als bron, PNG per maat via Chromium.
import pathlib
from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
ICONEN = REPO / 'iconen'
MATERIALEN = {
  'papier': dict(grond='#F5F1E8', boven='#A8791C', onder='#8E97A1', onder_dekking=1),
  'zaal':   dict(grond='#131215', boven='#D6B25E', onder='#6F6B64', onder_dekking=1),
  'inkt':   dict(grond='#14181C', boven='#F5F1E8', onder='#F5F1E8', onder_dekking=0.55),
  'goud':   dict(grond='#C9A45C', boven='#14181C', onder='#14181C', onder_dekking=1),
}
def svg(m, afgerond=True):
    # merk 46 × 28 op 56% van de zijde, gecentreerd in een vak van 100
    schaal = 56 / 46; x0 = (100 - 46 * schaal) / 2; y0 = (100 - 28 * schaal) / 2
    rx = 23 if afgerond else 0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="{rx}" fill="{m['grond']}"/>
  <g transform="translate({x0:.3f} {y0:.3f}) scale({schaal:.5f})">
    <rect x="0" y="4" width="23" height="5" rx="2.5" fill="{m['boven']}"/>
    <circle cx="29" cy="6.5" r="3.2" fill="{m['boven']}"/>
    <rect x="0" y="19" width="46" height="4" rx="2" fill="{m['onder']}" fill-opacity="{m['onder_dekking']}"/>
  </g>
</svg>'''
ICONEN.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for naam, m in MATERIALEN.items():
        open(ICONEN / f'tenor-{naam}.svg', 'w').write(svg(m))
        # 180: vol vierkant, iOS rondt zelf af (doorzichtige hoeken worden daar zwart); 192 en 512: hoekstraal 23%
        for maat, afgerond in ((180, False), (192, True), (512, True)):
            pg = b.new_page(viewport={'width': maat, 'height': maat})
            pg.set_content(f'<style>html,body{{margin:0;background:transparent}}svg{{display:block;width:{maat}px;height:{maat}px}}</style>{svg(m, afgerond)}')
            pg.screenshot(path=str(ICONEN / f'tenor-{naam}-{maat}.png'), omit_background=True)
            pg.close()
    b.close()
print('iconen klaar')
