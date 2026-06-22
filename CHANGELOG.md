# Changelog — DKC2-HD-Tools Viewer & Mesen2 SNES HD Fork

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
