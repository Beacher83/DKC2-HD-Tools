const RT_TRACK_DIST = 14;    // SD-Pixel, die ein Partikel je Frame hoechstens macht
const RT_SUCC_MIN = 0.45;    // Anteil, ab dem ein Nachfolger als belegt gilt
function rtParticleAnimations(frames) {
  // 1) Partikel ueber die Frames verfolgen (Naechster-Nachbar mit Vorhersage).
  const tracks = [];
  let active = [];
  let prevF = null;
  for (const fr of frames) {
    if (prevF !== null && fr.frame - prevF > 3) { tracks.push(...active); active = []; }
    prevF = fr.frame;
    const ents = fr.ents.filter(e => e.hashes.length === 1);
    const pairs = [];
    active.forEach((t, ti) => ents.forEach((e, ei) => {
      const d = Math.abs(e.x - t.px) + Math.abs(e.y - t.py);
      if (d <= RT_TRACK_DIST) pairs.push([d, ti, ei]);
    }));
    pairs.sort((a, b) => a[0] - b[0]);
    const usedT = new Set(), usedE = new Set();
    for (const [, ti, ei] of pairs) {
      if (usedT.has(ti) || usedE.has(ei)) continue;
      usedT.add(ti); usedE.add(ei);
      const t = active[ti], e = ents[ei];
      const vx = e.x - t.x, vy = e.y - t.y;
      t.x = e.x; t.y = e.y; t.px = e.x + vx; t.py = e.y + vy; t.miss = 0;
      t.seq.push({ hash: e.hashes[0], pal: e.pal });
    }
    const keep = [];
    active.forEach((t, ti) => {
      if (usedT.has(ti)) { keep.push(t); return; }
      if (++t.miss <= 2) { t.px += t.px - t.x; t.py += t.py - t.y; keep.push(t); }
      else tracks.push(t);
    });
    active = keep;
    ents.forEach((e, ei) => {
      if (usedE.has(ei)) return;
      active.push({ x: e.x, y: e.y, px: e.x, py: e.y, miss: 0,
                    seq: [{ hash: e.hashes[0], pal: e.pal }] });
    });
  }
  tracks.push(...active);

  // 2) Nachfolger zaehlen, ueber Bahnen mit genug Sichtungen.
  const succ = new Map();
  const palOf = new Map();
  for (const t of tracks) {
    for (const s of t.seq) if (!palOf.has(s.hash)) palOf.set(s.hash, s.pal);
    if (t.seq.length < 6) continue;
    const u = [];
    for (const s of t.seq) if (!u.length || u[u.length - 1] !== s.hash) u.push(s.hash);
    for (let i = 0; i + 1 < u.length; i++) {
      if (!succ.has(u[i])) succ.set(u[i], new Map());
      const m = succ.get(u[i]);
      m.set(u[i + 1], (m.get(u[i + 1]) || 0) + 1);
    }
  }
  const next = new Map();
  for (const [a, m] of succ) {
    let best = null, n = 0, tot = 0;
    for (const [b, k] of m) { tot += k; if (k > n) { n = k; best = b; } }
    if (best && n >= 2 && n / tot >= RT_SUCC_MIN) next.set(a, best);
  }

  // 3) Der Nachfolger-Graph ist FUNKTIONAL -- jede Kachel hat hoechstens einen
  // Nachfolger -- und damit sind seine Zyklen eindeutig bestimmt. Die erste
  // Fassung suchte sie gierig und bekam je nach Startreihenfolge ein anderes
  // Ergebnis (JS 6 Zyklen, die Python-Gegenrechnung 8). Deshalb: erst ALLE
  // Zyklen bestimmen, dann die Ketten, die in sie hineinlaufen, dann der Rest.
  const done = new Set(), inCycle = new Set(), cycles = [];
  for (const start of next.keys()) {
    if (done.has(start)) continue;
    const path = [], pos = new Map();
    let cur = start;
    while (cur !== undefined && !done.has(cur)) {
      if (pos.has(cur)) { const cyc = path.slice(pos.get(cur)); cycles.push(cyc); cyc.forEach(h => inCycle.add(h)); break; }
      pos.set(cur, path.length); path.push(cur); cur = next.get(cur);
    }
    path.forEach(h => done.add(h));
  }
  // Ketten beginnen dort, wo nichts hinfuehrt: sonst waere ein Stueck davon
  // doppelt vergeben und die laengere Kette bliebe unerkannt.
  const indeg = new Map();
  for (const b of next.values()) indeg.set(b, (indeg.get(b) || 0) + 1);
  const groups = cycles.map(c => ({ kind: 'cycle', tiles: c }));
  const taken = new Set(inCycle);
  for (const h of next.keys()) {
    if (taken.has(h) || indeg.get(h)) continue;
    const path = []; let cur = h;
    while (cur !== undefined && !taken.has(cur)) { path.push(cur); taken.add(cur); cur = next.get(cur); }
    if (path.length >= 3) groups.push({ kind: 'chain', tiles: path });
    else path.forEach(x => taken.delete(x));
  }
  for (const h of palOf.keys()) if (!taken.has(h)) groups.push({ kind: 'single', tiles: [h] });
  return groups.map(g => ({ ...g, pals: g.tiles.map(h => palOf.get(h) || 0) }));
}