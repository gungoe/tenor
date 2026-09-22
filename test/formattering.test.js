const { Model: m, test, gelijk, S, M } = require('./omgeving');

test('euro: duizendtal met punt, harde spatie na €', () => gelijk(m.euro(101240), `€${S}101.240`));
test('euro: afronden op hele euro', () => gelijk(m.euro(356.49), `€${S}356`));
test('euro: koers met twee decimalen', () => gelijk(m.euro(78.6, 2), `€${S}78,60`));
test('euro: negatief met min-teken vóór het symbool', () => gelijk(m.euro(-1240), `${M}€${S}1.240`));
test('euro: miljoen', () => gelijk(m.euro(1234567), `€${S}1.234.567`));
test('euro: geen getal geeft lege tekst', () => gelijk(m.euro(undefined), ''));
test('pct: fractie naar procent met komma', () => gelijk(m.pct(0.012), '1,2%'));
test('pct: met teken bij winst', () => gelijk(m.pct(0.012, 1, true), '+1,2%'));
test('pct: min-teken bij verlies', () => gelijk(m.pct(-0.18, 0, true), `${M}18%`));
test('pct: nul krijgt geen teken', () => gelijk(m.pct(0.0001, 1, true), '0,0%'));
test('pct: +954% zonder decimalen', () => gelijk(m.pct(9.54, 0, true), '+954%'));
test('pt: procentpunten zonder eenheid', () => gelijk(m.pt(0.0063), '0,6'));
test('pt: negatief verschil', () => gelijk(m.pt(-0.031), `${M}3,1`));
test('pt: afgerond nul is geen −0,0', () => gelijk(m.pt(-0.0001), '0,0'));
test('datum kort', () => gelijk(m.datum('2026-09-10'), 'do 10 sep 2026'));
test('datum: daglabel in het grootboek', () => gelijk(m.datum('2026-09-10', 'lang'), 'DO 10 SEP'));
test('datum zonder weekdag', () => gelijk(m.datum('2027-09-09', 'dmj'), '9 sep 2027'));
test('datum op de x-as', () => gelijk(m.datum('2026-09-09', 'as'), '9 sep'));
test('datum in cijfers en dag-maand', () => {
  gelijk(m.datum('2024-01-31', 'cijfers'), '31-01-2024');
  gelijk(m.datum('2026-08-31', 'dagmaand'), '31-08');
});
test('ongeldige datum geeft lege tekst', () => gelijk(m.datum('2026-02-30'), ''));
test('tijd in lokale tijd', () => gelijk(m.tijd('2026-09-10T16:21:04Z'), '18:21'));
test('stuks en dagen', () => {
  gelijk(m.stuks(1200), `1.200${S}st`);
  gelijk(m.dagenTekst(1), '1 dag');
  gelijk(m.dagenTekst(947), '947 dagen');
});
test('maandafkortingen drie letters zonder punt, ook in datums', () => {
  gelijk(m.datum('2026-03-02', 'dm'), '2 mrt'); gelijk(m.datum('2026-09-09', 'dm'), m.datum('2026-09-09', 'as'));
});
test('hoofdletter voor getalwoorden', () => { gelijk(m.hoofdletter(m.inWoorden(1)), 'Eén'); gelijk(m.hoofdletter('drie'), 'Drie'); });
test('lege secties op Vandaag', () => {
  gelijk(m.legeZin('kopen', { rust: true, open_plaatsen: 3, cash: 10290 }), `Geen aankopen tijdens Rest. Drie plaatsen open, €${S}10.290 in cash.`);
  gelijk(m.legeZin('kopen', { open_plaatsen: 0 }), 'Geen aankopen; alle plaatsen zijn bezet.');
  gelijk(m.legeZin('kopen', { open_plaatsen: 1 }), 'Geen aankopen. Eén plaats open.');
  gelijk(m.legeZin('verkopen'), 'Geen verkopen.');
});
test('datum met weekdag zonder jaar, voor Cadence en de grafiek', () => gelijk(m.datum('2026-08-14', 'wdm'), 'vr 14 aug'));
