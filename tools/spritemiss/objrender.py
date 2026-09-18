import json, os, re, sys
from PIL import Image
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'gfxlib.py')).read())
MISS = r"C:\Users\beach\Downloads\snes_hd_spritemiss.txt"
rx = re.compile(r"^SPRMISS (\w) P(\d+) O(\d+) G(\d+) H([0-9A-F]{16}) T([0-9A-F]{64}) C([0-9A-F]{64})")
cgmap = {}
for line in open(MISS, encoding='utf-8', errors='replace'):
    m = rx.match(line)
    if m: cgmap.setdefault(m.group(5), m.group(7))
def pal_from(chex):
    out=[]
    for i in range(16):
        v=int(chex[i*4:i*4+4],16)
        out.append(((v&31)*255//31, ((v>>5)&31)*255//31, ((v>>10)&31)*255//31))
    return out

def desc(gref):
    if DESC+gref+3 >= len(d): return None
    a=_b(DESC+gref)|(_b(DESC+gref+1)<<8)|(_b(DESC+gref+2)<<16)
    if not a: return None
    f=snes2file(a)
    big=d[f]; small=d[f+1]; tileBase=d[f+2]; extra=d[f+3]; flags=d[f+4]
    blk1=d[f+5]; r2=d[f+6]; blk2=d[f+7]&0x0F
    tot=big+small+extra
    if not (0<tot<=128): return None
    p=f+8
    ents=[]
    for i in range(tot):
        rx_,ry=d[p+i*2], d[p+i*2+1]
        ents.append((rx_-0x80, ry-0x80, 16 if i<big else 8))
    p+=tot*2
    b1=d[p:p+blk1*32]; b2=d[p+blk1*32:p+blk1*32+blk2*32]
    return dict(big=big,small=small,tileBase=tileBase,extra=extra,flags=flags,
                blk1=blk1,blk2=blk2,r2=r2,ents=ents,b1=b1,b2=b2)

def get_slot(D, slot):
    if D['b2'] and D['r2']>0:
        b2 = slot - D['r2']
        if 0 <= b2 < D['blk2']:
            o=b2*32
            if o+32<=len(D['b2']): return D['b2'][o:o+32]
    if 0 <= slot < D['blk1']:
        o=slot*32
        if o+32<=len(D['b1']): return D['b1'][o:o+32]
    return None

def draw(img, px, bts, ox, oy, pal, W, H):
    for y in range(8):
        p0=bts[y*2]; p1=bts[y*2+1]; p2=bts[16+y*2]; p3=bts[16+y*2+1]
        for x in range(8):
            bit=7-x
            v=((p0>>bit)&1)|(((p1>>bit)&1)<<1)|(((p2>>bit)&1)<<2)|(((p3>>bit)&1)<<3)
            if v==0: continue
            X,Y=ox+x,oy+y
            if 0<=X<W and 0<=Y<H: px[X,Y]=pal[v]

def render(gref, fallback_pal=None):
    D=desc(gref)
    if not D: return None
    xs=[e[0] for e in D['ents']]; ys=[e[1] for e in D['ents']]
    minX=min(xs); minY=min(ys)
    maxX=max(e[0]+e[2] for e in D['ents']); maxY=max(e[1]+e[2] for e in D['ents'])
    W,H=maxX-minX, maxY-minY
    if not(0<W<=256 and 0<H<=256): return None
    img=Image.new('RGB',(W,H),(30,30,36)); px=img.load()
    placed=[]
    def put(bts,ox,oy):
        h=f"{fnv(bts,0,32):016X}"
        pal = pal_from(cgmap[h]) if h in cgmap else (fallback_pal or [(255,0,255)]*16)
        draw(img,px,bts,ox,oy,pal,W,H); placed.append((h,ox,oy,h in cgmap))
    for i in range(min(D['big'],len(D['ents']))):
        tx,ty,_=D['ents'][i]; ox,oy=tx-minX,ty-minY
        ts=(i//8)*32+(i%8)*2
        for s,dx,dy in ((ts,0,0),(ts+1,8,0),(ts+16,0,8),(ts+17,8,8)):
            t=get_slot(D,s)
            if t: put(t,ox+dx,oy+dy)
    for j in range(D['small']):
        idx=D['big']+j
        if idx>=len(D['ents']): break
        tx,ty,_=D['ents'][idx]
        t=get_slot(D,D['tileBase']+j)
        if t: put(t,tx-minX,ty-minY)
    for k in range(D['extra']):
        idx=D['big']+D['small']+k
        if idx>=len(D['ents']): break
        tx,ty,_=D['ents'][idx]
        t=get_slot(D,D['flags']+k)
        if t: put(t,tx-minX,ty-minY)
    return img, placed, D

GR=[int(x,16) for x in sys.argv[1:]] or [0x2D20,0x2D24,0x2D40,0x3170,0x319C]
Z=5
imgs=[]
for g in GR:
    r=render(g)
    if not r: print(f"{g:04X}: keine Beschreibung"); continue
    img,placed,D=r
    nmiss=sum(1 for p in placed if p[3])
    print(f"{g:04X}: {img.size[0]}x{img.size[1]} px, {len(placed)} Kacheln platziert, {nmiss} davon im Lauf verfehlt (16x16={D['big']} 8x8={D['small']} extra={D['extra']})")
    imgs.append((g,img))
if imgs:
    W=sum(i.size[0] for _,i in imgs)*Z + 10*len(imgs)
    H=max(i.size[1] for _,i in imgs)*Z
    out=Image.new('RGB',(W,H),(15,15,18)); x=0
    for g,i in imgs:
        s=i.resize((i.size[0]*Z,i.size[1]*Z), Image.NEAREST)
        out.paste(s,(x,0)); x+=s.size[0]+10
    out.save(os.path.join(SP,'objs.png')); print("Bild:", out.size, "Reihenfolge:", [f"{g:04X}" for g,_ in imgs])
