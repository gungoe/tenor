// Testfixtures voor toestanden die het voorbeeld (dag 3) niet heeft: Rest, afroombaar, restje, verlies, transacties,
// een positie buiten de top-60, open plaatsen, een dividend zonder bruto en inhouding, een positie zonder beschrijving.
// ENR.DE krijgt bewust een instap van vóór de 200 dagen (+954%, geen instapstreep); dat is een randgeval, geen historiek.
const fs = require('fs'), path = require('path');
const basis = JSON.parse(fs.readFileSync(path.join(__dirname, 'voorbeeld.json'), 'utf8'));
const d = JSON.parse(JSON.stringify(basis));
const STAND = basis.stand.datum;
const r5 = n => Math.round(n * 1e5) / 1e5;
const enr = d.posities.find(p => p.ticker === 'ENR.DE');
Object.assign(enr, { koers: 78.6, dagkoers_verandering: 0.014, instap: '2024-01-31', koers_in: 7.46, rendement: 9.536,
  winst_eur: 71138, gewicht: 0.145, gewicht_bij_aankoop: 0.033, sector_n: 6, rang: 4, score: 91, dagen: 947,
  afstand_sma200: -0.18, aantal: 1000 });
const f = 78.6 / enr.reeks[199]; enr.reeks = enr.reeks.map(v => Math.round(v * f * 100) / 100);
enr.sma_reeks = enr.sma_reeks.map(v => Math.round(v * f * 0.93 * 100) / 100); enr.sma200 = enr.sma_reeks[199];
enr.afstand_sma200 = Math.round((enr.sma200 - 78.6) / 78.6 * 1e4) / 1e4;
enr.koers_vs_sma200 = r5(78.6 / enr.sma200 - 1);
const sie = d.posities.find(p => p.ticker === 'SIE.DE');
sie.rendement = -0.0063; delete sie.beschrijving;
const rhm = d.posities.find(p => p.ticker === 'RHM.DE');
Object.assign(rhm, { gewicht: 0.0082, rendement: -0.412, winst_eur: -1204, in_top60: false, rang: 77, score: 38 });
d.posities.find(p => p.ticker === 'SAAB-B.ST').naam = 'Saab Aktiebolag serie B (fictief lange naam)';
// het breedtegeval van hoofdstuk 3: de langste metaregel op Detail, `ESSITY-B.ST · Cyclische consumptie · 8 van 8`.
// Alleen een maat voor de breedtetest, geen uitspraak over Essity; zonder beschrijving, want die is niet nagekeken.
const breed = d.posities.find(p => p.ticker === 'MC.PA');
Object.assign(breed, { ticker: 'ESSITY-B.ST', naam: 'Essity', sector: 'Cyclische consumptie', sector_n: 8, sector_max: 8 });
delete breed.beschrijving;
d.grootboek.filter(r => r.ticker === 'MC.PA').forEach(r => { r.ticker = 'ESSITY-B.ST'; });
d.marktfilter = { aan: false, afstand: -0.021, maanden_onder: 2, bevestiging: 2, laatste_maandeinde: '2026-08-31',
  tekst: 'De markt sloot twee maanden onder haar 10-maandsgemiddelde; er wordt niet gekocht tot ze erboven sluit.' };
d.stand.zin = 'Rest. De markt sloot twee maanden onder haar gemiddelde; er wordt niet gekocht tot ze erboven sluit.';
d.stand.portefeuille = 97120; d.stand.tracker = 100610; d.stand.sinds_start[d.stand.sinds_start.length - 1] = [STAND, 97120, 100610];
d.vandaag = { datum: STAND, zin: 'Rest. De markt sloot twee maanden onder haar gemiddelde; er wordt niet gekocht tot ze erboven sluit.',
  verkopen: [{ ticker: 'RHM.DE', naam: 'Rheinmetall', reden: 'onder SMA200 en uit de top-60 (rang 77)', aantal: 1, bedrag: 1007 }],
  kopen: [],
  afromingen: [{ ticker: 'ENR.DE', naam: 'Siemens Energy', reden: 'twaalf stukken boven 8% voor de aankoop van SAP.DE', aantal: 12, bedrag: 943, voor: 'SAP.DE' }],
  open_plaatsen: 3, cash: 10290 };
d.grootboek.push(
  { datum: STAND, ticker: 'RHM.DE', kant: 'VERKOOP', aantal: 1, koers: 1007.2, bedrag: 1007.2, beurstaks: 3.53, spread: 1.01, reden: 'onder SMA200' },
  { datum: STAND, ticker: 'ENR.DE', kant: 'AFROMING', aantal: 12, koers: 78.6, bedrag: 943.2, beurstaks: 3.3, spread: 0.94, reden: 'boven 8%' },
  { datum: STAND, ticker: 'SAP.DE', kant: 'DIVIDEND', bedrag: 31.5, reden: 'dividend 2,42 per stuk' },
  { datum: STAND, ticker: 'VOW3.DE', kant: 'VERKOOP', aantal: 11234, koers: 88.12, bedrag: 989940.08, beurstaks: 3464.79, spread: 989.94, reden: 'lang bedrag' });
d.posities.find(p => p.ticker === 'SAP.DE').dividend_eur = 31.5;
fs.writeFileSync(path.join(__dirname, 'rest.json'), JSON.stringify(d));
// oud en fout
const oud = JSON.parse(JSON.stringify(basis)); oud.hartslag.tijd = '2026-09-18T18:21:04+02:00';
fs.writeFileSync(path.join(__dirname, 'oud.json'), JSON.stringify(oud));
console.log('fixtures geschreven');
