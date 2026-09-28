# Pack file for BG tile at address A (and palette P) vs the SD layer image at the tilemap
# positions where the REAL tilemap uses that tile. Palette-independent cut test.
import sys, os, re, numpy as np, random
from PIL import Image
packdir, layer, gfx, vram_p, tm, chr_, w, h, bpp, sdimg = sys.argv[1:11]
tm = int(tm, 16); chr_ = int(chr_, 16); w = int(w); h = int(h); bpp = int(bpp)
v = open(vram_p, 'rb').read()
sd = np.asarray(Image.open(sdimg).convert('RGBA'), float)
pos = {}
for ty in range(h):
    for tx in range(w):
        sc = (tx // 32) + (ty // 32) * (w // 32)
        eo = ((tm + sc*0x400 + (ty % 32)*32 + (tx % 32)) * 2) & 0xFFFF
        e = v[eo] | (v[eo+1] << 8); t = e & 0x3FF; p = (e >> 10) & 7
        a = (chr_ + t*(8 if bpp == 2 else 16)) & 0x7FFF
        pos.setdefault((a, p), []).append((tx, ty, (e >> 14) & 1, (e >> 15) & 1))
d = os.path.join(packdir, 'bg', layer, 'gfxset_'+gfx)
fs = [f for f in os.listdir(d) if re.match(r'^[0-9A-F]{4}_P\d\d\.png$', f)]
random.seed(1); fs = random.sample(fs, min(80, len(fs)))
res = []; nopos = 0
for f in fs:
    a = int(f[:4], 16); p = int(f[6:8])
    ps = pos.get((a, p))
    if not ps: nopos += 1; continue
    im = np.asarray(Image.open(os.path.join(d, f)).convert('RGBA').resize((8, 8), Image.BOX), float)
    best = 1e9
    for tx, ty, fx, fy in ps:
        s = sd[ty*8:ty*8+8, tx*8:tx*8+8]
        if s.shape[:2] != (8, 8): continue
        if fx: s = s[:, ::-1]
        if fy: s = s[::-1]
        m = (s[..., 3] > 128) | (im[..., 3] > 128)
        if m.sum() == 0: best = min(best, 0); continue
        e = np.abs(s[..., :3] - im[..., :3]).mean(axis=2); e[(s[..., 3] > 128) != (im[..., 3] > 128)] = 255
        best = min(best, e[m].mean())
    res.append(best)
res = np.array(res)
print(f'{layer}/gfxset_{gfx}: {len(res)} Dateien geprueft, {nopos} ohne Position in der echten Tilemap; '
      f'Median-Abweichung zur SD-Vorlage {np.median(res) if len(res) else float("nan"):.1f}, gut(<15) {(res < 15).sum()}')
