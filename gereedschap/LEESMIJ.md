# Gereedschap

Scripts om Tenor na te kijken en om de voorbeelden en iconen te maken. Ze horen in de app-repo, naast `index.html`, en je draait ze vanuit de map van de repo:

```
python3 gereedschap/controle.py
```

Het model test je zonder dit gereedschap, met `node test/draai.js`. Alles wat je hier vindt, test de schermen en de service worker: dat wat een modeltest niet ziet.

## Wat je eerst nodig hebt

| | getest met | minimum |
|---|---|---|
| Node | 22.22 | 18 |
| Python | 3.12 | 3.9 |
| Playwright (Python) | 1.56 | — |
| Chromium van Playwright | 141 | — |

```
pip3 install playwright
python3 -m playwright install chromium
```

Meer is er niet nodig: geen npm-pakketten, geen Pillow, geen Safari. Klaagt `pip3` over een "externally-managed environment", maak dan eerst een venv (`python3 -m venv .venv && source .venv/bin/activate`). De scripts gebruiken Chromium, niet Safari; het laatste woord heeft dus altijd de iPhone.

## De controlescripts

| script | duurt | wat het doet |
|---|---|---|
| `controle.py` | ~2 min | Elk scherm op 390 × 844, in dag en avond, met elke fixture, Portefeuille in elk van de drie sorteringen en Detail met een zichtbaar instaplabel. Meldt alles wat buiten de marge valt, afbreekt of een tikdoel onder 44 px heeft, controleert de rij CASH als laatste, de grenslijn bij RANG en de grootboekrij met breukdeel, en legt van elk scherm twee afdrukken in `werkmap/`. Met argumenten te beperken: `python3 gereedschap/controle.py voorbeeld dag`. |
| `stap3.py` | ~20 s | De app met nagebootste GitHub-antwoorden: eerste installatie, kopie en vernieuwen, geweigerd token, offline, laadscherm, lange druk op het merk, trek om te vernieuwen, gefilterd grootboek, oude en mislukte run. |
| `stap3b.py` | ~1 min | Per reviewpunt: rendement onder 10%, een naam die verdwijnt, dividend, balklengtes, "pt" in Gold ink, 5xx, 404 met en zonder kopie, de wachtregel na 8 s en de time-out van 15 s. Daarom de wachttijden. |
| `beweging.py` | ~10 s | De vier gebaren en de navigatie: strijk bij openen, detail heen en terug, gefilterd grootboek, aflezen van de grafiek. Meldt fouten uit de console. |
| `swtest.py` | ~15 s | De service worker, op een eigen servertje (poort 8765): wat er in de cache komt, dat GitHub ongemoeid blijft, openen in vliegtuigstand, en het opruimen van een oude cache. |
| `uitrol.py` | ~20 s | Een uitrol achter `max-age=600`, zoals GitHub Pages. `python3 gereedschap/uitrol.py nieuw 8802` hoort `0.5.0 → 9.9.9 → 9.9.9` te geven: de nieuwe versie bij de tweede opening. Met `oud` draait hij dezelfde proef zonder de twee cacheregels in `sw.js`; dan blijft hij hangen op de oude versie. |
| `pages_server.py` | — | Het servertje dat `Cache-Control: max-age=600` meestuurt. De andere scripts starten het zelf. |
| `omgeving.py` | — | Paden, de kijkbestanden en het starten van de server. Geen script om te draaien. |

Na een wijziging in `index.html` is dit de ronde: `node test/draai.js`, dan `stap3.py`, `stap3b.py`, `controle.py`, `beweging.py`, en `swtest.py` als je aan `sw.js` of het manifest kwam.

Alle scripts eindigen met `fouten: geen` of met een lijst. Draai je zonder internet, dan meldt `beweging.py` een 403 voor Google Fonts: dat komt van het kijkbestand, niet van de app.

## De makers

| script | schrijft |
|---|---|
| `maak_voorbeeld.js` | `test/fixtures/voorbeeld.json` — dag 3 na de herstart van 22 september 2026, fictief maar met vaste willekeur, dus altijd hetzelfde resultaat. `node gereedschap/maak_voorbeeld.js` |
| `../test/fixtures/maak_fixtures.js` | `rest.json` en `oud.json`, afgeleid uit `voorbeeld.json`. Draai dit dus ná de vorige. |
| `maak_iconen.py` | `iconen/` — één vorm, vier materialen, als SVG en als PNG van 180, 192 en 512. |
| `maak_voorbeeld_html.py` | Een los html-bestand met een fixture erin. De controlescripts roepen het zelf aan; het resultaat staat in `werkmap/`. |

## werkmap/

`gereedschap/werkmap/` vult zich met kijkbestanden en schermafdrukken en mag altijd weg. Hij staat in `.gitignore`. De scripts werken verder in `/tmp/tenor-*`; ook die mappen zijn wegwerpbaar.
