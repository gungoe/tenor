const { Model: m, test, gelijk } = require('./omgeving');
const nu = (s) => new Date(s);
const run = (tijd, status = 'ok') => ({ tijd, status, namen: 593, run: 'Yahoo gaf geen koersen' });

test('hartslag ok: run gisteravond', () => {
  const h = m.hartslag(run('2026-09-10T18:21:00+02:00'), nu('2026-09-11T09:00:00+02:00'));
  gelijk(h.soort, 'ok'); gelijk(m.cadenceLabel(h), 'CADENCE 18:21 · OK');
});
test('hartslag ok: vrijdag gedraaid, maandag bekeken (weekend telt niet)', () =>
  gelijk(m.hartslag(run('2026-09-11T18:21:00+02:00'), nu('2026-09-14T12:00:00+02:00')).soort, 'ok'));
test('hartslag oud: vrijdag gedraaid, woensdag bekeken', () => {
  const h = m.hartslag(run('2026-09-11T18:21:00+02:00'), nu('2026-09-16T12:00:00+02:00'));
  gelijk(h.soort, 'oud'); gelijk(h.dagen, 3);
  gelijk(m.cadenceLabel(h), 'CADENCE · 3 DAGEN OUD');
  gelijk(m.oudZin(h, '2026-09-11'), 'De laatste run is drie dagen oud. De cijfers hieronder zijn van vr 11 sep 2026.');
});
test('hartslag fout', () => {
  const h = m.hartslag(run('2026-09-10T18:21:00+02:00', 'fout'), nu('2026-09-11T09:00:00+02:00'));
  gelijk(m.cadenceLabel(h), 'CADENCE · FOUT'); gelijk(h.tekst, 'Yahoo gaf geen koersen');
});
test('hartslag fout houdt de tijd van de run bij', () =>
  gelijk(m.cadenceLabel(m.hartslag(run('2026-09-10T18:21:00+02:00', 'fout'), nu('2026-09-11T09:00:00+02:00'))), 'CADENCE · FOUT'));
test('hartslag zonder bruikbare tijd wordt weggelaten', () => gelijk(m.hartslag({ status: 'ok' }, new Date()), null));
test('Rest volgt marktfilter.aan', () => {
  gelijk(m.rust({ marktfilter: { aan: false } }), true);
  gelijk(m.rust({ marktfilter: { aan: true } }), false);
  gelijk(m.rust({}), null);
});
test('alarm: token gaat voor, dan fout, dan oud', () => {
  const monitor = { hartslag: run('2026-09-01T18:21:00+02:00') };
  const n = nu('2026-09-11T09:00:00+02:00');
  gelijk(m.toestanden({ monitor, nu: n }).alarm, 'oud');
  gelijk(m.toestanden({ monitor, nu: n, tokenOngeldig: true }).alarm, 'token');
  gelijk(m.toestanden({ monitor: { hartslag: run('2026-09-10T18:21:00+02:00', 'fout') }, nu: n }).alarm, 'fout');
});
test('offline wordt doorgegeven zonder alarm', () => {
  const t = m.toestanden({ monitor: { hartslag: run('2026-09-10T18:21:00+02:00') }, nu: nu('2026-09-11T09:00:00+02:00'), offline: true });
  gelijk([t.offline, t.alarm], [true, null]);
});
test('thema automatisch: avond van 19:00 tot 07:00', () => {
  gelijk(m.thema('automatisch', nu('2026-09-11T18:59:00+02:00')), 'dag');
  gelijk(m.thema('automatisch', nu('2026-09-11T19:00:00+02:00')), 'avond');
  gelijk(m.thema('automatisch', nu('2026-09-12T06:59:00+02:00')), 'avond');
  gelijk(m.thema('dag', nu('2026-09-11T23:00:00+02:00')), 'dag');
});
test('Cadence-onderregel: gisteren en volgende run', () => {
  const laatste = nu('2026-09-10T18:21:00+02:00');
  gelijk(m.relatieveDag(laatste, nu('2026-09-11T09:00:00+02:00')), 'gisteren');
  gelijk(m.volgendeRun(laatste, nu('2026-09-11T09:00:00+02:00')), 'vanavond');
  gelijk(m.volgendeRun(nu('2026-09-11T18:21:00+02:00'), nu('2026-09-11T20:00:00+02:00')), 'maandag');
  gelijk(m.volgendeRun(laatste, nu('2026-09-10T20:00:00+02:00')), 'morgenavond');
});
test('regel onder Cadence: offline bij netwerkfout, anders niet bijgewerkt', () => {
  gelijk(m.kopieRegel('offline', '2026-09-11T07:42:00+02:00', nu('2026-09-11T09:00:00+02:00')), 'offline · kopie van 07:42');
  gelijk(m.kopieRegel('niet-bijgewerkt', '2026-09-11T07:42:00+02:00', nu('2026-09-11T09:00:00+02:00')), 'niet bijgewerkt · kopie van 07:42');
  gelijk(m.kopieRegel('offline', '2026-09-10T18:30:00+02:00', nu('2026-09-11T09:00:00+02:00')), 'offline · kopie van do 10 sep 18:30');
});
test('ophalen: statuscodes naar toestand', () => {
  gelijk([200, 401, 403, 404, 500].map(m.ophaalSoort), ['ok', 'token', 'token', 'niet-gevonden', 'fout']);
});
test('monitorUrl uit eigenaar/repo, ook met plak-rommel', () => {
  gelijk(m.monitorUrl('gunther/tenor-data'), 'https://api.github.com/repos/gunther/tenor-data/contents/monitor.json');
  gelijk(m.monitorUrl(' https://github.com/gunther/tenor-data/ '), 'https://api.github.com/repos/gunther/tenor-data/contents/monitor.json');
  gelijk(m.monitorUrl('tenor-data'), null);
  gelijk(m.monitorUrl(''), null);
});
