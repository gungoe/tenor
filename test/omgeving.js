// Laadt het model-deel uit index.html in een afgeschermde context; tijdzone vast op Brussel.
process.env.TZ = 'Europe/Brussels';
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const begin = html.indexOf('/* ==== model ==== */'), einde = html.indexOf('/* ==== einde model ==== */');
if (begin < 0 || einde < 0) throw new Error('Model-deel niet gevonden in index.html');
const context = {};
vm.createContext(context);
vm.runInContext(html.slice(begin, einde) + '\nthis.Model = Model;', context);

const gevallen = [];
let suite = '';
const test = (naam, fn) => gevallen.push({ suite, naam, fn });
const suiteNaam = n => { suite = n; };
// objecten uit de vm-context hebben een ander prototype; vergelijk op inhoud
const inhoud = v => (v !== null && typeof v === 'object' ? JSON.parse(JSON.stringify(v)) : v);
const gelijk = (a, b, uitleg) => assert.deepStrictEqual(inhoud(a), inhoud(b), uitleg);
const voorbeeld = () => JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'voorbeeld.json'), 'utf8'));
const S = '\u00a0', M = '\u2212';

function draai() {
  let goed = 0;
  let vorige = null;
  for (const { suite: s, naam, fn } of gevallen) {
    if (s !== vorige) { console.log(`\n${s}`); vorige = s; }
    try { fn(); goed++; console.log('  ✓ ' + naam); }
    catch (e) { console.log('  ✗ ' + naam + '\n    ' + e.message.split('\n').join('\n    ')); }
  }
  console.log(`\n${goed} van ${gevallen.length} tests groen`);
  process.exitCode = goed === gevallen.length ? 0 : 1;
}

module.exports = { suiteNaam, Model: context.Model, test, gelijk, voorbeeld, draai, S, M };
