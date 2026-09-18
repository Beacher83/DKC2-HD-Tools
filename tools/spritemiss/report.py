# Hauptbericht: was im Spiel verfehlt wurde, was im Pack liegt, was exportierbar ist.
#   python report.py            -> Gesamtzahlen + Gruppentabelle
#   python report.py Krow Rattly -> nur diese Namensmuster
# Liest direkt die Recorder-Dateien aus Downloads und den installierten Pack.
import os, sys, re, json, struct, collections
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'lib2.py')).read())

def load_refs_from_pack():
    """Hash -> Referenzpalettenindex aus sprite_palettes.bin des installierten Packs.
    Ein Hash mit Referenz wird von Mesen SLOT-FREI geladen (SnesHdSpriteAnyPalette)."""
    p = os.path.join(PACKDIR, 'sprite_palettes.bin')
    if not os.path.exists(p): return {}
    d = open(p,'rb').read()
    pc = struct.unpack_from('<H', d, 1)[0]
    off = 3 + pc*16*2
    ec = struct.unpack_from('<I', d, off)[0]; off += 4
    return {f"{h:016X}": pi for h, pi in
            (struct.unpack_from('<QH', d, off + i*10) for i in range(ec))}

names = load_names(); a2h = anim2h()
packed = load_packed(); refs = load_refs_from_pack()
miss = load_miss(); cap, _ = load_cap()

print(f"Pack:       {len(packed)} Sprite-Hashes, {len(refs)} davon slot-frei (mit Referenzpalette)")
print(f"spritecap:  {len(cap)} Hashes")
print(f"spritemiss: {len(miss)} verfehlte Hashes")
print(f"  ohne Pack-Kunst:                         {sum(1 for h in miss if h not in packed)}")
print(f"  im Pack UND verfehlt (Slot passt nicht): {sum(1 for h in miss if h in packed)}")
print(f"  mit spritecap-Slot -> exportierbar:      {sum(1 for h in miss if h in cap)}")
print(f"  ohne Slot -> Export verwirft die Kunst:  {sum(1 for h in miss if h not in cap)}")

pats = sys.argv[1:] or ['Krow','Kleever','King B','Puftup','Rattly','Snapjaw','Ducking',
                        'Auto Barrel Cannon','Squawks','Kudgel',r'K\. Rool']
print(f"\n{'Kacheln':>8} {'Pack':>5} {'MISS':>6} {'spritecap':>10}  Gruppe")
for pat in pats:
    aids = [a for a,n in names.items() if re.search(pat, n)]
    hs = set()
    for a in aids: hs |= a2h.get(a, set())
    if not hs: print(f"{'-':>8} {'-':>5} {'-':>6} {'-':>10}  {pat}  (kein Treffer)"); continue
    print(f"{len(hs):8d} {sum(1 for h in hs if h in packed):5d} {sum(1 for h in hs if h in miss):6d} "
          f"{sum(1 for h in hs if h in cap):10d}  {pat} ({len(aids)} Animationen)")
