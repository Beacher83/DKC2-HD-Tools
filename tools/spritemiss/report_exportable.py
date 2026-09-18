import os, sys, json, collections, re
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'lib2.py')).read())
names = load_names(); a2h = anim2h(); packed = load_packed()
mall = load_miss(); cap,_ = load_cap()
print(f"spritemiss (beide Laeufe): {len(mall)} Hashes")
print(f"  ohne Pack-Kunst: {sum(1 for h in mall if h not in packed)}")
print(f"  jetzt mit spritecap-Eintrag (exportierbar, sobald upgescalt): {sum(1 for h in mall if h in cap)}")
print(f"  noch ohne spritecap: {sum(1 for h in mall if h not in cap)}")
print(f"\n{'Kacheln':>8} {'Pack':>5} {'MISS':>6} {'in spritecap':>13}  Gruppe")
for lbl,pat in [('Krow (ohne Eier)',r'Krow'),('Kleever',r'Kleever'),('King B / King Zing',r'King B'),
                ('Puftup',r'Puftup'),('Rattly',r'Rattly'),('Snapjaw',r'Snapjaw'),('Squawks',r'Squawks'),
                ('DD/DX Ducking',r'Ducking'),('Abschussfass 0x015B',r'Auto Barrel Cannon')]:
    aids=[a for a,n in names.items() if re.search(pat,n)]
    hs=set()
    for a in aids: hs |= a2h.get(a,set())
    print(f"{len(hs):8d} {sum(1 for h in hs if h in packed):5d} {sum(1 for h in hs if h in mall):6d} {sum(1 for h in hs if h in cap):13d}  {lbl}")
