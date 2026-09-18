import json, os, re, collections
SP = os.path.dirname(os.path.abspath(__file__))
names = {int(k):v for k,v in json.load(open(os.path.join(SP,'names.json'))).items()}
h2a   = json.load(open(os.path.join(SP,'hash2anim.json')))
miss  = json.load(open(os.path.join(SP,'miss.json')))
PACK  = r"C:\Users\beach\OneDrive\Dokumente\Mesen2\HdPacks\Donkey Kong Country 2\sprites"

packed = collections.defaultdict(set)
for fn in os.listdir(PACK):
    if fn.lower().endswith('.png'):
        p = fn.split('_')
        packed[p[0].upper()].add(p[1].split('.')[0] if len(p)>1 else '')

anim2h = collections.defaultdict(set)
for h,aids in h2a.items():
    for a in aids: anim2h[a].add(h)

def report(title, aids):
    print(f"\n=== {title} ===")
    print(f"{'anim':>6} {'Kacheln':>8} {'im Pack':>8} {'MISSES':>7}  Name")
    tot=hv=ms=0
    for a in aids:
        hs = anim2h.get(a, set())
        if not hs: 
            print(f"0x{a:04X} {'-':>8} {'-':>8} {'-':>7}  {names.get(a,'?')}  (keine ROM-Kacheln)")
            continue
        h_pack = {h for h in hs if h in packed}
        h_miss = {h for h in hs if h in miss}
        tot+=len(hs); hv+=len(h_pack); ms+=len(h_miss)
        flag = ''
        if h_miss & h_pack: flag = f'  <-- {len(h_miss & h_pack)} im Pack UND verfehlt'
        print(f"0x{a:04X} {len(hs):8d} {len(h_pack):8d} {len(h_miss):7d}  {names.get(a,'?')}{flag}")
    print(f"{'SUMME':>6} {tot:8d} {hv:8d} {ms:7d}")

krow = [a for a,n in names.items() if 'Krow' in n]
report("Boss Krow (alle Animationen mit 'Krow')", sorted(krow))

# palette detail for Krow tiles that are packed but missed
print("\n--- Krow: Kacheln im Pack, die im Lauf verfehlt wurden (Palettenslot-Vergleich) ---")
for a in sorted(krow):
    for h in sorted(anim2h.get(a,set())):
        if h in miss and h in packed:
            print(f"0x{a:04X} {h}  Pack-Paletten={sorted(packed[h])}  Laufzeit-Paletten={miss[h]['pal']} G={miss[h]['gfx']} n={miss[h]['n']}")
