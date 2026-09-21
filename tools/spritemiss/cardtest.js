// cardtest.js — prueft die HD-Deckungsanzeige der Laufzeit-Karte.
//
// Schneidet buildRuntimeCard per Klammerzaehlung aus index.html und laesst sie
// gegen einen DOM-Stub laufen. Geprueft werden die drei Faelle, die es seit dem
// 21.09. gibt: vollstaendig HD, TEILWEISE (neu) und gar nichts. Der mittlere ist
// der Grund fuer den Test -- er hat gefehlt, und deshalb sah der Kleever-Hook in
// der Galerie aus wie ein Objekt ohne jede HD-Kunst, obwohl 6 von 8 Kacheln da
// waren.
//
//   node cardtest.js
const fs = require('fs');
const path = require('path');

const HTML = path.join(__dirname, '..', '..', 'dkc2-viewer', 'index.html');
const src = fs.readFileSync(HTML, 'utf8');

function cut(name) {
  const start = src.indexOf('function ' + name + '(');
  if (start < 0) throw new Error('nicht gefunden: ' + name);
  let i = src.indexOf('{', start), depth = 0;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('Klammern unausgeglichen: ' + name);
}

// --- DOM-Stub: nur was die Karte anfasst ----------------------------------
const made = [];
function el() {
  const e = {
    style: { cssText: '', color: '' }, children: [], className: '', title: '',
    textContent: '', dataset: {}, checked: false, type: '',
    classList: { add() {}, remove() {}, contains() { return false; } },
    appendChild(c) { this.children.push(c); return c; },
    addEventListener() {},
    getContext() { return { drawImage() {}, clearRect() {}, fillRect() {}, putImageData() {}, createImageData: () => ({ data: [] }) }; },
  };
  made.push(e);
  return e;
}
global.document = { createElement: () => el(), querySelectorAll: () => [] };
global.window = {};

// Abhaengigkeiten, die die Karte aufruft, als harmlose Platzhalter.
const stubs = `
  var runtimeSelection = new Set(), runtimeStars = new Set();
  function rtCoveredKeys(){ return new Set(); }
  function updateRuntimeSelectionUI(){}
  function drawRuntimeObject(){ return null; }
  function rtObjectCanvas(){ return document.createElement('canvas'); }
  function toggleRuntimeStar(){}
  var hdRuntimeBitmaps = null, RT_ZOOM = 1;
  function rtWantHd(){ return false; }
  function rtHdBitmapFor(){ return null; }
  function sprTileIsHole(){ return false; }
  function rtPhaseCanvas(){ return document.createElement('canvas'); }
  function rtDrawPhase(){}
  var spriteMissByHash = null, hdPack = null, oamObjects = [];
  function renderRuntimeObject(){ return document.createElement('canvas'); }
  function renderRuntimeObjectHd(){ return { canvas: document.createElement('canvas'), hdCount: 0, total: 0 }; }
  var oamKeepList = new Set(), oamDropList = new Set();
  function saveOamKeepList(){}
`;

let fn;
try {
  fn = new Function(stubs + '\n' + cut('buildRuntimeCard') + '\nreturn buildRuntimeCard;')();
} catch (e) {
  console.error('Funktion laesst sich nicht laden:', e.message);
  process.exit(1);
}

function mk(n, covered) {
  const keys = [], cells = [];
  for (let i = 0; i < n; i++) {
    const hash = ('A' + i).padEnd(16, '0');
    keys.push(`${hash}_P3`);
    cells.push({ x: (i % 2) * 8, y: Math.floor(i / 2) * 8, hash, pal: 3 });
  }
  return {
    obj: {
      id: 'G32-16x16-P4-TEST', gfx: 32, w: 16, h: 16, cellCount: 1, pals: [4],
      seen: 100, phases: [cells], phaseCount: 1, tiles: cells,
      allTiles: keys, missing: 0, drawablePhases: 1,
    },
    done: new Set(keys.slice(0, covered)),
  };
}

let fails = 0;
function check(label, cond, extra) {
  console.log((cond ? '  OK   ' : '  FEHL ') + label + (cond ? '' : '   -> ' + extra));
  if (!cond) fails++;
}

console.log('Fall 1: alle 8 Kacheln als HD');
let { obj, done } = mk(8, 8);
let card = fn(obj, done);
let label = made[made.length - 1];
check('Tooltip meldet 8/8', /8\/8/.test(card.title), card.title);
check('Label zeigt ✓HD', /✓HD/.test(label.textContent), label.textContent);
check('Label gruen', label.style.color === '#4caf50', label.style.color);

console.log('Fall 2: 6 von 8 — der neue Fall');
made.length = 0;
({ obj, done } = mk(8, 6));
card = fn(obj, done);
label = made[made.length - 1];
check('Tooltip meldet 6 von 8', /nur 6 von 8/.test(card.title), card.title);
check('Tooltip nennt die fehlenden Hashes', /es fehlen: /.test(card.title), card.title);
check('Label zeigt ◐6/8 HD', /◐6\/8 HD/.test(label.textContent), label.textContent);
check('Label bernstein', label.style.color === '#ffb300', label.style.color);
check('kein ✓HD bei Teildeckung', !/✓HD/.test(label.textContent), label.textContent);

console.log('Fall 3: gar keine HD-Kunst');
made.length = 0;
({ obj, done } = mk(8, 0));
card = fn(obj, done);
label = made[made.length - 1];
check('Label ohne HD-Angabe', !/HD/.test(label.textContent), label.textContent);
check('Label neutral gefaerbt', label.style.color === '', label.style.color);
check('Tooltip ohne Teilmeldung', !/nur 0 von/.test(card.title), card.title);

console.log(fails ? `\n${fails} Pruefung(en) fehlgeschlagen` : '\nalle Pruefungen bestanden');
process.exit(fails ? 1 : 0);
