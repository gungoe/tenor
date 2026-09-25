const { Model: m, test, gelijk, S } = require('./omgeving');

// 5.5 en 9: aantallen met breukdeel en de dividendrij
test('aantal: heel zonder komma', () => gelijk(m.aantal(69), '69'));
test('aantal: breukdeel met punt als duizendtal', () => gelijk(m.aantal(1565.7439), '1.565,7439'));
test('aantal: geen nullen achteraan', () => gelijk(m.aantal(12.5), '12,5'));
test('aantal: hoogstens vier decimalen, nooit afgekapt op hele stukken', () => {
  gelijk(m.aantal(0.12345), '0,1235');
  gelijk(m.aantal(1200), '1.200');
  gelijk(m.aantal(undefined), '');
});
test('stuks in Vandaag en in de transactielijst dragen het breukdeel', () => gelijk(m.stuks(1565.7439), `1.565,7439${S}st`));

test('grootboekrij met heel aantal: aantal × koers = bedrag, eronder de kosten', () =>
  gelijk(m.grootboekRegels({ kant: 'KOOP', aantal: 69, koers: 64.12, bedrag: 4424.28, beurstaks: 15.48, spread: 4.42 }),
    { boven: `69 × 64,12 = €${S}4.424`, onder: `kosten €${S}20`, breuk: false }));
test('grootboekrij met breukdeel: bedrag bovenaan, aantal × koers in de onderregel', () =>
  gelijk(m.grootboekRegels({ kant: 'TRACKER', aantal: 1565.7439, koers: 64.12, bedrag: 100395.49, beurstaks: 38.2, spread: 10 }),
    { boven: `€${S}100.395`, onder: `1.565,7439 × 64,12 · kosten €${S}48`, breuk: true }));

test('dividendrij met bruto en inhouding: netto bovenaan, eronder "ingehouden"', () => {
  const g = m.grootboekRegels({ kant: 'DIVIDEND', ticker: 'SHEL.L', bedrag: 12.4, bruto: 17.71, inhouding: 5.31 });
  gelijk(g, { boven: `€${S}12,40`, onder: `bruto €${S}17,71 · ingehouden €${S}5,31`, breuk: false });
  gelijk(g.onder.includes('ingehouden'), true);
});
test('dividendrij zonder bruto en inhouding: "netto · op ex-datum", zonder aantal × koers', () => {
  gelijk(m.grootboekRegels({ kant: 'DIVIDEND', ticker: 'SAP.DE', bedrag: 31.5 }), { boven: `€${S}31,50`, onder: 'netto · op ex-datum', breuk: false });
  gelijk(m.grootboekRegels({ kant: 'DIVIDEND', bedrag: 31.5, bruto: 45 }).onder, 'netto · op ex-datum');
});
test('bruto en inhouding worden gelezen; aantal behoudt zijn breukdeel', () => {
  const r = m.leesMonitor({ grootboek: [
    { datum: '2026-09-23', ticker: 'SHEL.L', kant: 'DIVIDEND', bedrag: 12.4, bruto: 17.71, inhouding: 5.31 },
    { datum: '2026-09-22', ticker: 'EXSA.DE', kant: 'TRACKER', aantal: 1565.7439, koers: 64.12, bedrag: 100395.49 }] });
  gelijk(r.data.grootboek[0].bruto, 17.71); gelijk(r.data.grootboek[0].inhouding, 5.31);
  gelijk(r.data.grootboek[1].aantal, 1565.7439);
});
