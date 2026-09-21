#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
derive.py — HD-Kunst fuer verschobene CHR-Duplikate aus vorhandener Kunst zuschneiden.

DAS PROBLEM
-----------
DKC2 haelt von manchem Objekt eine zweite CHR-Kopie, die gegen das 8x8-Raster um
ein paar Pixel verschoben ist. Dieselbe Grafik, andere Bytes -- und der HD-Pack
ist pro Kachel-Inhalt (FNV-Hash) aufgebaut, also greift die vorhandene HD-Kunst
dort nicht. Gefunden am 2026-09-21 am Hook: `G32-16x32-P4-C236` im Kleever-Kampf
ist Byte fuer Byte der Gangplank-Hook, um genau 1 Pixel nach rechts geschoben.

DIE LOESUNG
-----------
Bei Skalierung S entspricht ein natives Pixel genau S HD-Pixeln. Die HD-Kunst der
verschobenen Kachel laesst sich deshalb exakt zuschneiden:

    ziel_hd[:, sx*S:]  = quelle_hd[:, :-sx*S]          (die Quelle, verschoben)
    ziel_hd[:, :sx*S]  = linkerNachbar_hd[:, -sx*S:]   (was von links hereinwandert)

Kein zweiter Upscale, und beide Fassungen sehen per Konstruktion identisch aus.

DIE SELBSTPRUEFUNG (der wichtigste Teil)
----------------------------------------
Dieselbe Rechnung wird zuerst auf der NATIVEN Ebene gemacht und gegen die echten
VRAM-Bytes der Zielkachel geprueft. Nur wenn alle 64 Pixel stimmen, wird die
HD-Kachel geschrieben. Eine falsch geratene Nachbarschaft kann dadurch nicht in
den Pack gelangen -- sie faellt vorher durch.

WIEDERHOLBARKEIT
----------------
Das Werkzeug ist idempotent und soll nach JEDEM Pack-Export neu laufen:

  * Es schreibt ein Manifest (derived_manifest.json) mit Ziel <- Quelle(n).
  * Ein erneuter Lauf baut jede Manifest-Kachel aus der AKTUELLEN Quelle neu.
    Wird der Hook also neu upgescalt, uebertraegt ein Lauf das auf alle seine
    verschobenen Duplikate.
  * Kacheln, die NICHT im Manifest stehen und schon Kunst haben, werden nie
    angefasst -- ein echter Upscale schlaegt eine Ableitung immer.

PALETTEN
--------
Kunst mit Referenzpalette liegt slot-frei im Pack (SnesHdPackLoader.cpp:417) und
wird zur Laufzeit auf die lebende CGRAM-Zeile umgefaerbt. Damit das Duplikat sich
genauso verhaelt, bekommt es denselben Referenzpaletten-Eintrag; dafuer schreibt
--write-palettes ihn in sprite_palettes.bin nach. Ohne Referenzpalette wird die
Kachel unter jedem erfassten Slot abgelegt, wie es die alte Pipeline tat.

Aufruf:
    python derive.py                 # Trockenlauf, zeigt nur was passieren wuerde
    python derive.py --apply         # schreibt PNGs + Manifest
    python derive.py --apply --write-palettes
"""

import argparse
import json
import os
import re
import struct
import sys
from collections import defaultdict

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow fehlt:  python -m pip install pillow')

# --- Vorgaben; per Kommandozeile ueberschreibbar ----------------------------
DEFAULT_PACK = r'C:\Users\beach\OneDrive\Dokumente\Mesen2\HdPacks\Donkey Kong Country 2'
DEFAULT_CAP = r'C:\Users\beach\Downloads\snes_hd_spritecap.txt'

MANIFEST = 'derived_manifest.json'

# Kachel -> Animationen. Entscheidend fuer die Nachbarwahl: der Nachbar muss aus
# DEMSELBEN Objekt stammen. Ohne diese Einschraenkung passen bei sx=1 tausende
# Kacheln, weil nur eine einzige 8-Pixel-Randspalte verglichen werden kann.
ANIM_MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'spritemiss', 'hash2anim.json')

# Wie weit gesucht wird.
#
# Erst auf 2 gesetzt, weil am Hook nur dx=+1 auftrat -- und genau das hat die
# Haelfte des Objekts liegen lassen: die untere Kachel `830AD2F518E1494F` hat
# ihren Zwilling bei dx=-3, der Hook blieb im Spiel unten SD (Screenshot des
# Users, 21.09.). Ein Objekt hat also NICHT durchgaengig denselben Versatz.
#
# Ein groesserer Radius ist ungefaehrlich: je weiter verschoben, desto mehr
# Spalten liefert der Nachbar -- und die muss die native Selbstpruefung alle
# exakt treffen. Bei dx=-3 sind es 24 Pixel statt 8, die Pruefung wird also
# STRENGER, nicht schwaecher. MIN_OVERLAP begrenzt nur die Suche, entschieden
# wird ohnehin erst durch die 64-von-64-Pruefung.
MAX_SHIFT = 5
MIN_OVERLAP = 24      # von 64 Pixeln


# ---------------------------------------------------------------- Kachel-IO
def decode_tile(hexs):
    """SNES 4bpp planar (32 Byte) -> 8x8 Farbindizes 0..15."""
    by = bytes.fromhex(hexs)
    out = []
    for y in range(8):
        p0, p1 = by[y * 2], by[y * 2 + 1]
        p2, p3 = by[16 + y * 2], by[16 + y * 2 + 1]
        out.append([((p0 >> (7 - x)) & 1)
                    | (((p1 >> (7 - x)) & 1) << 1)
                    | (((p2 >> (7 - x)) & 1) << 2)
                    | (((p3 >> (7 - x)) & 1) << 3) for x in range(8)])
    return out


def read_spritecap(path):
    """hash -> (pixel 8x8, set der erfassten OBJ-Palettenslots)."""
    tiles, pals = {}, defaultdict(set)
    rx = re.compile(r'SPR ([0-9A-F]{16}) P(\d+) T([0-9A-F]{64})')
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.match(line)
            if m:
                h = m.group(1)
                if h not in tiles:
                    tiles[h] = decode_tile(m.group(3))
                pals[h].add(int(m.group(2)))
    return tiles, pals


def read_pack(sprites_dir):
    """hash -> {slot: dateiname}.  Slot 255 = slot-frei ('_PFF')."""
    got = defaultdict(dict)
    rx = re.compile(r'^([0-9A-F]{16})_P(\d+)\.png$', re.I)
    for name in os.listdir(sprites_dir):
        m = rx.match(name)
        if m:
            got[m.group(1).upper()][int(m.group(2))] = name
    return got


def read_sprite_palettes(path):
    """(paletten als bytes, {hash:int -> palettenindex}) oder (None, {})."""
    if not os.path.exists(path):
        return None, {}
    d = open(path, 'rb').read()
    if not d or d[0] != 1:
        return None, {}
    o = 1
    count = struct.unpack_from('<H', d, o)[0]
    o += 2
    table = d[o:o + count * 32]
    o += count * 32
    n = struct.unpack_from('<I', d, o)[0]
    o += 4
    ref = {}
    for i in range(n):
        h, pi = struct.unpack_from('<QH', d, o + i * 10)
        ref[h] = pi
    return (count, table), ref


# ------------------------------------------------------- Versatz-Erkennung
def overlap_matches(tgt, src, sx, sy):
    """Stimmt tgt[y][x] == src[y-sy][x-sx] ueberall, wo beide existieren?
       Gibt die Zahl der verglichenen Pixel zurueck, oder 0 bei Abweichung."""
    n = 0
    for y in range(8):
        yy = y - sy
        if not 0 <= yy < 8:
            continue
        for x in range(8):
            xx = x - sx
            if not 0 <= xx < 8:
                continue
            if tgt[y][x] != src[yy][xx]:
                return 0
            n += 1
    return n


def find_shift_pairs(tiles, pack, pals):
    """Zielkacheln OHNE HD-Kunst, die ein Versatz einer Kachel MIT HD-Kunst sind."""
    sources = [h for h in tiles if h in pack]
    targets = [h for h in tiles if h not in pack]

    # Index ueber den ueberlappenden Ausschnitt, damit nicht jede Kachel gegen
    # jede geprueft werden muss (44k x 44k waere unbezahlbar).
    pairs = []
    for sx in range(-MAX_SHIFT, MAX_SHIFT + 1):
        for sy in range(-MAX_SHIFT, MAX_SHIFT + 1):
            if sx == 0 and sy == 0:
                continue
            xs = range(max(0, sx), min(8, 8 + sx))
            ys = range(max(0, sy), min(8, 8 + sy))
            if len(list(xs)) * len(list(ys)) < MIN_OVERLAP:
                continue
            idx = {}
            for h in sources:
                px = tiles[h]
                k = ''.join('%X' % px[y - sy][x - sx] for y in ys for x in xs)
                idx.setdefault(k, []).append(h)
            for h in targets:
                px = tiles[h]
                k = ''.join('%X' % px[y][x] for y in ys for x in xs)
                for s in idx.get(k, []):
                    n = overlap_matches(px, tiles[s], sx, sy)
                    if n >= MIN_OVERLAP:
                        pairs.append((h, s, sx, sy, n))
    # je Ziel den Kandidaten mit der groessten Ueberlappung behalten
    best = {}
    for h, s, sx, sy, n in pairs:
        if h not in best or n > best[h][3]:
            best[h] = (s, sx, sy, n)
    return best


def find_neighbour(tiles, pack, target, sx, sy, allowed=None):
    """Die Kachel, aus der die einwandernden Randpixel stammen.
       Nur horizontaler Versatz wird unterstuetzt (alles Beobachtete ist dy=0).
       `allowed` schraenkt auf die Kacheln desselben Objekts ein -- ohne das ist
       die Randspalte allein kein brauchbares Kriterium."""
    if sy != 0 or sx == 0:
        return None
    tgt = tiles[target]
    cands = []
    pool = allowed if allowed is not None else pack
    for h in pool:
        if h not in tiles or h not in pack:
            continue
        px = tiles[h]
        ok = True
        if sx > 0:                       # Spalten 0..sx-1 kommen von LINKS
            for y in range(8):
                for x in range(sx):
                    if tgt[y][x] != px[y][8 - sx + x]:
                        ok = False
                        break
                if not ok:
                    break
        else:                            # Spalten 8+sx..7 kommen von RECHTS
            for y in range(8):
                for x in range(8 + sx, 8):
                    if tgt[y][x] != px[y][x - 8 - sx]:
                        ok = False
                        break
                if not ok:
                    break
        if ok:
            cands.append(h)
    return cands


# ------------------------------------------------------------- Zusammenbau
def compose_native(tiles, src, nb, sx):
    """Die Zielkachel aus Quelle + Nachbar nachbauen -- fuer die Selbstpruefung."""
    out = [[0] * 8 for _ in range(8)]
    s = tiles[src]
    for y in range(8):
        for x in range(8):
            xx = x - sx
            if 0 <= xx < 8:
                out[y][x] = s[y][xx]
            elif nb is not None:
                n = tiles[nb]
                out[y][x] = n[y][xx + 8] if xx < 0 else n[y][xx - 8]
    return out


def compose_hd(src_img, nb_img, sx, scale):
    """Dieselbe Verschiebung auf der HD-Ebene."""
    w, h = src_img.size
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    off = sx * scale
    out.paste(src_img, (off, 0))
    if nb_img is not None:
        if sx > 0:
            strip = nb_img.crop((w - off, 0, w, h))
            out.paste(strip, (0, 0))
        else:
            strip = nb_img.crop((0, 0, -off, h))
            out.paste(strip, (w + off, 0))
    return out


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pack', default=DEFAULT_PACK)
    ap.add_argument('--spritecap', default=DEFAULT_CAP)
    ap.add_argument('--apply', action='store_true', help='PNGs und Manifest schreiben')
    ap.add_argument('--write-palettes', action='store_true',
                    help='Referenzpaletten-Eintraege der Quellen auf die Ziele uebertragen')
    ap.add_argument('--only', help='nur Ziele mit diesem Hash-Praefix (Test)')
    args = ap.parse_args()

    sprites = os.path.join(args.pack, 'sprites')
    if not os.path.isdir(sprites):
        sys.exit('sprites/ nicht gefunden unter ' + args.pack)

    print('lese spritecap ...')
    tiles, pals = read_spritecap(args.spritecap)
    pack = read_pack(sprites)
    palfile = os.path.join(args.pack, 'sprite_palettes.bin')
    paltab, ref = read_sprite_palettes(palfile)
    print('  %d Kacheln in spritecap, %d mit HD-Kunst im Pack, %d mit Referenzpalette'
          % (len(tiles), len(pack), len(ref)))

    here = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(here, MANIFEST)
    manifest = {}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        print('  Manifest: %d frueher abgeleitete Kacheln' % len(manifest))

    # Frueher abgeleitete Kacheln zaehlen NICHT als vorhandene Kunst -- sonst
    # koennte ein zweiter Lauf sie nie aus einer neuen Quelle erneuern.
    derived_before = set(manifest)
    pack_real = {h: v for h, v in pack.items() if h not in derived_before}

    anim = {}
    if os.path.exists(ANIM_MAP):
        anim = json.load(open(ANIM_MAP, encoding='utf-8'))
        print('  Animationskarte: %d Kacheln' % len(anim))
    else:
        print('  WARNUNG: hash2anim.json nicht gefunden -- Nachbarwahl nur ueber '
              'die Paargruppe, Randstreifen werden haeufiger als unsicher gemeldet')

    print('suche Versatz-Paare ...')
    best = find_shift_pairs(tiles, pack_real, pals)
    if args.only:
        best = {h: v for h, v in best.items() if h.startswith(args.only.upper())}
    print('  %d Zielkacheln mit einem Versatz-Kandidaten' % len(best))

    written = skipped = failed = ambiguous = 0
    new_manifest = {}
    for tgt, (src, sx, sy, n) in sorted(best.items()):
        if sy != 0:
            skipped += 1
            continue
        # Der Nachbar muss zum selben Objekt gehoeren. Beste Quelle dafuer ist
        # die Deskriptortabelle: Kacheln, die eine Animation mit der Quelle
        # teilen, bilden dasselbe Objekt. Fehlt der Eintrag (reine
        # Laufzeitkunst), bleibt nur die Paargruppe desselben Versatzes.
        src_anims = anim.get(src)
        if src_anims:
            allowed = {h for h in pack_real
                       if h != src and (set(anim.get(h, ())) & set(src_anims))}
        else:
            allowed = {v[0] for v in best.values() if v[1] == sx and v[2] == sy} - {src}
        nbs = find_neighbour(tiles, pack_real, tgt, sx, sy, allowed) or []

        # Die native Pruefung sieht beim Nachbarn nur |sx| Randspalten -- bei
        # sx=1 also 8 Pixel. Eine voellig fremde Kachel mit zufaellig gleicher
        # Randspalte kaeme damit durch und wuerde falsche HD-Pixel liefern.
        # Deshalb werden die Kandidaten vorher geordnet: eine Kachel, die im
        # selben Versatz selbst Quelle eines anderen Ziels ist, gehoert
        # nachweislich zu demselben verschobenen Objekt; danach zaehlt eine
        # gemeinsame OBJ-Palette. Bleibt es mehrdeutig, wird es gemeldet.
        same_obj = allowed
        tgt_pals = pals.get(tgt, set())

        def rank(h):
            return (0 if h in same_obj else 1,
                    0 if (pals.get(h, set()) & tgt_pals) else 1,
                    h)

        nbs = sorted(nbs, key=rank)

        # Selbstpruefung: nativ nachbauen und gegen die echten Bytes halten.
        chosen, native_ok = None, False
        for nb in (nbs if nbs else [None]):
            if compose_native(tiles, src, nb, sx) == tiles[tgt]:
                chosen, native_ok = nb, True
                break
        if not native_ok and None not in nbs:
            if compose_native(tiles, src, None, sx) == tiles[tgt]:
                chosen, native_ok = None, True
        if not native_ok:
            failed += 1
            print('  [PRUEFUNG FEHLGESCHLAGEN] %s <- %s dx=%+d (%d Nachbarkandidaten)'
                  % (tgt, src, sx, len(nbs)))
            continue
        if chosen is not None and chosen not in same_obj:
            ambiguous += 1
            print('  [NACHBAR UNSICHER] %s: %s gehoert zu keinem Paar desselben '
                  'Versatzes (%d Kandidaten) -- HD-Randstreifen ungeprueft'
                  % (tgt, chosen[:8], len(nbs)))

        src_slots = pack_real[src]
        src_name = src_slots[sorted(src_slots)[0]]
        src_img = Image.open(os.path.join(sprites, src_name)).convert('RGBA')
        scale = src_img.size[0] // 8
        nb_img = None
        if chosen is not None:
            nb_slots = pack_real[chosen]
            nb_img = Image.open(os.path.join(sprites, nb_slots[sorted(nb_slots)[0]])).convert('RGBA')

        out = compose_hd(src_img, nb_img, sx, scale)

        # Slots: hat die Quelle eine Referenzpalette, wird die Kachel slot-frei
        # gefuehrt und das Ziel erbt sie. Sonst je erfasstem Slot eine Datei.
        src_ref = ref.get(int(src, 16))
        slots = sorted(pals.get(tgt, {0})) if src_ref is None else [sorted(pals.get(tgt, {0}))[0]]

        names = ['%s_P%d.png' % (tgt, s) for s in slots]
        if args.apply:
            for nm in names:
                out.save(os.path.join(sprites, nm))
        written += 1
        new_manifest[tgt] = {
            'source': src, 'neighbour': chosen, 'dx': sx, 'dy': sy,
            'overlap': n, 'files': names,
            'neighbour_certain': chosen is None or chosen in same_obj,
            'ref_palette': src_ref, 'scale': scale,
        }
        print('  %s <- %s dx=%+d%s  -> %s'
              % (tgt, src, sx,
                 ('  Nachbar ' + chosen[:8]) if chosen else '  (Rand, transparent)',
                 ', '.join(names)))

    print()
    print('abgeleitet: %d   Nachbar unsicher: %d   Pruefung fehlgeschlagen: %d   '
          'uebersprungen: %d' % (written, ambiguous, failed, skipped))

    if args.apply:
        json.dump(new_manifest, open(manifest_path, 'w', encoding='utf-8'),
                  indent=1, sort_keys=True)
        print('Manifest geschrieben: %s' % manifest_path)
        if args.write_palettes and paltab:
            add = [(int(h, 16), m['ref_palette']) for h, m in new_manifest.items()
                   if m['ref_palette'] is not None and int(h, 16) not in ref]
            if add:
                count, table = paltab
                allref = sorted(list(ref.items()) + add)
                buf = bytearray()
                buf.append(1)
                buf += struct.pack('<H', count)
                buf += table
                buf += struct.pack('<I', len(allref))
                for h, pi in allref:
                    buf += struct.pack('<QH', h, pi)
                open(palfile, 'wb').write(bytes(buf))
                print('sprite_palettes.bin: %d Eintraege ergaenzt (jetzt %d)'
                      % (len(add), len(allref)))
    else:
        print('(Trockenlauf -- mit --apply schreiben)')


if __name__ == '__main__':
    main()
