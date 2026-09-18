# Auswertung der Mesen-Recorder (Stand 2026-09-18)

Rechnet die Aufzeichnungen aus `%USERPROFILE%\Downloads` gegen den ROM-Kachelindex und den
installierten HD-Pack. Alles liest direkt von der Platte, es gibt keinen Zwischenspeicher zu
pflegen. `python` (nicht `python3`), Pillow nur für die Bild-Skripte.

| Datei | Zweck |
|---|---|
| `report.py` | **Hier anfangen.** Gesamtzahlen + Tabelle je Figur. `python report.py Krow Rattly` filtert. |
| `lib2.py` | Lader: spritemiss, spritecap (mit CGRAM-Zeilen), Pack, ROM-Index. Wird von allen `exec`-eingebunden. |
| `gfxlib.py` | ROM-Seite: Deskriptor-Tabelle `$3C8000`, FNV-1a über 32 Kachelbytes, Kachelbytes je gfxRef. |
| `objrender.py` | Setzt ein Objekt aus seinem Deskriptor zusammen (16x16-Slotformel wie im Viewer) und rendert es SD. |
| `report_anim.py` | Deckung je Animation (Kacheln / im Pack / verfehlt) + Palettenslot-Vergleich. |
| `report_exportable.py` | Was nach dem nächsten Upscale ausgeliefert würde. |
| `report_dimmed.py` | Portierung von `findDimmedHashes` — welche Kacheln der Export als "auch gedimmt gezeichnet" verwirft. |
| `report_palrows.py` | Alle CGRAM-Zeilen je Kachel. Beweist Farbvarianten (dieselbe Kunst unter zwei Paletten). |
| `report_sheet.py` | Kontaktabzug aller Objekte, die im Lauf vorkamen und 0 Kacheln im Pack haben. |
| `test_sprwatch_parser.py` | Prüft den Hex-Parser von `SNES_HD_SPRWATCH` (S41) gegen echte Eingaben. |
| `ledger.py` | Älteres Vorabwerkzeug, das `hash2anim.json` erzeugt hat. Nur als Referenz. |

`names.json` (780 Animationsnamen), `hash2anim.json` (53.381 Kachel-Hashes → Animation),
`unused_gfx.json` (Gruppen ohne Animationseintrag), `orphans_js.json` (verwaiste Sequenzen)
sind aus dem ROM abgeleitete Tabellen und stabil, solange das ROM dasselbe ist.

**Kernbefund, den diese Werkzeuge gezeigt haben:** der Pack-Export liefert eine Kachel nur
aus, wenn sie in `snes_hd_spritecap.txt` steht (gemessen: 30.610 von 30.610 Pack-Hashes haben
einen Eintrag, keine Ausnahme). Upgescalte Kunst ohne Eintrag wird stillschweigend verworfen.
