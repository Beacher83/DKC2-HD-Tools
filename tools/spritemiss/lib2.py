import os, re, json, collections
SP = os.path.dirname(os.path.abspath(__file__))
DL = r"C:\Users\beach\Downloads"
PACKDIR = r"C:\Users\beach\OneDrive\Dokumente\Mesen2\HdPacks\Donkey Kong Country 2"

def load_names():
    return {int(k):v for k,v in json.load(open(os.path.join(SP,'names.json'))).items()}
def load_h2a():
    return json.load(open(os.path.join(SP,'hash2anim.json')))
def anim2h():
    a2h = collections.defaultdict(set)
    for h,aids in load_h2a().items():
        for a in aids: a2h[a].add(h)
    return a2h

_rxm = re.compile(r"^SPRMISS (\w) P(\d+) O(\d+) G(\d+) H([0-9A-F]{16}) T([0-9A-F]{64}) C([0-9A-F]{64})")
def load_miss(session=None, with_bytes=False):
    """session: None=alle, 1/2=nur diese Session"""
    out = {}
    s = 0
    for line in open(os.path.join(DL,'snes_hd_spritemiss.txt'), encoding='utf-8', errors='replace'):
        if line.startswith('==='): s += 1; continue
        m = _rxm.match(line)
        if not m: continue
        if session and s != session: continue
        ms,pal,ov,gfx,h,tb,cg = m.groups()
        e = out.setdefault(h, {'n':0,'pal':set(),'gfx':set(),'ms':collections.Counter(),'sess':set()})
        e['n']+=1; e['pal'].add(int(pal)); e['gfx'].add(int(gfx)); e['ms'][ms]+=1; e['sess'].add(s)
        if with_bytes: e.setdefault('bytes', tb); e.setdefault('cg', cg)
    return out

def load_cap(upto_session=None):
    """hash -> set(slots); optional nur bis Session n"""
    cap = collections.defaultdict(set)
    cgr = {}
    s = 0
    for line in open(os.path.join(DL,'snes_hd_spritecap.txt'), encoding='utf-8', errors='replace'):
        if line.startswith('==='): s += 1; continue
        if not line.startswith('SPR '): continue
        if upto_session and s > upto_session: break
        p = line.split(' ')
        h = p[1]; slot = int(p[2][1:])
        cap[h].add(slot)
        if len(p) > 4: cgr.setdefault((h,slot), p[4].strip()[1:])
    return cap, cgr

def load_packed():
    packed = collections.defaultdict(set)
    for fn in os.listdir(os.path.join(PACKDIR,'sprites')):
        if fn.lower().endswith('.png'):
            p = fn.split('_'); packed[p[0].upper()].add(p[1].split('.')[0])
    return packed
def load_refs():
    return json.load(open(os.path.join(SP,'refs.json')))
