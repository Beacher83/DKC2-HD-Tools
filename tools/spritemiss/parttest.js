const fs = require('fs');
const SP = 'C:/Users/beach/AppData/Local/Temp/claude/C--DEV-Claude-Mesen2-SNES-HD-Projekt/b6deec50-769e-4ba7-84a5-e8bfa5d8240b/scratchpad/';
eval(fs.readFileSync(SP + 'partcut.js', 'utf8'));

// OAM-Datei in die Struktur bringen, die der Viewer intern hat
const frames = [];
let cur = null;
for (const line of fs.readFileSync('C:/Users/beach/Downloads/snes_hd_oam.txt', 'latin1').split('\n')) {
  const l = line.trimEnd();
  let m = l.match(/^OAMF G(-?\d+) S([0-9A-F]{16}) F(\d+) M(\d+) N(\d+)$/);
  if (m) { cur = { gfx: +m[1], frame: +m[3], ents: [] }; frames.push(cur); continue; }
  m = l.match(/^OAM I(\d+) X([+-]\d+) Y(\d+) W(\d+) H(\d+) T([0-9A-F]+) P(\d) R(\d) (.)(.) (.+)$/);
  if (!m || !cur) continue;
  cur.ents.push({ x: +m[2], y: +m[3], w: +m[4], h: +m[5], pal: +m[7], hashes: m[11].split(/\s+/) });
}
console.log(`${frames.length} OAM-Frames eingelesen`);
const groups = rtParticleAnimations(frames.filter(f => f.gfx === 32));
const shards = new Set(JSON.parse(fs.readFileSync(SP + 'shardhashes.json', 'utf8')));
const shardGroups = groups.filter(g => g.tiles.every(h => shards.has(h)));
const cyc = shardGroups.filter(g => g.kind === 'cycle').map(g => g.tiles.length).sort((a,b)=>b-a);
const chn = shardGroups.filter(g => g.kind === 'chain').map(g => g.tiles.length).sort((a,b)=>b-a);
const sng = shardGroups.filter(g => g.kind === 'single').length;
const covered = new Set(shardGroups.filter(g=>g.kind!=='single').flatMap(g => g.tiles)).size;
console.log(`Splitter-Gruppen: ${cyc.length} Zyklen ${JSON.stringify(cyc)}, ${chn.length} Ketten ${JSON.stringify(chn)}, ${sng} Einzelbilder`);
console.log(`in Zyklen/Ketten eingeordnet: ${covered} von ${shards.size}`);
// Knochen-Zyklus
const bone = shardGroups.find(g => g.tiles.some(h => h.startsWith('938A')));
console.log(`\nKnochen: ${bone ? bone.kind + ', ' + bone.tiles.length + ' Bilder' : 'NICHT GEFUNDEN'}`);
if (bone) console.log('  ' + bone.tiles.map(h => h.slice(0,6)).join(' '));
// Python-Referenz mit derselben Eingabe UND derselben Definition: ref2.py
// (alle 8x8-Partikel im Gfxset 32, funktionaler Graph, Schwelle 0.45).
const PY = { cycles: [16,16,13,12,8,8], chains: [11,10,9,8,8,8,6,5,3,3,3], covered: 147 };
let ok = true;
const chk = (n, got, exp) => { const g = JSON.stringify(got) === JSON.stringify(exp); ok = ok && g;
  console.log(`${g?'OK    ':'FEHLER'} ${n.padEnd(34)} ${JSON.stringify(got)} (Python: ${JSON.stringify(exp)})`); };
chk('Zykluslaengen', cyc, PY.cycles);
chk('Kettenlaengen', chn, PY.chains);
chk('eingeordnete Kacheln', covered, PY.covered);
chk('Knochen ist ein 13er-Zyklus', bone ? [bone.kind, bone.tiles.length] : null, ['cycle', 13]);
console.log(ok ? '\nJS und Python stimmen ueberein.' : '\nABWEICHUNG zwischen JS und Python.');
process.exit(ok ? 0 : 1);
