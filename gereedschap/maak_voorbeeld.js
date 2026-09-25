// Schrijft test/fixtures/voorbeeld.json. Fictief voorbeeld: dag 3 van de vooruit-meting (herstart di 22 sept 2026, stand do 24 sept 2026).
let zaad = 20260909;
const rnd = () => { zaad = (zaad * 1664525 + 1013904223) % 4294967296; return zaad / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());
const r2 = n => Math.round(n * 100) / 100, r4 = n => Math.round(n * 1e4) / 1e4, r5 = n => Math.round(n * 1e5) / 1e5;
const START = '2026-09-22', MIDDEN = '2026-09-23', STAND = '2026-09-24';
const TAKS = 0.0035, SPREAD = 0.001, K = 100000;
// ticker, naam, sector (in het Nederlands, zoals de Mac ze wegschrijft), koers bij instap, beschrijving (hoogstens 90 tekens, geen cijfer)
const namen = [
 ['RHM.DE','Rheinmetall','Industrie',1712.5,'Voertuigen, munitie en luchtverdediging voor krijgsmachten, en onderdelen voor auto\'s.'],
 ['ENR.DE','Siemens Energy','Industrie',104.6,'Gasturbines, windturbines en netapparatuur voor het opwekken en vervoeren van stroom.'],
 ['SAAB-B.ST','Saab','Industrie',51.8,'Gevechtsvliegtuigen, radar, raketten en onderzeeërs voor defensie en civiele veiligheid.'],
 ['LDO.MI','Leonardo','Industrie',49.3,'Helikopters, defensie-elektronica en onderdelen voor vliegtuigen en de ruimtevaart.'],
 ['BA.L','BAE Systems','Industrie',22.4,'Oorlogsschepen, gevechtsvoertuigen, vliegtuigen en elektronica voor krijgsmachten.'],
 ['SAF.PA','Safran','Industrie',286.2,'Vliegtuigmotoren, landingsgestellen en cabine-uitrusting voor de luchtvaart.'],
 ['SIE.DE','Siemens','Industrie',236.9,'Automatisering voor fabrieken, gebouwtechniek, spoorwegen en medische beeldvorming.'],
 ['ABBN.SW','ABB','Industrie',61.7,'Elektrificatie, motoren en automatisering voor industrie, gebouwen en infrastructuur.'],
 ['SAN.MC','Banco Santander','Financiële diensten',8.62,'Bank voor particulieren en bedrijven in Europa en in Noord- en Zuid-Amerika.'],
 ['UCG.MI','UniCredit','Financiële diensten',67.4,'Bank voor particulieren en bedrijven in Italië, Duitsland en Centraal- en Oost-Europa.'],
 ['ISP.MI','Intesa Sanpaolo','Financiële diensten',5.71,'Italiaanse bank met sparen, verzekeren en vermogensbeheer voor particulieren en bedrijven.'],
 ['BBVA.MC','BBVA','Financiële diensten',16.9,'Bank voor particulieren en bedrijven in Spanje, Mexico, Turkije en Zuid-Amerika.'],
 ['DBK.DE','Deutsche Bank','Financiële diensten',31.2,'Zakenbank en bank voor bedrijven, particulieren en vermogensbeheer, vanuit Duitsland.'],
 ['ALV.DE','Allianz','Financiële diensten',361.8,'Schade-, levens- en zorgverzekeringen en vermogensbeheer voor klanten wereldwijd.'],
 ['ZURN.SW','Zurich Insurance','Financiële diensten',612.4,'Schade- en levensverzekeringen voor particulieren en bedrijven wereldwijd.'],
 ['CBK.DE','Commerzbank','Financiële diensten',34.1,'Duitse bank voor middelgrote bedrijven en particulieren, ook actief in Polen.'],
 ['ASML.AS','ASML','Informatietechnologie',742.3,'Lithografiemachines waarmee chipmakers patronen op siliciumschijven belichten.'],
 ['SAP.DE','SAP','Informatietechnologie',248.1,'Bedrijfssoftware voor boekhouding, inkoop, personeel en logistiek, ook in de cloud.'],
 ['IFX.DE','Infineon','Informatietechnologie',38.6,'Halfgeleiders voor auto\'s, stroomvoorziening en industriële toepassingen.'],
 ['ROG.SW','Roche','Gezondheidszorg',289.5,'Geneesmiddelen, vooral tegen kanker, en diagnostische tests voor laboratoria.'],
 ['AZN.L','AstraZeneca','Gezondheidszorg',131.2,'Geneesmiddelen tegen kanker en voor hart, longen, nieren en zeldzame ziekten.'],
 ['NOVN.SW','Novartis','Gezondheidszorg',104.8,'Geneesmiddelen op voorschrift voor hart, kanker, immuunziekten en het zenuwstelsel.'],
 ['IBE.MC','Iberdrola','Nutsbedrijven',17.4,'Stroom uit wind, water en zon, en elektriciteitsnetten in Europa en Amerika.'],
 ['ENEL.MI','Enel','Nutsbedrijven',8.31,'Opwekking en levering van stroom en gas, en elektriciteitsnetten in Italië en Spanje.'],
 ['SHEL.L','Shell','Energie',31.9,'Olie- en gaswinning, vloeibaar aardgas, raffinage en tankstations wereldwijd.'],
 ['TTE.PA','TotalEnergies','Energie',55.2,'Winning, raffinage en levering van olie, gas en stroom, en tankstations wereldwijd.'],
 ['NESN.SW','Nestlé','Basisconsumptiegoederen',84.7,'Voeding en dranken, waaronder koffie, dierenvoeding, zuivel en babyvoeding.'],
 ['ULVR.L','Unilever','Basisconsumptiegoederen',53.6,'Verzorgingsproducten, schoonmaakmiddelen en voeding voor huishoudens wereldwijd.'],
 ['MC.PA','LVMH','Duurzame consumptiegoederen',612.0,'Mode, lederwaren, wijn en sterke drank, parfum, horloges en juwelen.'],
 ['DTE.DE','Deutsche Telekom','Communicatiediensten',31.4,'Mobiele en vaste telefonie en internet in Duitsland, Europa en de Verenigde Staten.']
];
const sectorN = {}; namen.forEach(n => sectorN[n[2]] = (sectorN[n[2]] || 0) + 1);
const rangen = [...Array(30).keys()].map(i => i + 1 + Math.floor(rnd() * 3 * (i / 29)));
const deel = K / 30;
let beurstaksTot = 0, spreadTot = 0, cash = K, omzetTot = 0;
const grootboek = [], posities = [];
namen.forEach(([ticker, naam, sector, koersIn, beschrijving], i) => {
  const aantal = Math.floor(deel / (koersIn * (1 + TAKS + SPREAD)));
  const bedrag = r2(aantal * koersIn), taks = r2(bedrag * TAKS), spr = r2(bedrag * SPREAD);
  cash -= bedrag + taks + spr; beurstaksTot += taks; spreadTot += spr; omzetTot += bedrag;
  grootboek.push({ datum: START, ticker, kant: 'KOOP', aantal, koers: koersIn, bedrag, beurstaks: taks, spread: spr,
    reden: `rang ${rangen[i]} · plaats vrij` });
  // 400 slotkoersen met trend omhoog, de voorlaatste = koersIn
  const drift = 0.0009 + rnd() * 0.0012, vol = 0.012 + rnd() * 0.01;
  const log = [0]; for (let d = 1; d < 399; d++) log.push(log[d - 1] + drift + vol * gauss());
  const schaalf = koersIn / Math.exp(log[398]);
  const hist = log.map(l => r2(Math.exp(l) * schaalf));
  const dagVerandering = (rnd() - 0.48) * 0.035;
  const koers = r2(koersIn * (1 + dagVerandering)); hist.push(koers);
  const sma = []; for (let d = 199; d < 400; d++) sma.push(r2(hist.slice(d - 199, d + 1).reduce((a, b) => a + b, 0) / 200));
  const reeks = hist.slice(200), smaReeks = sma.slice(1);
  const sma200 = smaReeks[199];
  // koers_vs_sma200 met vijf decimalen; afstand_sma200 (omgekeerd teken) schrijft de Mac nog, de app gebruikt het nooit
  posities.push({ ticker, naam, beschrijving, sector, sector_n: sectorN[sector], sector_max: 8, aantal, koers,
    dagkoers_verandering: r4(koers / koersIn - 1), instap: START, koers_in: koersIn,
    rendement: r4(koers / koersIn - 1), winst_eur: r2(aantal * (koers - koersIn)), dividend_eur: 0, gewicht: 0, gewicht_bij_aankoop: 0,
    sma200, koers_vs_sma200: r5(koers / sma200 - 1), afstand_sma200: r4((sma200 - koers) / koers), rang: rangen[i], score: Math.round(99 - rangen[i] * 0.9 - rnd() * 2),
    in_top60: true, dagen: 2, reeks, sma_reeks: smaReeks, _waardeIn: aantal * koersIn });
});
// een dividend met bruto en inhouding, geboekt op de ex-datum; het netto staat in de cash, niet in het rendement
const DIV = { ticker: 'SHEL.L', bruto: 17.71, inhouding: 5.31 };
const netto = r2(DIV.bruto - DIV.inhouding);
grootboek.push({ datum: MIDDEN, ticker: DIV.ticker, kant: 'DIVIDEND', bedrag: netto, bruto: DIV.bruto, inhouding: DIV.inhouding, reden: 'interimdividend' });
posities.find(x => x.ticker === DIV.ticker).dividend_eur = netto;
cash = r2(cash + netto);
const waardeIn = posities.reduce((a, p) => a + p._waardeIn, 0) + cash;
const waarde = posities.reduce((a, p) => a + p.aantal * p.koers, 0) + cash;
posities.forEach(p => { p.gewicht = r4(p.aantal * p.koers / waarde); p.gewicht_bij_aankoop = r4(p._waardeIn / waardeIn); delete p._waardeIn; });
// tracker: houdt zijn breukdelen, nooit afgekapt op hele stukken
const exIn = 55.84, exNu = 55.62, exAantal = r4(K / (exIn * 1.0022));
const exBedrag = r2(exAantal * exIn), exTaks = r2(exBedrag * 0.0012), exSpr = r2(exBedrag * 0.001);
grootboek.push({ datum: START, ticker: 'EXSA.DE', kant: 'TRACKER', aantal: exAantal, koers: exIn, bedrag: exBedrag,
  beurstaks: exTaks, spread: exSpr, reden: 'Baseline · startpositie' });
const exCash = K - exBedrag - exTaks - exSpr;
const trackerIn = r2(exAantal * exIn + exCash), trackerNu = r2(exAantal * exNu + exCash);
const p = r2(waarde), pIn = r2(waardeIn);
const verschil = ((p - trackerNu) / K * 100);
// gedeelde kalender: 200 werkdagen tot en met do 24 sept 2026
const handelsdagen = []; for (let d = new Date(Date.UTC(2026, 8, 24)); handelsdagen.length < 200; d.setUTCDate(d.getUTCDate() - 1)) {
  if (d.getUTCDay() % 6 !== 0) handelsdagen.unshift(d.toISOString().slice(0, 10)); }
const monitor = {
  hartslag: { tijd: `${STAND}T18:21:04+02:00`, status: 'ok', namen: 593, laatste_dag: STAND, run: 'dagadvies en vooruit bijgewerkt' },
  stand: { datum: STAND,
    zin: `Tenor staat ${Math.abs(verschil).toFixed(1).replace('.', ',')} punt ${verschil >= 0 ? 'boven' : 'onder'} Baseline. Kopen mag; de zaal is rustig.`,
    portefeuille: p, tracker: trackerNu,
    sinds_start: [[START, pIn, trackerIn], [MIDDEN, r2((pIn + p) / 2), r2((trackerIn + trackerNu) / 2)], [STAND, p, trackerNu]],
    start: { kapitaal: K, datum: START } },
  beslisregel: { startdatum: START, oordeeldatum: '2027-09-22', marge_pp: 3, dag: 3, van: 252, oordeel: 'loopt' },
  marktfilter: { aan: true, afstand: 0.083, maanden_onder: 0, bevestiging: 2, laatste_maandeinde: '2026-08-31',
    tekst: 'De markt sloot 8,3% boven haar 10-maandsgemiddelde; kopen mag.' },
  posities,
  vandaag: { datum: STAND, zin: 'Geen verkoop, geen aankoop; alle dertig plaatsen zijn bezet.',
    verkopen: [], kopen: [], afromingen: [], open_plaatsen: 0, cash },
  grootboek,
  kosten: { beurstaks: r2(beurstaksTot + exTaks), spread: r2(spreadTot + exSpr), omzet: r2(omzetTot / pIn) },
  handelsdagen,
  rangorde_datum: '2026-08-31'
};
require('fs').writeFileSync(require('path').join(__dirname, '..', 'test', 'fixtures', 'voorbeeld.json'), JSON.stringify(monitor, null, 1));
console.log(monitor.stand, monitor.kosten, 'cash', cash, 'verschil pt', verschil.toFixed(2),
  'max gewicht', Math.max(...posities.map(x => x.gewicht)), 'min', Math.min(...posities.map(x => x.gewicht)),
  'koers_vs_sma200', posities.slice(0,4).map(x=>x.koers_vs_sma200), 'tracker', exAantal);
const lang = namen.filter(n => n[4].length > 90 || /\d/.test(n[4]));
if (lang.length) throw new Error('beschrijving te lang of met cijfer: ' + lang.map(n => n[0]).join(', '));
