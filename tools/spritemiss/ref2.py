# Referenz mit GENAU derselben Eingabe wie der Viewer: alle 8x8-Partikel in Gfxset 32.
import os, sys, re, json, collections
SPD=os.path.dirname(os.path.abspath(__file__))
DL=r"C:\Users\beach\Downloads"
rxf=re.compile(r"^OAMF G(-?\d+) S([0-9A-F]{16}) F(\d+) M(\d+) N(\d+)$")
rxe=re.compile(r"^OAM I(\d+) X([+-]\d+) Y(\d+) W(\d+) H(\d+) T([0-9A-F]+) P(\d) R(\d) (.)(.) (.+)$")
frames=[]; cur=None
for line in open(os.path.join(DL,'snes_hd_oam.txt'), encoding='latin-1'):
    l=line.rstrip()
    m=rxf.match(l)
    if m: cur={'g':int(m.group(1)),'f':int(m.group(3)),'e':[]}; frames.append(cur); continue
    m=rxe.match(l)
    if not m or cur is None: continue
    hs=m.group(11).split()
    cur['e'].append({'x':int(m.group(2)),'y':int(m.group(3)),'pal':int(m.group(7)),'hs':hs})
frames=[f for f in frames if f['g']==32]
DIST=14
tracks=[]; active=[]; prevF=None
for fr in frames:
    if prevF is not None and fr['f']-prevF>3: tracks+=active; active=[]
    prevF=fr['f']
    ents=[e for e in fr['e'] if len(e['hs'])==1]
    pairs=[]
    for ti,t in enumerate(active):
        for ei,e in enumerate(ents):
            d=abs(e['x']-t['px'])+abs(e['y']-t['py'])
            if d<=DIST: pairs.append((d,ti,ei))
    pairs.sort()
    uT=set(); uE=set()
    for d,ti,ei in pairs:
        if ti in uT or ei in uE: continue
        uT.add(ti); uE.add(ei)
        t=active[ti]; e=ents[ei]
        vx,vy=e['x']-t['x'], e['y']-t['y']
        t.update(x=e['x'],y=e['y'],px=e['x']+vx,py=e['y']+vy,miss=0)
        t['seq'].append((e['hs'][0], e['pal']))
    keep=[]
    for ti,t in enumerate(active):
        if ti in uT: keep.append(t); continue
        t['miss']+=1
        if t['miss']<=2:
            t['px']+=t['px']-t['x']; t['py']+=t['py']-t['y']; keep.append(t)
        else: tracks.append(t)
    active=keep
    for ei,e in enumerate(ents):
        if ei in uE: continue
        active.append({'x':e['x'],'y':e['y'],'px':e['x'],'py':e['y'],'miss':0,'seq':[(e['hs'][0],e['pal'])]})
tracks+=active
succ=collections.defaultdict(collections.Counter); palOf={}
for t in tracks:
    for h,p in t['seq']: palOf.setdefault(h,p)
    if len(t['seq'])<6: continue
    u=[]
    for h,_ in t['seq']:
        if not u or u[-1]!=h: u.append(h)
    for a,b in zip(u,u[1:]): succ[a][b]+=1
nxt={}
for a,c in succ.items():
    tot=sum(c.values()); b,n=c.most_common(1)[0]
    if n>=2 and n/tot>=0.45: nxt[a]=b
done=set(); inC=set(); cycles=[]
for start in nxt:
    if start in done: continue
    path=[]; pos={}; cur2=start
    while cur2 is not None and cur2 not in done:
        if cur2 in pos:
            cyc=path[pos[cur2]:]; cycles.append(cyc); inC|=set(cyc); break
        pos[cur2]=len(path); path.append(cur2); cur2=nxt.get(cur2)
    done|=set(path)
indeg=collections.Counter(nxt.values())
groups=[('cycle',c) for c in cycles]; taken=set(inC)
for h in nxt:
    if h in taken or indeg[h]: continue
    path=[]; cur2=h
    while cur2 is not None and cur2 not in taken:
        path.append(cur2); taken.add(cur2); cur2=nxt.get(cur2)
    if len(path)>=3: groups.append(('chain',path))
    else: taken-=set(path)
shard=set(json.load(open(os.path.join(SPD,'shardhashes.json'))))
sg=[g for g in groups if all(h in shard for h in g[1])]
cyc=sorted([len(t) for k,t in sg if k=='cycle'],reverse=True)
chn=sorted([len(t) for k,t in sg if k=='chain'],reverse=True)
cov=len({h for k,t in sg for h in t})
print(json.dumps({'cycles':cyc,'chains':chn,'covered':cov}))
