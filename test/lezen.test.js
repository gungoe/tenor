const { Model: m, test, gelijk, voorbeeld } = require('./omgeving');

test('voorbeeld (test/fixtures/voorbeeld.json) leest volledig in', () => {
  const r = m.leesMonitor(JSON.stringify(voorbeeld()));
  gelijk(r.ok, true);
  gelijk(r.data.posities.length, 30);
  gelijk(r.data.posities[0].reeks.length, 200);
  gelijk(r.data.posities[0].sma_reeks.length, 200);
  gelijk(r.data.handelsdagen.length, 200);
  gelijk(r.data.handelsdagen[199], '2026-09-10');
  gelijk(Object.keys(r.data).sort(), ['beslisregel', 'grootboek', 'handelsdagen', 'hartslag', 'kosten', 'marktfilter', 'posities', 'rangorde_datum', 'stand', 'vandaag']);
});
test('voorbeeld is intern consistent: gewichten tellen op tot ± 100% min cash', () => {
  const d = voorbeeld();
  const som = d.posities.reduce((a, p) => a + p.gewicht, 0) + d.vandaag.cash / d.stand.portefeuille;
  gelijk(Math.abs(som - 1) < 0.002, true, `som ${som}`);
});
test('ongeldige JSON geeft een Nederlandse fout', () => {
  const r = m.leesMonitor('{kapot');
  gelijk([r.ok, r.fout], [false, 'Het bestand monitor.json is geen geldige JSON.']);
});
test('ontbrekende onderdelen blijven weg, er wordt niets verzonnen', () => {
  const r = m.leesMonitor({ stand: { portefeuille: 101240 } });
  gelijk(r.data, { stand: { portefeuille: 101240 } });
  gelijk(m.standVerschil(r.data.stand), null);
  gelijk(m.rust(r.data), null);
});
test('velden van het verkeerde type vallen weg', () => {
  const r = m.leesMonitor({ hartslag: { tijd: 'gisteren', status: 'misschien', namen: '593' }, marktfilter: { aan: 'ja' } });
  gelijk(r.data.hartslag, {}); gelijk(r.data.marktfilter, {});
});
test('ontbrekende koerspunten blijven op hun plaats als leeg', () => {
  const r = m.leesMonitor({ posities: [{ ticker: 'X', reeks: [1, 'a', 3] }] });
  gelijk(r.data.posities[0].reeks, [1, null, 3]);
});
test('onbekende kant in het grootboek: rij blijft, tag valt weg', () => {
  const r = m.leesMonitor({ grootboek: [{ datum: '2026-09-10', ticker: 'X', kant: 'RUIL', bedrag: 10 }] });
  gelijk(r.data.grootboek, [{ datum: '2026-09-10', ticker: 'X', bedrag: 10 }]);
});
test('sinds_start: onvolledige punten vallen weg', () => {
  const r = m.leesMonitor({ stand: { sinds_start: [['2026-09-09', 1, 2], ['2026-09-10', 1]] } });
  gelijk(r.data.stand.sinds_start, [['2026-09-09', 1, 2]]);
});
test('handelsdagen: ongeldige datum blijft op zijn plaats als leeg', () => {
  const r = m.leesMonitor({ handelsdagen: ['2026-09-09', 'gisteren', '2026-09-11'], rangorde_datum: '31-08-2026' });
  gelijk(r.data.handelsdagen, ['2026-09-09', null, '2026-09-11']);
  gelijk(r.data.rangorde_datum, undefined);
});
test('dag van een koerspunt komt uit handelsdagen op dezelfde index', () => {
  const dagen = ['2026-09-08', '2026-09-09', '2026-09-10'];
  gelijk(m.dagVanPunt(dagen, 2, 3), '2026-09-10');
  gelijk(m.dagVanPunt(dagen, 0, 3), '2026-09-08');
  gelijk(m.dagVanPunt(undefined, 0, 3), null);
  gelijk(m.datum(m.dagVanPunt(dagen, 0, 3), 'wdm'), 'di 8 sep');
});
