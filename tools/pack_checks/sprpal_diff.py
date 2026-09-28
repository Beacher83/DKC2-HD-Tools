# Diff two sprite_palettes.bin files: which content hashes changed their reference palette?
import sys, struct
def load(p):
    b = open(p, 'rb').read(); o = 0
    ver = b[o]; o += 1
    pc = struct.unpack_from('<H', b, o)[0]; o += 2
    pals = [tuple(struct.unpack_from('<16H', b, o + i*32)) for i in range(pc)]; o += pc*32
    ec = struct.unpack_from('<I', b, o)[0]; o += 4
    ent = {}
    for i in range(ec):
        h, pi = struct.unpack_from('<QH', b, o); o += 10
        ent[h] = pals[pi]
    return ver, pals, ent
_, po, eo = load(sys.argv[1]); _, pn, en = load(sys.argv[2])
print(f'alt: {len(po)} Paletten, {len(eo)} Eintraege | neu: {len(pn)} Paletten, {len(en)} Eintraege')
common = eo.keys() & en.keys()
chg = [h for h in common if eo[h] != en[h]]
print(f'gemeinsam {len(common)}, Palette geaendert {len(chg)}, nur alt {len(eo.keys()-en.keys())}, nur neu {len(en.keys()-eo.keys())}')
open(sys.argv[3], 'w').write('\n'.join('%016X' % h for h in sorted(chg)))
from collections import Counter
pairs = Counter((eo[h], en[h]) for h in chg)
for (a, b), n in pairs.most_common(8):
    print(f'{n:5d}x  alt {" ".join("%04X" % c for c in a[:8])}...')
    print(f'        neu {" ".join("%04X" % c for c in b[:8])}...')
