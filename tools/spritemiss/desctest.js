// Prueft descriptorTileHashes aus index.html gegen das echte ROM und gegen die
// unabhaengige Python-Auswertung.
const fs = require('fs');
eval(fs.readFileSync('C:/Users/beach/AppData/Local/Temp/claude/C--DEV-Claude-Mesen2-SNES-HD-Projekt/b6deec50-769e-4ba7-84a5-e8bfa5d8240b/scratchpad/viewercut.js','utf8'));

// ROM-Stub mit derselben Schnittstelle wie der Viewer
let d = fs.readFileSync("C:/Users/beach/Downloads/Donkey Kong Country 2 - Diddy's Kong Quest.smc");
if (d.length % 1024 === 512) d = d.subarray(512);
let pos = 0;
const rom = {
  size: d.length,
  seek: (p) => { pos = p; },
  getPosition: () => pos,
  readByte: () => d[pos++],
  readBytes: (n) => { const b = d.subarray(pos, pos + n); pos += n; return b; },
  readByteAt: (p) => d[p],
  readWordAt: (p) => d[p] | (d[p+1] << 8),
};
const t0 = Date.now();
const set = descriptorTileHashes(rom);
console.log(`Dauer: ${Date.now()-t0} ms`);

// --- Gegenproben
// Unabhaengig in Python gerechnet: 75980 Hashes aus 3915 Deskriptoren, wenn man
// ALLE Kacheln der DMA-Bloecke zaehlt (was gfxRefTileHashes tut). Zaehlt man nur
// die Kacheln, die ein Deskriptor auch PLATZIERT, sind es 64953 -- die Differenz
// von 11027 sind Kacheln, die ein Block mitlaedt, ohne sie selbst zu setzen.
// Fuer den Filter geprueft: von den 3809 spritemiss-Hashes liegen 61 nur in der
// weiten Menge, und alle 61 sind ueber eine Tabellenanimation in der Galerie
// erreichbar -- die weite Definition blendet also nichts Unerreichbares aus.
const PY_EXPECTED = 75980;
const shards = JSON.parse(fs.readFileSync('C:/Users/beach/AppData/Local/Temp/claude/C--DEV-Claude-Mesen2-SNES-HD-Projekt/b6deec50-769e-4ba7-84a5-e8bfa5d8240b/scratchpad/shardhashes.json','utf8'));
const inDesc = shards.filter(h => set.has(h));
// Kacheln, die einen Deskriptor HABEN muessen
const withDesc = JSON.parse(fs.readFileSync('C:/Users/beach/AppData/Local/Temp/claude/C--DEV-Claude-Mesen2-SNES-HD-Projekt/b6deec50-769e-4ba7-84a5-e8bfa5d8240b/scratchpad/descexpected.json','utf8'));
let ok = true;
const check = (name, got, exp) => {
  const good = got === exp; ok = ok && good;
  console.log(`${good ? 'OK    ' : 'FEHLER'} ${name.padEnd(52)} ${got} (erwartet ${exp})`);
};
check('Gesamtzahl Deskriptor-Hashes (== Python)', set.size, PY_EXPECTED);
check('Splitter MIT Deskriptor (muss 0 sein)', inDesc.length, 0);
for (const [label, hs] of Object.entries(withDesc)) {
  check(`${label}: Kacheln im Deskriptor-Set`, hs.filter(h => set.has(h)).length, hs.length);
}
console.log(ok ? '\nAlle Gegenproben bestanden.' : '\nABWEICHUNG.');
process.exit(ok ? 0 : 1);
