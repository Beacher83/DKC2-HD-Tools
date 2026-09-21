// keeptest.js — prueft, dass ein gemerktes Objekt (★) die Inhaltsfilter ueberlebt.
//
// Der Fall, der das ausgeloest hat: der Kleever-Hook `G32-16x32-P4-C236`. Alle
// seine Kacheln stehen in der Deskriptortabelle, also hat ihn der Standardhaken
// "nur ohne Deskriptor" aus der Laufzeit-Ansicht geworfen -- und er fehlte in der
// Upscale-Runde mit den Splittern, obwohl der User ihn dort haben wollte.
//
// Geprueft wird beides: dass der Stern die Inhaltsfilter aushebelt UND dass er
// die ausdruecklichen Einschraenkungen (Gfxset, Palette, Suche, "nur gemerkte")
// NICHT aushebelt -- sonst waere der Stern ein Generalschluessel und die Filter
// waeren kaputt.
//
//   node keeptest.js
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'dkc2-viewer', 'index.html'), 'utf8');

// Die Filterkette aus rtFilteredObjects() schneiden: vom `return pool.filter(`
// bis zur schliessenden Klammer.
const start = src.indexOf('  return pool.filter(o => {');
if (start < 0) { console.error('Filterkette nicht gefunden'); process.exit(1); }
let depth = 0, end = -1;
for (let i = src.indexOf('{', start); i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
}
const body = src.slice(src.indexOf('{', start) + 1, end);

const checkboxes = {};
global.document = { getElementById: (id) => ({ checked: !!checkboxes[id] }) };

function makeFilter(env) {
  const { gfxSel, palSel, onlyDrawable, hideTiny, onlyAnimated, descSet, searchRaw, oamKeepList } = env;
  return new Function('o', 'gfxSel', 'palSel', 'onlyDrawable', 'hideTiny',
                      'onlyAnimated', 'descSet', 'searchRaw', 'oamKeepList', body)
    .bind(null);
}

const HOOK = {
  id: 'G32-16x32-P4-C236', gfx: 32, pals: [4], w: 16, h: 32,
  phaseCount: 1, drawablePhases: 0, particle: false,
  allTiles: ['C2368B86616E9F60_P4', 'A1B38551AA40D609_P4'],
};
const descSet = new Set(['C2368B86616E9F60', 'A1B38551AA40D609']);

function run(o, keep, opts) {
  const f = makeFilter({});
  return f(o, opts.gfxSel || 'all', opts.palSel || 'all',
           !!opts.onlyDrawable, !!opts.hideTiny, !!opts.onlyAnimated,
           opts.descSet === undefined ? descSet : opts.descSet,
           opts.searchRaw || '', keep);
}

let fails = 0;
function check(label, got, want) {
  const ok = got === want;
  console.log((ok ? '  OK   ' : '  FEHL ') + label + (ok ? '' : `   (erwartet ${want}, war ${got})`));
  if (!ok) fails++;
}

const none = new Set();
const starred = new Set([HOOK.id]);

console.log('Ohne Stern — die Inhaltsfilter greifen wie bisher');
check('Deskriptor-Filter wirft ihn weg', run(HOOK, none, {}), false);
check('"nur zeichenbare" wirft ihn weg', run(HOOK, none, { descSet: null, onlyDrawable: true }), false);
check('"nur animierte" wirft ihn weg', run(HOOK, none, { descSet: null, onlyAnimated: true }), false);

console.log('Mit Stern — er bleibt sichtbar');
check('trotz Deskriptor-Filter', run(HOOK, starred, {}), true);
check('trotz "nur zeichenbare"', run(HOOK, starred, { descSet: null, onlyDrawable: true }), true);
check('trotz "nur animierte"', run(HOOK, starred, { descSet: null, onlyAnimated: true }), true);
check('trotz aller drei zusammen',
      run(HOOK, starred, { onlyDrawable: true, onlyAnimated: true, hideTiny: true }), true);

console.log('Mit Stern — ausdrueckliche Einschraenkungen gelten WEITER');
check('anderes Gfxset blendet ihn aus', run(HOOK, starred, { gfxSel: '7' }), false);
check('andere Palette blendet ihn aus', run(HOOK, starred, { palSel: '2' }), false);
check('Suche nach Fremdem blendet ihn aus', run(HOOK, starred, { searchRaw: 'ZZZZ' }), false);
check('Suche nach seiner ID findet ihn', run(HOOK, starred, { searchRaw: 'C236' }), true);

console.log('Ein kleines 8x8-Objekt');
const tiny = { ...HOOK, id: 'G32-8x8-P4-BEEF', w: 8, h: 8, allTiles: ['DEADBEEFDEADBEEF_P4'] };
check('ohne Stern von "8x8 ausblenden" geworfen',
      run(tiny, none, { descSet: null, hideTiny: true }), false);
check('mit Stern sichtbar',
      run(tiny, new Set([tiny.id]), { descSet: null, hideTiny: true }), true);

console.log(fails ? `\n${fails} Pruefung(en) fehlgeschlagen` : '\nalle Pruefungen bestanden');
process.exit(fails ? 1 : 0);
