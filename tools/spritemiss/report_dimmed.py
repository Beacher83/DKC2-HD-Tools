import os, sys, re, json, collections
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'lib2.py')).read())
rowid = {}; hashrows = collections.defaultdict(set)
rx = re.compile(r"^SPR ([0-9A-F]{16}) P(\d) T[0-9A-F]{64} C([0-9A-F]{64})")
for line in open(os.path.join(DL,'snes_hd_spritecap.txt'), encoding='utf-8', errors='replace'):
    m = rx.match(line)
    if not m: continue
    h, p, c = m.groups()
    i = rowid.setdefault(c, len(rowid))
    hashrows[h].add(i)
rows = [None]*len(rowid)
for hex_, i in rowid.items():
    rows[i] = [int(hex_[k*4:k*4+4],16) & 0x7FFF for k in range(16)]
print(f"{len(rowid)} verschiedene CGRAM-Zeilen, {len(hashrows)} Hashes")
def isdim(a,b):
    n=0; s=0.0; lo=9e9; hi=-9e9
    for i in range(1,16):
        for sh in (0,5,10):
            ca=(a[i]>>sh)&31
            if ca<6: continue
            r=((b[i]>>sh)&31)/ca
            s+=r; n+=1; lo=min(lo,r); hi=max(hi,r)
    if n<15: return False
    m=s/n
    return 0.30<=m<=0.90 and (hi-lo)<=0.30
partners=collections.defaultdict(set)
for i in range(len(rows)):
    for j in range(len(rows)):
        if i!=j and isdim(rows[i],rows[j]): partners[i].add(j)
dimmed=set()
for h,ids in hashrows.items():
    for i in ids:
        if i in partners and (partners[i] & ids): dimmed.add(h); break
print(f"{len(partners)} Zeilen haben eine gedimmte Kopie, {len(dimmed)} Kacheln unter beiden")
names = load_names(); a2h = anim2h(); packed = load_packed()
import re as _re
for lbl,pat in [('Krow',r'Krow'),('Kleever',r'Kleever'),('King B',r'King B'),('DD Ducking',r'^DD Ducking'),('Rattly',r'Rattly')]:
    hs=set()
    for a in [a for a,n in names.items() if _re.search(pat,n)]: hs |= a2h.get(a,set())
    print(f"  {lbl:12s}: {len(hs):5d} Kacheln, {sum(1 for h in hs if h in dimmed):5d} als 'gedimmt' markiert")
json.dump(sorted(dimmed), open(os.path.join(SP,'dimmed.json'),'w'))
