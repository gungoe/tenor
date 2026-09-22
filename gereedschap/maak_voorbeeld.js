// Schrijft test/fixtures/voorbeeld.json. Fictief voorbeeld: dag 2 van de vooruit-meting (start wo 9 sept 2026, stand do 10 sept 2026).
let zaad = 20260909;
const rnd = () => { zaad = (zaad * 1664525 + 1013904223) % 4294967296; return zaad / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());
const r2 = n => Math.round(n * 100) / 100, r4 = n => Math.round(n * 1e4) / 1e4;
const TAKS = 0.0035, SPREAD = 0.001, K = 100000;
const namen = [
 ['RHM.DE','Rheinmetall','Industrials',1712.5],['ENR.DE','Siemens Energy','Industrials',104.6],
 ['SAAB-B.ST','Saab','Industrials',51.8],['LDO.MI','Leonardo','Industrials',49.3],
 ['BA.L','BAE Systems','Industrials',22.4],['SAF.PA','Safran','Industrials',286.2],
 ['SIE.DE','Siemens','Industrials',236.9],['ABBN.SW','ABB','Industrials',61.7],
 ['SAN.MC','Banco Santander','Financials',8.62],['UCG.MI','UniCredit','Financials',67.4],
 ['ISP.MI','Intesa Sanpaolo','Financials',5.71],['BBVA.MC','BBVA','Financials',16.9],
 ['DBK.DE','Deutsche Bank','Financials',31.2],['ALV.DE','Allianz','Financials',361.8],
 ['ZURN.SW','Zurich Insurance','Financials',612.4],['CBK.DE','Commerzbank','Financials',34.1],
 ['ASML.AS','ASML','Information Technology',742.3],['SAP.DE','SAP','Information Technology',248.1],
 ['IFX.DE','Infineon','Information Technology',38.6],['ROG.SW','Roche','Health Care',289.5],
 ['AZN.L','AstraZeneca','Health Care',131.2],['NOVN.SW','Novartis','Health Care',104.8],
 ['IBE.MC','Iberdrola','Utilities',17.4],['ENEL.MI','Enel','Utilities',8.31],
 ['SHEL.L','Shell','Energy',31.9],['TTE.PA','TotalEnergies','Energy',55.2],
 ['NESN.SW','Nestlé','Consumer Staples',84.7],['ULVR.L','Unilever','Consumer Staples',53.6],
 ['MC.PA','LVMH','Consumer Discretionary',612.0],['DTE.DE','Deutsche Telekom','Communication Services',31.4]
];
const sectorN = {}; namen.forEach(n => sectorN[n[2]] = (sectorN[n[2]] || 0) + 1);
const rangen = [...Array(30).keys()].map(i => i + 1 + Math.floor(rnd() * 3 * (i / 29)));
const deel = K / 30;
let beurstaksTot = 0, spreadTot = 0, cash = K, omzetTot = 0;
const grootboek = [], posities = [];
namen.forEach(([ticker, naam, sector, koersIn], i) => {
  const aantal = Math.floor(deel / (koersIn * (1 + TAKS + SPREAD)));
  const bedrag = r2(aantal * koersIn), taks = r2(bedrag * TAKS), spr = r2(bedrag * SPREAD);
  cash -= bedrag + taks + spr; beurstaksTot += taks; spreadTot += spr; omzetTot += bedrag;
  grootboek.push({ datum: '2026-09-09', ticker, kant: 'KOOP', aantal, koers: koersIn, bedrag, beurstaks: taks, spread: spr,
    reden: `rang ${rangen[i]} · plaats vrij` });
  // 400 slotkoersen met trend omhoog, eindigend op 9 sept = koersIn
  const drift = 0.0009 + rnd() * 0.0012, vol = 0.012 + rnd() * 0.01;
  const log = [0]; for (let d = 1; d < 399; d++) log.push(log[d - 1] + drift + vol * gauss());
  const schaalf = koersIn / Math.exp(log[398]);
  const hist = log.map(l => r2(Math.exp(l) * schaalf));
  const dagVerandering = (rnd() - 0.48) * 0.035;
  const koers = r2(koersIn * (1 + dagVerandering)); hist.push(koers);
  const sma = []; for (let d = 199; d < 400; d++) sma.push(r2(hist.slice(d - 199, d + 1).reduce((a, b) => a + b, 0) / 200));
  const reeks = hist.slice(200), smaReeks = sma.slice(1);
  const sma200 = smaReeks[199];
  posities.push({ ticker, naam, sector, sector_n: sectorN[sector], sector_max: 8, aantal, koers,
    dagkoers_verandering: r4(koers / koersIn - 1), instap: '2026-09-09', koers_in: koersIn,
    rendement: r4(koers / koersIn - 1), winst_eur: r2(aantal * (koers - koersIn)), gewicht: 0, gewicht_bij_aankoop: 0,
    sma200, afstand_sma200: r4((sma200 - koers) / koers), rang: rangen[i], score: Math.round(99 - rangen[i] * 0.9 - rnd() * 2),
    in_top60: true, dagen: 1, reeks, sma_reeks: smaReeks, _waardeIn: aantal * koersIn });
});
cash = r2(cash);
const waardeIn = posities.reduce((a, p) => a + p._waardeIn, 0) + cash;
const waarde = posities.reduce((a, p) => a + p.aantal * p.koers, 0) + cash;
posities.forEach(p => { p.gewicht = r4(p.aantal * p.koers / waarde); p.gewicht_bij_aankoop = r4(p._waardeIn / waardeIn); delete p._waardeIn; });
// tracker
const exIn = 55.84, exNu = 55.62, exAantal = Math.floor(K / (exIn * 1.0022));
const exBedrag = r2(exAantal * exIn), exTaks = r2(exBedrag * 0.0012), exSpr = r2(exBedrag * 0.001);
grootboek.push({ datum: '2026-09-09', ticker: 'EXSA.DE', kant: 'TRACKER', aantal: exAantal, koers: exIn, bedrag: exBedrag,
  beurstaks: exTaks, spread: exSpr, reden: 'Baseline · startpositie' });
const exCash = K - exBedrag - exTaks - exSpr;
const trackerIn = r2(exAantal * exIn + exCash), trackerNu = r2(exAantal * exNu + exCash);
const p = r2(waarde), pIn = r2(waardeIn);
const verschil = ((p - trackerNu) / K * 100);
// gedeelde kalender: 200 werkdagen tot en met do 10 sept 2026
const handelsdagen = []; for (let d = new Date(Date.UTC(2026, 8, 10)); handelsdagen.length < 200; d.setUTCDate(d.getUTCDate() - 1)) {
  if (d.getUTCDay() % 6 !== 0) handelsdagen.unshift(d.toISOString().slice(0, 10)); }
const monitor = {
  hartslag: { tijd: '2026-09-10T18:21:04+02:00', status: 'ok', namen: 593, laatste_dag: '2026-09-10', run: 'dagadvies en vooruit bijgewerkt' },
  stand: { datum: '2026-09-10',
    zin: `Tenor staat ${Math.abs(verschil).toFixed(1).replace('.', ',')} punt ${verschil >= 0 ? 'boven' : 'onder'} Baseline. Er wordt gekocht; de zaal is rustig.`,
    portefeuille: p, tracker: trackerNu,
    sinds_start: [['2026-09-09', pIn, trackerIn], ['2026-09-10', p, trackerNu]],
    start: { kapitaal: K, datum: '2026-09-09' } },
  beslisregel: { startdatum: '2026-09-09', oordeeldatum: '2027-09-09', marge_pp: 3, dag: 2, van: 252, oordeel: 'loopt' },
  marktfilter: { aan: true, afstand: 0.083, maanden_onder: 0, bevestiging: 2, laatste_maandeinde: '2026-08-31',
    tekst: 'De markt sloot 8,3% boven haar 10-maandsgemiddelde; er wordt gekocht.' },
  posities,
  vandaag: { datum: '2026-09-10', zin: 'Geen verkoop, geen aankoop; alle dertig plaatsen zijn bezet.',
    verkopen: [], kopen: [], afromingen: [], open_plaatsen: 0, cash },
  grootboek,
  kosten: { beurstaks: r2(beurstaksTot + exTaks), spread: r2(spreadTot + exSpr), omzet: r2(omzetTot / pIn) },
  handelsdagen,
  rangorde_datum: '2026-08-31'
};
require('fs').writeFileSync(require('path').join(__dirname, '..', 'test', 'fixtures', 'voorbeeld.json'), JSON.stringify(monitor, null, 1));
console.log(monitor.stand, monitor.kosten, 'cash', cash, 'verschil pt', verschil.toFixed(2),
  'max gewicht', Math.max(...posities.map(x => x.gewicht)), 'min', Math.min(...posities.map(x => x.gewicht)),
  'afstand', posities.slice(0,4).map(x=>x.afstand_sma200));
