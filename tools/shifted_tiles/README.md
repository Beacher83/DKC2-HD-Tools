# shifted_tiles — HD-Kunst für verschobene CHR-Duplikate

## Wofür

DKC2 hält von manchen Objekten eine **zweite CHR-Kopie, die gegen das 8×8-Raster um ein
paar Pixel verschoben ist**. Optisch dieselbe Grafik, aber andere Bytes — und weil der
HD-Pack pro Kachel-Inhalt (FNV-Hash) aufgebaut ist, greift die vorhandene HD-Kunst dort
nicht. Das Objekt bleibt SD, obwohl seine Kunst längst im Pack liegt.

Gefunden am 2026-09-21 am **Hook**: die Haken über der Lava im Kleever-Kampf sind Byte für
Byte der Hook aus Gangplank Galley, **um genau 1 Pixel nach rechts geschoben**.

```
dx = −1, dy = 0 :  56 überlappende Pixel, 100,0 % identisch
dx =  0          :  64 überlappende Pixel,  43,8 % identisch
```

## Wie es funktioniert

Bei Skalierung S entspricht ein natives Pixel genau S HD-Pixeln (bei 4× also 4). Die
HD-Kunst der verschobenen Kachel lässt sich deshalb **exakt zuschneiden** statt neu
hochzurechnen:

```
ziel_hd[:, sx*S:] = quelle_hd[:, :-sx*S]         # die Quelle, um sx*S verschoben
ziel_hd[:, :sx*S] = linkerNachbar_hd[:, -sx*S:]  # was von links hereinwandert
```

Beide Fassungen sehen danach **per Konstruktion** identisch aus, und es kostet keine
Upscale-Runde.

### Die Selbstprüfung ist der Kern

Dieselbe Rechnung läuft zuerst auf der **nativen** Ebene und wird gegen die echten
VRAM-Bytes der Zielkachel gehalten. Nur wenn **alle 64 Pixel** stimmen, wird geschrieben.
Eine falsch geratene Nachbarschaft kann dadurch nicht in den Pack gelangen — im Lauf vom
21.09. sind so 520 Kandidaten durchgefallen und 19 durchgekommen.

### Die Nachbarwahl braucht die Objektzugehörigkeit

Bei `sx = 1` vergleicht die native Prüfung beim Nachbarn nur **eine 8-Pixel-Randspalte**.
Das allein ist wertlos: im ersten Entwurf passten **3.784** Kacheln. Deshalb wird der
Nachbar auf Kacheln eingeschränkt, die laut `../spritemiss/hash2anim.json` eine
**Animation mit der Quelle teilen** — also zum selben Objekt gehören. Damit wurde die Wahl
beim Hook eindeutig und korrekt (`0D77F83A`, eine der sieben Hook-Kacheln).

Fehlt der Animationseintrag (reine Laufzeitkunst), bleibt nur die Paargruppe desselben
Versatzes; solche Fälle werden als **`[NACHBAR UNSICHER]`** gemeldet, weil der
HD-Randstreifen dann ungeprüft ist.

## Wiederholbarkeit — nach jedem Pack-Export neu laufen lassen

Die abgeleiteten Kacheln sind gewöhnliche PNGs. **Wird eine Quelle neu upgescalt, muss die
Ableitung neu gerechnet werden.** Dafür führt das Werkzeug `derived_manifest.json`
(Ziel ← Quelle, Nachbar, Versatz, Dateien).

- Ein erneuter Lauf baut jede Manifest-Kachel aus der **aktuellen** Quelle neu.
  Lädst du also eine neue HD-Fassung des Gangplank-Hooks hoch, überträgt ein Lauf sie auf
  alle seine verschobenen Duplikate.
- Kacheln, die **nicht** im Manifest stehen und bereits Kunst haben, werden nie angefasst
  — ein echter Upscale schlägt eine Ableitung immer.
- Der Viewer-Export schreibt `sprite_palettes.bin` neu; mit `--write-palettes` werden die
  Referenzpaletten-Einträge der Quellen wieder auf die Ziele übertragen.

**Fester Platz im Ablauf:** Upscale → Import → Pack exportieren → **`derive.py --apply
--write-palettes`** → einsetzen.

## Paletten

Kunst mit Referenzpalette liegt slot-frei im Pack (`SnesHdPackLoader.cpp:417` →
`SnesHdSpriteAnyPalette`) und wird zur Laufzeit auf die lebende CGRAM-Zeile umgefärbt.
Damit sich das Duplikat genauso verhält, erbt es denselben Referenzpaletten-Eintrag
(`--write-palettes`). Ohne Referenzpalette wird die Kachel unter jedem erfassten Slot
abgelegt, wie es die alte Pipeline tat.

## Aufruf

```bash
python derive.py                              # Trockenlauf, zeigt nur was passieren würde
python derive.py --only C236                  # nur ein Ziel, zum Prüfen
python derive.py --apply --write-palettes     # schreibt PNGs, Manifest und Paletten
```

Optionen: `--pack <HdPack-Ordner>`, `--spritecap <snes_hd_spritecap.txt>`.

## ⚠ Ein Objekt hat NICHT durchgängig denselben Versatz

Der erste Entwurf stand auf `MAX_SHIFT = 2`, weil am Hook nur `dx=+1` auftrat — eine
Verallgemeinerung aus einem einzigen Beispiel. Im Spiel blieb der Hook daraufhin **unten zu
25 % SD** (Screenshot des Users, 21.09.): die untere Kachel `830AD2F518E1494F` hat ihren
Zwilling bei **`dx=−3`** und fiel durch das Raster.

Der enge Radius war auch aus dem falschen Grund gewählt. Größere Versätze sind **nicht**
unsicherer: je weiter verschoben, desto mehr Spalten liefert der Nachbar — und die muss die
native Selbstprüfung alle exakt treffen. Bei `dx=−3` sind es 24 Pixel statt 8, die Prüfung
wird also **strenger**. `MIN_OVERLAP` begrenzt nur die Suche; entschieden wird ohnehin erst
durch die 64-von-64-Prüfung. Seitdem: `MAX_SHIFT = 5`, `MIN_OVERLAP = 24`.

## Stand 2026-09-21 (Lauf über den ganzen Pack, angewandt)

| | |
|---|---|
| abgeleitet (Selbstprüfung bestanden, Nachbar sicher) | **19** |
| Selbstprüfung fehlgeschlagen (nicht geschrieben) | 520 |
| übersprungen (vertikaler Versatz, s. u.) | 2.285 |

Sechs der sieben Hook-Kacheln des Kleever-Kampfs:

```
C2368B86616E9F60 <- 6D34E59BBCEBD3DE dx=+1   Nachbar 0D77F83A
D40681AD2F80EC0D <- 0D77F83A30A48735 dx=+1   Nachbar 0EC78EA4
47CC0BB72F529E54 <- 0EC78EA4FD9B3DE7 dx=+1   Nachbar 0D77F83A
A1B38551AA40D609 <- 286773B77EC44DDD dx=+1   Nachbar 6D34E59B
360C6F92275BE879 <- 3F8C0CF12358C3B6 dx=-2   Nachbar 0EC78EA4
5EC004BB611F7CC5 <- 830AD2F518E1494F dx=-3   (Rand, transparent)
```

Die siebte, `6AA148E3AD83BEA2`, hat **keinen Zwilling in spritecap** — auch nicht mit
Spiegelung oder Versatz bis ±5. Entweder benutzt das Kleever-Objekt sie nicht, oder ihr
Gegenstück wurde nie erfasst und ist dem Werkzeug damit unsichtbar. Dagegen hilft nur ein
Lauf, der sie in spritecap bringt, gefolgt von einem erneuten `derive.py`.

## Bekannte Grenzen

- **Vertikaler Versatz wird nicht unterstützt — und er kommt vor.** Die achte Kachel des
  Kleever-Hooks, `71DE2AEEFF1DD88A`, sitzt bei **dx=+2, dy=−3** auf `6AA148E3AD83BEA2`
  (nativ 64/64 geprüft) und wurde am 21.09. von Hand eingetragen, weil das Werkzeug jeden
  vertikalen Versatz überspringt. Wer das ausbaut: die Ableitung ist dieselbe Rechnung, nur
  mit `oy = dy*S` zusätzlich zu `ox = dx*S`, und die Selbstprüfung bleibt das Sicherheitsnetz.
- **Vertikaler Versatz wird nicht unterstützt.** 2.285 Kandidaten mit `dy ≠ 0` werden
  übersprungen. Ein voller 2D-Test über die sieben Hook-Kacheln (21.09.) fand darunter
  **keinen einzigen Kandidaten mit mehr als 30 überlappenden Pixeln** — für dieses Objekt
  ist vertikaler Versatz also reines Rauschen. Ob das allgemein gilt, ist damit nicht
  gezeigt; sieben Kacheln sind keine Stichprobe. Derselbe Ansatz funktioniert dort genauso (Nachbar oben/unten statt
  links/rechts), es ist nur noch nicht gebaut — und ob es echte Duplikate sind oder
  Zufallstreffer kleiner Kacheln, sagt erst die Selbstprüfung. Nach der Erfahrung mit
  `MAX_SHIFT` wäre das der nächste blinde Fleck, den ein Objekt ausnutzen kann.
- **Kombinierter Versatz mit Spiegelung** wird nicht gesucht.
- Die Suche stützt sich auf `spritecap`: eine Kachel, die noch nie erfasst wurde, kann
  weder Quelle noch Ziel sein.
