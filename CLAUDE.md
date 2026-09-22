# Tenor — app-repo

Mobiele monitor (PWA) van een trendvolgend systeem op STOXX 600-aandelen. De app rekent
niets uit: ze toont `monitor.json`, dat een Mac na de avondrun naar een tweede, private
repo pusht. Versie staat in `index.html` en `sw.js`, in `const VERSIE`.

## Rol
Je voert uit, je ontwerpt niet. Het ontwerp ligt vast en is nagekeken; het staat in
`tenor-bouwprompt.md`, buiten deze repo. Je voegt geen schermen, kleuren, animaties,
teksten of functies toe die er niet in staan, ook niet als je ze beter vindt: noteer
ze als suggestie aan het einde. Waar iets niet vastligt, kies je het rustigste
alternatief en meld je die keuze in één zin. Waar iets zichzelf tegenspreekt of niet
kan, stop je en stel je één concrete vraag in plaats van te gokken.

Leidend voor het werk zelf: `LEESMIJ.md` en `gereedschap/LEESMIJ.md`.

## Grenzen
- `index.html` is de enige bron van de app. Er is geen bouwstap en geen `bron/`-map.
- `letters/haal_letters.py` schrijft zelf in `index.html` en `sw.js`, tussen merktekens.
  Raak die merktekens en wat ertussen staat niet met de hand aan.
- De service worker cachet alleen de app, iconen en lettertypes. Aanroepen naar
  `api.github.com` blijven ongemoeid: een tweede kopie zou een netwerkfout laten lijken
  op een geslaagde 200 en de offline-regel verbergen.
- `VERSIE` verhoog je alleen bij een echte uitrol, en dan in `index.html` én `sw.js`
  met hetzelfde nummer.
- Geen bibliotheken, frameworks of npm-pakketten. Vanilla HTML, CSS en JavaScript.
- Nederlands in de interface én in de code: geen Engelse woorden op het scherm, geen
  emoji, geen placeholdertekst.
- Deze repo is **publiek**. Er staat nooit een `monitor.json` in (het voorbeeld heet
  `test/fixtures/voorbeeld.json`), nooit een token, nooit echte cijfers.
- Blijf in deze map. De mappen erboven horen bij het tradingsysteem en niet bij de app.

## Na elke wijziging
1. `node test/draai.js` — het model, 84 tests.
2. `python3 gereedschap/stap3.py` en `stap3b.py` — de foutpaden en de toestanden.
3. `python3 gereedschap/controle.py` — elk scherm op 390 × 844, dag en avond.
4. `python3 gereedschap/beweging.py` — de vier gebaren.
5. `python3 gereedschap/swtest.py` en `uitrol.py nieuw` — alleen na werk aan `sw.js`
   of het manifest.

Alles hoort te eindigen op `fouten: geen`. Een wijziging die alleen door het
testharnas komt, is niet nagekeken: de schermen zitten in de scripts hierboven.

## Wat Günther zelf doet
De repo's aanmaken, GitHub Pages aanzetten, het leestoken maken, en de controle op de
iPhone (stap 6 van `LEESMIJ.md`). Het token komt nooit in een bestand, een commit of
een commando terecht.
