const { Model: m, test, gelijk } = require('./omgeving');

// 5.3 en 9: de rustige dag op Vandaag
const dag = (vandaag, aan = true) => ({
  marktfilter: { aan },
  vandaag: { verkopen: [], kopen: [], afromingen: [], open_plaatsen: 0, ...vandaag }
});
const verkoop = [{ ticker: 'RHM.DE', aantal: 1, bedrag: 1007 }];

test('rustige dag: alle drie leeg, geen open plaats, kopen mag', () => gelijk(m.rustigeDag(dag({})), true));
test('rustige dag: open_plaatsen mag ontbreken', () => {
  const d = dag({}); delete d.vandaag.open_plaatsen;
  gelijk(m.rustigeDag(d), true);
});
test('geen rustige dag bij open plaatsen zonder aankoop', () => gelijk(m.rustigeDag(dag({ open_plaatsen: 3 })), false));
test('geen rustige dag tijdens Rest', () => gelijk(m.rustigeDag(dag({}, false)), false));
test('geen rustige dag zonder marktfilter: aan moet waar zijn', () => {
  const d = dag({}); delete d.marktfilter;
  gelijk(m.rustigeDag(d), false);
});
test('geen rustige dag zodra één sectie een rij heeft', () => {
  gelijk(m.rustigeDag(dag({ verkopen: verkoop })), false);
  gelijk(m.rustigeDag(dag({ kopen: verkoop })), false);
  gelijk(m.rustigeDag(dag({ afromingen: verkoop })), false);
});
