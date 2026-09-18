const fs = require('fs');
const SP = 'C:/Users/beach/AppData/Local/Temp/claude/C--DEV-Claude-Mesen2-SNES-HD-Projekt/b6deec50-769e-4ba7-84a5-e8bfa5d8240b/scratchpad/';
eval(fs.readFileSync(SP + 'partcut.js', 'utf8'));
const frames = []; let cur = null;
for (const line of fs.readFileSync('C:/Users/beach/Downloads/snes_hd_oam.txt', 'latin1').split('\n')) {
  const l = line.trimEnd();
  let m = l.match(/^OAMF G(-?\d+) S([0-9A-F]{16}) F(\d+) M(\d+) N(\d+)$/);
  if (m) { cur = { gfx: +m[1], frame: +m[3], ents: [] }; frames.push(cur); continue; }
  m = l.match(/^OAM I(\d+) X([+-]\d+) Y(\d+) W(\d+) H(\d+) T([0-9A-F]+) P(\d) R(\d) (.)(.) (.+)$/);
  if (!m || !cur) continue;
  cur.ents.push({ x: +m[2], y: +m[3], pal: +m[7], hashes: m[11].split(/\s+/) });
}
const shards = new Set(JSON.parse(fs.readFileSync(SP + 'shardhashes.json', 'utf8')));
const sparks = new Set(JSON.parse(fs.readFileSync(SP + 'descexpected.json', 'utf8'))['Funken 0x022F']);
let all = [];
const byGfx = new Map();
for (const f of frames) { if (!byGfx.has(f.gfx)) byGfx.set(f.gfx, []); byGfx.get(f.gfx).push(f); }
for (const [g, fr] of byGfx) for (const grp of rtParticleAnimations(fr)) all.push({ ...grp, gfx: g });
const g32 = all.filter(g => g.gfx === 32);
const mixedPal = all.filter(g => new Set(g.pals).size > 1).length;
const mixedKind = g32.filter(g => g.tiles.some(h => shards.has(h)) && g.tiles.some(h => sparks.has(h))).length;
const shardGroups = g32.filter(g => g.tiles.every(h => shards.has(h)));
const cyc = shardGroups.filter(g => g.kind==='cycle').map(g=>g.tiles.length).sort((a,b)=>b-a);
const chn = shardGroups.filter(g => g.kind==='chain').map(g=>g.tiles.length).sort((a,b)=>b-a);
const bone = shardGroups.find(g => g.tiles.some(h => h.startsWith('938A')));
console.log(`Gruppen gesamt (alle Gfxsets): ${all.length}`);
console.log(`Splitter-Gruppen: ${cyc.length} Drehungen ${JSON.stringify(cyc)}, ${chn.length} Folgen ${JSON.stringify(chn)}`);
console.log(`Knochen: ${bone ? bone.kind + ' mit ' + bone.tiles.length + ' Bildern' : 'NICHT GEFUNDEN'}`);
let ok = true;
const chk = (n, got, exp) => { const g = JSON.stringify(got) === JSON.stringify(exp); ok = ok && g;
  console.log(`${g?'OK    ':'FEHLER'} ${n.padEnd(46)} ${JSON.stringify(got)} (erwartet ${JSON.stringify(exp)})`); };
chk('keine Gruppe mischt Paletten', mixedPal, 0);
chk('keine Gruppe mischt Splitter und Funken', mixedKind, 0);
chk('keine Einzelbild-Gruppen', all.filter(g => g.tiles.length < 3).length, 0);
chk('Knochen bleibt eine 13er-Drehung', bone ? [bone.kind, bone.tiles.length] : null, ['cycle', 13]);
console.log(ok ? '\nAlle Proben bestanden.' : '\nABWEICHUNG.');
process.exit(ok ? 0 : 1);
