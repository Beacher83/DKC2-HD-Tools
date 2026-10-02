import sys,struct,os
from PIL import Image
from collections import Counter
def load(p):
    b=open(p,'rb').read();o=1
    pc=struct.unpack_from('<H',b,o)[0];o+=2
    pals=[struct.unpack_from('<16H',b,o+i*32) for i in range(pc)];o+=pc*32
    ec=struct.unpack_from('<I',b,o)[0];o+=4;ent={}
    for i in range(ec):
        h,pi=struct.unpack_from('<QH',b,o);o+=10;ent[h]=pi
    return pals,ent
def rgb(c): return ((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31)
def fitp(px,pal): 
    q=[rgb(c) for c in pal[1:]]
    return sum(min(sum((a-b)**2 for a,b in zip(p[:3],r)) for r in q) for p in px)/len(px)
if __name__=='__main__':
    N,old,out=sys.argv[1:4]
    pals,ent=load(N+'/sprite_palettes.bin'); _,eo=load(old+'/sprite_palettes.bin')
    _,e28=load(sys.argv[4])
    hs=[h for h in eo if h not in e28]
    print(len(hs),'Gfx-14A8-Hashes; Refpaletten',Counter(ent.get(h) for h in hs).most_common(8))
    files={}
    for f in os.listdir(N+'/sprites'): files.setdefault(f[:16].upper(),[]).append(f)
    rows=[]
    for h in hs:
        fs=files.get('%016X'%h)
        if not fs: rows.append((h,None,None,None));continue
        px=[p for p in Image.open(N+'/sprites/'+fs[0]).convert('RGBA').getdata() if p[3]>128][::4]
        if not px: continue
        own=fitp(px,pals[ent[h]])
        best=min(range(len(pals)),key=lambda i:fitp(px,pals[i]))
        rows.append((h,ent[h],own,best,fitp(px,pals[best]),fs[0]))
    print('ohne Datei',sum(1 for r in rows if r[1] is None))
    bad=[r for r in rows if r[1] is not None and r[2]>3*r[4]+300]
    print('Ref passt schlecht:',len(bad))
    for r in bad[:30]: print('%016X ref=%s own=%.0f best=%d(%.0f) %s'%r)
    open(out,'w').write('\n'.join('%016X'%r[0] for r in bad))
