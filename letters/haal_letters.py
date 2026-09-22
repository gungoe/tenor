#!/usr/bin/env python3
"""Zet de lettertypes van Tenor in de repo (eenmalig, en opnieuw als je ze wilt verversen).

Haalt bij Google Fonts de woff2-bestanden op voor precies de gewichten uit hoofdstuk 8 —
Newsreader 400, 500 en 400 cursief, IBM Plex Sans 400/500/600, IBM Plex Mono 400/500 —
en neemt alleen de Latin-deelverzameling, die € · − × al bevat. Daarna:
  - bewaart het de bestanden in letters/,
  - schrijft het de @font-face-regels in index.html (tussen de letters-merktekens),
  - zet het de bestandsnamen in de cachelijst van sw.js (idem).
Alleen de standaardbibliotheek van Python; draai vanuit de map van de repo:  python3 letters/haal_letters.py
"""
import pathlib, re, sys, urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
MAP = REPO / 'letters'
API = ('https://fonts.googleapis.com/css2?'
       'family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400'
       '&family=IBM+Plex+Sans:wght@400;500;600'
       '&family=IBM+Plex+Mono:wght@400;500&display=swap')
# een gewone desktopbrowser krijgt woff2 met unicode-range per deelverzameling
AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
NODIG = {0x20AC: '€', 0x00B7: '·', 0x2212: '−', 0x00D7: '×'}
VERWACHT = {('Newsreader', 'normal', '400'), ('Newsreader', 'normal', '500'), ('Newsreader', 'italic', '400'),
            ('IBM Plex Sans', 'normal', '400'), ('IBM Plex Sans', 'normal', '500'), ('IBM Plex Sans', 'normal', '600'),
            ('IBM Plex Mono', 'normal', '400'), ('IBM Plex Mono', 'normal', '500')}


def haal(url):
    verzoek = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(verzoek, timeout=30) as antwoord:
        return antwoord.read()


def lees_css(css):
    """Geeft per Latin-regel: familie, stijl, gewicht, url, unicode-range."""
    regels = []
    for deel, blok in re.findall(r'/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{([^}]*)\}', css):
        if deel != 'latin':
            continue
        veld = lambda naam: (re.search(naam + r'\s*:\s*([^;]+);', blok) or [None, ''])[1].strip()
        url = re.search(r'url\(([^)]+)\)', blok)
        regels.append({'familie': veld('font-family').strip('\'"'), 'stijl': veld('font-style') or 'normal',
                       'gewicht': veld('font-weight'), 'url': url[1] if url else '', 'bereik': veld('unicode-range')})
    return regels


def dekt(bereik, codepunt):
    for stuk in bereik.split(','):
        stuk = stuk.strip().upper().removeprefix('U+')
        if not stuk:
            continue
        van, _, tot = stuk.partition('-')
        if int(van, 16) <= codepunt <= int(tot or van, 16):
            return True
    return False


def bestandsnaam(r):
    familie = r['familie'].lower().replace(' ', '-')
    return f"{familie}-{r['stijl']}-{r['gewicht'].replace(' ', '-')}.woff2"


def vervang_tussen(tekst, begin, einde, nieuw):
    i, j = tekst.index(begin) + len(begin), tekst.index(einde)
    return tekst[:i] + nieuw + tekst[j:]


def verwerk(regels, laad=haal):
    gevonden = {(r['familie'], r['stijl'], r['gewicht']) for r in regels}
    ontbreekt = VERWACHT - gevonden
    if ontbreekt:
        sys.exit(f'Stop: Google gaf deze snitten niet terug: {sorted(ontbreekt)}')
    for r in regels:
        mist = [teken for cp, teken in NODIG.items() if not dekt(r['bereik'], cp)]
        if mist:
            sys.exit(f"Stop: {r['familie']} {r['stijl']} {r['gewicht']} dekt {' '.join(mist)} niet")

    MAP.mkdir(exist_ok=True)
    per_url, css, lijst = {}, [], []
    for r in sorted(regels, key=lambda r: (r['familie'], r['stijl'], r['gewicht'])):
        if r['url'] not in per_url:                      # variabele letters: één bestand voor meer gewichten
            naam = bestandsnaam(r)
            (MAP / naam).write_bytes(laad(r['url']))
            per_url[r['url']] = naam
            lijst.append(f"  './letters/{naam}',")
        css.append(f"@font-face {{ font-family: '{r['familie']}'; font-style: {r['stijl']}; font-weight: {r['gewicht']}; "
                   f"font-display: swap; src: url(./letters/{per_url[r['url']]}) format('woff2'); unicode-range: {r['bereik']}; }}")

    index = REPO / 'index.html'
    tekst = index.read_text()
    tekst = vervang_tussen(tekst, '/* ==== letters ==== */', '/* ==== einde letters ==== */', '\n' + '\n'.join(css) + '\n')
    index.write_text(tekst)
    sw = REPO / 'sw.js'
    tekst = sw.read_text()
    tekst = vervang_tussen(tekst, '/* ==== letters ==== */', '  /* ==== einde letters ==== */', '\n' + '\n'.join(lijst) + '\n')
    sw.write_text(tekst)
    grootte = sum((MAP / n).stat().st_size for n in per_url.values())
    print(f'{len(per_url)} bestanden ({grootte // 1024} kB) in letters/, {len(css)} @font-face-regels in index.html, cachelijst in sw.js bijgewerkt.')
    print('Verhoog nu VERSIE in sw.js en index.html, en push.')


if __name__ == '__main__':
    verwerk(lees_css(haal(API).decode('utf-8')))
