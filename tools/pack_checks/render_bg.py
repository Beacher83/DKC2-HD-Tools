# Render a BG layer straight from a real VRAM dump and compare with the viewer's SD export image.
import sys, numpy as np
from PIL import Image
vram_p, cg_p, tm, chr_, w, h, bpp, ref, out = sys.argv[1:10]
tm = int(tm, 16); chr_ = int(chr_, 16); w = int(w); h = int(h); bpp = int(bpp)
v = open(vram_p, 'rb').read(); cg = open(cg_p, 'rb').read()
pal = [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)
       for c in (int.from_bytes(cg[i*2:i*2+2], 'little') for i in range(256))]
img = np.zeros((h*8, w*8, 4), np.uint8)
for ty in range(h):
    for tx in range(w):
        sc = (tx // 32) + (ty // 32) * (w // 32)
        eo = ((tm + sc*0x400 + (ty % 32)*32 + (tx % 32)) * 2) & 0xFFFF
        e = v[eo] | (v[eo+1] << 8); t = e & 0x3FF; p = (e >> 10) & 7; fx = (e >> 14) & 1; fy = (e >> 15) & 1
        a = ((chr_ + t*(8 if bpp == 2 else 16)) * 2) & 0xFFFF
        for y in range(8):
            yy = 7-y if fy else y
            p0, p1 = v[a+yy*2], v[a+yy*2+1]
            p2, p3 = (v[a+16+yy*2], v[a+16+yy*2+1]) if bpp == 4 else (0, 0)
            for x in range(8):
                s = x if fx else 7-x
                i = ((p0 >> s) & 1) | (((p1 >> s) & 1) << 1) | (((p2 >> s) & 1) << 2) | (((p3 >> s) & 1) << 3)
                if i: img[ty*8+y, tx*8+x] = (*pal[(p*4 if bpp == 2 else p*16)+i], 255)
Image.fromarray(img).save(out)
r = np.asarray(Image.open(ref).convert('RGBA'), float)
if r.shape == img.shape:
    m = (r[..., 3] > 128) | (img[..., 3] > 128)
    d = np.abs(r[..., :3] - img[..., :3].astype(float)).mean(axis=2)
    d[(r[..., 3] > 128) != (img[..., 3] > 128)] = 255
    print('Vergleich mit Export: mittlere Abweichung %.1f, Pixel identisch %.1f %%' % (d[m].mean(), 100*(d[m] < 1).mean()))
else:
    print('Groessen verschieden', r.shape, img.shape)
