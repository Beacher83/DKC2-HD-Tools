import os, sys, json, collections
from PIL import Image, ImageDraw
SP = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(SP,'lib2.py')).read())
exec(open(os.path.join(SP,'objrender.py')).read().split("GR=[int")[0])
cand = json.load(open(os.path.join(SP,'cand.json')))
seen={}
cells=[]
for g,n,m in cand:
    r = render(g)
    if not r: continue
    img, placed, D = r
    key = tuple(sorted(p[0] for p in placed))
    if key in seen: continue
    seen[key]=g
    cells.append((g,img,n,m))
print(f"{len(cells)} eindeutige Objekte")
COLS=9; CW=112; CH=112
out = Image.new('RGB',(COLS*CW, ((len(cells)+COLS-1)//COLS)*CH),(18,18,22))
dr = ImageDraw.Draw(out)
for i,(g,img,n,m) in enumerate(cells):
    cx=(i%COLS)*CW; cy=(i//COLS)*CH
    s=img
    if s.size[0]>CW-4 or s.size[1]>CH-16:
        f=min((CW-4)/s.size[0], (CH-16)/s.size[1]); s=s.resize((max(1,int(s.size[0]*f)),max(1,int(s.size[1]*f))), Image.NEAREST)
    out.paste(s,(cx+(CW-s.size[0])//2, cy+12))
    dr.text((cx+3,cy+1), f"{g:04X} {m}/{n}", fill=(200,200,90))
out.save(os.path.join(SP,'sheet.png'))
print("Bild:", out.size)
json.dump([c[0] for c in cells], open(os.path.join(SP,'sheet_order.json'),'w'))
