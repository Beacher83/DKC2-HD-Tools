// Testet die geaenderte Zeichenbarkeits-Regel gegen die ECHTE snes_hd_spritemiss.txt.
const fs = require('fs');
const MISS = 'C:/Users/beach/Downloads/snes_hd_spritemiss.txt';

// --- echte Daten laden: (hash,pal) -> Pixel vorhanden
const pixels = new Set();          // "HASH_Ppal"
const knownHashes = new Set();     // HASH unter irgendeiner Palette
const palsOf = new Map();
for (const line of fs.readFileSync(MISS, 'latin1').split('\n')) {
  const m = line.match(/^SPRMISS \w P(\d+) O\d+ G\d+ H([0-9A-F]{16})/);
  if (!m) continue;
  pixels.add(`${m[2]}_P${m[1]}`);
  knownHashes.add(m[2]);
  if (!palsOf.has(m[2])) palsOf.set(m[2], new Set());
  palsOf.get(m[2]).add(Number(m[1]));
}
console.log(`spritemiss: ${pixels.size} (hash,pal)-Schluessel, ${knownHashes.size} Hashes`);

const rtTilePixels = (key) => pixels.has(key) ? {} : null;
const sprMissKnowsHash = (h) => knownHashes.has(h);

// --- die ausgeschnittenen Funktionen
function sprTileIsHole(t) {
  return !rtTilePixels(`${t.hash}_P${t.pal}`) && sprMissKnowsHash(t.hash);
}
function rtTileHasPixels(t) {
  return !!rtTilePixels(`${t.hash}_P${t.pal}`);
}
const drawableALT = (ph) => !ph.some(sprTileIsHole);
const drawableNEU = (ph) => !ph.some(sprTileIsHole) && ph.some(rtTileHasPixels);

// --- ein echtes Loch suchen: Hash unter einer Palette bekannt, unter einer anderen nicht
let hole = null;
for (const [h, ps] of palsOf) {
  for (let p = 0; p < 8 && !hole; p++) if (!ps.has(p)) hole = { hash: h, pal: p };
  if (hole) break;
}

const T = (h, p) => ({ hash: h, pal: p });
const faelle = [
  ['Splitter-Phase (2 echte Splitterkacheln)',
   [T('A40CB4E29F51FFAA',3), T('63F930F0F87BC0B5',3)], true,  true ],
  ['leere Karte D0FB (Kunst liegt im Pack, spritemiss kennt sie nicht)',
   [T('D0FBA89265953A5B',1), T('D0FBF8F70DC2A0E4',3)], true,  false],
  ['leere Karte 55D2',
   [T('55D221FEA895C0A8',1), T('55D223AD722811F5',1)], true,  false],
  ['Bananenfall: eine unbekannte Kachel neben einer gezeichneten',
   [T('0C8210784D8AF5A5',0), T('A40CB4E29F51FFAA',3)], true,  true ],
  ['echtes Loch (Hash unter anderer Palette bekannt)',
   [hole, T('A40CB4E29F51FFAA',3)],                    false, false],
];
let ok = true;
console.log(`\n${'Fall'.padEnd(62)} ${'alt'.padEnd(6)} ${'neu'.padEnd(6)} Erwartung`);
for (const [name, ph, expAlt, expNeu] of faelle) {
  const a = drawableALT(ph), n = drawableNEU(ph);
  const good = a === expAlt && n === expNeu;
  ok = ok && good;
  console.log(`${(good?'OK   ':'FEHLER ')+name.padEnd(56)} ${String(a).padEnd(6)} ${String(n).padEnd(6)} alt=${expAlt} neu=${expNeu}`);
}
console.log(`\nLochbeispiel: ${hole.hash}_P${hole.pal} (bekannt unter P${[...palsOf.get(hole.hash)].join(',')})`);
console.log(ok ? '\nAlle Faelle wie erwartet.' : '\nMINDESTENS EIN FALL ABWEICHEND.');
process.exit(ok ? 0 : 1);
