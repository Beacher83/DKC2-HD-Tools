import os,sys,json,collections
ROM=r"C:\Users\beach\Downloads\Donkey Kong Country 2 - Diddy's Kong Quest.smc"
PACK=r"C:\Users\beach\OneDrive\Dokumente\Mesen2\HdPacks\Donkey Kong Country 2\sprites"
d=open(ROM,'rb').read()
if len(d)%1024==512: d=d[512:]
ANIM=0x390000; DESC=0x3C8000
def w(o): return d[o]|(d[o+1]<<8)
def b(o): return d[o]
def snes2file(a): return ((a>>16)&0x3F)<<16 | (a&0xFFFF)

M=0xFFFFFFFFFFFFFFFF
def fnv(buf,off,n):
    h=0xcbf29ce484222325
    for i in range(off,off+n):
        h^=buf[i]; h=(h*0x100000001b3)&M
    return h

def frames(aid):
    ptr=ANIM+aid*4
    if ptr+4>len(d): return []
    off=w(ptr)
    if off in (0,0xFFFF): return []
    out=[]; pos=ANIM+off; vis=set()
    for _ in range(512):
        if pos>=len(d) or pos in vis: break
        c=b(pos)
        if c in (0x80,0x94): break
        if 0x01<=c<=0x7f:
            g=w(pos+1)
            if 0<g<0x8000: out.append([g])
            pos+=3
        elif c==0x82: vis.add(pos); pos=ANIM+w(pos+1)
        elif c in (0x81,0x83,0x84): pos+=3
        elif c in (0x85,0x89): out.append([w(pos+2),w(pos+4)]); pos+=6
        elif c in (0x86,0x8a): out.append([w(pos+2),w(pos+4)]); pos+=10
        elif c in (0x87,0x8b): out.append([w(pos+2)]); pos+=8
        elif c in (0x88,0x8c): pos+=5
        elif c==0x8d: out.append([w(pos+2),w(pos+4)]); pos+=8
        elif c in (0x8e,0x93): pos+=3
        elif c in (0x8f,0x90): pos+=5
        elif c==0x91: pos+=4
        elif c==0x92: pos+=3
        else: break
    return out

_dc={}
def desc_hashes(gref):
    if gref in _dc: return _dc[gref]
    r=None
    if DESC+gref+3 < len(d):
        a=b(DESC+gref)|(b(DESC+gref+1)<<8)|(b(DESC+gref+2)<<16)
        if a:
            f=snes2file(a)
            if f+8<len(d):
                big=b(f); sm=b(f+1); extra=b(f+3)
                blk1=b(f+5); blk2=b(f+7)&0x0F
                tot=big+sm+extra
                if 0<tot<=128:
                    p=f+8+tot*2
                    hs=[]
                    for t in range(blk1):
                        o=p+t*32
                        if o+32<=len(d): hs.append(fnv(d,o,32))
                    p2=p+blk1*32
                    for t in range(blk2):
                        o=p2+t*32
                        if o+32<=len(d): hs.append(fnv(d,o,32))
                    r=hs
    _dc[gref]=r
    return r

packed=set()
for fn in os.listdir(PACK):
    if fn.endswith('.png'):
        packed.add(fn.split('_')[0].upper())
print(f"Pack: {len(packed)} distinkte Sprite-Hashes ({len(os.listdir(PACK))} Dateien)\n")

rows=[]
hash2anim=collections.defaultdict(set)
for aid in range(1,0x030C):
    fr=frames(aid)
    if not fr: continue
    allh=[]; perframe=[]
    for f in fr:
        fh=set()
        for g in f:
            hs=desc_hashes(g)
            if hs: fh.update(hs)
        perframe.append(fh); allh.append(fh)
    uni=set().union(*allh) if allh else set()
    if not uni: continue
    for h in uni: hash2anim[h].add(aid)
    have=sum(1 for h in uni if f"{h:016X}" in packed)
    # frames fully covered
    fullframes=sum(1 for fh in perframe if fh and all(f"{h:016X}" in packed for h in fh))
    nonempty=sum(1 for fh in perframe if fh)
    rows.append((aid,len(fr),nonempty,fullframes,len(uni),have))

json.dump({f"{h:016X}":sorted(a) for h,a in hash2anim.items()},open('hash2anim.json','w'))
print(f"ROM-Index: {len(hash2anim)} distinkte Kachel-Hashes ueber {len(rows)} Animationen")
tot=set(hash2anim); hav={h for h in tot if f"{h:016X}" in packed}
print(f"davon im Pack: {len(hav)}  ({100*len(hav)/len(tot):.1f}%)   fehlend: {len(tot)-len(hav)}\n")
json.dump(rows,open('rows.json','w'))
print(f"{'animId':>7} {'Frames':>6} {'volle HD-Frames':>16} {'Kacheln':>8} {'im Pack':>8}")
for aid,nf,ne,ff,nu,hv in rows:
    if aid in (0x0001,0x00A4,0x0007,0x00AA,0x00AB,0x0008):
        print(f" 0x{aid:04X} {nf:6d} {ff:8d}/{ne:<7d} {nu:8d} {hv:8d}")
