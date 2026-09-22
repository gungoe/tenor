# Bouwverslag Tenor 0.4.0

Geschreven door wie het gebouwd heeft, als aanvulling op `OVERDRACHT.md`. Twee dingen die daar niet in konden staan: hoe de service worker is nagekeken, en hoe de bouw verliep.

## Hoe de service worker is nagekeken

Er is geen iPhone in de bouwomgeving, dus de controle liep op localhost, dat als veilige context telt en dus een service worker toelaat.

**Gewone controle.** Een kopie van de repo in `/tmp`, daar `python3 -m http.server 8765`, en Chromium erop via Playwright. Wat ik zag:

- `caches.keys()` gaf precies één cache: `tenor-app-0.4.0`.
- De inhoud van die cache was `/`, `/index.html`, `/manifest.webmanifest` en de drie papier-iconen. Meer niet.
- De aanvraag naar `api.github.com` ging langs de service worker naar het netwerk. De omgeving heeft geen internet, dus die mislukte, en onder Cadence stond "offline · kopie van do 10 sep 18:30". Precies het gedrag dat een gegevenscache zou verbergen.
- Geen enkel GitHub-antwoord zat in een cache.
- Met `context.set_offline(True)` en herladen opende de app uit de cache, met dezelfde regel.
- Na `VERSIE` op `0.4.1` en een `registration.update()` bleef alleen `tenor-app-0.4.1` over.

**Uitrol achter de HTTP-cache.** GitHub Pages stuurt `max-age=600`, dus een tweede servertje (`pages_server.py`) dat diezelfde header meestuurt. Daarna een uitrol nagebootst: `VERSIE` verhogen in `index.html` en `sw.js`, en drie keer openen. Met de oude service worker zag ik 0.4.0 → 0.4.0 → 0.4.0; de nieuwe cache kreeg de oude `index.html` uit de HTTP-cache. Met `cache: 'reload'` bij install en `cache: 'no-cache'` bij het verversen werd het 0.4.0 → 0.4.1 → 0.4.1: de nieuwe versie bij de tweede opening, zoals de LEESMIJ belooft.

**Lettertypes.** In een derde kopie draaide `haal_letters.py` met een nagemaakt Google-antwoord. Daarna waren er acht `@font-face`-regels actief en stonden de acht bestanden in de cache van de service worker.

## De bouw in vier stappen

**1. Model en tests.** Bij het doorlezen botsten hoofdstuk 4.3 en 8 (goud is nooit tekst, contrast minstens 4,5:1) met hoofdstuk 5, dat cijfers en labels in goud zet. Ik heb het model en 54 tests gebouwd — die hangen niet van kleur af — en daarna gestopt met één vraag. Dat leverde Gold ink op, en een palet dat wél haalbaar is.

**2. Schermen.** Vijf schermen, vier gebaren, dag en avond. Twee dingen bleken pas op 390 × 844 zichtbaar: de as-labels van de grafieken liepen dwars door de lijnen (opgelost met een eigen strook links), en de avondspot werd afgedekt door de vaste kop van Portefeuille (die kop draagt nu dezelfde lichtvlek). De kop "Stand" die ik netjes volgens de algemene regel had toegevoegd, moest er weer af: de held ís daar de kop.

**3. Toestanden en ophalen.** Hier zaten de echte fouten, en ze kwamen allemaal uit hetzelfde hoekje: wat doet de app ná een mislukte poging. Een geweigerd token stuurde je naar Instellingen, de terugpijl haalde meteen opnieuw op, en je stuiterde terug — een lus. Zonder kopie liep de terugpijl dood op een leeg laadscherm. Een hangende fetch hield "bezig" vast, zodat elke trek genegeerd werd. Pas toen "uitkomst van het ophalen → volgend scherm" een pure functie in het model werd, met een tabeltest per uitkomst, met en zonder kopie en vanuit elk scherm, waren die gevallen niet langer een kwestie van geheugen.

**4. De PWA-laag.** De service worker bewaart alleen de app. Cachet hij ook `monitor.json`, dan ziet een netwerkfout eruit als een geslaagde 200 en verdwijnt precies de eerlijkheid die stap 3 opleverde. Daarna kwam de hosting: Pages zet alles in de gepubliceerde repo publiek online, dus de app en de cijfers wonen nu in twee repo's, en in de app-repo staat nergens een `monitor.json`.

Wat er telkens misging, ging mis op dezelfde plek: niet in wat het scherm toont, maar in wat er gebeurt als iets niet lukt.
