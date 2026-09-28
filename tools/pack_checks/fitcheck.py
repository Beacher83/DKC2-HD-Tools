# Python twin of the viewer's fitLayerImage(): mean RGB distance over pixels the image covers,
# 255 where the render is transparent there. Used to validate LAYER_FIT_MAX_ERR = 25.
import sys, numpy as np
from PIL import Image
img_p, vram_p, cg_p, tm, chr_, w, h, bpp = sys.argv[1:9]
tm = int(tm, 16); chr_ = int(chr_, 16); w = int(w); h = int(h); bpp = int(bpp)
v = open(vram_p, 'rb').read(); cg = open(cg_p, 'rb').read()
img = np.asarray(Image.open(img_p).convert('RGBA').resize((w*8, h*8), Image.LANCZOS), float)
tmb = v[tm*2: tm*2 + w*h*2]
s = 0.0; n = 0
for ty in range(h):
    for tx in range(w):
        off = ((ty & 31)*32 + (tx & 31))*2 + (0x800 if tx >= 32 else 0) + ((0x1000 if w > 32 else 0x800) if ty >= 32 else 0)
        e = tmb[off] | (tmb[off+1] << 8); t = e & 0x3FF; p = (e >> 10) & 7; fx = e & 0x4000; fy = e & 0x8000
        a = (chr_*2 + t*(16 if bpp == 2 else 32)) & 0xFFFF
        for y in range(8):
            yy = 7-y if fy else y
            p0, p1 = v[a+yy*2], v[a+yy*2+1]
            p2, p3 = (v[a+16+yy*2], v[a+17+yy*2]) if bpp == 4 else (0, 0)
            for x in range(8):
                px = img[ty*8+y, tx*8+x]
                if px[3] <= 128: continue
                n += 1
                sh = x if fx else 7-x
                ci = ((p0 >> sh) & 1) | (((p1 >> sh) & 1) << 1) | (((p2 >> sh) & 1) << 2) | (((p3 >> sh) & 1) << 3)
                if not ci: s += 255; continue
                c = int.from_bytes(cg[((p*4 if bpp == 2 else p*16)+ci)*2:][:2], 'little')
                s += (abs(px[0]-((c & 31) << 3)) + abs(px[1]-(((c >> 5) & 31) << 3)) + abs(px[2]-(((c >> 10) & 31) << 3)))/3
print('%.1f' % (s/n if n else 255))
