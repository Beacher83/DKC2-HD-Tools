# Changelog — DKC2-HD-Tools Viewer

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
