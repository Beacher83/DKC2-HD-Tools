import os, collections
ROM = r"C:\Users\beach\Downloads\Donkey Kong Country 2 - Diddy's Kong Quest.smc"
PACKDIR = r"C:\Users\beach\OneDrive\Dokumente\Mesen2\HdPacks\Donkey Kong Country 2"
_d = open(ROM,'rb').read()
if len(_d)%1024==512: _d=_d[512:]
d=_d
DESC=0x3C8000
M=0xFFFFFFFFFFFFFFFF
def _b(o): return d[o]
def snes2file(a): return ((a>>16)&0x3F)<<16 | (a&0xFFFF)
def fnv(buf,off,n):
    h=0xcbf29ce484222325
    for i in range(off,off+n):
        h^=buf[i]; h=(h*0x100000001b3)&M
    return h
def desc_blocks(gref):
    if DESC+gref+3 >= len(d): return None
    a=_b(DESC+gref)|(_b(DESC+gref+1)<<8)|(_b(DESC+gref+2)<<16)
    if not a: return None
    f=snes2file(a)
    if f+8>=len(d): return None
    big=_b(f); sm=_b(f+1); extra=_b(f+3); blk1=_b(f+5); blk2=_b(f+7)&0x0F
    tot=big+sm+extra
    if not (0<tot<=128): return None
    p=f+8+tot*2
    return f, p, blk1, blk2
def desc_hashes(gref):
    r = desc_blocks(gref)
    if not r: return None
    f,p,blk1,blk2 = r
    hs=[]
    for t in range(blk1):
        o=p+t*32
        if o+32<=len(d): hs.append(fnv(d,o,32))
    p2=p+blk1*32
    for t in range(blk2):
        o=p2+t*32
        if o+32<=len(d): hs.append(fnv(d,o,32))
    return hs
def desc_tilebytes(gref):
    r = desc_blocks(gref)
    if not r: return []
    f,p,blk1,blk2 = r
    out=[]
    for t in range(blk1):
        o=p+t*32
        if o+32<=len(d): out.append((fnv(d,o,32), d[o:o+32], 4))
    p2=p+blk1*32
    for t in range(blk2):
        o=p2+t*32
        if o+32<=len(d): out.append((fnv(d,o,32), d[o:o+32], 4))
    return out
def load_packed():
    packed = collections.defaultdict(set)
    for fn in os.listdir(os.path.join(PACKDIR,'sprites')):
        if fn.lower().endswith('.png'):
            p=fn.split('_'); packed[p[0].upper()].add(p[1].split('.')[0] if len(p)>1 else '')
    return packed
