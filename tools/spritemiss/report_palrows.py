import os, sys, re, json, collections
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'lib2.py')).read())
names = load_names(); a2h = anim2h()
krow = {a for a,n in names.items() if 'Krow' in n and 'Egg' not in n}
kh = set()
for a in krow: kh |= a2h.get(a,set())
# ALLE Zeilen pro Hash, aus spritecap (beide Läufe) und spritemiss
rx = re.compile(r"^SPRMISS \w P(\d+) O\d+ G(\d+) H([0-9A-F]{16}) T[0-9A-F]{64} C([0-9A-F]{64})")
rows = collections.defaultdict(set); gfxof = collections.defaultdict(set)
for line in open(os.path.join(DL,'snes_hd_spritemiss.txt'), encoding='utf-8', errors='replace'):
    m = rx.match(line)
    if m and m.group(3) in kh:
        rows[m.group(3)].add(m.group(4)); gfxof[m.group(3)].add(int(m.group(2)))
caprows = collections.defaultdict(set); capslots = collections.defaultdict(set)
for line in open(os.path.join(DL,'snes_hd_spritecap.txt'), encoding='utf-8', errors='replace'):
    if not line.startswith('SPR '): continue
    p = line.split(' ')
    if p[1] in kh:
        caprows[p[1]].add(p[4].strip()[1:]); capslots[p[1]].add(int(p[2][1:]))
print(f"Krow-Kacheln: {len(kh)}")
print(f"  in spritemiss aufgezeichnet: {len(rows)}   in spritecap: {len(caprows)}")
d1 = collections.Counter(len(v) for v in caprows.values())
print(f"  Verteilung CGRAM-Zeilen je Kachel (spritecap): {dict(sorted(d1.items()))}")
d2 = collections.Counter(len(v) for v in rows.values())
print(f"  Verteilung CGRAM-Zeilen je Kachel (spritemiss): {dict(sorted(d2.items()))}")
multi = [h for h,v in caprows.items() if len(v)>1]
print(f"  Kacheln unter MEHR ALS EINER Zeile: {len(multi)}")
if multi:
    h = multi[0]
    print(f"  Beispiel {h}: Slots {sorted(capslots[h])}")
    for r in sorted(caprows[h]):
        print("     " + " ".join(r[i*4:i*4+4] for i in range(1,9)))
# alle vorkommenden Zeilen insgesamt
allrows = collections.Counter()
for h,v in caprows.items():
    for r in v: allrows[r]+=1
print(f"\n  verschiedene CGRAM-Zeilen über alle Krow-Kacheln: {len(allrows)}")
for r,c in allrows.most_common(5):
    print(f"    {c:5d} Kacheln  " + " ".join(r[i*4:i*4+4] for i in range(1,9)))
