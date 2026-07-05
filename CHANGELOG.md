# Changelog — DKC2-HD-Tools Viewer & Mesen2 SNES HD Fork

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
