const { Model: m, test, gelijk } = require('./omgeving');
const bijna = (a, b) => gelijk(Math.abs(a - b) < 1e-9, true, `${a} ≠ ${b}`);
const stand = { portefeuille: 101240, tracker: 100610, start: { kapitaal: 100000 } };

test('verschil in procentpunten na kosten', () => {
  const v = m.standVerschil(stand);
  bijna(v.tenor, 0.0124); bijna(v.baseline, 0.0061); bijna(v.verschil, 0.0063);
  gelijk(m.pt(v.verschil), '0,6');
});
test('verschil ontbreekt zonder startkapitaal', () => gelijk(m.standVerschil({ portefeuille: 1, tracker: 1 }), null));
test('balken: 0,3 pt verschil is zichtbaar (langste 58%, kortste 58% × (1 − 0,15 × pt))', () => {
  const b = m.standBalken({ portefeuille: 100300, tracker: 100000, start: { kapitaal: 100000 } });
  bijna(b.tenor, 0.58); bijna(b.baseline, 0.58 * (1 - 0.15 * 0.3));
});
test('balken: kortste nooit onder 29%, bereikt rond 3,3 pt', () => {
  const b = m.standBalken({ portefeuille: 96000, tracker: 100000, start: { kapitaal: 100000 } });
  bijna(b.baseline, 0.58); bijna(b.tenor, 0.29);
  bijna(m.standBalken({ portefeuille: 103333.4, tracker: 100000, start: { kapitaal: 100000 } }).baseline, 0.29);
});
test('balken: gelijke stand geeft twee even lange balken', () => {
  const b = m.standBalken({ portefeuille: 100000, tracker: 100000, start: { kapitaal: 100000 } });
  gelijk([b.tenor, b.baseline], [0.58, 0.58]);
  gelijk(m.standBalken({ portefeuille: 1, tracker: 1 }), null);
});
test('gewichtstags: afroombaar boven 8%, restje onder 1%', () => {
  gelijk(m.gewichtTag(0.0801), 'AFROOMBAAR'); gelijk(m.gewichtTag(0.08), null);
  gelijk(m.gewichtTag(0.0099), 'RESTJE'); gelijk(m.gewichtTag(0.033), null);
});
test('portefeuille gesorteerd op gewicht, zonder gewicht achteraan', () => {
  const l = m.portefeuilleLijst([{ ticker: 'A', gewicht: 0.02 }, { ticker: 'B' }, { ticker: 'C', gewicht: 0.145 }]);
  gelijk(l.map(p => p.ticker), ['C', 'A', 'B']);
});
test('voortgang beslisregel', () => { bijna(m.voortgang({ dag: 63, van: 252 }), 0.25); gelijk(m.voortgang({ dag: 3 }), null); });
test('grootboek per dag, nieuwste eerst, filter op naam', () => {
  const rijen = [{ datum: '2026-09-09', ticker: 'A' }, { datum: '2026-09-10', ticker: 'B' }, { datum: '2026-09-10', ticker: 'A' }];
  gelijk(m.grootboekPerDag(rijen).map(g => [g.datum, g.rijen.length]), [['2026-09-10', 2], ['2026-09-09', 1]]);
  gelijk(m.grootboekPerDag(rijen, 'B').length, 1);
});
test('transacties per naam: soorten en lijst', () => {
  const t = m.transactiesVoorNaam([
    { datum: '2026-10-02', ticker: 'ENR.DE', kant: 'AFROMING', aantal: 12 },
    { datum: '2026-09-09', ticker: 'ENR.DE', kant: 'KOOP', aantal: 31 },
    { datum: '2026-09-09', ticker: 'SAP.DE', kant: 'KOOP', aantal: 13 }], 'ENR.DE');
  gelijk(t.soorten, 'koop · afroming'); gelijk(t.lijst, '09-09 · 31\u00a0st, 02-10 · 12\u00a0st');
});
test('raster: drie ronde lijnen die de reeks omvatten', () => {
  const r = m.raster([99567.22, 99665.8, 99387.67, 99780.59]);
  gelijk(r.lijnen.length, 3);
  gelijk(r.min <= 99387.67 && r.max >= 99780.59, true);
  gelijk(r.lijnen.every(v => Number.isInteger(v / r.stap * 1) || Math.abs(v / r.stap - Math.round(v / r.stap)) < 1e-6), true);
});
test('raster: vlakke reeks geeft toch drie lijnen', () => gelijk(m.raster([50, 50]).lijnen.length, 3));
test('pad slaat ontbrekende waarden over', () => {
  const r = m.raster([1, 3]); const s = m.schaal(3, r, { breedte: 350, hoogte: 140 });
  const d = m.pad([1, null, 3], s);
  gelijk((d.match(/M/g) || []).length, 2);
});
test('schaal: tik op x vindt de dichtste dag', () => {
  const s = m.schaal(200, { min: 0, max: 1 }, { breedte: 350, hoogte: 150 });
  gelijk(s.index(0), 0); gelijk(s.index(350), 199); gelijk(s.index(175), 100);
});
test('rendement op Detail: één decimaal onder 10%, kleur volgt het afgeronde getal', () => {
  gelijk(m.rendementWeergave(-0.0063, { detail: true }), { tekst: '\u22120,6%', positief: false });
  gelijk(m.rendementWeergave(0.004, { detail: true }), { tekst: '+0,4%', positief: true });
  gelijk(m.rendementWeergave(0.0004, { detail: true }), { tekst: '0,0%', positief: false });
  gelijk(m.rendementWeergave(0.0996, { detail: true }).tekst, '+10%');
  gelijk(m.rendementWeergave(9.536, { detail: true }).tekst, '+954%');
});
test('rendement in rijen: altijd één decimaal', () => {
  gelijk(m.rendementWeergave(9.536).tekst, '+953,6%');
  gelijk(m.rendementWeergave(-0.00004), { tekst: '0,0%', positief: false });
});
test('aria-label van een portefeuillerij: naam, rendement en gewicht', () =>
  gelijk(m.positieLabel({ ticker: 'ENR.DE', naam: 'Siemens Energy', rendement: 9.536, gewicht: 0.145 }),
    'Siemens Energy, +953,6% sinds instap, gewicht 14,5%'));
test('Rest op Vandaag: getal zonder teken als de markt eronder staat', () => {
  gelijk(m.maandslotTekst(-0.021), 'maandslot 2,1% onder het 10-maandsgemiddelde');
  gelijk(m.maandslotTekst(0.083), 'maandslot +8,3% boven het 10-maandsgemiddelde');
});
test('detail blijft alleen staan zolang de naam in de posities staat', () => {
  gelijk(m.detailGeldig({ ticker: 'RHM.DE' }, [{ ticker: 'RHM.DE' }]), true);
  gelijk(m.detailGeldig({ ticker: 'RHM.DE' }, [{ ticker: 'SAP.DE' }]), false);
  gelijk(m.detailGeldig(null, []), false);
});
test('DIVIDEND als kant in grootboek en transactielijst', () => {
  const r = m.leesMonitor({ grootboek: [{ datum: '2026-09-15', ticker: 'SAP.DE', kant: 'DIVIDEND', bedrag: 31.5 }] });
  gelijk(r.data.grootboek[0].kant, 'DIVIDEND');
  gelijk(m.transactiesVoorNaam([{ datum: '2026-09-09', ticker: 'SAP.DE', kant: 'KOOP', aantal: 13 }, ...r.data.grootboek], 'SAP.DE').soorten, 'koop · dividend');
});
