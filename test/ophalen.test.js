const { Model: m, test, gelijk } = require('./omgeving');

// uitkomst van het ophalen → volgend scherm, vanuit elke modus, met en zonder kopie
const MODI = ['laden', 'app', 'instellingen'];
function tabel(uitkomst, verwacht) {
  for (const modus of MODI) for (const kopie of [true, false]) {
    if (modus === 'app' && !kopie) continue;               // de app toont nooit iets zonder kopie
    if (modus === 'laden' && kopie) continue;              // het laadscherm bestaat alleen zonder kopie
    gelijk(m.volgendScherm(uitkomst, { modus, kopie }), verwacht(modus, kopie), `${uitkomst} vanuit ${modus}, ${kopie ? 'met' : 'zonder'} kopie`);
  }
}
// wat een fout doet die niets met instellingen te maken heeft: kopie blijft, zonder kopie het laadscherm
const zwijgend = soortRegel => (modus, kopie) => ({
  modus: modus === 'instellingen' ? 'instellingen' : (kopie ? 'app' : 'laden'),
  melding: null,
  regel: kopie ? soortRegel : null
});

test('200: naar de app; wie met een kopie in Instellingen zit blijft, zonder kopie opent de app vanzelf', () =>
  tabel('ok', (modus, kopie) => ({ modus: modus === 'instellingen' && kopie ? 'instellingen' : 'app', melding: null, regel: null })));
test('200 na een veld verlaten in Instellingen zonder kopie: Instellingen blijft, de terugpijl verschijnt', () => {
  gelijk(m.volgendScherm('ok', { modus: 'instellingen', kopie: false, zelf: true }), { modus: 'instellingen', melding: null, regel: null });
  gelijk(m.volgendScherm('ok', { modus: 'instellingen', kopie: false, zelf: false }).modus, 'app');
});
test('401/403: altijd Instellingen met het tokenalarm; de kopie is niet bijgewerkt', () => {
  gelijk([401, 403].map(m.ophaalSoort), ['token', 'token']);
  tabel('token', (modus, kopie) => ({ modus: 'instellingen', melding: 'token', regel: kopie ? 'niet-bijgewerkt' : null }));
});
test('404 zonder kopie: Instellingen met de regel onder het repoveld', () => {
  gelijk(m.ophaalSoort(404), 'niet-gevonden');
  gelijk(m.volgendScherm('niet-gevonden', { modus: 'laden', kopie: false }), { modus: 'instellingen', melding: 'niet-gevonden', regel: null });
  gelijk(m.volgendScherm('niet-gevonden', { modus: 'instellingen', kopie: false }), { modus: 'instellingen', melding: 'niet-gevonden', regel: null });
});
test('404 met kopie: zoals een 5xx, het scherm wisselt niet', () => {
  gelijk(m.volgendScherm('niet-gevonden', { modus: 'app', kopie: true }), { modus: 'app', melding: null, regel: 'niet-bijgewerkt' });
  gelijk(m.volgendScherm('niet-gevonden', { modus: 'app', kopie: true }), m.volgendScherm('fout', { modus: 'app', kopie: true }));
});
test('404 met kopie vanuit Instellingen: de regel onder het repoveld, zonder van scherm te wisselen', () =>
  gelijk(m.volgendScherm('niet-gevonden', { modus: 'instellingen', kopie: true }), { modus: 'instellingen', melding: 'niet-gevonden', regel: 'niet-bijgewerkt' }));
test('5xx en andere fouten: kopie blijft met "niet bijgewerkt", zonder kopie het laadscherm', () => {
  gelijk([500, 502, 503, 429, 418].map(m.ophaalSoort), ['fout', 'fout', 'fout', 'fout', 'fout']);
  tabel('fout', zwijgend('niet-bijgewerkt'));
});
test('netwerkfout: kopie blijft met "offline", zonder kopie het laadscherm', () => tabel('offline', zwijgend('offline')));
test('time-out: is een netwerkfout', () => tabel('time-out', zwijgend('offline')));
test('kapotte monitor.json: kopie blijft met "niet bijgewerkt", zonder kopie het laadscherm', () => tabel('kapot', zwijgend('niet-bijgewerkt')));
test('geweigerd token wordt niet opnieuw geprobeerd tot het verandert', () => {
  const ins = { repo: 'g/t', token: 'a' };
  gelijk(m.magOphalen(ins, { soort: 'token', token: 'a' }), false);
  gelijk(m.magOphalen({ ...ins, token: 'b' }, { soort: 'token', token: 'a' }), true);
  gelijk(m.magOphalen({ ...ins, repo: 'g/ander' }, { soort: 'token', token: 'a' }), false);
});
test('een 404 houdt het opnieuw proberen niet tegen', () =>
  gelijk(m.magOphalen({ repo: 'g/t', token: 'a' }, null), true));
test('zonder token of met een ongeldige repo wordt niet opgehaald', () => {
  gelijk(m.magOphalen({ repo: 'g/t', token: '' }, null), false);
  gelijk(m.magOphalen({ repo: 'alleen-een-naam', token: 'a' }, null), false);
});
