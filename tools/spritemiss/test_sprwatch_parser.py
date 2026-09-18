# Portiert 1:1 aus der eingefuegten C++-Schleife, um den Parser gegen echte Eingaben zu pruefen
def parse(env, MaxWatch=8):
    watch=[]; q=0
    while q < len(env) and len(watch) < MaxWatch:
        h=0; n=0
        while q < len(env) and env[q] != ',':
            c=env[q]; q+=1
            v = ord(c)-48 if '0'<=c<='9' else (ord(c)-65+10 if 'A'<=c<='F' else (ord(c)-97+10 if 'a'<=c<='f' else -1))
            if v>=0: h=((h<<4)|v) & 0xFFFFFFFFFFFFFFFF; n+=1
        if n>0: watch.append(h)
        if q < len(env) and env[q]==',': q+=1
    return [f"{x:016X}" for x in watch]
tests = [
 ("E563D7702FE967CC", ["E563D7702FE967CC"]),
 ("E563D7702FE967CC,38E78F2E2A1400EC", ["E563D7702FE967CC","38E78F2E2A1400EC"]),
 ("e563d7702fe967cc", ["E563D7702FE967CC"]),
 ("E563D7702FE967CC,", ["E563D7702FE967CC"]),
 (",E563D7702FE967CC", ["E563D7702FE967CC"]),
 ("0x38E78F2E2A1400EC", ["38E78F2E2A1400EC"]),          # 'x' wird ignoriert, fuehrende 0 schadet nicht
 ("A,B,C,D,E,F,1,2,3,4", ["000000000000000A","000000000000000B","000000000000000C","000000000000000D","000000000000000E","000000000000000F","0000000000000001","0000000000000002"]),
 ("", []),
]
ok=True
for env, exp in tests:
    got=parse(env)
    good = got==exp
    ok &= good
    print(("OK  " if good else "FEHLER ") + repr(env) + " -> " + str(got) + ("" if good else f"  erwartet {exp}"))
print("\nalle Faelle bestanden" if ok else "\nFEHLER im Parser")
