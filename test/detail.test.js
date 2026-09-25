const { Model: m, test, gelijk, fixture, S } = require('./omgeving');

// 5.6 en 9: de woorden bij de SMA-lijn, de instapstreep, de rijen Dividend en Rangorde
const r4 = x => Math.round(x * 1e4) / 1e4, r5 = x => Math.round(x * 1e5) / 1e5;
const ligging = (koers, sma200) => koers / sma200 - 1;

test('fixtures: het teken van koers_vs_sma200 klopt met koers en sma200 (koers boven ⇔ positief)', () => {
  for (const naam of ['voorbeeld', 'rest']) {
    const posities = fixture(naam).posities;
    gelijk(posities.every(p => typeof p.koers_vs_sma200 === 'number'), true, `${naam}: koers_vs_sma200 bij elke positie`);
    for (const p of posities) {
      gelijk(p.koers > p.sma200, p.koers_vs_sma200 > 0, `${naam} ${p.ticker}: koers ${p.koers}, sma200 ${p.sma200}, ${p.koers_vs_sma200}`);
      gelijk(p.koers_vs_sma200, r5(ligging(p.koers, p.sma200)), `${naam} ${p.ticker}: vijf decimalen`);
    }
  }
});
test('de ligging zelf: koers 29,37 en sma200 30,00 is −0,0210, koers 30,00 en sma200 29,37 is +0,02145', () => {
  gelijk(r4(ligging(29.37, 30)), -0.021);
  gelijk(r5(ligging(30, 29.37)), 0.02145);
  gelijk(r4(ligging(30, 29.37)), 0.0215);
});
test('koers 29,37 onder sma200 30,00 (−0,0210): KOERS 2,1% ONDER SMA200', () =>
  gelijk(m.smaLabel(-0.0210), 'KOERS 2,1% ONDER SMA200'));
test('koers 30,00 boven sma200 29,37: vier decimalen (+0,0215) geven 2,2%', () =>
  gelijk(m.smaLabel(0.0215), 'KOERS 2,2% BOVEN SMA200'));
test('koers 30,00 boven sma200 29,37: vijf decimalen (+0,02145) geven 2,1%', () =>
  gelijk(m.smaLabel(0.02145), 'KOERS 2,1% BOVEN SMA200'));
test('+0,004: KOERS 0,4% BOVEN SMA200', () => gelijk(m.smaLabel(0.004), 'KOERS 0,4% BOVEN SMA200'));
test('+0,1234: vanaf 10% geen decimaal, KOERS 12% BOVEN SMA200', () => gelijk(m.smaLabel(0.1234), 'KOERS 12% BOVEN SMA200'));
test('+0,0004 en −0,0004: KOERS GELIJK AAN SMA200', () => {
  gelijk(m.smaLabel(0.0004), 'KOERS GELIJK AAN SMA200');
  gelijk(m.smaLabel(-0.0004), 'KOERS GELIJK AAN SMA200');
});
test('alleen afstand_sma200, zonder koers_vs_sma200: geen label', () => {
  const p = m.leesMonitor({ posities: [{ ticker: 'REL.L', koers: 29.37, sma200: 30, afstand_sma200: 0.0215 }] }).data.posities[0];
  gelijk(p.afstand_sma200, 0.0215);                        // blijft in het schema: keur_monitor.js laat niets wegvallen
  gelijk(m.smaLabel(p.koers_vs_sma200), '');
});
test('afronding zoals in het bestand: 0,0215 wordt 2,2%, nooit 2,1% door de binaire benadering', () => {
  gelijk(m.pct(0.0215, 1), '2,2%');
  gelijk(m.pct(-0.0215, 1), '−2,2%');
  gelijk(m.pct(0.02145, 1), '2,1%');
  gelijk(m.pct(1.005, 0), '101%');
});

const dagen = [];
for (let d = new Date(Date.UTC(2026, 8, 24)); dagen.length < 200; d.setUTCDate(d.getUTCDate() - 1)) {
  if (d.getUTCDay() % 6 !== 0) dagen.unshift(d.toISOString().slice(0, 10));
}
test('instapstreep: binnen de 200 dagen op de index van de instapdag', () => {
  gelijk(m.instapIndex(dagen, '2026-09-22', 200), 197);
  gelijk(m.instapIndex(dagen, dagen[0], 200), 0);
  gelijk(m.instapIndex(dagen, dagen[120], 200), 120);
  gelijk(m.instapIndex(dagen, '2026-09-20', 200), 196);  // een zondag: de eerstvolgende handelsdag
});
test('instapstreep: buiten de 200 dagen geen streep', () => {
  gelijk(m.instapIndex(dagen, '2024-01-31', 200), null);
  gelijk(m.instapIndex(dagen, '2026-09-25', 200), null);
  gelijk(m.instapIndex(undefined, '2026-09-22', 200), null);
});
test('instapstreep: het label vervalt vlak bij "nu" en bij "200 dagen geleden", de streep blijft', () => {
  gelijk(m.instapLabelPast(344, 350), false);        // instap eergisteren: vlak bij "nu"
  gelijk(m.instapLabelPast(120, 350), false);        // vlak bij "200 dagen geleden"
  gelijk(m.instapLabelPast(220, 350), true);
  gelijk(m.instapLabelPast(276, 350), true);         // de grens ligt op 40 px van "nu"
  gelijk(m.instapLabelPast(279, 350), false);
});

test('rij Dividend alleen bij dividend_eur groter dan 0', () => {
  gelijk(m.toonDividend({ dividend_eur: 12.4 }), true);
  gelijk(m.toonDividend({ dividend_eur: 0 }), false);
  gelijk(m.toonDividend({}), false);
});
test('rij Dividend: sub met één en met meer uitkeringen sinds instap', () => {
  const rijen = [
    { datum: '2026-09-23', ticker: 'SHEL.L', kant: 'DIVIDEND', bedrag: 12.4 },
    { datum: '2026-10-14', ticker: 'SHEL.L', kant: 'DIVIDEND', bedrag: 12.1 },
    { datum: '2026-05-14', ticker: 'SHEL.L', kant: 'DIVIDEND', bedrag: 9 },   // vorige periode: telt niet mee
    { datum: '2026-10-14', ticker: 'SAP.DE', kant: 'DIVIDEND', bedrag: 31.5 }];
  gelijk(m.dividendRegel(rijen.slice(0, 1), 'SHEL.L', '2026-09-22'), 'netto · geboekt op ex-datum 23-09');
  gelijk(m.dividendRegel(rijen, 'SHEL.L', '2026-09-22'), 'netto · 2 keer, laatst op ex-datum 14-10');
  gelijk(m.dividendRegel([], 'SHEL.L', '2026-09-22'), 'netto');
  gelijk(m.euro(12.4, 2), `€${S}12,40`);
});
test('Sinds instap: winst of verlies in woorden, nooit "−€ … winst"', () => {
  gelijk(m.winstTekst(94), `€${S}94 winst`);
  gelijk(m.winstTekst(-1240), `€${S}1.240 verlies`);
  gelijk(m.winstTekst(-0.2), `€${S}0 winst`);
});
test('Rangorde: rang en score door de getalhelper, sub zoals de grenslijn', () => {
  gelijk(m.rangordeRechts({ rang: 40, score: 57 }), 'rang 40 · score 57');
  gelijk(m.rangordeRechts({ rang: 1204, score: 57.4 }), 'rang 1.204 · score 57');
  gelijk(m.rangordeSub({ in_top60: true }, '2026-08-31'), 'van 31-08 · blijft in de top-60');
  gelijk(m.rangordeSub({ in_top60: false }, '2026-08-31'), 'van 31-08 · buiten de top-60 · SMA200 beslist');
});
test('nieuwe velden van een positie worden gelezen: beschrijving, dividend_eur, koers_vs_sma200', () => {
  const p = m.leesMonitor({ posities: [{ ticker: 'REL.L', beschrijving: 'Data, analyses en software voor juristen, wetenschappers en verzekeraars.',
    dividend_eur: 0, koers_vs_sma200: -0.021, aantal: 12.5 }] }).data.posities[0];
  gelijk(p, { ticker: 'REL.L', beschrijving: 'Data, analyses en software voor juristen, wetenschappers en verzekeraars.',
    aantal: 12.5, dividend_eur: 0, koers_vs_sma200: -0.021 });
});
