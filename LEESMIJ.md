# Tenor

De mobiele monitor van het STOXX-600-systeem. De app rekent niets uit. Ze toont `monitor.json`, dat de Mac na de avondrun pusht. De volledige opdracht staat in `tenor-bouwprompt.md`.

## Twee repo's

| repo | zichtbaarheid | inhoud |
|---|---|---|
| `tenor` | publiek, GitHub Pages | de app: deze map |
| `tenor-data` | privaat | `monitor.json`, later ook `abonnementen/` |

GitHub Pages zet alles in de gepubliceerde repo publiek online. Daarom staan de cijfers apart.

In `tenor` staat nergens een `monitor.json`. Het voorbeeld met fictieve cijfers zit in `test/fixtures/voorbeeld.json`. Zo kan de Mac nooit per ongeluk echte cijfers publiek pushen.

**In `tenor`:**

| | |
|---|---|
| `index.html` | de app, één bestand |
| `sw.js` | service worker: bewaart alleen app, iconen en lettertypes; laat GitHub ongemoeid |
| `manifest.webmanifest` | naam, kleuren, iconen voor het beginscherm |
| `iconen/` | het icoon in vier materialen (papier is het standaardicoon) |
| `letters/` | de lettertypes, plus `haal_letters.py` dat ze ophaalt |
| `test/` | het testharnas: `node test/draai.js` |

## 1. De repo's

1. Maak `tenor` aan als **publieke** repo en zet deze map erin.
2. Zet GitHub Pages aan: Settings → Pages → Deploy from a branch → `main`, map `/ (root)`.
3. Maak `tenor-data` aan als **private** repo. Laat de Mac `monitor.json` alleen daarheen pushen.

## 2. De lettertypes (eenmalig, met internet)

```
python3 letters/haal_letters.py
```

Het script haalt Newsreader (400, 500 en 400 cursief), IBM Plex Sans en IBM Plex Mono op als woff2, alleen Latin, met € · − ×. Daarna:

- zet het de bestanden in `letters/`;
- schrijft het de `@font-face`-regels in `index.html`;
- zet het de bestandsnamen in de cachelijst van `sw.js`.

Commit daarna alle drie.

Krijg je later een nieuwe `index.html` of `sw.js`, draai het script dan opnieuw. Zonder deze stap toont de app de reserveletters (Georgia, Helvetica Neue, Menlo).

Geeft het script `CERTIFICATE_VERIFY_FAILED`, dan komt dat door de Python van python.org. Draai eenmalig `Install Certificates.command` in de map van die Python-versie in Programma's.

## 3. De drie tokens

Drie fijnmazige tokens, elk voor één taak. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token. Bij elk: Repository access → **Only select repositories**, en onder Repository permissions alleen **Contents**. Verder niets.

| naam | repo | Contents | waar het staat |
|---|---|---|---|
| **tenor push** | `tenor` | Read and write | in de sleutelhanger van de Mac, om de app te pushen |
| **tenor lezen** | `tenor-data` | Read-only | in de app, in Instellingen |
| **tenor-data schrijven** | `tenor-data` | Read and write | in de sleutelhanger van de Mac, voor de avondrun |

Twee tokens voor dezelfde host (`github.com`) houdt git alleen uit elkaar als het per repo onthoudt. Draai daarom één keer op de Mac:

```
git config --global credential.useHttpPath true
```

Daarna vraagt git bij de eerste push naar elke repo om een wachtwoord: plak daar het token dat bij die repo hoort. Een token komt nooit in een bestand, een commit of een commando.

Over het leestoken in de app:

- Werkt het niet (verlopen of fout ingevuld), dan toont Tenor "Het leestoken werkt niet."
- Heeft het nog geen toegang tot `tenor-data`, of staat `monitor.json` er nog niet, dan antwoordt GitHub met 404. Tenor toont dan "Niet gevonden — klopt de repo of het pad?" en opent vanzelf zodra het lukt.

## 4. Op het beginscherm

1. Open `https://gungoe.github.io/tenor/` in Safari → Deel → **Zet op beginscherm**.
2. Open Tenor vanaf het beginscherm. Zonder token opent Instellingen: vul `gungoe/tenor-data` en het token "tenor lezen" in, tik **Token testen**, en daarna op de terugpijl.
3. Instellingen later terugvinden: houd het merk linksboven 0,6 s ingedrukt.

## 5. Bij elke uitrol

1. Verhoog `VERSIE` in `sw.js` én in `index.html` (zoek naar `const VERSIE`), met hetzelfde nummer.
2. Push naar `tenor`.
3. Wacht tot 10 minuten: zo lang mag de iPhone de vorige versie van GitHub Pages nog uit zijn eigen buffer halen.
4. Open de app, sluit ze, en open ze opnieuw. De eerste keer haalt ze de nieuwe versie op de achtergrond binnen, de tweede keer toont ze die.

Instellingen toont het versienummer, zodat je kunt zien welke versie draait.

## 6. Controle op de iPhone

Deze dingen zie je alleen op het toestel zelf:

- **Statusbalk**: Paper overdag, Stage 's avonds, de gedimde zaal bij Rest. Forceer de avond via Instellingen → Thema → Avond.
- **Vliegtuigstand**: de app opent en toont onder Cadence "offline · kopie van …".
- **Lettertypes**: de held in Newsreader, de cijfers in Plex Mono met een echt min-teken, de openingszin cursief. Controleer dat ook in vliegtuigstand.
- **Trek naar beneden** op elk hoofdscherm: het merk strijkt mee en de stand wordt vernieuwd.
- **Tokentest**: één keer met het echte fijnmazige token op `tenor-data`, niet alleen met een voorbeeld.
