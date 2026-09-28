# Pack-Prüfungen (entstanden 28.09.2026)

Messwerkzeuge, mit denen ein exportiertes Mesen-Pack VOR der Installation gegen echte Spieldaten geprüft
wird. Referenz sind immer die echten VRAM/CGRAM-Abzüge (`LuaScriptData/dkc2_vram_dump/gfxset_XX_vram.bin`,
Namen in HEX, dazu `_state.txt` mit den echten PPU-Registern) bzw. frische Abzüge aus `dkc2_vram_snapshot.lua`.

| Skript | Frage | gut / schlecht |
|---|---|---|
| `artcheck.py <pack> <vram> <cgram> <gfx>` | Passt BG1-Kunst an ihrer Adresse zum VRAM? (±$1000 zum Vergleich) | 3–8 / >60 |
| `artcheck2.py <pack> bg2\|bg3 <vram> <cgram> <gfx>` | dasselbe für BG2/BG3 (Dateien `ADDR_Pnn.png`) | 2–6 / >90 |
| `cutcheck.py <pack> <layer> <gfx> <vram> <tm> <chr> <w> <h> <bpp> <sd.png>` | Pack-Datei gegen SD-Vorlage an der echten Tilemap-Position (palettenunabhängig) | <15 |
| `fitcheck.py <bild> <vram> <cgram> <tm> <chr> <w> <h> <bpp>` | Ebenenbild gegen Render aus echtem VRAM (Zwilling von `fitLayerImage` im Viewer) | 2–5 / 73–181 |
| `render_bg.py ...` | eine BG-Ebene aus echtem VRAM rendern und mit einem Bild vergleichen | — |
| `fpcheck.js <fingerprints.bin> <vram>...` (aus `dkc2-viewer/` starten) | welches gfxset erkennt Mesen je Abzug (Dateireihenfolge = S56) | genau das eigene |
| `sprpal_diff.py <alt> <neu> <out>` | welche Sprite-Hashes haben ihre Referenzpalette verloren/gewechselt | 0 verloren |
| `viewer_harness.js <probe.js>` | lädt `index.html` in Node (Platzhalter-DOM), Viewer-Funktionen direkt aufrufbar; `__setRom(bytes)` | — |

Pfade in den Skripten sind teils fest auf `C:/Users/beach/...` gesetzt (Downloads, OneDrive, Google Drive).

**Lehre:** Ein Etikett ist nur so gut wie seine Quelle — das `G` in `snes_hd_bgcap.txt` ist das von Mesen
ERKANNTE gfxset, nicht das echte Level. Für Zuordnungsfragen immer gegen die Abzüge prüfen.
