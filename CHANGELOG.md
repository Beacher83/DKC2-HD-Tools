# Changelog — DKC2-HD-Tools Viewer & Mesen2 SNES HD Fork

## [2026-07-20b] — S6b Schritt 2: Anim-Frame-Klassifikation

- **`parseBgCap()` klassifiziert jetzt** jede Kachel: ein CHR-DMA-Anim streamt
  mehrere distinkte Tiles über EINE VRAM-Adresse, also ist ein
  `(gfx,layer,addr)`-Slot mit ≥2 distinkten Hashes eine Animation (jeder Hash =
  ein Frame), ein Slot mit einem Hash eine statische Coverage-Lücke. Jeder
  Entry trägt `isAnim` + `frameCount`. **Kein Katalog-Lookup nötig** — die
  Multiplizität steckt in den aufgezeichneten Daten selbst.
- Button zeigt „BG-Anim ✓ `<frames>`/`<addrs>`", Tooltip + Console listen
  Anim-Frames/-Adressen und statische Lücken.
- Validiert am echten Dump: 1081 Anim-Frames auf 142 Adressen + 2544 statische
  Lücken. G29 (Gusty) 106 Frames/17 Adressen — deckt sich mit der
  S6a-Prognose (~90 Frames / 16 Adressen $7010-$7110).

## [2026-07-20] — S6b Schritt 1: bgcap-Ingestion (BG-Anim-Tiles, Grundlage)

Erster Baustein für hash-adressierte animierte BG-Kacheln (CHR-DMA-Frames wie
Gusty-Wind-Blätter, Wasser/Lava-Zyklen). Quelle ist der Mesen-S6a-Recorder
`snes_hd_bgcap.txt`.

- **„BG-Anim"-Button** (Katalog-Toolbar, neben Spritecap): lädt
  `snes_hd_bgcap.txt`. `parseBgCap()` parst die `BGA`-Zeilen
  (`G<gfx> L<layer> P<pal> A<addr> H<hash16> T<bytes> C<cgram>`), verifiziert
  jede gegen ihre eigenen Tile-Bytes per FNV-1a (4bpp L0/L1 = 32 Byte/16
  Farben, 2bpp L2 = 16 Byte/4 Farben), dedupt auf distinkte Hashes und legt
  pro Tile `{gfx, layer, pal, addr, hash, bytes, cgram}` in `bgCapEntries` ab.
  Button zeigt „BG-Anim ✓ N" (grün) + Console-Breakdown pro Gfxset/Layer.
- Verifiziert gegen echten Recorder-Dump: 7715/7715 Zeilen, 0 Hash-Fehler.

**Ausstehend (nächste Schritte S6b):** (2) Klassifikation Anim-Frame vs.
Coverage-Lücke — Basis-Tile an `addr` via `tileNum=(addr−chrBase)/16` im
Katalog suchen, dabei BG1↔BG2-Retry nachbilden (Recorder probt exakten Key
ohne Retry → L1-„Lücken" teils falsch-positiv). (3) SD-Export in
`exportCatalogAsZip`: Tile aus `bytes`+`cgram` decodieren, Kontext-Padding vom
Basis-Tile (`bestNeighborhood(basePartId)`), Dateiname
`animtile_{hash16}_L{layer}_P{pal}.png` + Manifest-Sektion. (4) Upscale-Rückweg
→ `exportAsTexturePack` schreibt `h{hash16}_P{pal}.png` nach
`bg/bg{layer+1}/gfxset_XX/`. (5) Mesen-Loader `ParseTileFilename`: `h`-Präfix
+ 16 Hex → `Key.ContentHash` direkt.

## [2026-07-19d] — S5b-2: Sprite-Slicing im Pack-Export + Spritecap-Ingestion (HD-Sprite-Pipeline KOMPLETT)

Der letzte Baustein der HD-Sprite-Pipeline (Mesen S3/S4 rendern bereits):

- **„Spritecap"-Button** (Katalog-Toolbar, neben Clear HD): lädt
  `snes_hd_spritecap.txt` (Mesen-S5a-Recording). Jede Zeile wird gegen ihre
  eigenen Tile-Bytes hash-verifiziert; Ergebnis: hash→Set(palette-Slots).
  Button zeigt „Spritecap ✓ N" (grün).
- **`exportAsTexturePack()`: neue Sprite-Sektion** — schneidet die per
  „Import HD" geladenen HD-Sprite-Frames (Manifest v2, `tiles[]`) in
  8×-Scale-Zellen und schreibt `sprites/{hash16}_P{pal}.png` für jedes im
  Spritecap aufgezeichnete (hash,pal)-Paar. Zellposition =
  `(tileX + frameOffsetX) × scale` im gepaddeten Frame; voll transparente
  Zellen und scaleFactor ≠ 4 werden übersprungen. Dedup über alle Frames
  (erster Treffer gewinnt). Console-Summary: exportiert / ohne
  Runtime-Palette / ohne tiles[].
- `importHDSpritePack()` speichert dafür jetzt pro Frame `meta`
  (offsetX/offsetY + tiles[] aus dem Manifest).
- Ohne geladenes Spritecap läuft der Export mit Hinweis ohne Sprites weiter.
- Pack-manifest.json: neues Feld `total_sprite_tiles`; Erfolgsmeldung
  zeigt die Sprite-Tile-Zahl.

**Workflow erster HD-Sprite-Test:** Auswahl-Export (z.B. DD_Idle/Walk/Run)
→ upscalen (4×) → ZIP mit manifest re-packen → „Import HD" → „Spritecap"
laden → Container → „Texture Pack" → nach HdPacks entpacken → Mesen (S4.0+)
neu starten → Diddy ist HD.

## [2026-07-19c] — Sprite-Galerie: Export-Auswahl (Checkboxen)

Der Sprite-Export nahm bisher immer ALLE sichtbaren Sprites (787 Stück,
10k+ Dateien) — für gezielte Upscale-Batches (z.B. nur Diddy+Dixie) gab es
keine Auswahl. Neu:

- **Checkbox auf jeder Galerie-Karte** (oben links, grüner Rahmen bei
  Auswahl); Kartenklick bleibt Details.
- Toolbar: **„☑ Sichtbare wählen"** (fügt alle aktuell gefilterten Karten
  zur Auswahl hinzu — Auswahl bleibt über Filterwechsel erhalten, dadurch
  additiv kombinierbar: Filter „DD_" → wählen → Filter „DX_" → wählen),
  **„✕ Leeren"**, Zähler.
- Export-Button zeigt **„Export Auswahl (N)"**, sobald etwas gewählt ist,
  und exportiert dann GENAU die Auswahl (unabhängig vom aktuellen Filter);
  ohne Auswahl unverändert alle sichtbaren.
- ZIP-/Ordnerstruktur bewusst UNVERÄNDERT (Upscale-Pipeline des Users
  verarbeitet sie — sie braucht nur lange; kleinere Auswahl-Exporte sind
  die Antwort darauf).

## [2026-07-19b] — S5: Sprite-Export trägt Frame→Tile-Hashes (HD-Sprite-Pipeline)

Vorbereitung für hash-adressierte HD-Sprites (Mesen S3/S4 sind live):

- `renderSpriteFromDescriptor()` sammelt jetzt pro gerendertem Frame alle
  platzierten 8×8-OBJ-Tiles als `{x, y, hash}` (canvas-relativ, ungeflippt);
  `hash` = FNV-1a über die 32 ROM-Bytes des Tiles = exakt der Content-Hash,
  den Mesen zur Laufzeit aus OBJ-VRAM berechnet (VRAM = wörtliche ROM-Kopie,
  per Byte-Suche bewiesen). `renderCompositeFrame()` merged die Listen der
  Composite-Teile in Composite-Koordinaten.
- **Export Sprites ZIP (Manifest v2):** jeder Frame-Eintrag enthält
  `tiles: [{x, y, hash}]` (frame-relativ; für die gepaddete PNG offsetX/Y
  addieren). Damit kann der spätere Pack-Export upscaled Frames in
  hash-adressierte 32×32-Zellen (`sprites/{hash}_P{pal}.png`) schneiden.
- Mesen-Gegenstück (Build "S5a"): Sprite-Capture-Recording nach
  `%USERPROFILE%\Downloads\snes_hd_spritecap.txt` — alle im Spiel gesehenen
  (hash, palette)-Paare inkl. Tile-Bytes + OBJ-CGRAM-Farben; liefert dem
  Pack-Export die echten Palette-Slots. Ausstehend: Pack-Export-Slicing +
  Spritecap-Ingestion (nächster Schritt).

## [2026-07-19] — Edge-Seam-Cleanup im Pack-Export (Issue-S-Rest) + echtes Nachbarschafts-Padding im SD-Export + Export-Fortschrittsanzeige

### 0. Fortschrittsanzeige für den Mesen-Pack-Export

Der Pack-Export dauert inzwischen spürbar; ohne offene Console sah es aus,
als passiere nichts. Neu: fixes Overlay unten-mittig („Mesen2 HD Pack
Export") mit Statustext + Fortschrittsbalken über alle Phasen (BG1 pro
Set/Tile, BG2/Wall/BG3/cmFg, hashes.bin, fingerprints.bin, palettes.bin,
ZIP-Kompression mit Prozent). Die schweren synchronen Schleifen yielden
periodisch an den Browser (`setTimeout(0)`), damit das Overlay tatsächlich
neu zeichnet; Fehler/Abbruch blendet es über `finally` zuverlässig aus.

**Status Issue-S-Rest nach Test-Runde 2:** Hysterese entfernt mehr Saum-Pixel
(Set 37: 1283 → 2469 px), sichtbares Ergebnis in Lockjaw/Lava aber ~unverändert
— Rest ist vermutlich art-/upscaling-getrieben. Auf User-Entscheidung
ZURÜCKGESTELLT (Schönheitsfehler); Kandidat für eine verfeinerte
Upscaling-Methode statt Export-Nachbearbeitung.

### 0.5 Fingerprint-Auswahl bevorzugt STABILE Tiles (Gusty-Vorbereitung)

BG1-Hash-Einträge tragen jetzt ein `stable`-Flag: VRAM-Bytes identisch zu
chrRawData (ROM) = Tile wird zur Laufzeit nicht per DMA überschrieben. Die
fingerprints.bin-Auswahl sortiert stabile Tiles nach vorn und warnt, wenn
instabile Referenz-Tiles gewählt werden müssen. Hintergrund: Gusty Glades
Wind-DMA (vblank 15, nicht in animDefs modelliert) ändert VRAM-Regionen
laufend — ein Fingerprint auf einem Wind-Tile würde DetectActiveGfxset
meistens fehlschlagen lassen, und mit Mesens P4.2-Strict-Scoping bliebe das
ganze Set dann SD.

### 1. Edge-Seam-Cleanup (`exportAsTexturePack()`) — automatisch bei jedem Export

Der KI-Upscaler hat an Kanten zwischen zwei Farbclustern (grüne Algen ↔
braunes Holz) opake gelb-olive Blend-Säume in die Tiles eingebacken —
Pixel, deren Farbton in einem Band liegt, das die nativen Farben des Tiles
nie belegen. Unter Wasser macht der Sub-Operand-ADD daraus Leuchtrahmen.
Bisher wurden 4 Tiles manuell gefixt (29a0/29b0/3540/3590_P07), die jeder
Re-Export wieder überschrieb — deshalb sitzt der Fix jetzt im Export selbst:

- **Erkennung pro nativem Subtile, palettengetrieben — KEIN pauschaler
  Farbfilter:** Ein Pixel gilt nur dann als Saum, wenn es (a) in RGB weit
  von JEDER Palettenfarbe entfernt ist, die dieses Subtile laut `chrRawData`
  tatsächlich benutzt (Farben aus der Auto-Detect-Referenzpalette), UND
  (b) im Farbton weit von jeder gesättigten benutzten Farbe entfernt liegt
  (Schwellen: RGB-Distanz > 28, Hue-Distanz > 14°, Sättigung ≥ 40).
  Legitimes Gelb (Bananen, KONG-Buchstaben) ist sicher: es steht in der
  benutzten Palette des eigenen Tiles.
- **Ersetzung:** Saum-Pixel bekommen die Farbe des nächstgelegenen
  Nicht-Saum-Pixels (gleiche Methode wie der manuelle Fix vom 2026-07-17).
- **Nachschärfung nach erstem User-Test ("deutlich besser, aber Rest-Säume"):**
  (a) Hysterese-Wachstum — Pixel NEBEN erkannten Saum-Pixeln werden mit
  entspannten Schwellen (RGB > 18, Hue > 10°, max. 6 Iterationen) mitgereinigt;
  fängt den Blend-Restring um jeden Saum, ohne die globalen Schwellen
  anzuheben (Bananen-Risiko). (b) Guard gelockert: EINE gesättigte benutzte
  Farbe reicht (vorher ≥ 2 — Tiles mit nur einem Farbcluster wurden komplett
  übersprungen, obwohl fremde Säume vom gepaddeten Nachbarn auch dort
  vorkommen). (c) Basis-Hue-Schwelle 14° → 16°.
- **Voraussetzung dafür:** Die Referenzpaletten-Auflösung (Auto-Detect)
  wurde aus der `palettes.bin`-Sektion nach vorn in die Set-Schleife gezogen
  (`resolveReferencePalette()`); `palettes.bin` nutzt dieselben aufgelösten
  Einträge (kein doppeltes Scoring, Verhalten unverändert).
- Console: `[seam-cleanup] gfxset NN: scrubbed X seam px in Y sub-tiles`
  bzw. Warnung, wenn Cleanup mangels Referenzpalette/chrRawData übersprungen
  wurde. Gilt für BG1-Subtiles (dort trat Issue S auf); BG2/Wall unverändert.

### 2. Padding aus echten Vorkommen (`exportCatalogAsZip()`)

Die 96×96-`tile_XXXX_padded.png`s für den Upscaler umgaben das Zentrum
bisher mit dem *pro Richtung* statistisch häufigsten Nachbarn (Ecken sogar
zweistufig geraten) — die vier Seiten konnten aus vier verschiedenen Stellen
im Spiel stammen, eine Nachbarschaft, die so nie vorkommt und teils sichtbar
falsch aussah. Jetzt: Der Export sammelt alle ECHTEN Vorkommen jedes Tiles
über alle Level des Gfxsets (inkl. Flips) und nimmt EINE reale
3×3-Nachbarschaft — bevorzugt ungeflippt, vollständig (8 Nachbarn) und am
häufigsten. Existieren nur geflippte Vorkommen, wird die ganze Nachbarschaft
gespiegelt, damit das Zentrum in kanonischer Ausrichtung bleibt. Nachbarn
werden mit ihren echten Flips gerendert; die Ecken sind jetzt echte
Diagonalnachbarn statt zweistufiger Schätzungen.

**Mirror-Fallback (nach erstem User-Test):** ~12% der Tiles (z.B. 38/304 in
Gfxset 3) kommen in KEINER Tilemap des Sets vor (usage=0) — für sie existiert
keine echte Nachbarschaft, sie wurden bisher ohne Padding exportiert (war auch
beim alten Statistik-Padding so). Jetzt: fehlende Ring-Zellen (usage=0-Tiles
oder Vorkommen am Kartenrand) werden durch das GESPIEGELTE Zentrum gefüllt
(Seiten achsengespiegelt, Ecken doppelt gespiegelt) — plausible Fortsetzung
statt harter Transparenzkante. Manifest: neues Feld `padSource` pro Tile
(`real` | `mixed` | `mirror`).

## [2026-07-17] — Issue S: paletteSnapshot-Handling robuster (Schwesterlevel-Farbstich)

### Problem

Issue S (gelber Rahmen/Schleier auf Lockjaws P07-Tiles) entpuppte sich als
falsche R3-Referenzpalette: Für Gfxset 3 griff beim Export die ROM-Ableitung
über das ERSTE Level des Sets (**Lava Lagoon**, rot-braune Zeile 7), obwohl
die HD-Art unter **Lockjaws** grüner Palette erstellt wurde. Mesens
live/ref-Transform schob dadurch alle P07-Tiles Richtung Gelbgrün — hart an
Tile-Grenzen, über wie unter Wasser. Log-Beweis: PALDIFF P7=287/423/192 in
Lockjaw; in Lava Lagoon dagegen live==ref (Transform still) — was nebenbei
die alte "Spiel bearbeitet Paletten beim Laden nach"-Theorie widerlegt (war
ein Artefakt der falschen Referenz).

### Änderungen (`exportAsTexturePack()` + Container-Save)

1. **NEU: Referenz-Palette wird beim Export AUTOMATISCH ermittelt
   (Auto-Detect, kein User-Schritt mehr nötig).** Während des Tile-Exports
   sammelt der Export pro Gfxset bis zu 192 Subtile-Samples: native
   8×8-Palettenindizes aus `chrRawData` (4bpp-Decode, flip-korrigiert) +
   das auf 8×8 heruntergerechnete HD-Pixelbild. Dann wird JEDE
   Kandidaten-Palette (Container-Snapshot, falls vorhanden, + die
   `loadTileParts`-Palette JEDES Levels des Gfxsets) dagegen gescored
   (mittlerer quadratischer RGB-Fehler „erwartete Palettenfarbe vs.
   HD-Pixel"); die Palette mit dem kleinsten Fehler ist die, unter der die
   Art tatsächlich gerendert wurde — unabhängig davon, welches Level gerade
   geladen ist. Console zeigt alle Scores:
   `[palettes] gfxset 3: reference palette from AUTO-DETECT ROM "Lockjaw's Locker" (avgErr …; scores: …)`.
   Fallback ohne Samples (kein `chrRawData`): bisheriges Verhalten
   (Snapshot, sonst erstes Level) mit expliziter Warnung.
2. **Snapshot-Suche über ALLE Level-Einträge des Gfxsets** (`snapshotByGfx`):
   ein per Container-Save gespeicherter `paletteSnapshot` kann nicht mehr
   durch Iterationsreihenfolge verschattet werden; er konkurriert jetzt als
   Kandidat im Scoring (gewinnt nur, wenn er die Art wirklich am besten
   erklärt — ein versehentlich unter falschem Level gespeicherter Snapshot
   kann nichts mehr kaputt machen).
3. **Container-Save loggt Snapshot-Status:** `paletteSnapshot captured …`
   bzw. Warnung, wenn kein Level geladen war.

### Workflow

Kein zusätzlicher Schritt mehr: einfach ROM + Container laden → Export.
Die Console-Zeile `[palettes] gfxset N: … AUTO-DETECT …` beim Export
kontrollieren (für Set 3 muss "Lockjaw's Locker" deutlich besser scoren als
"Lava Lagoon").

## [2026-07-15] — R3: Referenz-Paletten-Export (`palettes.bin`)

### Änderung

HD-Tiles haben ihre Farben zur Export-Zeit "eingebacken" — CGRAM-Effekte des
Spiels (Lockjaw-Unterwasser-Verdunklung, Gangplank-Sunset-HDMA, Mainbrace-
Paletten-Zyklus) blieben auf ihnen unsichtbar. R3 behebt das über einen
Laufzeit-Transform in Mesen; der Viewer liefert dafür die Referenz:

1. **`hdSaveSet` (Level-Sets):** neues Feld `paletteSnapshot` — die 128
   BG-CGRAM-Einträge (8 Zeilen × 16 Farben, BGR555, `currentPalette`), unter
   denen die Tiles des Sets gerendert/hochskaliert wurden.
2. **`exportAsTexturePack()`:** schreibt `palettes.bin` ins Pack:
   `[uint8 gfxsetCount] × [uint8 gfxsetIdx, 128 × uint16le bgr555]`.
   Manifest bekommt `has_palettes`. Sets ohne Snapshot (vor diesem Feature
   gespeichert) werden mit Console-Warnung übersprungen.

### Workflow

**Bestehende Container funktionieren OHNE Neu-Speichern/Neu-Upscalen:**
Der Export leitet fehlende Referenz-Paletten automatisch aus dem ROM ab
(`loadTileParts()`-Palette des ersten Levels des Gfxsets — derselbe
deterministische Codepfad, mit dem die Tiles ursprünglich gerendert wurden).
Es reicht also: Viewer öffnen (ROM geladen) → Container laden → Texture-Pack
exportieren → in den Mesen-`HdPacks`-Ordner kopieren. Console zeigt pro
Gfxset die Paletten-Quelle (`snapshot` oder `ROM (level ...)`).
Ein `paletteSnapshot` aus einem späteren Container-Save hat Vorrang
(exakter, falls ein Set mal von einem anderen Level als dem ersten stammt).
Mesen-Seite (Build R3.0+) liest `palettes.bin` automatisch; ohne Datei
ändert sich nichts.

### Betroffene Datei
- `dkc2-viewer/index.html`: `hdSaveSet`-Payload (~Z. 7883),
  `exportAsTexturePack()` palettes.bin-Block + Manifest-Flag (~Z. 9424)

---

## [2026-07-06c] — Issue O: cmFg Export-Ordner Separation

### Änderung

cmFg (Honig-Overlay) PNG-Export-Ordner geändert:
- **Vorher:** `bg/bg1/gfxset_XX` — Honig-Tiles landeten im BG1-Ordner,
  wurden vom Mesen Loader als reguläre BG1-Tiles geladen und deckten den
  BG2-Terrain komplett ab (kein HD-Terrain sichtbar)
- **Nachher:** `cmFg/gfxset_XX` — separater Ordner, wird vom Mesen Loader
  NICHT gescannt (by design). Die cmFg-Tiles werden nicht als HD-Tiles geladen,
  so dass der BG1 Overlay-Blend Pfad im C++ Code den BG2-Terrain darunter
  nachschlagen und mit Honig-Tint rendern kann.

### Betroffene Datei
- `dkc2-viewer/index.html` (Zeile ~8935): Ordnerpfad-Änderung

### Hinweis
Die cmFg-Hashes in `hashes.bin` bleiben als harmlose Orphans bestehen.
Der Mesen Loader findet keine PNGs dafür und ignoriert sie. Zukünftig
könnte der Loader den `cmFg/`-Ordner scannen, um die Overlay-Tiles als
eigene Kategorie zu laden.

---

## [2026-07-06b] — Issue O: Revert wrong layer change, keep palette fix

### Problem with previous fix (2026-07-06)

The previous commit (38d19a5) changed cmFg export from layer=0 to layer=1,
based on the assumption that DKC2's $210B chrBase swap ($25→$52) moves honey
tiles to BG2.  **Diagnostic log analysis proved this wrong.**

Runtime diagnostic (post-log, Rambi Rumble sig CE539ABFD210DBD0) shows:
- BG1 (layer=0) renders honey tiles at VRAM $5xxx-$6xxx with pal=6
- BG2 (layer=1) renders terrain tiles at VRAM $2xxx-$4xxx with pal=3
- MISS entries: all layer=0, pal=6 (honey — content hash not found)
- LAYER MISMATCH: runtime_layer=1, pack_layer=0 (terrain)

The $210B register remains $25 (not $52) during these frames:
- BG1 ChrAddress=$5000, BG2 ChrAddress=$2000 (default, no swap)
- The palette difference (pal=6 vs pal=2) is a tilemap issue, not chrBase

### Fix (this commit)

**Layer** (reverted, 2 locations):
- Hash export: `layer: 1` → `layer: 0`, dedup key `_1_` → `_0_`
- PNG export: folder `bg/bg2/gfxset_XX` → `bg/bg1/gfxset_XX`

**Palette** (unchanged from 38d19a5 — BG2 tilemap override is correct):
- The BG2 tilemap at bg2TilemapBase has pal=6 (confirmed by VRAM ground truth)
- This palette override remains correct and is kept as-is

**chrBase** (unchanged — bg1ChrBase=$5000 is correct):
- Runtime BG1 ChrAddress=$5000 (no swap in these frames)
- Export uses bg1ChrBase=$5000 — matches runtime

### Remaining Issue

Despite correct layer + palette + chrBase, MISS entries persist for most honey
tiles.  This suggests the ground truth VRAM snapshot has different content at
$5xxx-$6xxx compared to runtime VRAM, producing different content hashes.
Investigation needed: compare exported hashes vs runtime hashes for specific
tile addresses.

---

## [2026-07-06] — Issue O: cmFg layer/palette mismatch (SSB chrBase swap) — REVERTED

### Problem

Rambi Rumble (gfxset 0x04) HD tiles were visually present in the exported Mesen
HD pack but produced **0% match rate** at runtime.  Diagnostic log showed two
distinct mismatch categories for every cmFg (honey overlay) tile:

- `PAL MISMATCH`: `runtime_pal=6 pack_pal=2`
- `LAYER MISMATCH`: `runtime_layer=1 pack_layer=0`

### Root Cause 1: Layer Mismatch

The viewer's ROM simulation models the honey overlay as BG1 (layer=0), because
the ppuConfig table stores `$210B = $25` → BG1 chrBase=$5000 (honey).  At
**runtime**, DKC2 reprograms $210B to `$52`, swapping chrBases:

| Layer | ROM ($210B=$25) | Runtime ($210B=$52) |
|-------|-----------------|---------------------|
| BG1 (layer=0) | chrBase=$5000 (honey) | chrBase=$2000 (terrain) |
| BG2 (layer=1) | chrBase=$2000 (terrain) | chrBase=$5000 (honey) |

So the honey tiles are rendered by **BG2 (layer=1)** at runtime, not BG1.  The
cmFg export wrote `layer: 0` in hashes.bin and placed PNGs in `bg/bg1/`, causing
a layer mismatch on every tile.

### Root Cause 2: Palette Mismatch

The cmFg export extracted palette values from the BG1 tilemap (DMA-loaded from
ROM).  Due to the chrBase swap, the **BG2 tilemap** at `bg2TilemapBase` in VRAM
is what the runtime PPU actually uses — and it carries palette=6 for all honey
tiles (confirmed: VRAM $6C00 = 1024 entries, all pal=6).  The BG1 tilemap had
stale palette=2 values, producing a palette mismatch on every tile.

### Fix (REVERTED in 2026-07-06b — layer change was wrong, palette fix kept)

**Layer** (2 locations) — **WRONG, reverted**:
- Hash export: `layer: 0` → `layer: 1`, dedup key `_0_` → `_1_`
- PNG export: folder `bg/bg1/gfxset_XX` → `bg/bg2/gfxset_XX`

**Palette** (2 locations):
- Added `bg2TilemapBase` to stored ppuConfig object
- cmFg PNG export: extracts BG2 tilemap from ground truth VRAM at
  `bg2TilemapBase`, overrides per-tile palette from BG1 tilemap entries with
  correct BG2 runtime palette.  Includes diagnostic palette histogram logging.

### Scope

The fix is generic for all SSB (Sub-Screen-Blend) levels — any level where the
runtime chrBase swap applies will benefit.  35 SSB levels across 6 ppuConfig
values (0x03, 0x24, 0x29, 0x2C, 0x31, 0x35) are covered.

### Known Limitation (Root Cause 3 — not addressed)

~18 terrain tiles (BG1 at $2000) are updated by VBlank DMA within 2 frames of
level load, changing their content hash.  The ground truth captures one animation
frame; runtime may differ.  This affects a small subset of terrain tiles, not the
honey overlay.  Low priority.

### Testing Required

Container must be re-exported after this fix.  Workflow: open viewer → load
container → "Export HD Pack" → test in Mesen with Rambi Rumble.

---

## [2026-07-05d] — Ground Truth VRAM Must Be Authoritative, Not a Gap-Filler; Fallback Data Must Not Depend on UI Navigation

### Problem with the 2026-07-05c fix

That fix chose between `currentBgData.vram` and `catalogData.vram` — but **both**
are the viewer's own ROM-based VRAM *simulation* (`loadLevelBackground()`), which
is documented (`SNES_HD_PACK_PROJECT.md`, "VRAM Dump/Import Feature", 2026-06-15)
to deviate from Mesen's real runtime VRAM for some gfxsets (e.g. 37 = Lava-Levels)
due to VBlank DMA / init-code writes it doesn't fully replicate — this is exactly
why the VRAM ground-truth dump pipeline (Lua-captured real VRAM, embedded for all
25 gfxsets, commit `882f23a`) exists in the first place. The 2026-07-05c fix
picked between two simulated sources without ever considering ground truth, so
it could still produce content hashes that don't match Mesen's actual runtime
even when gfxset identity was resolved correctly.

Separately: the fallback to `catalogData` for `tileArrangementData`/`chrRawData`/
`ppuConfig`/tilemaps assumed `catalogData` already matched the gfxset being
saved. That's only true if the user actively switches the Catalog view's own
gfxset dropdown. The viewer's actual primary navigation is the main Level
dropdown — selecting a level there drives *both* the Per-Level and Per-GfxSet
catalog views for that level, and the Catalog gfxset dropdown is a secondary,
independent control. If the user imports several gfxsets' ZIPs while `catalogData`
still reflects whatever level was loaded via the main dropdown, the "fallback to
catalogData" safety net silently reuses the wrong gfxset's data — the same bug
class as 2026-07-05c, just shifted one level down.

### Fix

- **`vramSnapshot`** (in both `saveCurrentHDToContainer()` and
  `refreshContainerSetMetadata()`): now checks `VRAM_GROUND_TRUTH[gfxset_XX]`
  **first, unconditionally** — not just as a last-resort gap-filler like
  `applyGroundTruthVram()` does elsewhere — before falling back to simulated
  `currentBgData.vram` (gated by `currentMatchesActive`) or `catalogData.vram`.
  Ground truth covers all 25 playable gfxsets, so this is expected to be the hit
  in the overwhelming majority of saves regardless of what's loaded in the UI.
- **Everything else** (`tileArrangementData`, `gfxCount`, `chrRawData`,
  `ppuConfig`, `bg2/bg3/bg1TilemapData`, `wallTilemapData`) has no ground-truth
  equivalent (they're ROM tile-arrangement/PPU-config, not VRAM content), so
  instead: both functions now rebuild `catalogData` fresh via
  `buildCatalogByGfxSet(activeGfxIdx / targetGfxIdx)` whenever the cached
  `catalogData.gfxSetIndex` doesn't already match the gfxset being saved —
  `buildCatalogByGfxSet()` only needs `rom`/`graphicsSetsMap` (always available
  once a ROM is loaded), so it produces correct data for *any* gfxset regardless
  of what Level or Catalog-dropdown selection currently happens to be displayed.
  The original `catalogData` is restored right before each function returns, so
  this is invisible to whatever the user is actually looking at.

### Net effect

Importing an HD ZIP for a given gfxset no longer depends on having that gfxset
"open" anywhere in the UI — main Level dropdown, Catalog gfxset dropdown, or
otherwise. The pack's own `manifest.gfxSetIndex` (already the source of
`hdPack.gfxSetIndex`/`activeGfxIdx`) is enough; ground truth and
`buildCatalogByGfxSet()` supply the rest directly from ROM/embedded dump data.

---

## [2026-07-05c] — Critical: Stale currentBgData/currentTileRawData Corrupted Every Field saveCurrentHDToContainer() Writes Except Tiles

### Problem

After importing all 6 gfxsets into a freshly-rebuilt container (with every fix from
2026-07-05/05b in place), the resulting Mesen HD Pack made **every level** render
as a mix of unrelated tiles — including Pirate Panic, which had always worked
before. Generating the pack also reported fingerprints for only 2 of 6 gfxsets.

### Root Cause

Confirmed empirically by cross-referencing the exported `hashes.bin`: BG1 content
hashes for gfxsets 3, 4, 7, and 29 were **100% identical** (918/918 shared hash
values) — impossible for genuinely different levels. This means the raw VRAM
bytes those hashes were computed from were themselves identical across 4
supposedly-different gfxsets.

`saveCurrentHDToContainer()` builds `vramSnapshot`, `chrRawData`,
`tileArrangementData`/`gfxCount`, `ppuConfig`, `bg2/bg3/bg1TilemapData`,
`wallTilemapData`, the wall/cmFg blobs, and legacy `tileChecksums` from
`currentBgData`/`currentTileRawData`/`currentFgData`/`currentStyle` **first**,
falling back to `catalogData` only if those were falsy. But those `current*`
globals are Level-load-scoped — only `loadLevel()` updates them. Switching
gfxsets via the Catalog dropdown updates `catalogData`/`selectedGfxSet` but
leaves `current*` frozen on whichever Level was loaded last. Since `current*`
stays truthy for the rest of the session after the first Level load, it was
**always** preferred over the correct, fresh `catalogData` — so importing
several different gfxsets via the dropdown (the exact workflow enabled by
2026-07-05's container-save fix) saved the **same stale Level's** VRAM/tile
data under every gfxset's container entry, varying only by which tiles/BG2/BG3
images happened to be attached (already fixed separately). `chrRawData` and
`tileArrangementData` had no `catalogData` fallback at all — they'd be either
wrong or entirely missing.

This bug almost certainly predates today — it just never surfaced before
because the setId/tile-filter bug (fixed earlier today) made every gfxset after
the first collide into the same container key anyway, and because prior
single-gfxset-at-a-time workflows likely always reloaded a real Level before
importing. Today's fixes were the first time a "import 6 gfxsets in one session
via the dropdown" workflow actually produced 6 *distinct* container entries —
which is what finally exposed that their VRAM/tile metadata was identical.

### Fix

Added `currentMatchesActive = currentStyle && activeGfxIdx != null &&
currentStyle.graphics === activeGfxIdx` in `saveCurrentHDToContainer()`. Every
`current*`-preferring branch now requires this guard before trusting `current*`,
falling through to `catalogData` otherwise:
`wallBlob`, `cmFgBlob`, `tileArrangementData`/`gfxCount`, `chrRawData`,
`ppuConfig`, `bg2TilemapData`, `bg3TilemapData`, the ShipDeck BG3 virtual-tilemap
override, `wallTilemapData`, `bg1TilemapData`, `vramSnapshot`, and the legacy
`tileChecksums`. `buildCatalogByGfxSet()` now also returns `tileArrangement`,
`gfxData`, `gfxCount`, and `tileCount` so `chrRawData`/`tileArrangementData` have
a real fallback (previously missing entirely).

### Not yet audited

`refreshContainerSetMetadata()` (the "Aktualisieren" button in the container
manager) has the same `currentBgData`-preferring pattern in a few places (BG2/
BG3/wall/cmFg tilemap refresh, ShipDeck override). Not fixed in this pass since
it wasn't implicated in today's reported symptoms — worth applying the same
`currentMatchesActive`-style guard there before relying on it for multi-gfxset
sessions.

### Recommended recovery

Delete the container and re-import all 6 already-upscaled ZIPs once more now
that this fix is in place, then re-export the Mesen HD Pack fresh. The ZIPs
themselves were never affected (this bug is purely in how the viewer wrote
container metadata) — no re-upscaling needed.

### Follow-up: refreshContainerSetMetadata() had the same bug, worse

The "Aktualisieren" button in the container manager — meant to refresh a set's
VRAM-derived metadata without re-uploading its HD tiles — had the identical
`currentBgData`-preferring pattern for every VRAM-derived field, **plus** an
unguarded `setId` computed directly from `currentStyle?.graphics` with no
match-check at all. Clicking it while `currentStyle` was stale (frozen on a
different Level than whatever gfxset the Catalog view was showing) could
silently refresh the **wrong** container entry with mismatched data — a
plausible independent (or contributing) cause of the corruption, given this
function's whole purpose is "patch VRAM data without a full re-upload."

Fixed the same way: `setId` now derives from `selectedGfxSet` when
`catalogView && catalogMode === 'gfxset'` (falls back to `currentStyle.graphics`
only in Level mode), and a `currentMatchesActive` guard (same as
`saveCurrentHDToContainer()`) gates every `current*`-preferring branch —
`tileArrangementData`/`gfxCount`, `chrRawData` (previously no catalogData
fallback, same gap), `ppuConfig`, `bg2/bg3/bg1TilemapData`, the ShipDeck
override, `wallTilemapData`, `vramSnapshot`, and `tileChecksums` (which also
used `currentStyle?.graphics` directly for its `gfxset` tag — now uses the
resolved `targetGfxIdx`).

### Note on age

Verified via `git log -S` rather than assumed: the vulnerable
`currentBgData`-preferring pattern in `saveCurrentHDToContainer()` dates to
commit `885c867` (2026-06-16) — about 3 weeks before this was caught, not
introduced today. It plausibly went unnoticed because the parallel setId/
tile-filter bug (fixed earlier on 2026-07-05) made multi-gfxset-in-one-session
imports collide into a single container key anyway, and/or because earlier
single-gfxset workflows likely always reloaded a real Level before each import,
which happened to keep `currentBgData` fresh by coincidence.

---

## [2026-07-05b] — Revert Cluster Padding (Export v4 → clean clusters)

### Problem

The 1-tile padding ring added to cluster exports (2026-07-03, "Tile Seam
Elimination") was meant to give the AI upscaler neighbor context at cluster
edges. Spot-checking several exported clusters (not an isolated case) showed the
padding frequently mismatching the real content right at the cluster/padding
boundary — e.g. a waving-flag cluster in Mainbrace Mayhem where the padding tile
picked by `bestNeighbor()` visibly didn't continue the flag's pattern, producing
a hard seam mid-graphic. Since a wrong padding neighbor is exactly the kind of
inconsistent edge context an AI upscaler reacts to, this risked making the real
seam-at-the-cluster-boundary problem worse instead of better.

### Fix

`exportCatalogAsZip()`'s cluster export (both auto-detected and manual clusters)
reverted to plain, unpadded output — matches pre-2026-07-03 behavior.
`buildPaddedClusterCanvas()` removed entirely (no remaining references).
Individual-tile padding (a separate, older code path using the same
`bestNeighbor()` helper, not reported as problematic) is untouched. Import-side
(`importHDPack()`) already treated `paddingTiles` as optional/defaulting to 0, so
no import changes were needed — clusters just come back through the "unpadded"
branch again. Score-based tile selection is unaffected in principle; cluster-
extracted tile candidates simply no longer get the padding bonus (correctly, since
they're no longer padded).

---

## [2026-07-05] — Container Save Regression Fix (Multi-GfxSet Import)

### Problem

Importing HD packs for several different gfxsets into the same container in one
session (e.g. 6 sets: 07, 25, 03, 04, 20, 1D) silently corrupted the container:
only 4 of 6 gfxsets ended up saved, a gfxset that displayed correct HD right after
its own import reverted to native rendering once further gfxsets were imported, and
some gfxsets (Rambi Rumble, Gusty Glade) ended up with zero HD tiles at all.

### Root Cause

`saveCurrentHDToContainer()` derived both the container key (`setId`) and the
tile-filtering prefix from `currentStyle?.graphics`. That variable is only updated
by `loadLevel()` when a full Level is (re)loaded — switching gfxsets via the
Catalog view's gfxset dropdown only updates `selectedGfxSet`, leaving
`currentStyle` frozen on whatever Level was last loaded (or `null`/`undefined` if
none was loaded yet this session).

Since `hdPack.tiles` intentionally accumulates across imports (to support
importing tiles + BG2 as separate ZIPs for the *same* gfxset), every import after
the first — for a *different* gfxset — got saved under the same stale
`currentStyle.graphics`-derived key, silently overwriting the previous gfxset's
container entry (including its BG2/BG3 images, which are unconditionally replaced
per import) while its own newly-imported tiles were discarded by the (also stale)
filter.

### Fix

- **`importHDPack()`**: `hdPack.gfxSetIndex` is now updated on *every* import (not
  only the first) from the ZIP's own `manifest.gfxSetIndex` — always correct,
  independent of any UI dropdown/Level state.
- **`saveCurrentHDToContainer()`**: container key and tile filter now derive from
  `hdPack.gfxSetIndex ?? selectedGfxSet ?? currentStyle?.graphics` instead of
  `currentStyle?.graphics` alone.
- **Memory**: after a successful save, that gfxset's tiles/BG2/BG3/wall/cmFg
  bitmaps are `close()`d and removed from `hdPack` — they're durably in IndexedDB
  now, no need to keep decoded bitmaps resident for the rest of the session
  (relevant when importing many gfxsets back-to-back; uncompressed 4x tile sets
  add up to hundreds of MB each).
- **`ensureGfxSetHDLoaded(gfxIdx)`** (new): called from `loadLevel()` on every
  level switch — if the level's gfxset isn't currently resident in `hdPack`
  (because it was freed after saving), transparently reloads just that gfxset's
  entry from the active container. No UI change needed — there's no "Laden"
  button in the normal workflow; HD tiles keep appearing automatically when
  picking a level from the dropdown, same as before.

### Workflow after fix

Import each gfxset's HD ZIP one after another into the same container — no need
to reload a Level or touch the catalog dropdown carefully in between. Each import
now always lands under its own correct `gfxset_XX` key. Existing containers built
under the buggy code remain corrupted and should be rebuilt (delete + re-import
all ZIPs, or re-import all ZIPs into the existing container to let the fix
self-correct each entry) before re-exporting the Mesen HD Pack.

### Follow-up fixes (same day) — introduced by the fix above

User testing surfaced three further bugs, all in the new auto-load path itself:

- **Stored `gfxSetIndex` metadata still stale**: `saveCurrentHDToContainer()` fixed
  the container *key* and tile *filter* to use `activeGfxIdx`, but the persisted
  `gfxSetIndex` field written to the IndexedDB entry was left as
  `currentStyle?.graphics || null` — the very value just proven unreliable. Reload
  paths (`ensureGfxSetHDLoaded`, `loadContainerToHDPack`) read this field to prefix
  tile keys and stamp `bg2GfxSet`/`bg3GfxSet`, so a stale value here mistagged
  everything on reload regardless of the key/filter fix. Now stores
  `activeGfxIdx ?? null`.
- **`ensureGfxSetHDLoaded()` residency check too narrow**: only checked whether
  *any* tiles with the target gfxset's prefix existed in `hdPack.tiles`. Tiles are
  safe to accumulate across gfxsets (prefixed, no collision), but `bg2`/`bg3`/
  `wall`/`cmFg` are single image slots and `clusters` is a flat array with raw
  (collision-prone) per-gfxset tile-ids — none of these are safe to merge across
  gfxsets. Revisiting a level whose tiles were still resident (but whose bg2/bg3/
  clusters had since been overwritten by a *different* gfxset visited in between)
  kept the foreign background/clusters on screen. Fixed: residency check is now
  `hdPack.gfxSetIndex === gfxIdx`, and bg2/bg3/wall/cmFg/clusters are always
  swapped wholesale (closed + replaced) on a gfxset switch, never merged.
  `saveCurrentHDToContainer()`'s memory-free step also now resets
  `hdPack.gfxSetIndex` to `null` when it frees the active gfxset's data, so the
  next visit to that same level correctly triggers a reload instead of trusting a
  now-empty cache.
- **Catalog view never called `ensureGfxSetHDLoaded()`**: only `loadLevel()`
  (the Level dropdown) did. Switching gfxsets via the Catalog view's own gfxset
  dropdown, its "Gfx Set" mode button, or opening Catalog view at all left
  `hdPack` unrefreshed even though `renderCatalog()` gates BG2/BG3 HD on
  `hdPack.bg2GfxSet/bg3GfxSet === catalogData.gfxSetIndex` — silently falling back
  to native and dropping HD clusters. Hooked in at all three entry points
  (`catModeLevel`, `catModeGfxSet`, `toggleCatalogView`).
- **Pre-existing bug (not introduced today, but what made clusters seem permanently
  broken during this testing round)**: `loadLevel()`'s "if catalog view is active,
  rebuild" step unconditionally called `buildCatalog()` (the Per-Level builder,
  which always returns `clusters: []`) on every level switch, regardless of whether
  `catalogMode === 'gfxset'`. The mode buttons kept showing "Per Set" as active
  while the actual catalog data silently reverted to Per-Level on every level
  change — so clusters could never appear while browsing levels in Per-GfxSet mode.
  Now branches on `catalogMode` like every other rebuild call site does.
- **`loadContainerToHDPack()` (bulk "Load Container") left bg2/bg3/clusters
  pointing at whichever set was iterated last**: it loops over every level set in
  the container, and since bg2/bg3/clusters/gfxSetIndex are single-slot fields
  (see above), each iteration overwrites the previous one — after the loop, they
  reflect the container's last-iterated set, not whatever level happens to be on
  screen (tiles are unaffected since they're gfxset-prefixed and correctly
  accumulate, which is why BG1 always showed HD immediately while BG2/BG3
  stayed native until a level switch happened to trigger `ensureGfxSetHDLoaded`).
  Now calls `ensureGfxSetHDLoaded(currentStyle.graphics)` right after the bulk
  load to sync bg2/bg3/clusters to the on-screen level immediately.
- **`exportCatalogAsZip()` silently exported empty clusters depending on which
  catalog sub-mode happened to be active**: the function reads the ambient
  `catalogData` global directly. Per-Level mode's `buildCatalog()` always returns
  `clusters: []`; if `catalogMode` was `'level'` at the moment "Export ZIP" was
  clicked — e.g. right after a fresh page/ROM reload, since `catalogMode` is a
  plain JS variable that always starts at `'level'` and only changes via an
  explicit mode-button click — the exported ZIP silently had zero clusters, named
  `gfxset_XX` regardless (both modes populate `gfxSetIndex` from the loaded
  level), with `manifest.mode: "level"` the only tell. Confirmed via a real
  export where clusters were visible natively in Per-GfxSet mode moments before
  export, yet missing from the resulting ZIP. Fix: `exportCatalogAsZip()` now
  always builds gfxset-scoped catalog data internally for the export (via
  `buildCatalogByGfxSet`) regardless of the currently displayed catalog mode,
  and restores the original `catalogData` in a `finally` block afterward so the
  visible view is unaffected. `exportAsTexturePack()` (the Mesen HD Pack export)
  was already unaffected — it reads directly from the IndexedDB container, not
  the live `catalogData`.

## [2026-07-03b] — Tile Seam Elimination (3 Interconnected Improvements)

### Problem

HD-upscaled tiles showed visible seams at tile boundaries because:
1. **Edge tiles** in clusters had no outer context for the AI upscaler, causing
   smoothing/anti-aliasing artifacts at cluster edges
2. **First-wins import** — if a tile appeared in multiple clusters, the first
   processed version won regardless of quality (edge vs inner tile)
3. **Covered tiles** in clusters were never exported individually with padding,
   removing the fallback for edge cases

### Improvement 1: Padded Cluster Export (Export v4)

- `buildPaddedClusterCanvas()` — Creates `(w+2)×(h+2)` tile canvas with a 1-tile
  padding ring using `bestNeighbor()` statistics from tilemap analysis
- **Padding ring**: top/bottom rows, left/right columns, 4 corners (transitive via
  bestNeighbor chains) — gives the AI upscaler full neighbor context at every edge
- Both auto-detected and manual clusters get padding
- Manifest entries include `paddingTiles: 1`, `paddedWidthPx`, `paddedHeightPx`
- Backwards compatible: old manifests without `paddingTiles` default to 0

### Improvement 2: Score-Based Tile Import

- Replaced first-wins `hdTiles.has()` check with quality scoring system
- `tileScore(clusterArea, exposedEdges, hasPadding)`:
  - `realContext = 4 - exposedEdges` (0-4 real neighbors)
  - `sizeBonus = min(floor(area/4), 6)` (larger clusters = better context)
  - `paddingBonus = hasPadding ? 10 : 0`
- Individual padded tiles: `PADDED_INDIVIDUAL_SCORE = 12`
- Score examples: large padded cluster inner=20, 1-edge=19, corner=18;
  small padded 2×2 corner=13; padded individual=12; unpadded cluster inner=10
- Phase 1: collect all candidates per tile; Phase 2: pick highest score, close() losers
- Debug logging shows scoring decisions for tiles with multiple candidates
- Padding offset: `padOffset = paddingTiles * tileSize` for correct tile extraction
  from padded cluster images

### Improvement 3: Whole-Cluster Rendering

- Before the tile-by-tile loop in `renderLevel()`, pattern-matches the tilemap against
  known cluster patterns
- **Anchor index**: `(partId, flip)` → candidate clusters for O(1) lookup
- Clusters sorted by area descending (larger clusters take priority)
- When a match is found, renders the WHOLE upscaled cluster image in one `drawImage()`
  call — zero seams within the cluster
- `coveredPositions` Set prevents double-drawing in the tile-by-tile fallback loop
- Clusters with empty positions (id < 0) are skipped for whole-cluster rendering
- `flips` array stored in `hdClusters` for flip-aware pattern matching

### Technical Details

- Export version bumped: 3 → 4
- `hdClusters` now includes `flips` array (previously missing)
- Cluster images cropped from padded source at import time for whole-cluster rendering
- Original padded images freed after tile extraction to save memory

## [2026-07-03] — BG1 Foreground Overlay + SSB Fine-Tuning + Syntax Fix

### Critical Bug Fix

- **Missing closing brace in `loadLevelBackground()`** — A missing `}` that closed the
  `if (ppu.bg3.enabled)` block caused a syntax error preventing ROM loading entirely.

### New Feature: BG1 Foreground Overlay Detection

DKC2 uses three distinct foreground layer types. Previously only SSB (Sub-Screen-Blend)
and standard color math (BG3 fog) were supported. This adds the third type:

**BG1 Overlay** — e.g., Gusty Glade (ppuConfig 0x1D):
- BG3 = background (sky/trees), BG2 = terrain (platforms), BG1 = foreground overlay (wind leaves)
- BG1 has a **separate chrBase** ($7000) from BG2 terrain ($2000) and its own VRAM tilemap ($5800)
- No color math involved — fully opaque overlay (alpha=1.0)
- Previously, BG1 leaves were incorrectly composited into the background image

**Detection heuristic** (`bg1IsSeparateOverlay`):
```
bg1TmLoaded && !isSubScreenBlend && ppu.bg2.enabled && (ppu.bg1.chrBase !== ppu.bg2.chrBase)
```

**Distinction from Hot Head Hop foreground tiles:**
Hot Head Hop foreground elements are Map32 tiles (tileArrangement) with priority bit 13 —
same chrBase as terrain. Gusty Glade leaves are on a separate BG1 VRAM tilemap with a
different chrBase — structurally a different SNES layer.

### Changes

- **`loadLevelBackground()`**: New `bg1IsSeparateOverlay` flag; BG1 excluded from bgData
  when true; new block renders BG1 as `fgData` with `mode: 'bg1overlay'`, `source: 'bg1'`,
  `alpha: 1.0`
- **`buildCatalog()`**: Mode check extended to accept `'colormath' || 'bg1overlay'`;
  `mode` field added to ssbFgImage metadata
- **`buildCatalogByGfxSet()`**: Same mode check extension + `mode` field propagation
- **`renderCatalog()`**: Dynamic label — "BG1 Foreground Overlay (priority, opaque)" for
  bg1overlay vs "Color Math Foreground - BG1/BG3 (...)" for colormath
- **`saveCurrentHDToContainer()`**: Mode gate updated to `mode === 'colormath' || mode === 'bg1overlay'`
- **`refreshContainerSetMetadata()`**: Same mode gate update
- **Console logging**: Uses "FG-Overlay" and "FG overlay cached" labels for bg1overlay

### Three BG1 Foreground Layer Types (Summary)

| Type | Example | fgData.mode | fgData.source | Alpha | Color Math |
|------|---------|-------------|---------------|-------|------------|
| SSB (Sub-Screen-Blend) | Rambi Rumble | `colormath` | `bg1` | 0.35/0.25 | Yes |
| BG1 Overlay | Gusty Glade | `bg1overlay` | `bg1` | 1.0 | No |
| Standard Color Math | Mainbrace Mayhem | `colormath` | `bg3` | 0.25/0.20 | Yes |

### Pipeline Compatibility

All downstream pipeline checks use `source === 'bg1'` (not `mode === 'colormath'`),
so bg1overlay flows through the existing cmFg pipeline automatically. Only the mode-gate
checks at pipeline entry points needed updating.

---

## [2026-06-22b] — Single-Best-ChrBase Detection (Fix v2 for Issue B)

### Problem with Previous Approach

The `detectChrBasesFromVRAM()` function returned ALL chrBases where >50% of
sampled tiles had non-zero data.  For gfxset 37, this returned 5 chrBases
($2000, $3000, $4000, $5000, $6000) because BG2, BG3, and tilemap data
at those addresses also contains non-zero bytes.

Generating hash entries at all 5 chrBases caused **cross-layer hash collisions**:
- Mesen's `TileByKey` uses `{ContentHash, PaletteIndex, LayerIndex}` — NOT vramAddr
- BG2 tile content hashes at $3000 could accidentally match BG1 hash entries
  exported from that same address → wrong HD tile image served
- Result: BG2 disappeared, BG3 fog broken, BG1 tiles visually misassigned

### Fix: Return Only the Single Best chrBase

`detectChrBasesFromVRAM()` now:
1. Scores each chrBase by non-zero tile count (same as before)
2. Returns ONLY the one with the highest score (not all above threshold)
3. Threshold raised to 70% (from 50%) for minimum acceptance

Calling code (PNG export + hash generation) changed:
- If VRAM detection returns a chrBase → use it EXCLUSIVELY (replaces stored)
- If detection fails → fallback to stored chrBase
- ROM ppuConfig scan REMOVED (was useless for gfxset 37, all return same value)

### Expected Results

```
[export] gfxset 07: (detection returns $2000, matches stored → no override)
[export] gfxset 37: stored chrBase $2000 overridden by VRAM detection → $6000
[hashes] gfxset 37: stored chrBase $2000 overridden by VRAM detection → $6000
[hashes] gfxset 37: BG1 → N hash entries (chrBases: $6000)
```

- Level 1: Only $2000 exported → no collision with BG2/BG3 at other addresses
- Level 2: Only $6000 exported → correct BG1 data, no collision with BG2 at $2000

---

## [2026-06-22] — VRAM-based chrBase Auto-Detection (Issue B Fix)

### Problem

Level 2 (Mainbrace Mayhem, gfxset 37) exportiert alle BG1 Hashes mit
chrBase=$2000 — aber die Tile-Daten liegen im VRAM bei $6000.  Der
vorherige multi-chrBase Fix (ROM ppuConfig Scan) hat nicht geholfen,
weil DKC2 den BG12NBA-Register **zur Laufzeit** ändert (VBlank/NMI).
Die ROM ppuConfig-Tabelle enthält für alle Levels im gfxset 37 denselben
Wert (BG12NBA low nibble = 2 → chrBase=$2000), obwohl der tatsächliche
Wert zur Laufzeit = 6 → chrBase=$6000 ist.

**Beweis:** VRAM Fingerprint zeigt `first32=[00 00 00 00 ...]` bei $2000 —
keine Tile-Daten dort.  Die 760 generierten Hashes hashten NULL-Bytes und
konnten niemals gegen die echten VRAM-Daten matchen.

### Lösung: `detectChrBasesFromVRAM()`

Neue Funktion die den **tatsächlichen** chrBase aus dem VRAM-Snapshot erkennt:
1. Sammelt Tile-Indices aus dem tileArrangement
2. Prüft für jeden der 8 möglichen chrBases ($0000–$7000) ob bei den
   berechneten VRAM-Adressen non-zero Daten existieren
3. chrBases mit >50% non-zero Tiles werden als gültig erkannt
4. Wird ZUSÄTZLICH zum ROM ppuConfig Scan aufgerufen (beide Strategien
   ergänzen sich)

### Erwartetes Console-Output

```
[export] gfxset 37: stored chrBase $2000 has NO tile data in VRAM! Detected actual chrBase(s): $6000
[export] gfxset 37: multiple BG1 chrBases: $2000, $6000
[hashes] gfxset 37: stored chrBase $2000 has NO tile data! Actual: $6000
[hashes] gfxset 37: BG1 → N hash entries (chrBases: $2000, $6000)
```

### Warum Content Hash trotzdem funktioniert

Entries für den falschen chrBase ($2000) hashen Null-Bytes und matchen
zur Laufzeit NIE (weil das Spiel dort echte Daten hat).  Entries für den
korrekten chrBase ($6000) hashen die echten Tile-Daten und matchen.
→ Falsch-positive Matches sind unmöglich.

---

## [2026-06-22a] — Multi-chrBase Export (vorheriger Versuch)

### Ansatz

Scan aller Levels im gfxset via `readPpuConfig()` um verschiedene
bg1ChrBase-Werte zu finden.  PNG und Hash-Einträge für jeden chrBase
generiert.

### Ergebnis

Funktioniert NICHT für gfxset 37: Alle Levels in der ROM ppuConfig-Tabelle
haben denselben BG12NBA-Wert.  DKC2 setzt den echten Wert erst zur Laufzeit.
→ Superseded by VRAM-based detection above.

---

## [2026-06-17b] — Enhanced MISS Diagnostik (Mesen2-Seite)

### Kontext / Was wir wissen

Nach dem Cross-Gfxset Contamination Fix zeigt Level 2 (Mainbrace Mayhem,
gfxset 37 / 0x25) immer noch KEINE HD Tiles. Level 1 funktioniert.

Bisherige Analyse ergab zwei getrennte Probleme:

1. **VBlank DMA Content Hash Mismatch (30 Tiles, VRAM 0x2000-0x21D0):**
   Viewer injiziert Animations-Frame 0, Spiel ist zur Laufzeit bei Frame N != 0.
   Alle 30 geloggten MISSes waren in diesem Bereich — das alte MISS-Limit (30)
   verhinderte, dass wir Tiles jenseits von 0x21D0 sehen konnten.

2. **Non-animated Tiles (0x2200+) — 100% Content Hash Match aber kein Display:**
   VRAM-Dump-Vergleich: 730 von 760 non-DMA Tiles haben IDENTISCHE Content Hashes
   zwischen Viewer-Snapshot und Mesen VRAM Dump. Trotzdem zeigt nichts an.

### HD Pack ZIP Analyse (`Test v1.0_mesen2_hdpack.zip`)

gfxset_37 enthält 1223 Tiles mit folgender Palette-Verteilung:

| Palette | Anzahl | Anteil |
|---------|--------|--------|
| P04     | 428    | 35%    |
| P07     | 252    | 21%    |
| P02     | 228    | 19%    |
| P03     | 128    | 10%    |
| P05     | 50     | 4%     |
| P06     | 50     | 4%     |
| P01     | 45     | 4%     |
| P00     | 42     | 3%     |

Die alte MISS-Diagnostik zeigte `pal=2` für alle 30 geloggten Tiles.
Hypothese: Wenn die Laufzeit-Palette (z.B. 2) nicht mit der Export-Palette
(z.B. P04) übereinstimmt, dann matcht `SnesHdTileKey::operator==` nicht —
obwohl der ContentHash identisch ist.

**Tile Matching Logik** (`SnesHdData.h:83-88`):
```cpp
return ContentHash == other.ContentHash
    && PaletteIndex == other.PaletteIndex  // <-- Verdacht: hier scheitert's
    && LayerIndex == other.LayerIndex;
```

### Neue Diagnostik (SnesHdVideoFilter.cpp)

Erweiterte Diagnose mit 4 Log-Kategorien:

| Log-Typ        | Was es zeigt                                          | Limit    |
|----------------|-------------------------------------------------------|----------|
| `MATCH`        | HD Tile gefunden (hash+pal+layer stimmen überein)     | Erste 5  |
| `PAL MISMATCH` | ContentHash existiert, aber mit ANDERER Palette       | Erste 20 |
| `MISS`         | ContentHash gar nicht im Pack (Limit 30 → 60 erhöht) | Erste 60 |
| `FRAME`        | bgPixels / match / miss / palMismatch / TileByKey + Level-ID | Erste 10 Frames |
| `CONTEXT CHANGE` | VRAM-Signatur hat sich geändert (Level-Wechsel) | Jedes Mal |

**Kernstück: `PAL MISMATCH`-Erkennung** — Bei jedem MISS werden alle 8 Paletten
(0-7) durchprobiert. Wenn der ContentHash mit einer anderen Palette im TileByKey
existiert, wird `PAL MISMATCH` statt `MISS` geloggt. Das bestätigt oder widerlegt
die Palette-Mismatch-Theorie definitiv.

### Kontext-Erkennung (VRAM-Signatur)

Mesen lädt beim Start automatisch den letzten Spielstand (oft Worldmap).
Ohne Schutz würden die statischen Diagnose-Zähler auf Worldmap-Daten verbraucht.

**Lösung:** VRAM-basierte Level-Erkennung:
- Zwei stabile Referenz-Tiles (außerhalb VBlank DMA-Bereich 0x2000-0x21D0):
  - `0x32E0` → bekannter Hash `0x1585855B0633F405` = **gfxset_37 (Level 2)**
  - `0x2080` → bekannter Hash `0xF33C58BA8611DF5D` = gfxset_07 (Level 1)
- Kombinierte Signatur wird jedes Frame berechnet
- Bei Signatur-Änderung: `CONTEXT CHANGE` geloggt, ALLE Zähler zurückgesetzt
- FRAME-Log zeigt `[LEVEL2]` oder `[other]` + Signatur-Hash

**Effekt:** Man kann auf der Worldmap starten, zum Level navigieren, und bekommt
frische Diagnose-Daten genau ab dem Frame wo Level 2 geladen wird.

### Erwartete Test-Ergebnisse

| Szenario | FRAME-Log | Bedeutung |
|----------|-----------|-----------|
| A: Palette-Mismatch bestätigt | `match=0, palMismatch=HOCH` | Export-Palette stimmt nicht mit Runtime überein. Fix nötig. |
| B: Tiles matchen doch | `match=HOCH` | HD Tiles werden geladen, Problem ist Rendering oder BG3-Verdeckung |
| C: Hash-Mismatch überall | `miss=HOCH, palMismatch=0` | Weder Hash noch Palette stimmt. Tieferes Problem. |

### Gelernt

- `GetMatchingTile()` (`SnesHdData.h:356-382`) ist simpel: `TileByKey.find(key)`,
  dann erstes nicht-transparentes Tile zurückgeben. Fingerprint-Scoping deaktiviert.
- Das alte 30-Tile MISS-Limit hat uns blind gemacht für non-DMA Tiles.
- Das HD Pack enthält ALLE 8 Palette-Varianten für manche Tiles, aber der Großteil
  hat nur eine spezifische Palette (z.B. P04). Wenn Runtime eine andere verwendet,
  gibt es keinen Match.

---

## [2026-06-17] — Cross-Gfxset Tile Contamination Fix

### Bug Fixes

- **Fix: Cross-gfxset tile contamination in save/export pipeline**
  - `saveCurrentHDToContainer()` now filters `hdPack.tiles` by gfxset prefix before saving. Only tiles belonging to the active gfxset are stored in the container.
  - `exportAsTexturePack()` adds defense-in-depth filtering: skips tiles with foreign gfxset prefixes (protects against pre-fix contaminated containers).
  - **Root cause**: After `loadContainerToHDPack()`, all tiles from all gfxsets were merged into a single global Map. Re-saving then dumped foreign tiles into the current set's container slot. During export, deduplication by `tileId` caused wrong bitmaps to win — Level 2 PNGs contained Level 1 pixel art.

- **Fix: Catalog-mode VRAM snapshot fallback**
  - `saveCurrentHDToContainer()` and `refreshContainerSetMetadata()` now fall back to `catalogData.vram` when `currentBgData` is null (catalog mode without active level load).

### New Features

- **BG3 tilemap caching in catalog mode**
  - `buildCatalogByGfxSet()` now caches BG3 tilemap data and full VRAM snapshot.
  - Provides correct data for export even when no level is actively loaded.

### Refactoring

- **`loadTileParts()` rewritten to use generic VRAM loading**
  - Replaces the hardcoded 3-case DMA switch with `readGfxSetEntries()` + full VRAM array approach.
  - Same proven method used by `loadLevelBackground()` — eliminates code duplication and handles all gfxset variants correctly.
  - `injectAnimatedTiles()` updated to accept explicit `bg1ChrBase` parameter.

---

## [Unreleased] — 2026-06-16

### VBlank DMA Injection Fix (Level 2 / Mainbrace Mayhem)

**Problem:** HD tiles for Level 2 (gfxset 0x25, decimal 37) showed 0% match in Mesen,
while Level 1 (gfxset 0x07) worked correctly.

**Root Cause:** Levels with VBlank animation types (7, 8, 13, 19) have DMA transfers
that overwrite parts of VRAM every VBlank frame. For gfxset 0x25 (vblankType 13),
960 bytes at VRAM 0x2010-0x21E0 (tiles 1-30) are overwritten with pirate flag
animation data. The viewer exported hashes from PRE-VBlank VRAM, but Mesen computes
hashes from POST-VBlank VRAM — producing completely different content hashes.

**Analysis:**
- VRAM dump at level entry confirmed Level 2 data (static tiles 31+ match perfectly)
- Dump was captured before animation started (pirate flag not yet visible)
- MISS hashes from Mesen debug log correspond to gameplay state (animation active)
- Palette mismatch (pal=2 vs P04) was a secondary issue, masked by the hash mismatch
- Palette variant expansion (from earlier commit `1b774a6`) already handles this

**Fixes:**
- `885c867` — Add `injectAnimatedTilesIntoVram()` function; injects frame 0 of VBlank
  DMA animation data into the VRAM snapshot at absolute VRAM byte addresses.
  Called from `loadLevelBackground()` after initial DMA entries load.
  `buildCatalogByGfxSet()` now returns `catalogVram` + `catalogBg3TilemapData`.
  Container save/refresh falls back to `catalogData.vram` in catalog mode.
- `a831c5d` — Auto-inject VBlank DMA into stored VRAM snapshots at export time.
  Ensures `hashes.bin` is always correct, even for containers saved before the fix.
  No manual "Refresh Metadata" step required.

**Known Limitation:** Only animation frame 0 is injected. Animated tiles (pirate flag)
cycle through multiple frames — tiles 1-30 match HD only during frame 0.
Multi-frame animation support is a separate milestone.

**Note on "gfxset 0x37" confusion:** Earlier documentation incorrectly referred to
Level 2's gfxset as "0x37". The value `style.graphics = 37` is decimal; the correct
hex notation is **0x25**. gfxset 0x37 (= decimal 55) does not exist in DKC2.

### Generic DMA Loading

- `85c0b29` — Replace hardcoded 3-case DMA switch in `loadTileParts()` with generic
  `readGfxSetEntries()` + `readPpuConfig()`. Fixes "No graphics data found" errors
  for gfxsets whose DMA entries target non-standard VRAM destinations.

---

## [M5.4-Phase2] — 2026-06-15

### BG1 Palette Variant Expansion

- `1b774a6` — `collectBG1PaletteVariantsFromROM()` scans ALL levels sharing a gfxset
  to find palette rows not present in the container's stored tile arrangement.
  Creates PNG copies for missing (vramAddr, palette) combinations at export time.

---

## [M5.3] — 2026-06-12/13

### BG1 Hash Fix + BG3 Support + Fingerprint System

- `ca46d89` — Major overhaul addressing three independent issues:

  1. **BG1 hash data source:** Changed from `chrRawData` (ROM decompression buffer)
     to `vramSnapshot` (actual VRAM bytes). SNES is a CHR-RAM system — hashes must
     come from live VRAM, not ROM-decompressed data.
  2. **Palette dedup key:** Added palette index to the PNG export dedup key
     (`${gfxset}_0_${vramWordAddr}_P${pal}`) so all palette variants are exported.
  3. **BG3 layer support:** BG3 tilemap extraction, 2bpp tile PNG export (32x32px),
     BG3 hashes in `hashes.bin` (layer=2), manifest format_version 3.
  4. **Fingerprint system:** `fingerprints.bin` for gfxset identification at runtime.

---

## [M5.2] — 2026-06-11

### Content Hash System

- `50a438f` — FNV-1a 64-bit content hash export (`hashes.bin`) + VRAM snapshot storage.
  Replaces address-based tile matching with content-based matching.
- `4331822` — Per-gfxset export folders and gfxset-keyed checksums.

---

## [M5.1] — 2026-06-10

### Checksum-Based Tile Matching

- `1628677` — VRAM checksums (`checksums.bin`) for tile collision detection.

---

## Earlier

- `62a1135` — BG2 tile export for Mesen2 HD Pack
- `2eed885` — Initial Mesen2 HD Pack export (`exportAsTexturePack`)
- `a26f533` — Gfxset-scoped HD tiles, container save/load, keyboard shortcuts
- `5b5d590` — Initial commit: DKC2 viewer, ASM docs, level data, HD integration research
