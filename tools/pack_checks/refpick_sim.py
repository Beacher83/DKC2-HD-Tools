# Nachbau von bestRefFor(): Stichprobe "alt" (erste 64 opake Texel von oben, vor eabf295) vs "neu" (gleichmaessig verteilt).
# N ist fest auf den installierten Pack gesetzt. (entstanden 29.09.2026)
from PIL import Image
N=r'C:/Users/beach/OneDrive/Dokumente/Mesen2/HdPacks/Donkey Kong Country 2/sprites/'
tab=lambda p:[((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3) for c in p[1:]]
def dist(p,q): return min(sum((a-b)**2 for a,b in zip(p,r)) for r in q)
def samples(f,mode):
    px=list(Image.open(N+f).convert('RGBA').getdata())
    if mode=='alt':
        s=[p[:3] for p in px[::2] if p[3]>=200][:64]
        if len(s)<32: s=[p[:3] for p in px if p[3]>=200][:64]
    else:
        op=[p[:3] for p in px if p[3]>=200]; s=[op[int(k*len(op)/64)] for k in range(min(64,len(op)))]
    return s
def pick(f,pool,mode):
    s=samples(f,mode); r=[]
    for name,p in pool.items():
        e=sorted(dist(x,tab(p)) for x in s); k=max(1,int(len(e)*.75))
        r.append((sum(e)/len(e),name,sum(e[:k])/k))
    r.sort(); return f'{r[0][1]} (mean {r[0][0]:.0f}, trim {r[0][2]:.0f})'
