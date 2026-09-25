const { Model: m, test, gelijk, S } = require('./omgeving');

// 5.2 en 9: sorteren op Portefeuille, de grenslijn en de rij CASH
const posities = [
  { ticker: 'SAP.DE', gewicht: 0.035, rendement: 0.028, rang: 40, in_top60: true },
  { ticker: 'ENR.DE', gewicht: 0.145, rendement: 9.536, rang: 4, in_top60: true },
  { ticker: 'ASML.AS', gewicht: 0.035, rendement: -0.006, rang: 12, in_top60: true },
  { ticker: 'RHM.DE', gewicht: 0.0082, rendement: -0.412, rang: 77, in_top60: false },
  { ticker: 'ABBN.SW', gewicht: 0.02, rendement: 0.028, rang: 12, in_top60: true }
];
const volgorde = (s, lijst = posities) => m.portefeuilleLijst(lijst, s).map(p => p.ticker);

test('GEWICHT: hoogste gewicht eerst', () =>
  gelijk(volgorde('gewicht'), ['ENR.DE', 'ASML.AS', 'SAP.DE', 'ABBN.SW', 'RHM.DE']));
test('SINDS INSTAP: hoogste rendement eerst', () =>
  gelijk(volgorde('instap'), ['ENR.DE', 'ABBN.SW', 'SAP.DE', 'ASML.AS', 'RHM.DE']));
test('RANG: rang 1 eerst', () =>
  gelijk(volgorde('rang'), ['ENR.DE', 'ABBN.SW', 'ASML.AS', 'SAP.DE', 'RHM.DE']));
test('gelijke waarden volgen de ticker, alfabetisch, in elke sortering', () => {
  gelijk(volgorde('gewicht').slice(1, 3), ['ASML.AS', 'SAP.DE']);   // beide 3,5%
  gelijk(volgorde('instap').slice(1, 3), ['ABBN.SW', 'SAP.DE']);    // beide +2,8%
  gelijk(volgorde('rang').slice(1, 3), ['ABBN.SW', 'ASML.AS']);     // beide rang 12
});
test('een positie zonder waarde staat onderaan, ook op ticker', () => {
  const lijst = [{ ticker: 'ZZ', rang: 3 }, { ticker: 'BB' }, { ticker: 'AA' }, { ticker: 'CC', rang: 1 }];
  gelijk(volgorde('rang', lijst), ['CC', 'ZZ', 'AA', 'BB']);
  gelijk(volgorde('gewicht', lijst), ['AA', 'BB', 'CC', 'ZZ']);
});
test('een label verdwijnt als het veld bij alle posities ontbreekt', () => {
  gelijk(m.sorteringen(posities), ['gewicht', 'instap', 'rang']);
  gelijk(m.sorteringen(posities.map(({ rang, ...p }) => p)), ['gewicht', 'instap']);
  gelijk(m.sorteringen([{ ticker: 'A', rang: 1 }]), ['rang']);
  gelijk([m.sorteerLabel('gewicht'), m.sorteerLabel('instap'), m.sorteerLabel('rang')], ['Gewicht', 'Sinds instap', 'Rang']);
});
test('bewaarde sortering: standaard GEWICHT, en terug naar de standaard als het label verdween', () => {
  gelijk(m.actieveSortering(undefined, posities), 'gewicht');
  gelijk(m.actieveSortering('rang', posities), 'rang');
  gelijk(m.actieveSortering('rang', posities.map(({ rang, ...p }) => p)), 'gewicht');
  gelijk(m.actieveSortering('gewicht', [{ ticker: 'A', rang: 1 }]), 'rang');
});
test('CASH is in elke sortering de laatste rij, ook bij € 0', () => {
  for (const s of ['gewicht', 'instap', 'rang']) {
    const rijen = m.portefeuilleRijen({ posities, vandaag: { cash: 0, open_plaatsen: 0 } }, s);
    gelijk(rijen[rijen.length - 1], { soort: 'cash', label: 'CASH', bedrag: 0 }, s);
    gelijk(rijen.filter(r => r.soort === 'cash').length, 1, s);
  }
});
test('grenslijn bij RANG tussen de laatste binnen en de eerste buiten de top-60', () => {
  const rijen = m.portefeuilleRijen({ posities, vandaag: { cash: 10290 } }, 'rang');
  gelijk(rijen.map(r => r.soort === 'positie' ? r.positie.ticker : r.soort),
    ['ENR.DE', 'ABBN.SW', 'ASML.AS', 'SAP.DE', 'grens', 'RHM.DE', 'cash']);
  gelijk(m.TOP60_BUITEN.toUpperCase(), 'BUITEN DE TOP-60 · SMA200 BESLIST');
});
test('grenslijn alleen als er een positie met in_top60: false is, en alleen bij RANG', () => {
  const binnen = posities.map(p => ({ ...p, in_top60: true }));
  gelijk(m.portefeuilleRijen({ posities: binnen }, 'rang').some(r => r.soort === 'grens'), false);
  gelijk(m.portefeuilleRijen({ posities }, 'gewicht').some(r => r.soort === 'grens'), false);
  gelijk(m.portefeuilleRijen({ posities }, 'instap').some(r => r.soort === 'grens'), false);
  gelijk(m.grensIndex(m.portefeuilleLijst(posities, 'rang'), 'rang'), 4);
});
test('de rij CASH: zonder open plaatsen, met één en met drie', () => {
  gelijk(m.cashLabel(0), 'CASH');
  gelijk(m.cashLabel(undefined), 'CASH');
  gelijk(m.cashLabel(1), 'CASH · 1 PLAATS OPEN');
  gelijk(m.cashLabel(3), 'CASH · 3 PLAATSEN OPEN');
});
test('aria-label bij RANG met de rang erbij', () => {
  const relx = { ticker: 'REL.L', naam: 'RELX', rang: 40, rendement: 0.028, gewicht: 0.035 };
  gelijk(m.positieLabel(relx, { rang: true }), 'RELX, rang 40, +2,8% sinds instap, gewicht 3,5%');
  gelijk(m.positieLabel(relx), 'RELX, +2,8% sinds instap, gewicht 3,5%');
});
test('cashbedrag in de rij: hele euro met harde spatie', () => gelijk(m.euro(10290), `€${S}10.290`));
