# Offene Tests — Stand 2026-10-05

## ▶ UPSCALER-LISTE (Stand 05.10., Auswertung Lauf 02.10. 21:42 S57 + 14:21/15:16)

Quelle: `snes_hd_spritemiss.txt` über ALLE Sitzungen (Recorder ist geseedet, eine einmal verfehlte Kachel
erscheint nie wieder) gegen das installierte Pack 02.10. 14:12; Zuordnung über frischen ROM-Index
(Deskriptoren, Animationen 1–0x30B, verwaiste Sequenzen). 5.290 je verfehlte Hashes: 3.632 inzwischen im Pack,
**~1.600 fehlen**, 58 im Pack unter falschem Slot. `G` im Log ist DEZIMAL (G46 = 0x2E).
Spieltest 02.10.: Klobber sauber ✔.

### A. Sprites, in den letzten Läufen gesehen und noch SD
| # | Was | Kacheln | gfxset | Im Viewer |
|---|---|---|---|---|
| 1 | Dixies Fall (Rattly) | 70 | 37 | `Seq E003` (Deskr. `$0DA4–$0DB8`) |
| 2 | K. Rools Blunderbuss | ~130 gesehen / 260 | 46 | 0x0251/0258/025F/0261/0263 |
| 3 | Rauchwolke/Explosion | 235 | 51, 29, 47 | `0x01BC Explosion` (teilt mit `0x0272 K. Rool Revival`) |
| 4 | Wolke/Dampf Hitze-Level | 145 | 32 | `0x020F Unknown` |
| 5 | Kunst ohne Animation Rickety Race/Target Terror | ~250 | 34 | `Gfx 2B08…2B50`, `Gfx 32FC` |
| 6 | Flitter besiegt | 105 | 37, 29, 38 | `0x019D Flitter Flip Over` |
| 7 | Funken | 131 (30 zuletzt) | 34, 44 | `0x01B1 Spark` |
| 8 | Verwaiste Sequenzen Bayou-Set | 45 | 38 | `Seq E01A` / `Seq E01B` |
| 9 | Laufzeit ohne Deskriptor | ~230 | 37 (86), 29 (62), 34 (55) | Laufzeit-Galerie |
| 10 | Kleinkram | je 2–26 | | X Barrel `0x02DA` (15), Seil-Anims DD/DX (~20, gfx 37), `Gfx 7E5C` (26), `Gfx 2FFC/3000` (12), `Gfx 1AA0` (8), Kudgels Keule `0x029D` (6), `Gfx 2300/2304`, DK Coin |

### B. Sprites aus älteren Läufen, laut Pack weiter ohne Kunst
`0x01B6 Spark?/Splash?` 57 (gfx 3 Lava/Lockjaw) · `Gfx 31A0–31B8` 64 Schrift/Rahmen (gfx 44/29) ·
`Gfx 0BB8–0D00` ~56 Inselkarte (gfx 53).

### C. Hintergründe (Anteil `miss/bg` je Kontext; Kontrolle: komplett-HD-Level = 0 %)
| Level | SD-Anteil | Befund |
|---|---|---|
| **Glimmer's Galleon (40)** | **61 %** | kein eigenes BG-Pack, läuft als Lockjaw (3) — Kacheln passen nicht |
| **Slime Climb (45), vermutlich** | **22 %** | kein eigenes BG-Pack, läuft als Mainbrace (37); ROM-Abgleich: 35 der Miss-Kacheln nur in Set 45. User-Bestätigung offen |
| Arctic Abyss/Clapper's Cavern (47) | 9 % | 101 BG1-Kacheln, vermutlich Schwesterlevel |
| Shops (Kollege, Klubba, Funky, PP-Versteck) | 2–7 % | BG3-Textschrift, 30–54 Kacheln je Shop |
| Windy Well | gering | 46 BG3-Kacheln ohne Kunst |
| 3 nicht erkannte Bildschirme | 100 % | Mode-0-Textbildschirm + zwei unbekannte (sig `7DB645E0`, `BF50841D`) |
MISS-Zeilen sind auf 60 je Kontext gedeckelt → Untergrenzen. Ohne eigenes BG-Pack außerdem: 33 Topsail, 36 Squawks's
Shaft, 41 Red-Hot Ride, 42 Krocodile Kore, 49 Toxic Tower, 52 Web Woods (laufen ggf. über Schwestersets, ungeprüft).
Vorsicht: `BGn − hdBGn` ist KEIN SD-Anteil (auch in gfx 7 mit miss=0 weit auseinander).

### D. Kein Upscale — Export/Slot
58 Kacheln im Pack unter anderem Slot: u. a. 6× `0x00E8 DX Got Prize` (P7), 19 Spritzer Bayou (P3), 24 Weltkarte.

### E. Transparente Linie Level-Ende (Diddys Sonnenbrille, Dixies Gitarre)
User-Test 05.10.: **„Sprite-Kanten glätten“ aus → Linie bei Diddy weg.** Ursache also in Mesens Kantenglättung,
nicht in der Kunst. Diddy `0x0045` (131 Frames, 87 Composite), Dixie `0x00E8` (130 Frames, 90 Composite).
→ **Mesen S58 gebaut (uncommittet):** An einer inneren Naht (alle 4 Nachbarn Sprite) wird nicht mehr gegen den BG
geblendet. Test: Level-Ende mit Glättung an, `sprSeam=` > 0; A/B `ab_no_seam_guard.bat`.
**User-Test 05.10.: Brille sauber, Linie größtenteils weg.** Rest GEPARKT: 1–2 Pixel zwischen Boombox und Diddy
scheinen kurz noch durch, vermutlich Nahtpixel mit einem Nachbarn ohne Sprite (die Prüfung mit 4 Nachbarn greift
dort nicht). Idee für später: als Untergrund den HD-Texel des Nachbar-Sprites nehmen statt des BG.
**Slime Climb / Glimmer:** Der User sieht beide als HD. Kandidat für den SD-Anteil ist die Wasseroberfläche
(BG3-Farbmathe aus Lockjaw, sieht auch dort kaum anders aus als SD). Slime Climb hat `sHd` ≈ 14.700 je Frame (der
Operand ist teils HD). Klären mit einem F12-Paar HD an/aus am selben Savestate.

---

## (alt) NÄCHSTE SITZUNG (Stand 02.10. abends)

**Installiert:** Pack 02.10. 14:12 (`Downloads\Anim Tiles v2_mesen2_hdpack (1).zip`), Mesen S57.
**Erledigt 02.10.** (Details im CHANGELOG beider Repos):
- N1 Klobber, N2 Diddy/Radio, N5 Tierfreunde: Composites werden in Teilen hochgerechnet, im Spiel bestätigt.
- Diddy auf Rattly HD. Nie aufgezeichnete Sprite-Kacheln gehen slot-frei über ihre Referenz ins Pack.
- Windy-Well-Blätter (#5) HD: animierte BG3-Kacheln, der Anim-Export nahm nur BG1/BG2.
- K. Rools Kabine (gfxset 46) neu im Pack.
- Ruckler in Screech's Sprint: Mesen S57 Kachel-Cache, Filter 12,35 → 4,48 ms.

**Nächster Colab-Lauf („King K.“-Run), zusammen exportieren:**
1. **`Seq 26BE` (0xE003) — Dixie fällt auf Rattly (Haare nach oben).** Im Viewer noch ohne HD-Version. Die 70
   Kacheln (Deskriptoren `$0DA4–$0DB8`, gfxset 37, Slot P2) fehlen im Pack. Nicht 0x0120: deren Dixie-Teil
   (120 Kacheln) ist komplett im Pack.
2. **K. Rools Blunderbuss** (0x0251, 0x0258, 0x025F, 0x0261, 0x0263; gfxset 46): 260 Kacheln, im Lauf 14:21 SD.
3. Danach Pack exportieren, vor dem Installieren prüfen lassen (Sprite-Referenzen, Fingerabdrücke).

**Weiter offen:**
- **Spieltest nachholen:** Klobber, Got Prize mit dem Radio und Team-Up nach dem Composite-Umbau (am 02.10.
  nicht getestet).
- **Rest-Ruckler:** In Screech's Sprint liegt die Filterzeit ab ~Frame 290 bei 6,5–7 ms ohne Cache-Fehltreffer
  (unter dem Budget, Ursache offen). Das Diagnose-Log deckt nur die ersten 600 Frames je Kontext ab. Falls es
  stört: Lauf mit `SNES_HD_PERF=1`.
- **Mesen-BG-Recorder merkt sich Kacheln ohne gfxset** (`SnesHdVideoFilter.cpp`, `seenKey`): Eine Kachel, die zwei
  gfxsets teilen, wird nur im ersten aufgezeichnet. Kleine Änderung, noch nicht gemacht.
- N3 übrige SD-Animationen/Gegner (Cat-O-9-Tails u. a., z. T. durch den Fix „nie aufgezeichnet“ erledigt, neu
  spielen und bgcap/spritemiss prüfen), N4 Castle-Crush-Fackeln.
- Nebenbefund `refcheck.py`: 87 Kacheln mit unpassender Referenz (37× Squitters Netz). Erst anschauen, wenn im Spiel
  sichtbar.
- Ghostly Grove (gfxset 30) und Speicherarchitektur: wie unten, unverändert.

---

## (alt) NÄCHSTE SITZUNG (Stand 29.09. abends)

**Installiert:** Pack 29.09. 13:54 (`Downloads\Anim Tiles v2_mesen2_hdpack (2).zip`, 83.663 Dateien), vorher
geprüft: 0 Sprite-Referenzen verloren/geändert, gfxset 39 mit 1113 Hashes + Fingerabdruck 8/8, sonst alle
Fingerabdrücke wie vorher. **Spieltest 29.09. (Mesen S56):** Bramble Blast HD ✔, Cattail-Kopf ✔, Funky-Jet-Icon ✔.
**Neu:** Cat-O-9-Tails noch SD (→ N3). **N1 Klobber und N2 Diddy weiter falsch** — beide analysiert, NICHT gefixt:

### N1 Klobber — Ursache BELEGT
- 4 Fassrand-Kacheln (`ABE09EB101C60D47`, `139A13CD207E78E3`, `68B4BCF83D09C231`, `C51354500AD1F879`, Bild
  `tools/pack_checks/data_2026-09-29/bad5.png`): HD-Kunst = Fass + grüner Rumpf (Export schneidet ohne Maske).
- Klobber ist Composite, Pool = [Klobber-Grün `0041 00A3 …`, Fass `0443 0465 …`]. Referenz im Pack = **Fass**.
  Mesen färbt das Grün über die Fass-Einträge um → Index 11/12 in Klobbers Palette = `3FDF` gelb / `241F` magenta.
- **Auslöser = Viewer `eabf295` (25.09. 12:15, „fair sampling“)**: `bestRefFor()` nahm vorher die ersten 64
  opaken Texel von oben (dort Rumpf → Klobber gewinnt), seitdem 64 verteilte (→ Fass gewinnt knapp). Nachgerechnet
  mit `refpick_sim.py`: alt = Klobber bei allen 4, neu = Fass bei allen 4.
- Mit ALLEN opaken Texeln gewinnt Klobber klar (Mittel 680–964 gegen 2017–3168; 61–76 % der Texel näher an Klobber).
  **Fix-Kandidat (gezielt, kein Vergleichspool):** Gewinner im Composite über alle opaken Texel bestimmen statt über
  64 Stichproben. Vorher prüfen, dass Klomps Schwanz (`617C145BEA9B1CC0`, Grund für eabf295) richtig bleibt und wie
  viele andere Referenzen sich dadurch ändern (Pack-Diff mit `sprpal_diff.py`).

### N2 Diddy Level-Ende — Mechanismus BELEGT, Auslöser OFFEN
- **Korrektur:** „Gfx 14A8“ ist der **Schädelwagen** (Viewer-CHANGELOG Z. 701), nicht Diddy. Der N2-Fix vom 28.09.
  hat den Schädelwagen repariert (494 Kacheln wieder mit Referenz) — war nicht Diddys Problem.
- Diddys Tanz = `DD Got Prize (level end)` 0x0045 (654 Kacheln, alle Ref = Diddy `0466 088A …`, Kunst passt).
  Laut spritecap zeichnet das Spiel **102 davon (das Radio) mit einer reinen Graustufen-Palette** (P3–P7,
  `0000 0842 0C63 … 7FFF`), Liste `data_2026-09-29/radio102.json`. Viewer-Pool für 0x45: nur Diddy (composite=true,
  aber keine Zweitpalette) → Radio im HD braun gebacken, Ref Diddy.
- Mesen färbt die Radio-Kacheln Diddy→Grau um: Radio wird korrekt schwarz, aber die **Gesichts-/Mützenpixel, die in
  den Radio-Kacheln mitgebacken sind**, werden ebenfalls schwarz/weiß. Simulation `data_2026-09-29/sim45.png`
  (links Pack-Kunst, rechts wie Mesen umfärbt) reproduziert den Screenshot.
- **Nicht der Auslöser** (geprüft): Stichproben-Änderung eabf295 (alt und neu → Ref Diddy), Mesen S53–S56 (nur
  BG), Radio in spritecap (schon vor 06.08. aufgezeichnet), HD-Kunst (identisch mit Container-Backup 14.09.).
- **Offen:** was vor Kackle anders war. Kandidaten: Mesen S44–S52 (21.–23.09.: Kantenglättung, Prioritäts-Tie,
  S50–S52 „live palette is the inverse“ = neues Umfärben) — wurde Diddys Level-Ende zwischen 23.09. und 25.09.
  überhaupt gespielt? Nächster Schritt: A/B mit den `ab_*.bat` aus S44/S49/S52 am Level-Ende (Savestate davor),
  bzw. prüfen, ob Mesen die HD-Radio-Kachel ganz zeichnet statt nur an Pixeln, wo das SD-Radio gewinnt.
- Denkbare gezielte Fixes (User entscheidet): Radio-Teil beim Export maskieren (nur Pixel, wo die SD-Radio-Kachel
  deckt) oder für 0x45 die Graustufen-Palette als Zweitpalette hinterlegen.

### Nebenbefund (nicht angefasst, User will keinen Vergleichspool)
`refcheck.py`: 87 Kacheln im Pack, deren Referenz >3x schlechter passt als eine andere Palette
(`data_2026-09-29/bad87.txt`): 37× Squitters Netz (0x02D5–02D7) mit Diddy-Palette, 4× Klobber, Rest meist
weiß/metallische Kunst mit farbiger Referenz. Erst anschauen, wenn im Spiel sichtbar.

### Danach
1. **Windy-Well-Blätter (#5):** wie Gusty Glade (29); Anim-Kacheln je gfxset gescoped → für 51 aus 29 übernehmen.
2. N3 SD-Animationen/Gegner (+ Cat-O-9-Tails), N4 Castle-Crush-Fackeln, N5 Tierfreunde getrennt rendern
   (gleiches Grundproblem wie N1/N2: Composite als EIN Bild hochgerechnet und ohne Maske geschnitten).

**Entscheidung offen — Ghostly Grove (gfxset 30):** läuft im Spiel in HD, weil Mesen es als Gusty Glade (29)
erkennt (gleiche Grafik). Das eigene Set 30 (Import 25.09., ohne Metadaten) ist nie im Pack. Bewusst NICHT neu
importiert: sonst würde GG als 30 erkannt und nutzte dessen Kunst. Später gezielt klären, ob GG eigene Unterschiede hat.

**Geparkt — Speicherarchitektur:** Container liegt in IndexedDB des Browsers (Edge, `file://`-Pfad des Viewers),
unsichtbar für Diagnose, ohne Sicherung/Verlauf. Idee: Container als Ordner auf der Platte (File System Access
API, funktioniert auch in Edge; Zugriff lässt sich dauerhaft erlauben). Kein Performance-Gewinn, eher Transparenz
und Sicherheit. User denkt noch nach. Bis dahin: gelegentlich Container-ZIP-Export als Sicherung.

---

## SPIELTEST 28.09. abends (Pack 20:50, Mesen S56) — ERLEDIGT + neue Issues

**Bestätigt sauber:** Haunted Hall komplett HD inkl. Kackle; Rickety Race, Target Terror, Klobber Karnage (Level),
Arctic Abyss; Castle Crush Laufband-Boden jetzt HD. Damit sind #1–#4 und #7 der Liste unten erledigt.

| # | Wo | Befund | Vermutung |
|---|---|---|---|
| N1 | Klobber Karnage | **Klobber (Sprite): Farbfehler an einigen Kacheln** — war vorher richtig | Regression; Sprite-Referenzpalette? |
| N2 | Level-Ende (Radio-Animation) | **Diddy: Farbfehler im Gesicht** — war vorher richtig | 29.09.: „Gfx 14A8“-Fix betraf den Schädelwagen, nicht Diddy; Mechanismus siehe oben (Radio-Kacheln) |
| N1b | — | Klobber-Daten im Pack identisch mit 25.09. | Ursache nicht im Sprite-Pack → Screenshot nötig |
| N3 | diverse Level | **Einige Diddy-/Dixie-Animationen und Gegner in SD** | Daten sollten in den Logs dieses Laufs stehen (spritecap/spritemiss) → in den Viewer |
| N4 | Castle Crush | **Wandfackeln SD** (Boden jetzt HD) | Laufzeit-Animation; bgcap? |
| N5 | Tierfreunde (Rattly u.a.) | **Darstellungsfehler: Upscale hat Tier MIT Kong als ein Bild hochgerechnet** → Kacheln vermischt | Viewer muss Tier- und Kong-Sprite für den Upscale getrennt rendern |
| #5 | Windy Well | Blätter im Vordergrund SD (wie Gusty Glade, dort HD) | offen (unten) |

---

## SPIELTEST 28.09. nachmittags (Pack 13:38, Mesen S56) — gefundene Issues

Vorgeschichte: Alles unten war VOR dem Kackle-Import (25.09.) sauber. Ursache des Rückfalls: Sets wurden am
25.09. mit Metadaten eines anderen Levels gespeichert (Pirate Panic im Viewer-Speicher; 34 und 48 vertauscht).
BG1 ist per `repairSetMetadataFromRom` repariert (Fehler 4–8 statt 60–146). Die SD-Exporte vom 25.09. sind
richtig (auch BG2/BG3: TT Rummelplatz, AA Eis, HH Kackle) — kaputt ist das Zerschneiden im Pack-Export.

| # | Level (gfxset) | Befund | Stand / Vermutung |
|---|---|---|---|
| 1 | Rickety Race, Target Terror (34) | BG1 HD ✓. **Hintergrund falsch, sieht aus wie Pirate Panic** | BG2/BG3-Kunst richtig, Tilemap/Adressen beim Pack-Export falsch |
| 2 | Arctic Abyss (47) | **Hintergrund falsch, wie Pirate Panic** | wie 1 |
| 3 | Haunted Hall (44) | **Hintergrund SD** | wie 1 (Messung BG2/BG3 44: Fehler 155/250) |
| 4 | Haunted Hall (44) | **Kackles Körper blau-transparent**; Kopf erstmals HD, Hände nur teilweise HD | offen (Körper liegt auf BG2 → evtl. wie 1) |
| 5 | Windy Well (51) | BG1+BG2 ✓. **Wehende Blätter im Vordergrund SD** — dieselben wie Gusty Glade (29), dort HD | Anim-Kacheln sind je gfxset gescoped → für 51 fehlen sie |
| 6 | Castle Crush (43) | **Laufender Boden unten teils SD, Wandfackeln SD** | Laufzeit-Animation, evtl. fehlen bgcap-Aufnahmen |
| 7 | Klobber Karnage (48) | nicht gespielt | BG2 im Pack jetzt leer |

---

## (alt) NÄCHSTE SITZUNG (26.09.) — Haunted Hall reparieren — überholt 28.09.

1. **Ground-Truth entschärfen** (`saveCurrentHDToContainer`, ~Z. 11557): nie über einen vorhandenen
   Container-Abzug schreiben; mit BG-Aufnahme gegenprüfen. Befund und Tabelle: CHANGELOG 25.09. spät.
2. **Set 44:** frischer VRAM-Dump aus Mesen in Haunted Hall → im Viewer für gfxset 44 importieren.
3. **Pack neu**, Test Haunted Hall: Kackle HD, Level bleibt HD während Kackle animiert; im Log
   `gfx=44` durchgehend. Rickety Race / Target Terror mitprüfen (gfxset 34).
4. Danach die zwei uncommitteten Viewer-Fixe (Export-Sperre, Fingerabdruck) committen + pushen.

Upload-Dateien: `snes_hd_spritecap.txt` (vollständig) und `snes_hd_bgcap_GESAMT_fuer_Viewer.txt`
(der Viewer ERSETZT beim Laden; neue Läufe erst zusammenführen).

---

## Stand der Repos

| Repo | Zustand |
|---|---|
| `Mesen2-SNES-HD_Projekt` | `feature/hd-compositing-engine` = **`b134e800`** (S49) **gepusht**. Working tree leer. Im Spiel getestet, `build=S49`. |
| `DKC2-HD-Tools` | `main` = **`dc490bb`** gepusht. Nur diese Datei untracked (Arbeitsdokument, bewusst so). **Am Viewer wurde nichts geändert.** |

---

# ⏸ BARREL BAYOU — GEPARKT am 23.09.

Zwei Tage, **keine Bildverbesserung**. Was daran belastbar ist, steht hier; was widerlegt
wurde, steht darunter, damit es nicht wiederkommt.

## Was gesichert ist

| # | Befund | Beleg |
|---|---|---|
| 1 | **Mesen zeichnet die HD-Kunst bitgenau.** Die Emulatorseite ist aus dem Rennen. | S48-Framebuffer-Dump (1024×896, exakter Ausgabepuffer): 35 von 40 Pack-Kacheln wiedergefunden, Abweichung **0,000**. Zusätzlich vom User per HD-An/Aus bestätigt. |
| 2 | **Es gibt keine Lücke zwischen „gefunden“ und „gezeichnet“.** | S45b: alle drei Ebenen **100 % gezeichnet**, Summe exakt `hdMatch`, `clip=0 noSampler=0 alpha0=0 subOp=0`. |
| 3 | **Ein Pack-Ordner liess sich nicht abschalten** — `std::stoul("38_aus")` ergibt 38. Zwei Ausschaltversuche waren nie in Kraft; darauf war die ganze Diagnose vom 21.09. gebaut. | `SnesHdPackLoader.cpp:311`. Quittung: `TileByKey` blieb bei 56515. Mit entferntem Ordner: 56294, `miss` 0 → 24.584, `hdBG3` → 0. **Gefixt in S46.** |
| 4 | **Die Quelle hat fast keinen Kontrast.** Darum bleiben die Flächen leer und nur das Kachelraster ist sichtbar. | Quelle BG3 gfx26: **84,1 %** der Nachbarpixel identisch, mittlerer Nachbarunterschied **1,15** von 255. Pirate Panic: 42,9 % / 10,25. Ergebnis: **5,5 %** Detailanteil gegen **61,2 %**. |
| 5 | **Der Upscale glättet über Kachelgrenzen, das Pack holt ~40 % davon zurück.** Prinzipbedingt: eine Fassung je Inhalts-Hash, 223 Dateien für 1021 Szenenzellen. | Tonsprung Grenze÷innen: nativ **4,74**, Upscale **1,91**, Pack-Prinzip **2,62**. Nur 5,5 % der Szenenzellen liegen bitgenau im Pack. |
| 6 | **Die Transparenz ist NICHT die Ursache.** | 80,1 % der BG3-Kachelgrenzen sind beidseitig voll deckend, dort sitzen **75 %** des Farbsprungs. |
| 7 | **Sprite-Ränder und Kachelnahte sind verschiedene Dinge.** Sprite-Rand = Silhouette gegen eine andere Ebene → Alpha-Blend glättet (`SnesHdVideoFilter.cpp:1996`). Kachelnaht = zwei DECKENDE Kacheln derselben Ebene → kein Blend möglich, weiche Ränder ergäben eine Lücke. Stetigkeit dort ist eine **Inhalts**-, keine Darstellungsfrage. | Code + Messung 6. |
| 8 | **Die BG-Glättung kommt aus dem Upscale, nicht aus Mesen.** `HdSmoothSpriteEdges` (S44) ist ein reiner Sprite-Schalter. Mesen zeichnet weiche BG-Kanten längst. | Vom User richtiggestellt; Blend-Pfad im Code bestätigt. |

## Was WIDERLEGT wurde — nicht wiederholen

| Hypothese (meine) | Widerlegung |
|---|---|
| `noSampler` verwirft 2bpp-Kacheln | Alle 223 PNGs sind 32×32; `7*4+4 = 32`, `32 > 32` ist falsch. Tor kann nicht feuern. |
| `alpha0` — Kunst sei transparent | 52 Kacheln vollflächig deckend, 171 gemischt, **keine** komplett transparent. |
| `bg3.png` sei ein ungepolsterter **Atlas** | Es ist eine **Szene**: 1017 von 1024 Zellen belegt, 387 verschiedene Kacheln, 75 % Wiederholungen. Die echten Nachbarn waren da. |
| Beim **Zuschneiden** gehe viel verloren | Fassungen derselben Kachel unterscheiden sich im Mittel **0,93** von 255 (Rand 1,18 / innen 0,56). Real, aber winzig. |
| Die **Helligkeit** sei der Treiber | Über acht Gfxsets **r = −0,30**. gfxset_03 ist bei Helligkeit 63,8 detailärmer als Pirate Panic bei 29,8. |
| Der **Paletten-LUT** verfälsche die Farben | Für gfx38 exakt Identität (alle Verhältnisse 256). Greift gar nicht. |
| **Kachelnaht am Steg und BG3-Pixeligkeit haben dieselbe Wurzel** | **Nein.** Cluster-Fassungen desselben BG1-Blocks sehen praktisch gleich aus (Rand 1,66 / innen 0,82; die 15 Fassungen von Block 261 sind mit blossem Auge identisch). Der Cluster-Kollaps erklärt die Naht **nicht**. Der User hat auf der Trennung bestanden — zu Recht. |

## Was bliebe, wenn wir es wieder aufnehmen

- **BG3 Barrel Bayou:** sichtbar besser wird es nur über die Kunst — Kontrast **vor** dem
  Upscale anheben und danach zurückrechnen, oder Handarbeit. Gestaltungsentscheidung, kein
  Fehler in der Kette.
- **Kachelnaht am Steg:** Ursache **unbekannt**. Statistik über 195 Blöcke findet keinen Defekt
  an EINER Stelle. **Gebraucht wird der Screenshot der Naht** (Spiel und Viewer) oder die
  Laufzeit-Karten-ID der betroffenen Kachel — so wie `G32-16x32-P4-C236` beim Kleever-Hook,
  das den Fall in einer Minute löste.
- **Schlafender Fehler:** der Paletten-LUT rechnet sein Verhältnis über die Palettenein­träge
  **1–15**, obwohl eine 2bpp-Kachel nur **1–3** nutzen kann (`SnesHdVideoFilter.cpp:~2300`).
  In Barrel Bayou schläft er (Referenz == Live). In einem Level mit nachbearbeiteter Palette
  würde er die 2bpp-Ebene verfärben. **Nicht behoben, eigener Test nötig.**
- **Aufräumen im Viewer-Export (unabhängig, klein):** im Manifest trägt **jeder** der 292
  Blöcke `"layer": "bg1"`, deshalb liegt die BG2-Kunst in `bg1/` und `bg2/gfxset_38` hat eine
  einzige Datei. Harmlos — der BG1↔BG2-Retry fängt es über den ContentHash **korrekt** auf,
  zieht also keine falsche Kunst.

## Methodische Lehren dieser zwei Tage

1. **Ein Ausschaltversuch braucht eine Quittung** — eine Zahl, die sich ändern MUSS. Hier:
   `TileByKey`. Ohne sie ist ein Negativergebnis kein Befund, sondern ein ungeprüfter Test.
2. **Ein Mustertreffer ohne Trennschärfe ist kein Beweis.** „Korrelation 0,997, Abweichung
   0,4“ stand auf Kacheln, bei denen HD und nativ um 0,57 von 255 auseinanderliegen. Immer
   BEIDE Hypothesen an der Fundstelle messen.
3. **Ein Fensterfoto ist kein Messmittel.** Massstab 4,1836 verwischt das native Pixelraster,
   also genau das Signal. Framebuffer holen (S48), nicht das Fenster fotografieren.
4. **Der Mittelwert versteckt den Befund.** Cluster-Fassungen: Mittel 1,66 — aber acht Blöcke
   liegen bei 5–10 mit Spitzen von 179. Immer auch die Verteilung ansehen.
5. **Wenn der User auf einer Unterscheidung besteht, hat er meistens recht.** Zweimal an
   diesem Tag: beim Trennen der Themen und beim Nachhaken zur gemeinsamen Wurzel.

---

## ❌ ERLEDIGT UND VERWORFEN: Overlay-Franse — zweimal gemessen, zweimal unsichtbar

**Nicht wieder aufbauen.** Am 23.09. zum zweiten Mal geprueft, gleiches Ergebnis wie im
September: der User war in Mainbrace Mayhem und Lockjaw's Locker und sieht keinen Unterschied.

**Richtigstellung meiner eigenen Notiz.** Ich hatte geschrieben „Overlay-Level bekommen gar
keine Kanten, 2.225 ungeglaettete Pixel je Frame“. Falsch. Ueber 2.301 Overlay-Frames gemessen:

| | je Frame |
|---|---|
| `sprHdSub` — Figuren MIT HD-Kunst ueber den Operanden | **1.581** |
| `sprEdge` — Franse | 459,8 |
| Frames ganz ohne Franse | **810 von 2.301 (35,2 %)**, dort `sprSubHd ≈ 2.951` |

Die Figuren sind dort **HD mit harten Umrissen**, nicht nativ. Es fehlt nur der weiche Rand —
und der ist duenn: `sprEdgeBlend/sprEdge` liegt bei 1,05 gegen 2,6 in normalen Kontexten.

**Mechanismus (bestaetigt, aber wirkungslos zu beheben):** beide Stellen, die Slot 2 fuellen,
haengen an `drawMain` (`SnesPpu.cpp:1276`, `:1307`); bei `Main=$04` ist OBJ nicht auf dem
Main-Screen.

**Vorgeschichte:** S25 (`4482908a`) hat es gebaut — 747 Subpixel/Frame in Mainbrace, 720 in
Lockjaw — und `18f6381f` hat es nach fuenf A/B-Laeufen über 3.634 Frames wieder entfernt.
Neu ist eine Tatsache, die nichts aendert: die damalige Begruendung („Operand wird addiert und
oft halbiert“, als Vermutung markiert) ist zur Haelfte widerlegt — **`Halve=0` in allen drei
Overlay-Kontexten** (`E10E4686511EB716`, `BD2C76B73C545997`, `F4AE27740B28F473`).

**Folge fuer den geplanten Umbau (zweiter Durchgang statt Ground-Suche):** die Overlay-Blindheit
faellt als Begruendung weg. Es bleiben die Ground-Suche (21 % der Suchen laufen leer) und der
Wegfall von neun Commits Sonderfaellen — kein sichtbarer Gewinn, nur weniger Code. **Damit ist
der Umbau derzeit nicht begruendet.**

---

## ☁ GEPARKT: Optimierung des BG-Umfaerbers (S52) — vermessen, nicht gebaut

**Stand:** S52 laeuft, der User hat viele Level gespielt, alle sehen richtig aus. Von
**16.069 Frames** liegen **2** ueber dem 16,7-ms-Budget (0,01 %), Median ueber alles
**2,88 ms**, p99 13,11. Beide Ausreisser in **gfxset 37** (Krow's Nest / Mainbrace Mayhem,
17,20 und 17,46 ms), dort auch der hoechste Median (~8 ms) und p95 (~14 ms).
Kontexte, die vor und nach S52 vorkommen: **+2,7 % bis +18,2 %**.
→ **Gruener Bereich. Optimierung nicht noetig, nur dokumentiert.**

### Was gemessen wurde, damit es niemand wiederholt

`HdSpriteRecolor::Apply` sucht je Texel die naechste von 15 Referenzfarben. Drei Wege wurden
an der echten Pack-Kunst durchgerechnet:

| Variante | Ersparnis | exakt? | Urteil |
|---|---|---|---|
| **Farbcache** (haeufigste Farben merken) | 4096 Eintraege bedienen nur **41–47 %** der Texel | ja | **untauglich** — hochgerechnete Kunst hat **80.000–100.000** verschiedene Farben je Gfxset, da wiederholt sich kaum etwas |
| **Tabelle auf 5 Bit gerundet** | **Faktor 80–190** weniger Suchen | **NEIN** | **untauglich** — 6,74 % der Texel bekommen eine andere Referenzfarbe, dort Abweichung Median **41**, p95 140, max **231** von 255. Bei invertierter Palette liegen Nachbarfarben nah, ihre Live-Entsprechungen weit auseinander → sichtbare Sprenkel |
| **Tabelle nur fuer eindeutige Eimer** | nur **15–33 %** Trefferquote | ja | schwach — die Palettenfarben liegen zu dicht, die meisten Eimer schneiden eine Entscheidungsgrenze |
| **★ Nachbarpruefung** | **35–62 %** der Suchen entfallen | **ja** | **die einzige brauchbare.** Zuerst den Index des Nachbartexels pruefen; liegt der Abstand unter dem halben kleinsten Palettenabstand, ist er BEWEISBAR der naechste |

Trefferquoten der Nachbarpruefung je Gfxset: **3 → 35,5 %**, **7 → 61,5 %**, **38 → 40,0 %**.
Raumliche Kohaerenz allgemein: 69–79 % der Texel haben denselben Index wie ihr Nachbar.

**Wenn es je gebraucht wird:** Nachbarpruefung einbauen (ein paar Zeilen, aendert kein Pixel),
erwartbar ein bis zwei Drittel der Suchen weg. Die beiden Tabellenvarianten sind erledigt.

### Bekannte Grenze, die dabei aufzuraeumen waere
`Apply` sucht ueber die Palettene­intraege **1–15**, eine 2bpp-Ebene kann nur **1–3** nutzen.
Derselbe Zaehlfehler steckt im R3-LUT (Verhaeltnis ueber 1–15). Wer einen aufraeumt, raeumt
beide auf.

---

## ▶ NÄCHSTE SITZUNG — andere Baustellen

### 1. ~~Den Kleever-Hook im Spiel prüfen~~ — ✅ ERLEDIGT (23.09.)

**Vom User abgeschlossen.** Die fehlende siebte Kachel (`6AA148E3AD83BEA2`, kein Zwilling in
spritecap, in keiner Aufzeichnung auffindbar) wird er zusätzlich durch den Upscaler schicken —
damit ist die Lücke geschlossen. Der OAMCAP-Lauf, der unten als nächster Schritt stand, wird
**nicht** mehr gebraucht. Historie darunter bleibt stehen.

<details><summary>Historie (Anlauf 1 und 2)</summary>


**Zweiter Anlauf.** Der erste (17 Kacheln, 15:06) ließ den Hook unten zu 25 % SD — mein
`MAX_SHIFT = 2` war eine Verallgemeinerung aus einem Beispiel, die untere Kachel sitzt bei
`dx = −3`. Jetzt `MAX_SHIFT = 5`: **19 Kacheln im Pack, davon 6 der 7 Hook-Kacheln**.
Die siebte (`6AA148E3AD83BEA2`) hat keinen Zwilling in spritecap.

**Test 16:13: genau eine Kachel unten links bleibt SD** — wie vorhergesagt. Erschöpfend
geprüft und ausgeschlossen:

- **Rekonstruktion über den Hash.** FNV-1a nachgebaut und an 3000/3000 spritecap-Zeilen
  verifiziert; die Konstruktion reproduziert exakt die sechs vorhandenen Kacheln. Für
  `6AA148E3` ergibt sie nichts — auch nicht mit allen 44.243 spritecap-Kacheln als Nachbar
  (einziger Treffer `dx=+7`, also 7 Spalten vom Nachbarn: entartet).
- **Vertikaler Versatz.** Voller 2D-Test (dx,dy −7..+7) für alle sieben Hook-Kacheln:
  32.575 Kandidaten mit `dy ≠ 0`, aber **kein einziger mit über 30 überlappenden Pixeln**.
  Kein echter vertikaler Zwilling.

**Schluss: die fehlende Kachel steht in keiner Aufzeichnung** — weder mit Bytes in spritecap
noch als Hash in diag oder spritemiss. Sie erreicht keinen der vier Sprite-Slots, ist also im
selben blinden Fleck wie seinerzeit das Bonusfass-Emblem.

**Nächster Schritt dafür:** ein Lauf mit `SNES_HD_OAMCAP=1` im Kleever-Kampf. Die
OAM-Aufzeichnung listet die Objektzusammensetzung und nennt die Kachel direkt, unabhängig
davon, ob sie je in einem Slot war. Aus einem frischen PowerShell-Fenster:

```powershell
$env:SNES_HD_OAMCAP="1"
& "C:\DEV Claude\Mesen2-SNES-HD_Projekt\bin\win-x64\Release\Mesen.exe"
```

Danach `snes_hd_oam.txt` liefern; mit der Kachel-Identität lässt sich die Ableitung rechnen,
ohne dass die Kachel je erfasst werden muss. **Kein Build nötig**, es sind reine Pack-Dateien — Mesen normal starten
(Doppelklick), Kleever-Kampf, die Haken über der Lava ansehen. Sie müssen jetzt genauso
aussehen wie in Gangplank Galley.

Geht etwas schief: `derived_manifest.json` in `tools/shifted_tiles/` listet jede geschriebene
Datei, und eine Sicherung der alten `sprite_palettes.bin` liegt im Session-Scratchpad.

### 2. Sonstiges

**S43 und S44 sind durch.** S43 (Lauf 11:45): Franse je Frame deckungsgleich mit dem
Schalterlauf um 10:28, Frame-Zeit Median **2,76 ms** (S42 2,82, S41 2,95), `spritemiss` nur
50 Zeilen, Lockjaw (Unterwasser-Farbmath) sauber. **S44: die Checkbox wirkt live, ohne
Neustart** — Einstellungen → SNES → „Smooth HD sprite edges".

**Damit gibt es zum ersten Mal ein A/B am laufenden Bild.** Das ist für die nächsten Fragen
das wichtigere Werkzeug als jeder Zähler: die letzten Wochen sind mehrfach daran hängen
geblieben, dass Zähler sagen WIE VIEL und nur das Bild sagt WAS. Bei jeder künftigen Meldung
„sieht kantig aus" also zuerst: Haken raus, Haken rein, hinsehen.

**Danach steht der zweite Durchgang an** (Abschnitt weiter unten) — jetzt mit zwei Gründen:
die Ground-Suche **und** der Prioritäts-Gleichstand (14,3 % der Franse, im Kleever-Kontext
jeder fünfte Kandidat).

---

</details>

## ★ GEKLÄRT 21.09.: der Kleever-Hook ist dieselbe Kunst, **um 1 Pixel versetzt**

**Frage war:** warum hat der Hook im Kleever-Kampf einen anderen Content-Hash als derselbe Hook
in anderen Leveln, wo er längst HD ist?

**Antwort:** Das ROM enthält eine **zweite Kopie der Hook-Kunst, horizontal um genau ein Pixel
verschoben**. Das 8×8-Raster schneidet dieselbe Grafik eine Spalte weiter, jede Kachel bekommt
dadurch andere Bytes — und damit einen anderen FNV-Hash.

**Beleg:** Die Laufzeit-Karte `G32-16x32-P4-C236` (vom User in der Kleever-Laufzeitansicht
gefunden) führt auf `C2368B86616E9F60`. Gegen die Gangplank-Kachel `6D34E59BBCEBD3DE` geprüft:

| Versatz | überlappende Pixel | Index gleich | Deckung gleich |
|---|---|---|---|
| **dx = −1, dy = 0** | 56 | **100,0 %** | **100,0 %** |
| dx = 0 | 64 | 43,8 % | 87,5 % |
| dx = −1, dy = ±1 | 49 | 49,0 % | 89,8 % |

Die Suche über alle 44.225 spritecap-Kacheln nach dieser Beziehung
(`K[y][1..7] == G[y][0..6]`) findet **4 der 7 Hook-Kacheln** als Paar:

| Gangplank (HD vorhanden) | Kleever (1 Px rechts) | erfasst | HD-Kunst |
|---|---|---|---|
| `6D34E59BBCEBD3DE` | `C2368B86616E9F60` | P3, P4 | **nein** |
| `0D77F83A30A48735` | `D40681AD2F80EC0D` | P3, P4 | **nein** |
| `0EC78EA4FD9B3DE7` | `47CC0BB72F529E54` | P3, P4 | **nein** |
| `286773B77EC44DDD` | `A1B38551AA40D609` | P3, P4 | **nein** |

Die restlichen 3 fehlen vermutlich nur in spritecap (noch nie in einem Lauf erfasst) — beim
nächsten Kleever-Besuch prüfen.

**Warum die früheren Suchen nichts fanden:** ich hatte auf Index-Permutation, Spiegelung und
Pixeldistanz geprüft — alles Transformationen, die das Raster **nicht** verschieben. Ein
Sub-Kachel-Versatz fällt durch jedes dieser Netze.

### Der Hash lässt sich nicht teilen — die Kunst schon

Der Hash wird aus dem Inhalt gebildet, und der Inhalt ist wirklich verschieden. **Aber die
HD-Kunst lässt sich exakt neu zuschneiden, ohne zweiten Upscale:**

Bei 4× entspricht der 1-Pixel-Versatz genau **4 HD-Pixeln**. Für jede Kleever-Kachel gilt:

```
neu[:, 4:32] = quelle[:, 0:28]            # die Gangplank-Kachel, 4 Px nach rechts
neu[:, 0:4]  = linkerNachbar[:, 28:32]    # die 4 Spalten, die von links hereinwandern
```

Am linken Rand des Objekts ist die einwandernde Spalte transparent. Der linke Nachbar lässt
sich aus den Daten bestimmen: gesucht ist die Hook-Kachel, deren Spalte 7 gleich Spalte 0 der
Kleever-Kachel ist.

**Vorteil gegenüber einem zweiten Upscale:** beide Haken sehen danach **per Konstruktion**
identisch aus, und es kostet keine Upscale-Runde. **Nachteil:** es braucht ein kleines Werkzeug,
das den Zuschnitt macht und `<kleever_hash>_P<slot>.png` schreibt.

**Alternative ohne neues Werkzeug:** die Karte `G32-16x32-P4-C236` im Viewer regulär
exportieren, upscalen, importieren. Einfacher, aber die beiden Haken wären zwei unabhängige
Upscales und könnten minimal verschieden aussehen.

**Offen: welcher Weg.** Und: beide Fassungen brauchen ohnehin einen Slot-Eintrag — die
Kleever-Kacheln sind unter P3 und P4 erfasst, also exportierbar.

---

## ★ ABGESCHLOSSEN 21.09.: der Herkunfts-Gate ist gemessen und entfernt (S42/S43)

### Die Kunst war es nie

| Stufe | weiche Texel (Alpha 1–247) |
|---|---|
| Upscale-Ausgabe `..._hd4x_edge.zip` | 1,9 % aller Texel, **0,49 je deckendem** |
| Installierter Pack, dieselben Kacheln | 14,4 % der Kachelfläche, **0,38 je deckendem** |
| 400 zufällige andere Sprite-Kacheln | 0,18 je deckendem |

Gegen die SD-Quelle aufgeteilt (158 Bildpaare): **27.867 weiche Texel, 75,7 % innerhalb der
nativen Silhouette, 24,3 % außerhalb.**

### Die Ursache war ein Gate

162 der 1.159 seit dem 18.09. neuen Kacheln haben keine Referenzpalette — **alle 18
Splitter-Objektpräfixe darunter** (übriger Pack: 1,4 %). Daran hingen **alle drei**
Glättungspfade. S21 (`2756fa1c`) nennt es ausdrücklich einen **Herkunftstest, keinen
Farbtest**. Für Laufzeit-Kunst war die Glättung damit dauerhaft aus, und die Splitter sind das
erste Objekt, das komplett über diese Kategorie kam.

### Lauf 1 — 09:04 Referenz (S41, 11.658 Frames) / 09:36 mit Schalter (S42, 17.482 Frames)

**56,2 % der gesamten Sprite-Fläche** ohne Referenzpalette. Franse pro Frame:

| Kontext | Frames A/B | Franse S41 → S42 | Faktor |
|---|---|---|---|
| `$13/$14/$23` | 707/1199 | 644 → **7.725** | ×12 |
| `$13/$04/$23` | 3/606 | 83 → **6.990** | ×84 |
| `$11/$00/$00` (Weltkartenprofil) | 606/1246 | 1.254 → **5.260** | ×4,2 |
| `WORLDMAP $11/$00/$00` | 0/772 | — → **5.643** | nur S42 |
| `$17/$00/$07` | 8990/9738 | 1.326 → 1.365 | ×1,03 |

**Die Weltkarte ist der Fall, für den der Gate gebaut wurde.** August: 898.087 Subpixel/Frame =
**97,9 % des Schirms**, ausgewaschen. Jetzt: **5.643 = 0,6 %**, Faktor 159 darunter, und der
User sieht sie sauber. Nicht leer: `SPRAREA` weist dort nur **33,1 % bzw. 51,9 %** der
Sprite-Fläche eine Referenz zu.

### Lauf 2 — 10:28, SPRWATCH auf acht Splitter-Hashes, 705 Frames

| | Pixel | im Pack |
|---|---|---|
| Silhouette (Slot 0) | 16.035 | **100,0 %** |
| **Franse (Slot 2)** | **43.638** | **100,0 %** |
| Verdrängtes Sprite (Slot 3) | 715 | **100,0 %** |
| `wonMain` | 15.946 von 16.035 | 99,4 % |

Die Franse ist das **2,7-fache der eigenen Silhouette**. Kein `fringe=0/0` wie beim Bonusfass —
Erfassung und Kunst sind beide da, der Gate war die einzige Sperre. **S43 entfernt ihn.**
Notausgang bleibt `SNES_HD_NO_SPRITE_EDGES=1`.

### ⚠ Ein Irrweg, der dokumentiert gehört

`sprFrTie` steigt in den Splitter-Frames um **+60,9/Frame**, SPRWATCH beziffert den Beitrag der
Splitter auf **+61,9/Frame** — 98 % Deckung, sah nach Beweis aus, dass der Gleichstand ihre
Franse frisst. **Die Gegenprobe pro Frame hat es umgeworfen** (`r = −0,148`, Bänder
widersprüchlich). Kontrollrechnung: Splitter-Silhouette gegen `sprHd` müsste Steigung 1 haben,
liefert **3,96** — in den Todesframes skaliert der ganze Bildinhalt mit. Zwei zufällig gleiche
Gruppenmittel.

**Merke: eine Übereinstimmung zweier Aggregate ist erst ein Befund, wenn sie die Auflösung pro
Frame überlebt.**

---

## ★ OFFEN UND NEU: der Prioritäts-Gleichstand kostet 14,3 % der Franse

| Kontext | Frames | Franse gefunden | abgelehnt | Verlust |
|---|---|---|---|---|
| `$17/$00/$07` (Kleever) | 5.145 | 980 | 230 | **19,0 %** |
| `$13/$14/$23` | 855 | 1.422 | 77 | 5,1 % |
| `WORLDMAP $11/$00/$00` | 325 | 1.613 | 86 | 5,1 % |
| `$11/$00/$00` | 509 | 1.623 | 37 | 2,2 % |
| **Gesamt** | **7.229** | **1.074** | **179** | **14,3 %** |

Zweig: `Sprites[2].Priority <= (MainScreenFlags & 0x0F)` — die Franse eines Sprites über einem
Sprite **gleicher** OBJ-Priorität. Der S23-Kommentar sagt es wörtlich voraus: *„A large number
here means equal priorities are common and the tie-break has to come from OAM order after
all."* Trifft jede Überlappung zweier Sprites derselben Priorität, nicht nur die Splitter.

**Im heutigen Pro-Pixel-Modell gibt es die OAM-Reihenfolge nicht.** Der zweite Durchgang unten
hätte sie, weil er in Reihenfolge malt — das ist ein zusätzlicher Grund für den Umbau.

---

## ★ S49 IST GETESTET — richtig, aber unsichtbar. Und das verschiebt den Umbau-Grund.

**Lauf 14:46, `build=S49`, 6.164 Frames.** Der Mechanismus greift:

| | je Frame |
|---|---|
| `sprEdge` (gezeichnete Franse) | 907,4 |
| `sprFrTieWon` (Gleichstand aufgelöst, jetzt gezeichnet) | **51,8** |
| `sprFrTie` (Gleichstand weiter verworfen) | 69,4 |
| **Anteil der Gleichstände aufgelöst** | **42,7 %** |

**Das sind gut 6 % mehr Franse — unterhalb der Wahrnehmungsschwelle.** Der User: „kein
merklicher Unterschied, aber nichts schlechter geworden.“ Genau das sagen die Zahlen.

**Die alte Zahl „14,3 % Verlust“ war nicht falsch, aber sie zählte KANDIDATEN, nicht sichtbare
Pixel** — und rund die Hälfte davon lag wirklich hinter dem Gewinner, wurde also zu Recht
verworfen. Das Tor ist jetzt hardwarerichtig; mehr war dort nicht zu holen.

**Behalten, weil generisch:** keine Level-Erkennung, kein Fingerprint, kein Sonderfall — eine
Eigenschaft der SNES-OBJ-Darstellung. Es führt die FETCH-Reihenfolge mit, nicht den rohen
OAM-Index, und erbt damit Mesens Behandlung der OAM-Prioritätsrotation. Rückfall jederzeit per
`SNES_HD_NO_OAM_TIEBREAK=1` bzw. `ab_no_oam_tiebreak.bat`.

### ★ DER EIGENTLICHE VERLUST LIEGT WOANDERS — im selben Lauf gemessen

| Umbau-Argument | Messung (6.164 Frames) |
|---|---|
| Ground-Suche läuft leer | **21,0 %** — 388 von 1.851 Suchen je Frame |
| **Overlay-Level bekommen GAR KEINE Franse** | **686 Frames** mit HD-Sub-Sprites und `sprEdge = 0`, dort **2.225 HD-Sub-Sprite-Pixel je Frame völlig ungeglättet** |

**Das ist 43-mal so viel wie der Gleichstand gebracht hat**, und es ist nicht verstreut, sondern
sitzt konzentriert in **einem** Kontext: **`Main=$04 / Sub=$13 / CM=$24`, gfxset 37**. OBJ ist
per HDMA vom Main-Screen genommen, die Figuren kommen nur über die Farbmath zurück — dort
greift die Glättung nicht schwach, sondern **null**.

→ **Die Begründung für den Umbau steht damit auf einem anderen Bein als bisher notiert: nicht
der Prioritäts-Gleichstand, sondern die Overlay-Blindheit.** Der Gleichstand ist erledigt.

---

## ★ BESTANDSAUFNAHME 23.09. — was heute tatsächlich im Code steht

**Frage des Users: „Ich dachte, wir hätten das schon so gemacht.“ — Nein. Aber der Eindruck
hat eine handfeste Quelle.**

### Warum es so aussieht, als wäre es schon zwei Durchgänge
`SnesHdData.h:146` sagt wörtlich **„Two-pass approach (like NES)“**. Diese zwei Durchgänge sind
aber **PPU-Aufzeichnung → Filter-Rendern**, nicht der Maleralgorithmus. Dazu kommen **vier
Sprite-Slots**, die wie Ebenen aussehen. Beides zusammen liest sich wie ein Schichtmodell.

### Was wirklich läuft: EIN Durchgang
`RenderHdRows` ist `for y { for x { alles } }`. Pro Pixel werden BG-Gewinner, Sprite-Gewinner,
Sub-Operand, Franse und alle Gründe aufgelöst, dann in der `hdScale×hdScale`-Subpixelschleife
komponiert. Kein zweiter Durchgang über Sprites, nirgends.

### Die vier Slots (alle im selben Pixelschritt ausgewertet)
| Slot | Inhalt | Herkunft |
|---|---|---|
| 0 | Sprite, das den **Main**-Screen gewinnt | S1, `SnesPpu.cpp:1281` |
| 1 | Sprite, das den **Sub**-Screen gewinnt | S1, `:1297` |
| 2 | **Franse-Kandidat** — Identität auch an nativ TRANSPARENTEN Pixeln | S21/S23, `:1267` und `:1308` |
| 3 | **verdrängtes** Sprite darunter („der Grund“) | S22, `:1231` |

### ★ DER FUND: die OAM-Reihenfolge ist da und wird weggeworfen
`SnesPpu.cpp:903` sagt es selbst: *„sprites are fetched in OAM order“*. Und
**`SpriteInfo.Index` (`SnesPpuTypes.h:25`) trägt den OAM-Index genau an der
Aufzeichnungsstelle** in `FetchSpriteTile`. Verworfen wird er zweimal:

1. Die Zeilenpuffer verdichten auf **einen** Eintrag je Pixel.
2. Die Franse-Auswahl entscheidet nur nach Priorität: `if(fr.ContentHash == 0 || e.Priority > fr.Priority)` (`:943`) — bei Gleichstand gewinnt willkürlich der erste.

### → Folge 1: der Gleichstand lässt sich OHNE den großen Umbau beheben
Das Tor bei `SnesHdVideoFilter.cpp:1811/1823` verwirft, weil es nicht entscheiden kann. Mit dem
OAM-Index kann es entscheiden — auf der SNES liegt der **niedrigere Index vorne**.

| Schritt | Aufwand |
|---|---|
| `uint8_t OamIndex` in `HdSpritePixel` (`SnesPpu.h:124`), gesetzt aus `_currentSprite.Index` | 2 Zeilen |
| Feld in `SnesHdPpuTileInfo` (`SnesHdData.h:129`), mitgeschrieben in `hdCaptureSpriteFrom` | 2 Zeilen |
| Tor auf `Priority > winner || (Priority == winner && OamIndex < winnerOam)` ändern | 1 Zeile |
| `keepFringe` bei Gleichstand nach OAM-Index entscheiden statt willkürlich | 1 Zeile |

**Speicherkosten: voraussichtlich null.** `SnesHdPpuTileInfo` beginnt mit `SnesHdTileKey`
(uint64 → 8-Byte-Ausrichtung) und nutzt danach rund 26 von 32 Byte — das Byte fällt in
vorhandene Polsterung. **Vor dem Bau mit `sizeof` nachmessen**, nicht glauben.

Das holt die gemessenen **14,3 % Fransenverlust** (19,0 % im Kleever-Kampf) zurück, ohne die
Architektur anzufassen.

### → Folge 2: der große Umbau braucht mehr, als die alte Notiz annahm
Die Notiz unten sagt „Was Durchgang 2 braucht, ist schon da — Slot 2 trägt den Durchgang ohne
OAM.“ **Das stimmt nur bis zu drei überlappenden Sprites.** Slot 2 hält genau EINEN
Franse-Kandidaten je Pixel, und der S22-Kommentar sagt für Slot 3 ausdrücklich: *„With three or
more stacked, the last displaced entry wins.“* Ein echter Maleralgorithmus bräuchte den
**Stapel** je Pixel oder eine **Kachelliste je Scanline** — das ist eine PPU-seitige
Strukturänderung, nicht nur eine Umstellung im Filter.

---

## ★ DER UMBAU, DER ANSTEHT: zweiter Durchgang statt Ground-Suche

**Das Muster:** neun Commits (`S21`, `S21b`, `S22/S24`, `S25–S27`, `S25 zurück`, `S30`, `S32`,
`S34`, `S37`) haben dieselbe Form. Der Filter löst Sichtbarkeit **nativ** auf, komponiert in
**HD**, und muss für jeden halbtransparenten Texel **raten, was dahinter liegt**. Die Zahl der
Fälle ist das Produkt aus {Main, Sub} × {BG, Sprite, Backdrop, nichts} × {Farbmath an/aus} ×
{Overlay oder nicht} — deshalb ist die Liste nicht abgeschlossen.

**Was das pro Frame kostet (gemessen, S42-Lauf):**

| Zähler | /Frame | was es ist |
|---|---|---|
| `multi` | 5.735 | Main-Sprite sucht eine BG-Kachel als Untergrund |
| `bgBot` / `bgNoBot` | 1.106 / **291** | BG-Operand-Grund — **21 % der Suchen gehen leer aus** |
| `subBot` / `subNoBot` | 257 / 8 | Sub-Sprite-Grund |
| `sprUnder` + `subSprUnder` | 238 | Fälle, für die es Slot 3 überhaupt nur gibt |

**Der Ausweg: in Reihenfolge malen statt raten.**

1. **Durchgang 1** = der heutige Code für alles, was nativ gewinnt → fertiges HD-Bild mit
   harten Silhouetten.
2. **Durchgang 2** = die HD-Sprite-Kunst mit Alpha über das fertige Bild. Der Mischpartner ist
   damit **per Konstruktion** das, was wirklich dahinter steht — auf Main wie Sub wie Overlay.

Was Durchgang 2 braucht, ist schon da:
- **Position** — Slot 2 (die PPU-Hälfte von S21) zeichnet die Kachel-Identität auch an nativ
  transparenten Pixeln auf. Trägt den Durchgang ohne OAM.
- **Priorität** — `MainScreenFlags & 0x0F` hält den echten Gewinner. **Bei Gleichstand die
  OAM-Reihenfolge**, siehe Abschnitt oben.
- **Farbmath** — die Mathematik des **Zielpixels** muss auf den Texel angewandt werden, sonst
  kommt Lockjaws heller Saum zurück (S21 löst das heute durch Einmischen *vor* der Mathematik).

**Was wegfällt:** die gesamte Ground-Suche (S22, S26, S27, S30, S32, S34, S37 und die halbe
S21), Slot 3 in der heißen Sprite-Fetch-Schleife der PPU, und die `drawMain`-Sperre auf Slot 2
— Overlay-Level bekämen zum ersten Mal überhaupt Kanten (gemessen: 2.814 Frames bei null, bei
gleichzeitig 1.958 HD-Sub-Sprite-Pixeln/Frame), das Bonusfass-B löst sich darin auf.

**Der Preis:** ein zusätzlicher Durchgang über die Sprite-Pixel. Frame-Zeit am 21.09.:
Median **2,95 ms (S41) → 2,85 ms (S42)**, p95 3,60 → 3,88 ms. Bei 60 fps stehen 16,7 ms zur
Verfügung — rund **13,8 ms Luft**.

**Die volle Endstufe** (Maleralgorithmus über *alle* Ebenen) bräuchte den kompletten
Kandidaten-Stack je Pixel in der PPU statt nur des Gewinners. Teure Variante, kann warten.

---

## Offene Arbeit, nach Größe (unverändert)

| Was | Kacheln | Zustand |
|---|---|---|
| **King Zing** (`King B`, 8 Animationen) | 620 | nie angespielt → **0 Palettenslots**, Export würde die Kunst verwerfen |
| **Puftup** (7 Animationen) | 651 | ebenso |
| Kloak + Kloak Throwing Object | 617 | Slots da, nur upscalen |
| Flitter (3 Animationen) | 369 | Slots da |
| Mini-Necky + Attack | 346 | Slots da |
| Spiny + Flip Over | 319 | Slots da |
| Explosion `0x01BC` / K. Rool Revival `0x0272` | 235 | dieselben Kacheln unter zwei Namen |
| KONG-Buchstaben `$319C`–`$31B8` | 72 | 8 Gruppen à 9, 0 im Pack |
| Abschussfass-Stern `$2D20`/`$2D24` | 50 | 0 im Pack |

**Ein Zing-Kampf und ein Puftup-Level sind der billigste nächste Gewinn.**

---

## ⚠ Weitere offene Punkte

**Die Fassdrehung `0x015B`** braucht vermutlich Flip-Behandlung (unbelegt, `SNES_HD_OAMCAP=1`
in einem Level mit Abschussfass würde es klären). `renderCompositeFrame` wendet
`frame.primaryOffset` nicht an. HD-Kunst von vor `acfc787` trägt die alte zentrierte Polsterung.

**Erledigt am 21.09.:** alle A/B-Schalter stehen in der A/B-Liste von `WriteSessionBanner`.
Die Splitter-Pipeline ist einmal ganz durchgelaufen (Recorder → Galerie → Upscale → Import →
Export → Pack → Spiel): 158 Kacheln, 100 % im Pack, Glättung offen bis S43 gebaut ist.
---

## Werkzeug

`tools/shifted_tiles/` (README im Ordner) — **neu am 21.09.** Findet CHR-Duplikate, die gegen
das 8×8-Raster verschoben sind, und schneidet ihre HD-Kunst aus der vorhandenen zu, statt sie
neu hochzurechnen. Selbstprüfend: die Ableitung wird zuerst nativ nachgebaut und gegen die
echten VRAM-Bytes gehalten, nur bei 64/64 Pixeln wird geschrieben.
**Gehört nach JEDEN Pack-Export:** Upscale → Import → Export →
`python derive.py --apply --write-palettes` → einsetzen. Ein erneuter Lauf zieht neue
Quell-Upscales automatisch auf alle Duplikate nach.

`DKC2-HD-Tools/tools/spritemiss/` (README im Ordner). `report.py` ist der Einstieg und rechnet
die Recorder gegen ROM-Index und installierten Pack. Dazu die Testskripte, die die
Viewer-Änderungen des Tages gegen die echten Daten geprüft haben: `desctest.js`,
`parttest2.js`, `drawtest.js`, `ref2.py`.

---

## Historie (ältere Sitzungen)

## Stand 18.09. früh (Historie): S40 lief, S41 war ungebaut

## Stand der Repos

| Repo | Zustand |
|---|---|
| `Mesen2-SNES-HD_Projekt` | `feature/hd-compositing-engine` = **`1954cc80`** (S39) gepusht. **Working tree: `SnesHdVideoFilter.cpp` geändert — S40 + S41, uncommittet.** |
| `DKC2-HD-Tools` | `main` = **`803df15`** gepusht. Uncommittet: diese Datei und `tools/spritemiss/` (neu). |

**S40 ist im Spiel bestätigt** (Lauf 17.09. 22:04, spritecap trägt ein `build=S40`-Banner und
ist von 38.289 auf 43.006 Hashes gewachsen). **S41 ist noch nicht gebaut.**

- **S40** — `spritecap` war seit dem 10.08. tot. Dieselbe Familie wie S39, aber der *zweite*
  Fehler, den die S39-Nachricht benennt und nur in spritemiss behoben hat: der `OpenRecorder`
  hing an der Antwort des Seedings. Bei 88 MB Datei ist der erste Kandidat eines Laufs fast
  immer einer, den eine frühere Sitzung hatte, also greift `continue` bei noch geschlossener
  Datei, `s_spriteCapAttempted` bleibt `true`, und jede weitere Kachel stirbt am
  `!file`-`break`. Letztes Banner vor dem Fix: `2026-08-10 21:24 build=S19`.
- **S41** — `SNES_HD_SPRWATCH`, der Gegenpart zu spritemiss (siehe unten).

---

## ★ HAUPTBEFUND: der Pack-Export hängt an spritecap

```js
const pals = spriteCapPairs.get(hashHex);
if (!pals || pals.size === 0) { noPalHashes.add(hashHex); continue; }   // fällt weg
```

Ohne spritecap-Eintrag wird eine Kachel **nicht exportiert**, egal wie gut die upgescalte
Kunst im Container ist. Gegenprobe: **30.610 von 30.610 Sprite-Hashes des installierten Packs
haben einen spritecap-Eintrag. Keine Ausnahme.**

Am Ducken auf die Kachel genau belegt:

| | Kacheln | im alten spritecap | im Export-ZIP |
|---|---|---|---|
| DD Ducking | 108 | **14** | **14** |
| DX Ducking | 14 | **5** | **5** |

Der Upscale war in Ordnung — der Export hat nur ausgeliefert, wessen Palettenslot er kannte.
Der tote spritecap war deshalb kein Nebenschaden, sondern das Nadelöhr der ganzen Pipeline.

**Stand nach dem S40-Lauf:** 7.601 verfehlte Hashes bekannt, **5.727 mit Slot** (exportierbar,
sobald Kunst da ist), 1.874 ohne.

| | Kacheln | im Pack | verfehlt | in spritecap |
|---|---|---|---|---|
| Krow | 1.444 | 77 | 1.293 | 1.370 |
| Kleever | 1.394 | 1 | 1.342 | 1.343 |
| Rattly | 1.034 | 485 | 521 | 1.006 |
| Snapjaw | 426 | 259 | 167 | 426 |
| DD/DX Ducking | 252 | 149 | 103 | 252 |
| Abschussfass `0x015B` | 422 | 385 | 37 | 422 |
| **King B (King Zing)** | 620 | 0 | 620 | **0** |
| **Puftup** | 651 | 0 | 507 | **0** |

Werkzeug dazu: `tools/spritemiss/report.py` (siehe dessen README).

---

## ▶ NÄCHSTE SITZUNG — in dieser Reihenfolge

### 1. S41 bauen
Nur `SnesHdVideoFilter.cpp` geändert, inkrementeller Build reicht (Ctrl+Shift+B).

### 2. Export starten und die Konsolenzeilen sichern — klärt die Krow-Frage
spritecap hat 4.717 Hashes dazugelernt, ein neuer Export ist sowieso fällig. **Die Zeilen
`[sprpal] …` und `[sprites] …` kopieren.** Sie entscheiden, warum Krow nicht ausgeliefert
wurde (siehe „Krow" unter den offenen Punkten): `N Frames ohne Platzierungs-Metadaten`, ein
`scaleFactor N != 4 — übersprungen`, oder keins von beidem.

### 3. Lauf mit `SNES_HD_SPRWATCH` — klärt B und Ziffern

```
SNES_HD_SPRWATCH=E563D7702FE967CC,38E78F2E2A1400EC
```

(erste Kachel des B-Emblems `$3170`, erste Kachel der Ziffer 0 aus `$2D40`)
Ein Level mit Bonusfass und mit Countdown-Zahlen anspielen. Je Frame und Hash eine Diag-Zeile:

```
SPRWATCH F1234 HE563D7702FE967CC main=96/96 sub=0/0 fringe=0/0 under=0/0 P0/-1/-1/-1 wonMain=96 wonSub=0
```

- **gar keine Zeile**, obwohl das Objekt sichtbar ist: die Kachel erreicht den HD-Pfad nie,
  dann kann der Pack nicht die Ursache sein.
- `main=0/96`: erfasst, aber kein Treffer, dann den Schlüssel gegen den Pack halten.
- `main=96/96 wonMain=96`: HD-Kunst wird angewandt und das Sprite gewinnt das Pixel, dann ist
  das kantige Ding auf dem Schirm ein anderes Objekt.

### 4. Upscale-Runde auf das, was jetzt exportierbar ist
Kleever (1.342), Krow (1.293), Rattly (521), Snapjaw (167), Ducken (103), Abschussfass (37),
KONG-Buchstaben (72 Kacheln, `$319C`–`$31B8`, 8 Gruppen à 9).

### 5. King Zing und Puftup anspielen
Die beiden kamen nur im Lauf vom 16.09. vor, als der Recorder tot war, haben also 0 Slots —
der Export würde ihre Kunst auch nach dem Upscale verwerfen. Ein Zing-Kampf, ein Level mit
Puftup.

**Aufzeichnungsdateien:** `spritemiss` NICHT umbenennen, solange der Pack derselbe bleibt —
das Seeding hält den Zuwachs auf echtes Neuland. Erst vor einem Messlauf GEGEN EINEN NEUEN
PACK umbenennen. `spritecap` nie umbenennen.

---

## Beantwortete Fragen aus dem Lauf 17.09.

### Die Geisterversion von Krow ist eine Farbversion — kein zweiter Upscale
Die grauen Deskriptoren `$1388`, `$138C`, `$1390`, `$1394`, `$1398` sind **Frames 3–6 derselben
Animationen** `0x01FD`, `0x0200`–`0x0203`, `0x0207`:

```
0x0203: B137C  B1384  G138C  G1390  G1394  G1398
```

Und **391 der 1.080 Krow-Kacheln sind unter mehr als einer CGRAM-Zeile aufgezeichnet** (302
unter zwei, 89 unter drei); eine davon ist eine Graurampe (`0421 0C63 14A5 1CE7 2529 2D6B
35AD`, 580 Kacheln). Dieselbe Kunst, zwei Einfärbungen. Weil Kunst mit Referenzpalette
slot-frei liegt und Mesen sie auf die lebende Zeile umfärbt, deckt **ein** Upscale der
vollständigen Krow-Animationen beide Kämpfe. Prüfbar mit `report_palrows.py`.

### Die weißen Ziffern sind im Pack
`$2D40`–`$2D64` = Ziffern **0–9**, je 6 Kacheln, **60 von 60 im Pack**, in keinem der beiden
Läufe verfehlt. Aus der Pack-Kunst zusammengesetzt: glatte weiße 3-D-Ziffern. Der als SD
gemeldete Zahlensatz ist also entweder ein anderer — oder erreicht den HD-Pfad nicht
(siehe Punkt 3). Nicht im Pack und im Lauf verfehlt sind dagegen `$2D34`/`$2D38`/`$2D3C`
(Kong-Kopf, 34 Kacheln).

### Das Abschussfass passt genau zur Beobachtung
`0x015B`: **385 von 422 Kacheln im Pack, 37 verfehlt** — „einige Treffer in HD, während der
Drehung einzelne SD-Kacheln" ist exakt das. Alle 422 sind jetzt in spritecap.
Das Fass mit dem weißen Stern selbst sind die Gruppen `$2D20`/`$2D24` (50 Kacheln, 0 im Pack).

---

## ⚠ Offene Punkte

**Krow wurde nicht ausgeliefert, und der Palettenslot war es NICHT.** 1.369 der 1.444 Kacheln
hatten schon vor dem Export einen Slot, im ZIP liegen 77 — und die sind komplett „Ghost Krow
Explosion". Ausgeschlossen:

- *Verworfen wegen gedimmter Palette:* `findDimmedHashes` nachgerechnet (`report_dimmed.py`) —
  7 Zeilen haben eine gedimmte Kopie, 7.663 Kacheln fallen darunter, davon **27** bei Krow.
- *Kunst unter falschem Hash:* 402 der 30.610 Pack-Hashes haben kein Deskriptor-Zuhause, das
  ist genau die Runtime-Kategorie. Kein Block von ~1.300 Fremdlingen.
- *Die 256-px-Grenze in `renderSpriteFromDescriptor`:* Krows größter Frame ist 102x88.

Übrig: `noMetaFrames` (bei frisch importierter Kunst der Hauptverdacht — der Export macht
`if (!meta || !meta.tiles) { noMetaFrames++; continue; }`, ohne pro Frame zu warnen; Behebung
wäre ein erneutes „Import HD"), `scaleFactor != 4`, oder Krow liegt gar nicht als Sprite-Set
im Container. **Alle drei stehen in der Export-Konsole**, siehe Punkt 2.

**Das B auf dem Bonusfass: die Pack-Seite ist nachweislich einwandfrei.** `$3170`, 10 von 10
Kacheln im Pack, alle slot-frei, und die Referenzpalette ist zeichengleich mit der lebenden
CGRAM-Zeile (`00C8 012E 1DB5 027B 077F 7FFF 6B5A`) — `HdSpriteRecolor::Init` setzt bei lauter
Null-Deltas `valid = false`, das Umfärben läuft also gar nicht. In keinem der beiden Läufe ein
Miss. Fehlende Kunst, falscher Slot und Umfärben sind damit ausgeschlossen; offen ist die
Aufzeichnungsseite, und dafür ist S41 gebaut.

**Der blinde Fleck, den S41 schließt:** spritemiss sieht nur Kacheln, die erfasst wurden *und*
keine Kunst fanden. Eine nie erfasste Kachel hinterlässt keine Spur — „nicht in spritemiss"
heißt also nicht „abgedeckt". Pro Pixel werden nur zwei Sprite-Kacheln erfasst (Main + Sub),
dazu Fransen-Slot 2 und verdrängte Kachel 3; ein kleines Aufkleber-Sprite auf einem Fass kann
alle vier verlieren.

**48 Kacheln liegen im Pack und wurden trotzdem verfehlt** — alle ohne Referenzpalette, also
per Slot gebacken, und das Spiel zeichnet sie unter einem anderen Slot (meist Wasser-Splash:
Pack `_P5`, Laufzeit Slot 4 und 6). Auch ein spritecap-Loch: der andere Slot wurde nie
aufgezeichnet. Von 30.610 Pack-Hashes sind 30.295 slot-frei, nur 315 per Slot.

**Erledigt:** `bgcap` schreibt (986 Zeilen am 16.09., Kopf `build=S39`, gfxset 32 und 4 auf
BG2). Der alte Punkt „bgcap schreibt trotz S39 nicht" stammte aus dem Vormittagslauf.

**Weiter offen aus früheren Sitzungen:** die Fassdrehung `0x015B` braucht vermutlich
Flip-Behandlung (unbelegt, `SNES_HD_OAMCAP=1` würde es klären); `renderCompositeFrame` wendet
`frame.primaryOffset` nicht an (eine Änderung verschiebt bestehende Container-Kunst);
HD-Kunst von vor `acfc787` trägt die alte zentrierte Polsterung.

---

## Die drei Kategorien der Galerie

| | IDs | Palette |
|---|---|---|
| 780 Tabellenanimationen | `0x0000`–`0x030B` | wie immer |
| 39 verwaiste Sequenzen (`Seq 39CC`) | ab `0xE000` | vom Tabellennachbarn geerbt |
| 36 Gruppen ohne Animationseintrag (`Gfx 14A8`) | ab `0xD000` | aus der aufgezeichneten CGRAM-Zeile |

**Spritecap muss mit CGRAM-Zeilen geladen sein**, sonst bleiben die `Gfx`-Einträge grau.

### Im Spiel identifiziert und bestätigt

| Eintrag | Was |
|---|---|
| `Seq 39CC` | Dixies langer Fall — **17.09. in HD bestätigt** |
| `Seq 57AA` | Lockjaw, Maul auf/zu |
| `Seq 4C88` / `4C8B` / `4C8E` | Dixie auf dem Schädelwagen (`4C8E` fährt runter) |
| `Seq 4D1F` / `4D22` / `4D25` | Diddy auf dem Schädelwagen |
| `Gfx 14A0` + `14A8` | der Schädelwagen selbst |
| `Gfx 3170` | Bonus-Fass-B: rotes Sternemblem mit weißem B, 10 Kacheln, vollständig im Pack |
| `Gfx 2D40`–`2D64` | die großen weißen Ziffern 0–9, je 6 Kacheln, vollständig im Pack |
| `Gfx 2D20` / `2D24` | Abschussfass mit weißem Stern, 50 Kacheln, 0 im Pack |
| `Gfx 319C`–`31B8` | KONG-Buchstaben, 8 Gruppen à 9 Kacheln, 0 im Pack |
| `Gfx 08AC` | rollende Fässer (9 von 24 im Pack) |
| `Gfx 0C38`, `0CE8`, `3128`, `3140` | Piratenflagge, Hub-Wespen, Luftschiff, Strickleiter |

---

## ★ HAUPTBEFUND: 39 Animationen stehen in KEINER Tabellenzeile

Die Animationstabelle in Bank `$F9` hat 780 Einträge (`0x0000`–`0x030B`). Im selben Bank
liegen aber **39 weitere, vollständig gültige Sequenzen, auf die keine Tabellenzeile zeigt** —
sie werden aus dem Spielcode heraus angesprungen (`$81`/`$83`/`$84` tragen 65816-Adressen).

**Der Viewer zählt nur Tabellenzeilen auf** (`isValidAnimId`, `buildSpriteGallery`). Diese 39
Sequenzen kann er deshalb weder anzeigen noch exportieren noch upscalen. Das ist die Ursache
für „Kunst, die im Viewer nie auftaucht".

**Umfang: 3985 Kacheln, davon 1662 im Pack, 2323 fehlen.**

### Lockjaws Zuschnappen = Sequenz `$57AA`

| | |
|---|---|
| Lage | zwischen `Lockjaw Mouth Movement` (`$574B`, `0x0179`) und `Lockjaw Flip Over` (`$57F7`, `0x017A`) — mitten im Lockjaw-Block |
| Form | 21 Bilder, gfxRefs `$0E14`–`$0E24` |
| Palette | P4, dunkle Rottöne |
| Kacheln | 244, davon 182 im Pack, **62 fehlen** — alle 62 im Miss-Log |

Vom User unabhängig beobachtet („ein Gegner sollte beim Zuschnappen fehlende Animationen
zeigen"). Zweiter Fall derselben Art wie Dixies Fall.

**Der Miss-Recorder hat kein Zeitfenster** — er läuft jeden Frame unbegrenzt. Nur die
`SPRAREA`-Stichprobe im Diag-Log ist auf 3/4 von `SNES_HD_DIAG_FRAMES` begrenzt.

### Dixies langer Fall = Sequenz `$39CC`

| | |
|---|---|
| Lage | zwischen `DX Jump` (`$3982`) und `DX Follower DD Glide` (`$3A26`) / `DX Fall` (`$3A3D`) — mitten in Dixies Sprung/Fall-Block |
| Form | 10 Bilder, gfxRefs `$30B4`–`$30CC`, Dauer je 1 Tick, `$82` springt auf den Anfang zurück = Endlosschleife |
| Palette | P2, Farben byte-identisch zu `DX Begin Ducking` aus demselben Lauf |
| Kacheln | **137, davon 0 im Pack — und alle 137 im Miss-Log des Laufs** |
| Reproduktion | Lockjaw starten, die Kongs fallen direkt ins Level |

Von beiden Seiten bestätigt: ROM-Analyse und Laufzeitmessung nennen dieselben 137 Kacheln.
`0x00AA DX Fall` ist mit 5/5 Bildern vollständig und war nie der Fall, den wir gesucht haben.

**Vorbehalt:** die Erkennung der 39 Sequenzen ist eine Heuristik (Lücken im Bank abscannen,
ab jeder Position parsen, ≥3 Bilder verlangen). Ein paar Einträge sehen nach Dubletten aus
(`$65F1`/`$6600`, je 3 Bilder / 173 Kacheln). Vor dem Upscale einzeln im Viewer ansehen.

---

## ▶ NÄCHSTER SCHRITT: verwaiste Sequenzen in die Galerie holen

Ohne das kommt an die 2323 fehlenden Kacheln niemand heran. Vorschlag: synthetische IDs wie
bei den Map-Icons (dort `0xF000+`), Galerie-Eintrag pro Sequenz-Offset, Name zunächst
`seq_$39CC`. Der Export-Pfad dahinter existiert unverändert.

---

## Bestätigte fehlende Kunst (Messlauf 16.09., S39)

| Animation | ROM | im Pack | fehlt |
|---|---|---|---|
| `seq_$39CC` **Dixie langer Fall** | 137 | 0 | **137** |
| `0x000D` DD Ducking | 108 | 14 | **94** |
| `0x00B0` DX Ducking | 14 | 5 | **9** |
| `0x00AF` DX Begin Ducking | 66 | 57 | **9** |
| `0x00A4` DX Idle | 611 | 609 | 2 |

Fertig und bestätigt: `DD Begin Ducking`, `DD Stop Ducking`, `DX Stop Ducking` — 0 Misses.

**Kein Fall mehr:** Diddys Jonglieren ist im Spiel bereits HD (User geprüft). Nur die Anzeige
im Viewer fehlt — siehe Hauptbefund, vermutlich dieselbe Ursache.

---

## ⏵ ZU PRÜFEN (User, 16.09.): werden diese Effekte im Viewer sauber dargestellt?

Im Messlauf mit aufgezeichnet, bisher nie angesehen:

| animId | Name | Kacheln im Miss-Log |
|---|---|---|
| `0x01BB` | Explosion | 111 |
| `0x0168` / `0x01FE` | Hit Effect / Ghost Krow Explosion (dieselben Kacheln, zwei Namen) | 77 |
| `0x01B6` | Spark? / Splash? | 57 |
| `$31A0`–`$31B8` | verwaist, Palette P0 = dieselbe wie die Explosionen | 36 |

Alle vier laufen unter derselben CGRAM-Zeile — vermutlich eine Effekt-Familie.

---

## ▶ NÄCHSTE SITZUNG: S39 bauen und testen

### Was repariert wurde

`snes_hd_spritemiss.txt` und `snes_hd_bgcap.txt` wurden **seit dem 10.08.2026 nie wieder
geschrieben**. Nicht wegen Sättigung (so stand es im Quelltext), sondern wegen der
Reihenfolge in `SnesHdVideoFilter.cpp`:

```
if(seen.find(key) != end) continue;
seen.insert(key);            // <-- eigener Eintrag
...
if(!attempted) {
    SeedRecorderSet(...);
    if(seen.find(key) != end) continue;   // findet IMMER den eigenen Eintrag
    file = OpenRecorder(...);             // nie erreicht
}
if(!file) break;                          // ab jetzt bricht jede Kachel ab
```

`spritecap` macht es richtig (`insert` erst nach dem Öffnen) und lief deshalb weiter.

**S39:** gedeckte Kacheln werden auf dem Covered-Zweig gemerkt, der Stale-Zweig merkt nichts
mehr (statt insert/erase), Seeding und Öffnen passieren, solange der Schlüssel noch nicht im
Set ist, und das Öffnen hängt nicht mehr an der Antwort des Seedings.

### Test

1. Inkrementell bauen, Kennung **S39** (steht in `snes_hd_diag.txt` in der SESSION-Zeile).
2. Alte `Downloads\snes_hd_spritemiss.txt` ist bereits als `snes_hd_spritemiss 10082026.txt`
   beiseite. `snes_hd_bgcap.txt` ebenfalls umbenennen — sonst seedet sie den alten Stand.
3. Kurzer, gezielter Lauf: **Dixie ducken, Dixie langer Fall, Diddy ducken.**
4. Erwartung: beide Dateien entstehen neu und sind **klein**.

**Wenn die Dateien wieder ausbleiben**, ist der Fix nicht die Ursache — dann direkt melden,
nicht weiterspielen.

### Danach

Die Hashes aus `snes_hd_spritemiss.txt` gegen den ROM-Animationsindex joinen → Animationsname
+ Frame statt anonymer Hash. Der Join ist an der Diagnose vom 16.09. schon erprobt: aus
14 `SPRAREA art=0`-Zeilen wurden acht Kacheln `0x00AF DX Begin Ducking` / `0x00B0 DX Ducking`
(bis 12.600 px) und sechs mehrdeutige.

---

## Bestätigte fehlende Kunst (User, 16.09.)

| Animation | Stand |
|---|---|
| `0x00B0` DX Ducking | fehlt — 0/3 Frames, 5/14 Kacheln im Pack |
| `0x00AF` DX Begin Ducking | unvollständig — 4/5 Frames, 57/66 Kacheln |
| `0x000D` DD Ducking | unvollständig — 2/15 Frames, 14/108 Kacheln |
| Dixie langer Fall | animId noch **unbekannt** — `0x00AA DX Fall` ist mit 5/5 vollständig, der lange Fall spielt etwas anderes. Kandidaten ohne jede HD-Kachel: `0x00DB DX Spread-Eagle` (8 Frames, 118 Kacheln), `0x0145 DX Float Up` (20 Frames, 188 Kacheln). **Nicht raten — der Messlauf entscheidet.** |

**Kein Fall mehr:** Diddys Jonglieren ist im Spiel bereits HD (vom User geprüft). Es wird nur
im Viewer nicht angezeigt — eigenes Thema, Anzeige, nicht Kunst.

---

## ℹ Was das zurückgenommene Deckungsregister gezeigt hat

Es verglich ROM (Soll) gegen Container (Ist) und beantwortete damit die falsche Frage: für
alles, was im Spiel SD aussieht, war der Bestand teils vollständig. Zwei Zahlen daraus sind
trotzdem brauchbar und stehen hier, damit sie nicht verloren gehen:

- 53.381 distinkte Sprite-Kacheln im ROM über 777 Animationen; 25.059 (46,9 %) im
  installierten Pack.
- **310 Animationen haben null HD-Kacheln** — überwiegend alle Rattly-Animationen (nie
  aufgezeichnet), dazu `DX Spread-Eagle`, `DX Float Up`, `DD Float Up`,
  `DD Descending Rope Spread-Eagle`.

Diese 310 sind echte Lücken und ein möglicher eigener Arbeitsvorrat — unabhängig davon, ob
sie im Spiel gerade auffallen.

---

## ▶ NÄCHSTE SITZUNG: S38 bauen (kein Test nötig)

`SnesHdPerf` ist ab S38 **standardmäßig aus** — die Messung lief bisher in jeder Sitzung mit,
obwohl ihre Frage beantwortet ist. Einziger Schalter ist jetzt `SNES_HD_PERF=1` (mit oder ohne
Pack). Gegatet sind die Uhr-Abfragen je Scanline, `SendFrame`, und die Übergaben je Frame.
Inkrementell bauen, Kennung **S38**. Es gibt nichts zu messen — nur: läuft alles normal, und
entsteht keine `snes_hd_perf.txt` mehr.

Die Recorder (`spritecap`, `bgcap`, `spritemiss`) bleiben **absichtlich an**, bis alle Level im
Detail geprüft sind — es kann noch Kunst dazukommen.

---

## ℹ Kein Test, nur Notiz: der ungenutzte Retry in S37

Der BG1↔BG2-Retry in der neuen Untergrundsuche hat in **keinem** Kontext gefeuert (`retry=0`).
Das ist **kein Fehler und keine Aufgabe** — der Zweig ist Absicherung für den Fall, dass die
chr-Basen eines Levels vertauscht sind (`$210B`) und die Kunst im Pack deshalb unter dem anderen
Layer-Index liegt. In Mainbrace sind sie normal (`$0642`), in Rambi vertauscht (`$0725`), aber
dort wurde der Untergrund schon beim ersten Versuch gefunden. Es gibt nichts zu tun; die Notiz
steht hier nur, damit niemand `retry=0` später für einen Defekt hält. Sollte irgendwann ein
Level harte BG-Ränder zeigen, **obwohl** `bgBot` hoch ist, ist dieser Zweig der erste Verdacht.

---

## ✅ Test J — Kantenglättung für BG1-HD-Kacheln (S37), bestätigt 14.09.: Mainbrace sauber, `bgNoBot=0` in allen acht Kontexten; Gangplank/Lockjaw/Rambi ohne Regression. Committet als `6454d4ea`.

**Anlass (User):** In Mainbrace Mayhem sind die BG1-Level-Kacheln an den Rändern pixelig,
obwohl geglättete HD-Kunst für alle Ebenen im Pack liegt. Für BG1-HD-Kacheln war bisher
keine Glättung aktiv — S21–S34 haben nur Sprite-Silhouetten behandelt.

**Was S37 ändert:** Der BG-Operand auf dem Sub-Screen bekommt denselben Untergrund, den der
Sprite-Operand seit S26 hat. In Mainbrace liegt BG1 (Level-Geometrie) auf dem Sub-Screen
(`DATA_FD7AB6`: Main=$04, Sub=$13), der Untergrund ist dann BG2. Details: Mesen-`CHANGELOG.md`,
Eintrag S37. **Sprite-Pfade unberührt.**

1. **Bauen:** inkrementell. Nur `SnesHdVideoFilter.cpp` geändert. Kennung: **S37**.
2. **Schauen:** Mainbrace Mayhem — sind die Ränder der Level-Geometrie jetzt weich?
   Danach Lockjaw und Rambi gegenprüfen, dass dort nichts schlechter wurde.
3. **A/B bei Zweifel:** `bin\win-x64\Release\TEST_S37_ohne_BG_Untergrund.bat` startet Mesen
   mit `SNES_HD_NO_SUB_BG_UNDER=1` — Verhalten bis S36. Ein Lauf, zwei Bilder, Frage geklärt.
4. **Schicken:** `snes_hd_diag.txt` — neue Zähler in der FRAME-Zeile:
   `bgBot` (Untergrund gefunden) · `bgBotRetry` (davon über den BG1↔BG2-Retry) ·
   `bgNoBot` (transparente Kachel ohne Untergrund) · `bgOpaque` (voll deckend, kein Rand —
   der ehrliche Nenner).

**Erwartung:** In Mainbrace sollte `bgBot` deutlich > 0 sein. Bleibt `bgNoBot` hoch, findet die
Suche den Untergrund nicht — dann ist `bgBotRetry` die nächste Frage. Ist fast alles
`bgOpaque`, haben die Kacheln gar keine transparenten Ränder und die Ursache liegt woanders.

---

## ✅ Erledigt 14.09.: Performance

Die Ruckler kamen **nicht** vom HD-Pack. Lauf D mit VSync + IntegerFpsMode: 14.975 Frames,
`late=2 drop=1` (Levelwechsel), 59,853 fps VSync-gerastet. Vorher 60,0988 fps gegen einen
60-Hz-Schirm ohne VSync => alle ~10 s ein Bild zu viel. Details: Mesen-`CHANGELOG.md`,
Einträge S35/S36 und „Test I ausgewertet“.

**Recorder-Dateien:** kein Handlungsbedarf. `spritecap` (88 MB), `spritemiss` (43 MB) und
`bgcap` (4,2 MB) sind seit 2026-08-10 unverändert — `SeedRecorderSet()` liest sie ein und
hängt nur neue Schlüssel an, es ist nichts Neues mehr aufgetaucht. Die Daten sind endlich
und vollständig. Kosten nur noch: ~136 MB Einlesen beim Mesen-Start (Teil des langen Ladens)
und der Dedup-Scan je Frame.

---

## ✅ Test I — A/B mit und ohne Pack (S36), durchgeführt 14.09.: Emulation liefert pünktlich; Ursache war die Bildausgabe (VSync + IntegerFpsMode)

**Stand nach Test H:** Der Messlauf vom 14.09. (08:15–08:19, Mainbrace + Lockjaw) zeigt zu
den gemeldeten Ruckler-Zeiten **kein einziges überlastetes Frame**: `over=0`, Arbeit im
Mittel 6,2 ms von 16,64 ms, ~10 ms Reserve pro Frame, `wait=0`. Der HD-Filter ist also nicht
der Engpass. Was fehlte: die **Frame-Periode** wurde gerechnet, aber nie ausgegeben — ein
Frame kann auch ohne Arbeit zu spät kommen. S36 gibt sie jetzt aus.

1. **Bauen:** inkrementell (Strg+Shift+B). Nur `SnesHdPerf.h` geändert, keine neue Datei.
   Build-Kennung: **S36**.
2. **Lauf A — mit Pack (wie bisher):** dieselbe Stelle in Lockjaw's Locker, dort wo es
   ruckelt. `snes_hd_perf.txt` vorher wegsichern oder umbenennen, damit die Läufe getrennt
   bleiben.
3. **Lauf B — Filter aus, Erfassung an:** Einstellungen → SNES → General → Haken bei
   „Enable HD packs“ raus. Wirkt sofort. **Achtung:** das schaltet nur den Filter ab
   (`SnesConsole.cpp:304`); HD-Erfassung je Pixel und das 16-MB-Clear hängen an `_hdData`
   und laufen weiter. Kein `SNES_HD_PERF` nötig.
4. **Lauf C — echte Nulllinie, gar kein Pack:**
   `bin\win-x64\Release\TEST_I_LaufC_ohne_Pack.bat` starten. Die Datei benennt den
   Pack-Ordner weg, setzt `SNES_HD_PERF=1`, startet Mesen und benennt nach dem Beenden
   zurück. Fenster offen lassen, bis Mesen zu ist. Kontrolle: die SESSION-Kopfzeile von
   Lauf B und C muss `build=? (HD filter not running)` zeigen, nicht `S36`.
5. **Schicken:** die eine `snes_hd_perf.txt` — die Läufe trennen sich über ihre
   `=== SESSION … ===`-Zeilen und die Uhrzeiten. Dazu eine Zeile: Reihenfolge der Läufe
   und **ob es in B bzw. C an derselben Stelle genauso geruckelt hat**. Das „ob“ ist die
   eigentliche Messgröße; die Zahlen sagen nur, ob die Bildrate etwas damit zu tun hat.

**Neue Felder:** `late=` (Frames > 20 ms Periode), `drop=` (> 25 ms, Bild wird wiederholt),
`period=Mittel/Max`. `SLOW` löst jetzt auch bei langer Periode aus, `why=` sagt welche.

**Lesart:**
- `late`/`drop` ≈ 0 in beiden Läufen und es ruckelt trotzdem → **DKC2s eigene Verlangsamung**
  bei vielen Objekten. Originalverhalten des Spiels, kein Emulator-Problem.
- `late`/`drop` > 0 nur in Lauf A → unser HD-Pfad, dann `period` gegen `work` halten.
- `late`/`drop` > 0 in beiden → Mesens Frame-Pacing / VSync, unabhängig vom Pack.

**Nebenbefund (kein Fokus):** `rec` kostet durchgehend ~1,0–1,6 ms pro Frame — die Recorder
(spritecap, bgcap, spritemiss) laufen im Spielbetrieb mit. Rund 8 % des Budgets für Daten,
die wir gerade nicht sammeln. Abschaltbar, aber nicht die Ursache der Ruckler.

---

## ✅ Test H — Performance-Messung (S35), durchgeführt 14.09. 08:15–08:19

**Anlass (User):** Das Spiel läuft meist flüssig, bricht aber an manchen Stellen unter 60 fps
ein, häufiger bei viel Betrieb (viele Gegner). Weltkarte und Level-Laden sind unauffällig.
Das lange Laden beim Mesen-Start kommt vom Pack und ist **nicht** der Fokus.

1. **Bauen:** inkrementell (Strg+Shift+B). `Core.vcxproj` hat einen neuen Header-Eintrag →
   Visual Studio fragt ggf. nach Neuladen, mit Ja bestätigen. Build-Kennung im Diag-Log: **S35**.
2. **Spielen:** Mesen normal starten (NICHT die OAM-Batch). Ein Level mit viel Betrieb
   komplett durchspielen. Beim Ruckeln grob die **Uhrzeit** merken.
3. **Schicken:** `Downloads\snes_hd_perf.txt` + `snes_hd_diag.txt` (für die Zuordnung
   `sig` → Level).

**Was in der Datei steht:** `PERF <Uhrzeit>` je Sekunde (Mittel/Max), `SLOW <Uhrzeit>` je
Frame mit Arbeit > 20 ms. Felder und Lesart: Mesen-`CHANGELOG.md`, Eintrag S35. Kurz:
- `over` > 0 und `wait` hoch → der **HD-Filter** ist der Engpass → `filter`,
  `pre`/`render`/`rec`/`post` ansehen.
- `over` > 0, `emu`/`scan` hoch, `wait` klein → **Emulation / HD-Erfassung in der PPU**.
- `clear` ist ein fester Block (~16 MB Pixelinfo je Frame löschen) — Kandidat, falls er groß ist.
- Periodische Spitzen in `emu` bei ruhigem `scan` → etwas außerhalb der PPU (Rewind?).

**Danach möglich:** A/B mit HD aus — `set SNES_HD_PERF=1` erzwingt die Messung ohne Pack.

---

## ✅ Erledigt heute (10.09.)

- **Zahlen-Seite** (Viewer): Ziffern einzeln, 6 Bögen / 161 Kacheln, Kopf/Banane/Stern/KONG,
  Pixel in `zahlen_groundtruth.js`, keine Aufzeichnung nötig. Export v3/v4 geprüft (0
  Pixelabweichungen). **Im Spiel HD und geglättet.**
- **Laufzeit-Galerie:** Ziffern werden herausgeschnitten statt ganze Objekte ausgeblendet
  (Kopf wieder da); Listener für `Zahlen ausblenden` und das Suchfeld nachgerüstet.
- **Weltkarten-Köpfe:** Ursache `tiles: null` gefunden, Map Icons + Pfeile tragen jetzt ihre
  Kachelliste; Fehlliste 49/49 im Pack. **Im Spiel HD und geglättet.**
- **Kantenglättung:** Referenzpaletten für Map Icons und Zahlen/HUD im Pack-Export.
- Pack-Installation zweimal per Skript gegen das ZIP geprüft (Dateien, CRC, Inhalt).

## ⏸ Geparkt / offen

- **Münzen** (Bananenmünze, Kremkoin, DK-Münze): der User prüft beim nächsten Aufzeichnungslauf,
  ob HUD- und Level-Version verschiedene Kacheln sind. Befund bisher: Bananenmünze = 8 Phasen,
  Slots P3–P6, byte-genau im ROM; Kremkoin/DK-Münze nie aufgezeichnet; alle drei sind
  ROM-Animationen (`0x01C1`–`0x01C3`) → Sprite-Galerie wäre slotfrei.
- **Totenkopf-Icon (Boss):** nie aufgezeichnet (Spielstand hatte ihn schon ersetzt). Neuer
  Spielstand + normaler Lauf → `spritecap` erfasst ihn → Spritecap im Viewer neu laden →
  Pack-Export. Dekodierung bis dahin ungeprüft.
- **OAM-Recorder:** `bin\win-x64\Release\TEST_AUFZEICHNUNG_oam.bat`. Vorher die alte
  `snes_hd_oam.txt` (813 MB) umbenennen.
- **Kartenschrift & übrige Laufzeit-Kunst** haben weiterhin keine Referenzpalette → keine
  Glättung. Referenz nur, wo die Palette sicher ist (bei der Kartenschrift aus spritemiss
  vorher gegen spritecap prüfen — dort gibt es verfälschte Erstsichtungen, siehe rote Münze).
- **Container-Backup:** ✅ **erledigt 14.09.** Export (2,7 GB, eine Datei), Import in einen neuen
  Container, Pack daraus exportiert — **49.693 von 49.694 Dateien byte-gleich** zum installierten
  Pack, die eine Abweichung ist der Containername im `notes`-Feld des Manifests. Sicherung liegt
  als `Downloads\Anim Tiles v2_container backup.zip`. Details im Viewer-CHANGELOG.
- Map Icons: 16 Frames, aber nur 6–16 verschiedene (Wiederholungen werden mit hochgerechnet);
  Sprite-Export setzt keinen Rand. Beides nur notiert.


---

## ⚠ OFFEN: `bgcap` schreibt trotz S39 immer noch nicht

Der Reihenfolge-Fix war **nötig, aber nicht hinreichend**. Im Lauf vom 16.09. gab es echte
BG-Misses in Lockjaw (`sig=E10E4686511EB716`), Frames mit `Main=$17`:

| Layer | BG-Pixel | mit HD | Abdeckung |
|---|---|---|---|
| BG1 | 14.520.048 | 9.335.916 | 64,3 % |
| BG2 | 32.496.050 | 17.072.129 | 52,5 % |
| BG3 | 1.510.161 | 690.096 | 45,7 % |

`snes_hd_bgcap.txt` war umbenannt und wurde **nicht neu angelegt** — es hat also kein
einziges BG-Tile den Schreibpunkt erreicht, obwohl Millionen Pixel missen.

**Hauptverdacht:** die Live-VRAM-Gegenprobe
`ComputeTileContentHash(hdScreen->Vram, t.VramWordAddr, words) != t.Key.ContentHash`.
DKC2 streamt BG-CHR per DMA in jedem VBlank (dokumentiert: der GfxSet-Fingerprint wurde
deshalb aufgegeben, `32bd50b9`). Wenn das VRAM zum Filterzeitpunkt schon überschrieben ist,
scheitert die Gegenprobe immer und jeder Kandidat wird als „stale" verworfen.

**Nicht auf dem kritischen Pfad** — bgcap liefert BG-Animationskacheln (CHR-DMA-Frames), nicht
Sprite-Kunst. Wenn es drankommt: eine `DiagLog`-Zeile mit den Zählern „Kandidaten / covered /
stale / geschrieben" entscheidet die Frage in einem Lauf.
