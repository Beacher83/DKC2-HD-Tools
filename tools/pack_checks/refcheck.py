# Jede Sprite-Kachel gegen ALLE Referenzpaletten des Packs: passt die eigene Referenz >3x schlechter
# als die beste andere? Aufruf: python refcheck.py "<Pack-Ordner>" <out.pkl>  (entstanden 29.09.2026)
import sys,os,numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__)); from sprpal_lib import load
N,out=sys.argv[1:3]
pals,ent=load(N+'/sprite_palettes.bin')
P=np.array([[((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31) for c in p[1:]] for p in pals],float) # K,15,3
res=[]
fl=os.listdir(N+'/sprites')
for i,f in enumerate(fl):
    h=int(f[:16],16)
    if h not in ent: continue
    a=np.asarray(Image.open(N+'/sprites/'+f).convert('RGBA'),float).reshape(-1,4)
    px=a[a[:,3]>128][:,:3]
    if len(px)<16: continue
    px=px[::3]
    d=((px[None,:,None,:]-P[:,None,:,:])**2).sum(-1).min(-1).mean(-1) # K
    own=d[ent[h]];b=int(d.argmin())
    res.append((f,ent[h],own,b,d[b],len(px)))
import pickle;pickle.dump(res,open(out,'wb'))
bad=[r for r in res if r[2]>3*r[4]+300]
print(len(res),'geprueft, schlecht',len(bad))
