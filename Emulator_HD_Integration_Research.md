# DKC2 HD Remaster — Emulator Integration Research
**Stand: 21. Mai 2026**

---

## 1. Ziel

Die im DKC2 HD Remaster Toolkit extrahierten und upscalten Assets (Level-Tiles, Sprites, Hintergründe) 
sollen in einem SNES-Emulator beim Spielen in Echtzeit als HD-Ersatz gerendert werden.

---

## 2. Bestehende SNES-Emulatoren — HD-Fähigkeiten

| Emulator        | HD Mode 7 | HD Textur-Replacement | Widescreen | Open Source | Genauigkeit     | Status          |
|-----------------|-----------|----------------------|------------|-------------|-----------------|-----------------|
| **bsnes-hd**    | Ja (bis 10x) | Nein               | Ja         | Ja (GPL-3)  | Cycle-accurate  | Beta 10.6 (2021), inaktiv |
| **Super ZSNES** | Ja (3D)   | Ja (per-game)        | Ja         | Nein        | Mittel          | v0.110b (2026), aktiv |
| **Snes9x**      | Nein      | Nein                 | Nein       | Ja          | Hoch            | Aktiv           |
| **Mesen 2**     | Nein      | Nein (NES: Ja!)      | Nein       | Ja (GPL-3)  | Sehr hoch       | v2.1.1 (Juli 2025), sehr aktiv |
| **RetroArch**   | Via bsnes-hd Core | Nur Shader-Filter | Via Core  | Ja          | Variiert        | Aktiv           |

### Fazit
Nur **Super ZSNES** hat aktuell echtes HD-Textur-Replacement im SNES-Bereich implementiert.
bsnes-hd hat einen offenen Feature Request (#71) mit Bounty seit 2021 — niemand hat es umgesetzt.
**Mesen 2** hat ein ausgereiftes HD Pack System für NES — aber noch nicht für SNES. Das ist die vielversprechendste Basis für eine Erweiterung.

---

## 3. Super ZSNES — Detailanalyse

### Überblick
- **Website:** https://zsnes.com/
- **Discord:** https://discord.gg/Qnpk2QjqWM
- **Patreon:** https://www.patreon.com/c/ZSNES
- **Entwickler:** Die zwei Original-ZSNES-Entwickler (seit ~1997), jetzt wiedervereint
- **Architektur:** Komplett neu geschrieben, GPU-basierter PPU-Kern
- **Plattformen:** Windows, Mac, Linux, Android (iOS geplant)
- **Lizenz:** Proprietär / Closed Source (ZEMU Software Inc.)

### "Super Enhancement Engine" — Features pro Spiel
| Feature                    | Beschreibung                                                        |
|---------------------------|---------------------------------------------------------------------|
| High Resolution Textures  | Manuell gezeichnete HD-Tiles (kein Auto-Upscaler)                   |
| Texture/Normal Maps       | HD-Details auf Hintergründen                                        |
| 3D Mode 7                 | Height-Mapped 3D statt flacher Mode 7 Rotation                     |
| Widescreen                | Wo das Spiel es intern unterstützt                                  |
| Unkomprimiertes Audio     | Ersetzt komprimierte SNES BRR-Samples                               |
| Overclock                 | Entfernt Slowdown bei betroffenen Spielen                           |

### Aktuell unterstützte Spiele (7 Titel)
1. Super Mario World
2. Super Metroid
3. Mega Man X
4. Super Castlevania IV
5. F-Zero
6. Gradius III
7. (7. Titel nicht explizit benannt auf Website)

### DKC2-Status: NICHT UNTERSTÜTZT

### Einschränkungen (Stand v0.110b)
- Noch keine Special Chips (DSP1, SuperFX, S-DD1 gerade erst hinzugefügt)
- Noch keine RetroAchievements
- Noch kein Netplay
- Enhancement-Daten sind "hand-tuned" pro Spiel — kein generisches Texture-Pack-Format
- Closed Source — keine Möglichkeit, selbst beizutragen
- Early Development Stage

### Kontaktmöglichkeit
- **Discord** ist der beste Kanal für Kontaktaufnahme
- Möglicher Pitch: Wir bieten komplette ROM-Analyse von DKC2 (Tile-IDs, Paletten, 
  GFX-Set-Zuordnungen, Sprite-Animationen) + extrahierte Assets als Grundlage für 
  DKC2-Enhancement im Super ZSNES

---

## 3b. Mesen 2 — Detailanalyse

### Überblick
- **GitHub:** https://github.com/SourMesen/Mesen2
- **Website:** https://www.mesen.ca
- **Entwickler:** Sour (seit 2014, aktiv)
- **Version:** 2.1.1 (Juli 2025), 3510+ Commits, 2.4k Stars
- **Architektur:** C++ Core (61.8%) + C# UI (20.5%), Multi-System
- **Systeme:** NES, SNES, GB, GBA, PCE, SMS/GG, WonderSwan
- **Plattformen:** Windows 10+, Linux, macOS (Intel + Apple Silicon)
- **Lizenz:** GPL-3.0 — Open Source, forkbar

### NES HD Pack System — Bestehendes Referenzsystem!

**Entscheidender Vorteil:** Mesen hat für den NES-Teil bereits ein **voll funktionsfähiges HD Pack System** (`Core/NES/HdPacks/`):

| Datei | Funktion |
|-------|----------|
| `HdData.h` | Datenstrukturen für HD-Tiles, Conditions, Rules |
| `HdPackLoader.cpp/h` | Lädt HD Pack Manifest + PNG-Texturen |
| `HdNesPack.cpp/h` | Tile-Matching/Lookup zur Laufzeit |
| `HdNesPpu.cpp/h` | Spezialisierte PPU-Variante mit HD-Rendering |
| `HdVideoFilter.cpp/h` | Skalierte Video-Ausgabe |
| `HdPackBuilder.cpp/h` | Tool zum automatischen Erstellen von HD Packs |
| `HdPackConditions.h` | Bedingte Tile-Auswahl (z.B. je nach Spielzustand) |
| `HdAudioDevice.cpp/h` | HD-Audio-Replacement (OGG statt NES-Audio) |
| `OggMixer/OggReader` | Audio-Streaming für HD Packs |

Das NES HD Pack Format unterstützt:
- Tile-Matching per CHR-Data-Hash + Palette
- Bedingte Rules (verschiedene HD-Tiles je nach Spielzustand)
- Skalierbare Ausgabe (1x bis beliebig)
- Audio-Replacement
- HD Pack Builder (automatisches Tile-Dumping)

### SNES PPU-Architektur (Quellcode-Analyse)

Die SNES-PPU-Emulation befindet sich in 3 Dateien:
- `Core/SNES/SnesPpu.h` (~230 Zeilen)
- `Core/SNES/SnesPpu.cpp` (~1500+ Zeilen)
- `Core/SNES/SnesPpuTypes.h` (~170 Zeilen)

#### Rendering-Pipeline
```
RenderScanline()
  ├─ EvaluateNextLineSprites()    // OAM evaluation (H=0..255)
  ├─ FetchTileData()              // Tilemap + CHR reads (H=0..263)
  │   ├─ GetTilemapData<>()       // Tilemap Word lesen → TileData.TilemapData
  │   └─ GetChrData<>()           // Bitplane-Daten → TileData.ChrData[4]
  ├─ RenderMode0..7()             // Pixel-Rendering
  │   ├─ RenderSprites()          // Sprite-Pixel → Main/Sub-Screen
  │   └─ RenderTilemap<>()        // BG-Tile-Pixel → Main/Sub-Screen
  ├─ RenderBgColor()              // Backdrop
  ├─ ApplyColorMath()             // Color Math (Add/Sub/Half)
  ├─ ApplyBrightness()            // Screen Brightness
  └─ ApplyHiResMode()             // In Output-Buffer schreiben (512x478)
```

#### Tile-Daten-Zugriff (Injection-Points)

**`TileData` Struct** (pro Tile-Spalte gepuffert):
```cpp
struct TileData {
    uint16_t TilemapData;   // Tile# (0-9), Palette (10-12), Prio (13), VFlip (15), HFlip (14)
    uint16_t VScroll;
    uint16_t ChrData[4];    // Bitplane-Daten (2/4/8 bpp)
};
```

**`LayerData`** speichert 33 Tiles pro Layer — alle Tile-Identitäten sind beim Rendering noch bekannt!

**Injection-Point 1 — `RenderTilemap<>()`:**
- Template-Parameter geben Layer, BPP, Priority
- `lookupIndex` → Tile-Spalte in `_layerData[layer].Tiles[]`
- `tilemapData` → Tile-Nummer + Palette + Flags
- VRAM-Adresse berechenbar: `config.ChrAddress + (tilemapData & 0x3FF) * 4 * bpp`
- Vor `GetTilePixelColor()` kann HD-Tile-Lookup eingebaut werden

**Injection-Point 2 — `FetchSpriteTile()`:**
- `_currentSprite.FetchAddress` = VRAM-Adresse
- `_currentSprite.Palette`, `Priority`, `HorizontalMirror` bekannt
- Statt VRAM-Read → HD-Sprite-Pixel schreiben

#### Vorteile gegenüber bsnes-hd für Texture Injection

| Aspekt | Mesen 2 | bsnes-hd (ppu-fast) |
|---|---|---|
| **Bestehendes HD Pack System** | Ja (NES) — adaptierbar! | Nein |
| **Codequalität** | Modern C++, sauber strukturiert | Älterer Stil, nall-Framework |
| **Tile-Daten separiert** | `TileData` struct gepuffert | Inline berechnet |
| **Template-Rendering** | Stark templatisiert | Weniger strukturiert |
| **Build-System** | MSBuild + Makefile | Proprietäres nall-System |
| **Debugger** | Exzellent (VRAM, Tilemap, OAM) | Minimal |
| **Maintainer** | Aktiv, responsive | Inaktiv seit 2021 |
| **PR-Akzeptanz** | Möglich (285 Forks, aktive PRs) | Unmöglich (inaktiv) |
| **Output-Buffer** | Fix 512x478 (muss skaliert werden) | Bereits HD-skalierbar |
| **HD Mode 7** | Nein | Ja (bis 10x) |

### Aufwandsschätzung: Mesen 2 Fork mit SNES HD Pack Support

| Arbeitspaket | Aufwand (Tage) | Beschreibung |
|---|---|---|
| 1. Build-Setup & Einarbeitung | 2-3 | Mesen 2 kompilieren (MSBuild/Make), SNES-PPU + NES HdPacks Code verstehen |
| 2. HD Pack Format für SNES adaptieren | 3-5 | NES HdData/HdPackLoader für SNES-spezifische Tiles anpassen (16-bit VRAM, 4-layer BG, 8/16/32/64 Sprites) |
| 3. SNES Tile-Hash/Lookup | 3-5 | Tile-Matching basierend auf VRAM-Adresse + Palette (einfacher als NES weil keine Mapper-Complications) |
| 4. BG-Tile HD-Rendering | 5-8 | `RenderTilemap<>()` hooking, skalierter Output-Buffer, HD-Pixel statt Bitplane-Decode |
| 5. Sprite HD-Rendering | 4-6 | `FetchSpriteTile()` / `RenderSprites()` hooking, Multi-Size-Sprites (8-64px) |
| 6. Output-Buffer Skalierung | 3-5 | Framebuffer von 512x478 auf N×512 × N×478 erweitern, `SendFrame()` anpassen |
| 7. Color Math & Compositing | 3-5 | `ApplyColorMath()` auf HD-Pixel anpassen, Window-Masking, Brightness |
| 8. HD Pack Builder (SNES) | 2-3 | Tile-Dumping-Tool adaptieren (optional, aber sehr hilfreich) |
| 9. DKC2-spezifisch | 3-5 | HDMA-Effekte, Palette-Swaps, Transparenz |
| 10. Testing & Debugging | 4-6 | Rendering-Artefakte, Edge-Cases, Performance |
| **Gesamt** | **32-51 Tage** | **~2-3 Monate Vollzeit** |

**Vergleich mit bsnes-hd:** Ähnlicher Gesamtaufwand (32-51 vs 38-56 Tage), ABER:
- AP1-3 sind deutlich schneller weil NES HdPacks als Vorlage dienen
- AP4-5 profitieren von saubererer Code-Struktur
- AP8 (Pack Builder) ist bei bsnes-hd gar nicht vorhanden
- **Langfristig besser:** Aktiver Maintainer, PR-Möglichkeit, Multi-System-Support

### Strategie-Empfehlung

**Mesen 2 ist der bessere Fork-Kandidat als bsnes-hd**, weil:
1. Das NES HD Pack System als bewährte Vorlage existiert
2. Der Code sauberer und moderner ist
3. Der Maintainer aktiv ist und PRs akzeptiert
4. Ein SNES HD Pack Feature könnte upstream gemergt werden
5. Die Community (2.4k Stars) könnte von HD Packs für SNES profitieren

**Risiko:** Sour könnte SNES HD Packs als out-of-scope ablehnen → dann Fork nötig (GPL-3 erlaubt das)

**Empfehlung:** Vor Fork-Beginn ein Issue auf GitHub eröffnen und fragen ob SNES HD Pack Support willkommen wäre.

| # | Ansatz                      | Machbarkeit | Aufwand    | Vorteile                                          | Nachteile                                          |
|---|----------------------------|-------------|------------|---------------------------------------------------|---------------------------------------------------|
| A | **Super ZSNES Kooperation** | Mittel      | Gering*    | Bewiesene Technologie, aktive Entwicklung, GPU-PPU | Closed Source, Abhängigkeit von Entwicklern, kein Einfluss auf Prioritäten |
| B | **bsnes-hd Fork**           | Hoch        | Sehr hoch  | Cycle-accurate, Open Source, volle Kontrolle       | PPU-Mod ist komplex, Projekt seit 2021 inaktiv     |
| B2| **Mesen 2 Fork**            | Hoch        | Hoch       | NES HD Packs als Vorlage, aktiver Maintainer, sauberer Code, PR-Möglichkeit | Output-Buffer muss skaliert werden, kein HD Mode 7 |
| C | **Eigener Web-Emulator**    | Niedrig     | Extrem hoch| Volle Kontrolle, Browser-basiert wie unser Toolkit | Monate Arbeit, Performance-Fragen                  |
| D | **RetroArch Overlay**       | Niedrig     | Mittel     | Nutzt bestehenden Emulator                         | Fragil, Sync-Probleme mit Scroll-Registern         |
| E | **Standalone Viewer (aktuell)** | Fertig  | Fertig     | Funktioniert jetzt, HD-Vorschau möglich            | Kein echtes Gameplay                               |
| F | **Video-Compositing**       | Mittel      | Mittel     | Post-Processing, keine Emulator-Modifikation       | Kein Echtzeit-Gameplay, nur für Videos/Screenshots |

*) Aufwand "Gering" bei Option A bezieht sich auf unseren Aufwand — wir liefern Daten, 
   die ZSNES-Entwickler implementieren die Engine. Gesamtaufwand ist natürlich höher.

### Empfohlene Strategie (AKTUALISIERT 21. Mai 2026)

**Entscheidung: Wechsel von bsnes-hd zu Mesen 2 als primärer Emulator-Kandidat.**

1. **Primär: Mesen 2 Fork** — SNES HD Pack Support implementieren, basierend auf dem NES HdPacks-Pattern
2. **Parallel: Super ZSNES Kooperation** — weiter verfolgen (Discord-Anfrage läuft)
3. **Pausiert: bsnes-hd Fork** — AP1-AP4 fertig, wird als Fallback aufbewahrt
4. **Langfristig:** Eigene Lösung nur als letzter Ausweg

#### Begründung für den Wechsel
- Mesen 2 hat ein **funktionierendes HD Pack System für NES** als Vorlage
- **Aktiver Maintainer** (Sour) vs. inaktives bsnes-hd (seit 2021)
- **Sauberer, moderner Code** — einfacher zu erweitern
- **PR-Möglichkeit** — Feature könnte upstream landen
- bsnes-hd Arbeit ist **nicht verschwendet**: Texture Pack Format, Viewer-Export, Lookup-Schema sind 1:1 übertragbar

---

## 5. Technische Anforderungen für Emulator-HD-Integration

### Was unser Toolkit bereits liefert
- Vollständige Tile-ID-Zuordnung für alle Level (GFX-Sets, BG1-BG4)
- Palette-Zuordnung inkl. Runtime-Overrides (routine1 Analyse komplett)
- Sprite-Extraktion mit Animation-Frames und Composite-Rendering
- Export-Format mit Manifest (JSON) + PNG-Tiles/Frames
- Container-System für persistente HD-Asset-Verwaltung

### Was ein Emulator zusätzlich braucht
- **Tile-Matching:** VRAM-Inhalt zur Laufzeit hashen und gegen HD-Lookup-Tabelle prüfen
- **Palette-Handling:** HD-Tiles sind bereits koloriert, SNES-Palette muss ignoriert werden
- **Sprite-Matching:** OAM-Einträge den richtigen HD-Sprites zuordnen (komplexer als Tiles)
- **Scroll-Synchronisation:** HD-Tiles müssen mit BG-Scroll-Registern mitscrollen
- **Layer-Compositing:** HD-Tiles korrekt in die BG1-BG4 Layer-Hierarchie einordnen
- **Transparenz-Effekte:** SNES Color Math auf HD-Tiles anwenden (oder HD-Variante)

---

## 6. bsnes-hd — Technische Details für Fork-Option

### Relevante Architektur
- **PPU-Rendering:** `bsnes/sfc/ppu/` — cycle-accurate PPU-Emulation
- **VRAM-Zugriff:** Tiles werden per DMA in VRAM geschrieben und ständig überschrieben
- **Feature Request #71:** "Add custom sprite/texture dumping/injection support" (offen seit Feb 2021)
  - URL: https://github.com/DerKoun/bsnes-hd/issues/71
  - Labels: "bounty", "help wanted"
  - Keine Implementierung vorhanden

### PPU-Quellcode-Analyse (abgeschlossen)

Der gesamte PPU-Code unter `bsnes/sfc/ppu/` wurde gelesen und analysiert:

| Datei | Funktion | Relevanz für Texture Injection |
|-------|----------|-------------------------------|
| `background.cpp` | BG-Tile-Rendering (fetchNameTable → fetchCharacter → run) | **Hoch** — Tile-Identität hier noch bekannt |
| `object.cpp` | Sprite/OAM-Rendering (fetch → run) | **Hoch** — Sprite-Tile-Identität hier noch bekannt |
| `screen.cpp` | Komposition (above/below, Color Math, cgram-Lookup) | Mittel — Tile-Identität bereits verloren |
| `main.cpp` | Haupt-Loop, cycle-accurate Template-Dispatch | Gering — nur Steuerung |
| `mode7.cpp` | Mode 7 HD (DerKouns Enhancement) | **Referenz** — zeigt wie HD-Skalierung eingebaut wurde |
| `ppu.hpp` | PPU-Struct, VRAM, IO-Register | Gering — nur Datenstrukturen |

#### Kernproblem: Pixel-Level-Renderer

Der PPU rendert **Pixel für Pixel**, nicht Tile für Tile. In `Background::run()` und `Object::run()` 
wird pro CPU-Zyklus genau **ein Pixel** ausgegeben. Zum Zeitpunkt der Komposition in `Screen::run()` 
ist die Tile-Herkunft bereits verloren — nur noch `palette`-Index + `priority` bleiben übrig.

Das bedeutet: Man kann HD-Texturen **nicht** einfach am Ende einspeisen. Man muss **früher** im 
Pipeline eingreifen, wo die Tile-Identität noch bekannt ist.

#### Ansatz A: Tile-Level Interception (empfohlen)

**Eingriffspunkt:** `Background::fetchNameTable()` + `Background::fetchCharacter()`

1. In `fetchNameTable()`: Tile-Nummer (`tileNum`) + Palette + Flip-Flags extrahieren
2. Diese als **Lookup-Key** verwenden: `{vramAddr, palette, hflip, vflip}` oder Hash des VRAM-Inhalts
3. Wenn HD-Ersatz existiert: Flag setzen, HD-Tile im Cache bereithalten
4. In `Background::run()`: Statt 1 Pixel aus VRAM-Daten, N Pixel aus HD-Tile emittieren
5. **Output-Buffer** muss um Faktor N² vergrößert werden (z.B. 4x = 16 Pixel pro Original-Pixel)

**Dasselbe für Sprites** in `Object::fetch()` / `Object::run()`.

**Problem:** Der cycle-accurate Renderer gibt pro Zyklus genau 1 Pixel aus. HD-Skalierung 
erfordert entweder:
- (a) Den Output-Buffer skalieren und pro Zyklus N×N Pixel schreiben (wie mode7.cpp es macht)
- (b) Einen separaten HD-Framebuffer pflegen und am Ende überlagern

DerKouns Mode 7 HD-Code in `mode7.cpp` zeigt Ansatz (a) — er schreibt bereits mehrere 
HD-Pixel pro Mode-7-Pixel. Dieses Pattern könnte für BG-Tiles und Sprites adaptiert werden.

#### Ansatz B: Post-Composition Replacement (nicht empfohlen)

Den PPU normal bei 1x rendern lassen, dann im `refresh()` den Framebuffer nach bekannten 
Tile-Patterns scannen und ersetzen. Probleme:
- Transparente Overlays, Color Math und Windowing verändern Pixel-Werte
- Tiles am Bildrand sind abgeschnitten
- Performance: Pattern-Matching auf 65.536 Pixel pro Frame
- **Fragil und unzuverlässig** — nicht praxistauglich

### Aufwandsschätzung: bsnes-hd Fork mit Texture Injection

| Arbeitspaket | Aufwand (Tage) | Beschreibung |
|---|---|---|
| 1. Build-Setup & Einarbeitung | 3-5 | bsnes-hd kompilieren, PPU-Code im Debugger nachvollziehen |
| 2. Texture-Pack-Format | 2-3 | Dateiformat definieren (Ordnerstruktur, Manifest, PNG-Tiles), Loader implementieren |
| 3. Tile-Hash/Lookup-System | 5-7 | VRAM-Inhalte hashen, Hash→HD-Tile-Cache aufbauen, Invalidierung bei VRAM-Writes |
| 4. BG-Tile Injection | 7-10 | `background.cpp` modifizieren: HD-Tile-Lookup, skalierte Pixel-Ausgabe, Scroll-Korrektheit |
| 5. Sprite Injection | 5-7 | `object.cpp` modifizieren: OAM→HD-Sprite-Mapping, Multi-Tile-Sprites (16×16, 32×32, 64×64) |
| 6. Screen Compositing Anpassung | 5-7 | `screen.cpp`: HD-Buffer-Komposition, Color Math auf HD-Tiles, Window-Masking |
| 7. Performance-Optimierung | 3-5 | Cache-Strategie, Lazy Hashing, Dirty-Flags für VRAM-Regionen |
| 8. DKC2-spezifische Anpassungen | 3-5 | HDMA-Effekte (Wasser, Nebel), Palette-Swaps, Transparenz-Layer |
| 9. Testing & Debugging | 5-7 | Rendering-Artefakte, Edge-Cases (Tile-Wechsel mid-scanline), Regression |
| **Gesamt** | **38-56 Tage** | **~2-3 Monate Vollzeit** für einen erfahrenen C++-Entwickler mit Emulator-Kenntnissen |

#### Warum hat es niemand gemacht?

1. **Projekt inaktiv seit Juni 2021** — kein Maintainer, der PRs reviewed oder merged
2. **Kein einziger Kommentar** auf Issue #71 — niemand hat auch nur einen Ansatz diskutiert
3. **BountySource ist tot** — die verlinkte Bounty-Plattform ist nicht mehr erreichbar
4. **Hohe Einstiegshürde:** Cycle-accurate PPU-Code ist komplex, undokumentiert, und der 
   pixel-level Ansatz macht Tile-Injection fundamental schwieriger als bei Tile-basierten Renderern
5. **Kleines Publikum:** SNES HD-Textur-Packs sind eine Nische in der Nische

#### Fazit

Ein bsnes-hd Fork ist **technisch machbar** aber **aufwändig** (2-3 Monate Vollzeit). 
DerKouns Mode 7 HD-Code beweist, dass der PPU skalierte Ausgabe unterstützen kann — 
das Pattern muss "nur" auf BG-Tiles und Sprites übertragen werden. 

Die **Super ZSNES Kooperation bleibt eine parallele Option**, weil:
- Die Entwickler bereits einen GPU-basierten PPU haben (einfacher für Texture Injection)
- Sie das Enhancement-Format und die Toolchain bereits haben
- Wir nur die Assets und ROM-Analyse liefern müssten

**UPDATE 21. Mai 2026:** bsnes-hd Fork wird zugunsten von Mesen 2 **pausiert**. Siehe Abschnitt 8.

---

## 7. Nächste Schritte

- [x] Super ZSNES Discord beitreten und Kontakt aufnehmen
- [ ] Fragen: Ist DKC2 auf der Roadmap? Akzeptieren sie externe Asset-Beiträge?
- [ ] Fragen: Wie funktioniert das Enhancement-Daten-Format intern?
- [ ] Falls Kooperation: Unsere ROM-Analyse und extrahierte Assets bereitstellen
- [x] bsnes-hd PPU-Code analysieren für Fork-Option — **abgeschlossen**, Aufwandsschätzung: 38-56 Tage
- [x] Mesen 2 SNES-PPU + NES HdPacks analysieren — **abgeschlossen**, Aufwandsschätzung: 32-51 Tage
- [ ] ~~Mesen 2 GitHub Issue eröffnen~~ → stattdessen direkt Fork + bauen (siehe Abschnitt 8)
- [ ] HD Sprite Import/Rendering Pipeline testen (steht noch aus)
- [ ] Container System End-to-End testen (steht noch aus)

---

## 8. Strategiewechsel: Mesen 2 als primärer Emulator (21. Mai 2026)

### Entscheidung

**bsnes-hd Fork wird pausiert. Mesen 2 wird der neue primäre Emulator-Kandidat.**

### Status bsnes-hd (pausiert, nicht eingestellt)

| AP | Status | Übertragbar auf Mesen? |
|----|--------|----------------------|
| AP1: Build-Setup | Erledigt | Nein (anderes Build-System) |
| AP2: Texture Pack Format | Erledigt | **Ja** — Format-Spec ist emulator-agnostisch |
| AP3: Tile-Hash/Lookup | Erledigt | **Ja** — Key-Schema (VRAM-Addr + Palette) ist identisch |
| AP4: BG-Tile Injection | Erledigt (kompiliert, ungetestet) | **Teilweise** — Konzept übertragbar, Code nicht direkt |
| AP5-AP9 | Offen | Entfällt |

### Was von bsnes-hd direkt wiederverwendet wird

1. **Texture Pack Format** (`TEXTURE_PACK_FORMAT.md`) — Ordnerstruktur, Dateinamen-Schema (`{vramAddr}_P{palette}.png`), Manifest-Format
2. **Lookup-Key-Schema** — `(tileBaseAddr << 8) | paletteGroup` funktioniert auch in Mesen
3. **Viewer-Export** — `exportAsTexturePack()` im DKC2-Viewer erzeugt bereits das richtige Format
4. **PPU-Pipeline-Verständnis** — SNES-PPU-Architektur ist dieselbe, egal welcher Emulator
5. **Kompatibilitäts-Analyse** — Map32 → 8×8 Sub-Tile Mapping bleibt identisch

### Mesen 2 Fork — Arbeitspakete

| AP | Aufwand | Beschreibung |
|----|---------|-------------|
| M1: Fork & Build-Setup | 2-3 Tage | Mesen 2 forken, kompilieren (Windows: MSBuild, Linux: Make), NES HdPacks-Code studieren |
| M2: SNES HdPack Datenstrukturen | 3-4 Tage | `Core/SNES/HdPacks/` Ordner anlegen, `HdData.h` für SNES adaptieren (16-bit VRAM-Adressen, 4 BG-Layer, 8-Palette-Gruppen, Sprite-Sizes) |
| M3: SNES HdPack Loader | 3-5 Tage | `HdPackLoader` für SNES adaptieren — unser Texture Pack Format laden, PNG→RGBA Cache aufbauen |
| M4: BG-Tile HD-Rendering | 5-8 Tage | In `RenderTilemap<>()` HD-Tile-Lookup einbauen: VRAM-Adresse aus `tilemapData` berechnen, bei Match HD-Pixel statt `GetTilePixelColor()` verwenden |
| M5: Sprite HD-Rendering | 4-6 Tage | In `FetchSpriteTile()` / `RenderSprites()` HD-Sprite-Lookup, Multi-Size-Support (8-64px) |
| M6: Output-Buffer Skalierung | 3-5 Tage | Framebuffer von 512×478 auf (512×N)×(478×N) erweitern, `ApplyHiResMode()` + `SendFrame()` anpassen |
| M7: Color Math & Compositing | 3-5 Tage | `ApplyColorMath()` auf HD-Pixel, Window-Masking, Brightness auf skalierten Buffer |
| M8: DKC2-spezifisch | 3-5 Tage | HDMA-Effekte (Wasser, Nebel), Palette-Swaps, Transparenz-Layer |
| M9: Testing & Debugging | 4-6 Tage | Rendering-Artefakte, Edge-Cases, Performance-Profiling |
| M10: Community & PR | 1-2 Tage | Nach M4 kurzes Issue/Discussion bei Mesen eröffnen, nach M9 PR anbieten |
| **Gesamt** | **31-49 Tage** | **~2-2.5 Monate Vollzeit** |

### Vorgehensweise (Hybrid-Ansatz)

1. **Sofort:** Mesen 2 forken, Build aufsetzen (M1)
2. **Phase 1 (M2-M4):** Minimaler Prototyp — BG-Tiles in einem Level ersetzen
3. **Nach M4:** Kurzes Issue bei SourMesen/Mesen2 eröffnen: "Working on SNES HD Pack support, any architectural preferences?"
4. **Phase 2 (M5-M7):** Sprites, Skalierung, Compositing
5. **Phase 3 (M8-M9):** DKC2-spezifisch, Polishing
6. **M10:** PR anbieten oder als eigenständigen Fork releasen

---

## Anhang: Quellen

- bsnes-hd GitHub: https://github.com/DerKoun/bsnes-hd
- bsnes-hd Issue #71: https://github.com/DerKoun/bsnes-hd/issues/71
- Super ZSNES Website: https://zsnes.com/
- Super ZSNES Discord: https://discord.gg/Qnpk2QjqWM
- Super ZSNES Patreon: https://www.patreon.com/c/ZSNES
- Super ZSNES AppImage: https://github.com/pkgforge-dev/SUPER-ZSNES-AppImage
- Mesen 2 GitHub: https://github.com/SourMesen/Mesen2
- Mesen 2 Website: https://www.mesen.ca
- Mesen 2 NES HdPacks: https://github.com/SourMesen/Mesen2/tree/master/Core/NES/HdPacks
- Mesen 2 SNES PPU: https://github.com/SourMesen/Mesen2/blob/master/Core/SNES/SnesPpu.cpp
