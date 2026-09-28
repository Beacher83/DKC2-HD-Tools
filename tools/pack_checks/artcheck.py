import sys, os, re, numpy as np
from PIL import Image
packdir, vram_path, cgram_path, gfx = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
vram = open(vram_path,'rb').read(); cg = open(cgram_path,'rb').read()
pal = [int.from_bytes(cg[i*2:i*2+2],'little') for i in range(256)]
def rgb(c): return np.array([(c&31)<<3, ((c>>5)&31)<<3, ((c>>10)&31)<<3], float)
def tile(addr, p):
    o = addr*2
    if o+32 > len(vram): return None
    b = vram[o:o+32]; out = np.zeros((8,8,3)); mask = np.zeros((8,8),bool)
    for y in range(8):
        p0,p1,p2,p3 = b[y*2], b[y*2+1], b[16+y*2], b[16+y*2+1]
        for x in range(8):
            s = 7-x; i = ((p0>>s)&1)|(((p1>>s)&1)<<1)|(((p2>>s)&1)<<2)|(((p3>>s)&1)<<3)
            if i: out[y,x] = rgb(pal[p*16+i]); mask[y,x] = True
    return out, mask
d = os.path.join(packdir, 'bg','bg1','gfxset_'+gfx)
files = sorted(f for f in os.listdir(d) if re.match(r'^[0-9A-F]{4}_P\d\d\.png$', f))
import random; random.seed(1); files = random.sample(files, min(150, len(files)))
offs = [-0x1000, 0, 0x1000]; wins = {o:0 for o in offs}; errs = {o:[] for o in offs}
for f in files:
    addr = int(f[:4],16); p = int(f[6:8])
    im = np.asarray(Image.open(os.path.join(d,f)).convert('RGBA').resize((8,8), Image.BOX), float)
    res = {}
    for o in offs:
        t = tile(addr+o, p)
        if t is None: continue
        rgbT, m = t
        a = im[...,3] > 128
        both = a | m
        if both.sum()==0: continue
        e = np.abs(im[...,:3]-rgbT).mean(axis=2)
        e[a != m] = 255
        res[o] = e[both].mean()
    if not res: continue
    best = min(res, key=res.get); wins[best]+=1
    for o,v in res.items(): errs[o].append(v)
print('gfxset', gfx, 'Stichprobe', len(files))
for o in offs: print(f'  Adresse {o:+#06x}: beste bei {wins[o]:3d} Dateien, mittlerer Fehler {np.mean(errs[o]) if errs[o] else float("nan"):6.1f}')
