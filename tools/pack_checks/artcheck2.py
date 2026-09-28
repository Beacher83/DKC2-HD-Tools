import sys, os, re, numpy as np, random
from PIL import Image
packdir, layer, vram_path, cgram_path, gfx = sys.argv[1:6]
bpp = 2 if layer=='bg3' else 4
vram = open(vram_path,'rb').read(); cg = open(cgram_path,'rb').read()
pal = [int.from_bytes(cg[i*2:i*2+2],'little') for i in range(256)]
rgb = lambda c: np.array([(c&31)<<3, ((c>>5)&31)<<3, ((c>>10)&31)<<3], float)
def tile(addr, p):
    o=addr*2; n=16 if bpp==2 else 32
    if o+n>len(vram): return None
    b=vram[o:o+n]; out=np.zeros((8,8,3)); m=np.zeros((8,8),bool)
    for y in range(8):
        p0,p1=b[y*2],b[y*2+1]; p2,p3=(b[16+y*2],b[16+y*2+1]) if bpp==4 else (0,0)
        for x in range(8):
            s=7-x;i=((p0>>s)&1)|(((p1>>s)&1)<<1)|(((p2>>s)&1)<<2)|(((p3>>s)&1)<<3)
            if i: out[y,x]=rgb(pal[(p*4 if bpp==2 else p*16)+i]); m[y,x]=True
    return out,m
d=os.path.join(packdir,'bg',layer,'gfxset_'+gfx)
if not os.path.isdir(d): print(layer,gfx,'kein Ordner'); sys.exit()
fs=[f for f in os.listdir(d) if re.match(r'^[0-9A-F]{4}_P\d\d\.png$',f)]
if not fs: print(layer,gfx,'keine Adress-Dateien (%d Dateien)'%len(os.listdir(d))); sys.exit()
random.seed(1); fs=random.sample(fs,min(100,len(fs))); errs=[]
for f in fs:
    a=int(f[:4],16); p=int(f[6:8]); t=tile(a,p)
    if t is None: continue
    im=np.asarray(Image.open(os.path.join(d,f)).convert('RGBA').resize((8,8),Image.BOX),float)
    al=im[...,3]>128; c,m=t; both=al|m
    if both.sum()==0: continue
    e=np.abs(im[...,:3]-c).mean(axis=2); e[al!=m]=255; errs.append(e[both].mean())
print(f'{layer}/gfxset_{gfx}: {len(errs)} Dateien, Median-Fehler {np.median(errs):.1f}, gut(<15) {sum(x<15 for x in errs)}')
