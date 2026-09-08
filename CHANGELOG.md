# Changelog — DKC2-HD-Tools Viewer & Mesen2 SNES HD Fork

## [2026-09-08] — S25 wieder ausgebaut (Rekonstruktion: Commit `4482908a`)

Nur Mesen. **S25 zeichnete, aber niemand konnte es sehen** — also raus, bevor es zu Code
wird, dessen einziger Beleg ist, dass er ausgeführt wird. Genau so hat sich der S23-Zweig
zu lange gehalten.

**Entfernt:** die Aufzeichnung des Saum-Slots auf dem Sub-Screen in `RenderSprites`
(`objDrawn`/`fringeWindowCount` zurück auf `drawMain`/`mainWindowCount`), die
Scanline-Flags `objOnMain`/`objOnSub`, der dritte Saum-Zweig im Filter samt Prio-Test gegen
den Sub-Gewinner, der Saum-Blend im Operanden, der Schalter `SNES_HD_NO_SUB_FRINGE` und die
Zähler `sprEdgeSub=A/B`.

**Beleg:** fünf A/B-Läufe über 3.634 Frames. S25 zeichnete 747 Subpixel je Frame in
Mainbrace — mit S25 aus meldete der User **keinen** Unterschied, mit dem Untergrund
(S26/S27) aus dagegen „nicht geglättet“. Vermutung, ungeprüft: der Operand wird zum Nebel
addiert und oft halbiert, was ein schwach gedeckter Saum nicht überlebt.
**Einschränkung:** Augen-A/B, kein Standbildvergleich derselben Stelle — wer S25
rehabilitieren will, macht genau den.

**S26 und S27 bleiben** und hängen nicht an S25: Slot 3 wird über den `drawSub`-Pfad
gefüllt, nicht über den Saum-Slot. Log-Rotation und OAM-Gate bleiben ebenfalls.

## [2026-09-08] — S25–S27: die Kantenglättung erreicht die Overlay-Level

Nur Mesen (`SnesPpu.cpp`, `SnesHdVideoFilter.cpp`), Commit `4482908a`.

**In Mainbrace, Rambi Rumble und Lockjaw unter Wasser lief die Kantenglättung nie — und die
Ursache war eine einzige Gate-Bedingung.** DKC2 nimmt OBJ per HDMA vom Main-Screen
(`$212C=$04`), also war `drawMain` für Sprites falsch und `RenderSprites` füllte den
Saum-Slot dort gar nicht erst. `sprEdge=0/0` in jedem Frame las sich wie kaputter Code und
war dieses Tor; die Saum-Zeilenpuffer waren die ganze Zeit gefüllt.

**S25** zeichnet den Saum in den **Color-Math-Operanden** statt in die Hauptfarbe — in einem
Overlay-Level existiert die Figur nur dort, ein Saum in der Hauptfarbe würde zum Nebel
*addiert* statt durch ihn hindurch gezeichnet.
**S26** gibt dem Sub-Sprite einen Untergrund. Es mischte noch gegen `nsR/nsG/nsB`, und das
ist an einem Sprite-Pixel die **eigene SD-Farbe** — dieselbe Wand, die S21 im Main-Pfad
eingerissen hat, hier unangetastet. Der Untergrund ist streng begründet: in diesem Zweig hat
das Sprite jede Sub-BG-Ebene geschlagen, sonst hätte `RenderTilemap` `SubScreenHasSprite`
gelöscht.
**S27** nimmt bevorzugt ein **zweites Sprite** als diesen Untergrund, exakt wie S22 im
Main-Pfad. `Sprites[3]` wird auch für den Sub-Slot gefüllt — nichts Neues aufzuzeichnen.
Beide S22-Fallen mitgenommen: die R3-Zeilen-LUT bleibt von einer Sprite-Unterlage fern, und
die Unterlage braucht die Umfärbung.

**Gemessen, nicht argumentiert.** Fünf A/B-Läufe über 3.634 Frames haben S25/S26 getrennt:
mit S26 aus meldet der User „nicht geglättet“ in Mainbrace und Lockjaw, während S25 weiter
über 400 Subpixel je Frame zeichnet — **der sichtbare Effekt ist S26, S25s Nutzen ist
unbelegt.** S27 hat eine saubere A/B/A-Kette am Fass, das Dixie über dem Kopf trägt:
glatt → hart → glatt, bei `subSprUnder` = 106 px/Frame in 140 von 248 Frames.

**Ein Zweig wurde als Zähler ausgeliefert und danach entfernt.** Die Vermutung, auch auf
Scanlines *mit* OBJ auf Main fehle Saum, war aus `sprHdSub` hochgerechnet — aber diese Pixel
liegen INNERHALB der Silhouette, und direkt daneben lässt `$212D=$10` den Sub-Screen leer.
Der Zähler kam in allen fünf Läufen als **0** zurück, auch in dem, der den Schalter
einschaltete. Raus statt auf der Begründung behalten — wie `sprFrOver` in S23.

**Recorder aufgeräumt.** `snes_hd_oam.txt` dedupliziert auf die **Komposition** eines Frames,
also zählte fast jedes Frame als neu; die Datei war auf **813 MB** gewachsen, während
`spritecap`/`bgcap`/`spritemiss` (Dedup je Kachel) seit dem 10.08. gesättigt sind. OAM ist
jetzt aus per Vorgabe (`SNES_HD_OAMCAP=1`) — dieselbe Behandlung wie `cgramcap` in S18; der
Viewer liest die Datei weiterhin über `parseOam` für die Laufzeit-Objekte.
Die zwei kleinen Logs hängen an und rotieren bei 16 MB. Ein erster Versuch mit „frisch je
Start“ hat binnen einer Stunde eine Vergleichsserie zerstört, weil ein außerhalb der
Testskripte gestarteter Lauf die beiden davor löschte.

## [2026-09-08] — S22–S24: Sprite-Kanten bei Überlappung

Nur Mesen (`SnesPpu.h`, `SnesPpu.cpp`, `SnesHdVideoFilter.cpp`).

**S21b hatte die Glättung dort abgeschaltet, wo zwei Sprites einander überlappen** — sichtbar
als harte Kante an Krunchas Arm vor der Sonne. **S22** rettet stattdessen das **verdrängte
Sprite** und benutzt es als Unterlage: `FetchSpriteTile` ist der einzige Moment, in dem beide
Sprites in der Hand sind; veröffentlicht wird es als `Sprites[3]` + `SpriteCount` Bit 3 — Slot
und Bit waren das letzte freie Paar. Zwei Fallen vorher im Code gefunden statt später im Bild:
`botLut` hatte keine Sprite-Ausnahme (der R3-LUT deckt nur BG-CGRAM-Reihen 0–7 ab, OBJ-Paletten
liegen bei 128–255), und eine Sprite-Unterlage braucht die Umfärbung auf die lebende
OBJ-Palette, sonst behält die Figur hinter der weichen Kante ihre eingebackenen Farben.

**S23 war ein Fehlschlag, und die Zähler haben ihn entlarvt.** Die Idee: `!spriteWon` streichen,
damit ein Saum auch über einem Sprite gezeichnet wird, das den Pixel gewonnen hat.
Das Ergebnis im Log: **`sprFrOver` blieb 0**, während `sprFrTie` in die Tausende ging — Saum
und Gewinner teilen sich fast immer eine Priorität, und der Prioritätsvergleich lehnt sie
korrekt ab. Der Zweig hat also nichts genutzt und dafür einen neuen Fehler erzeugt: Dixies
gelbe Haare schienen durch die Kiste, die sie über dem Kopf trägt.

**Entschieden haben zwei A/B-Schalter, nicht ein Argument** — die Hypothese des Autors war
falsch und wurde in einem Zug widerlegt:

| Lauf | Krunchas Arm | Dixies Haare |
|---|---|---|
| `SNES_HD_NO_SPRITE_UNDER=1` (S22 aus) | kantig | Bug da |
| `SNES_HD_NO_FRINGE_OVER_SPR=1` (S23 aus) | glatt | Bug weg |

Die Glättung kommt aus S22, der Bug aus S23. **S24** macht das zum Standard: `!spriteWon` ist
wieder drin, `sprFrOver` und der zugehörige Schalter entfallen (per Konstruktion wirkungslos).
`SNES_HD_NO_SPRITE_UNDER` bleibt — er hat sich bewährt.

**Performance.** Die zwei neuen Zeilenpuffer wurden je Scanline kopiert UND geleert und haben
damit die Sprite-Puffer-Last im **Emulations-Thread** verdreifacht — genau die Quelle, die seit
R6.1 als Verdacht für das Restruckeln notiert ist, und die in `ms` grundsätzlich nicht
auftaucht (`ms` misst nur den Filter). Vier Dirty-Flags lassen memcpy/memset nur noch dort
laufen, wo wirklich zwei Sprites aufeinandertreffen: `ms` max von **14,82 auf 5,53**, unter dem
Stand vor der ganzen Saum-Arbeit (6,53). Das Leeren beim Übergang „Copy leer, Ziel noch voll"
bleibt bewusst drin, sonst schmiert die Kunst der Vorzeile nach unten.

**Nebenbefund für später:** der in der Projektdoku als „risikoarmer Quick-Win" geführte
Umbau `Sprites[4]`→`Sprites[2]` ist **hinfällig** — S21 belegt Slot 2, S22 Slot 3.

## [2026-09-07] — S21b: zwei Fehler in der Kantenglättung, und der Beweis dass sie wirkt

Nur Mesen (`SnesPpu.h`, `SnesPpu.cpp`, `SnesHdVideoFilter.cpp`).

**Zuerst der Beweis, den S21 schuldig geblieben war.** Am 12.08. zeichnete Wand 1 im Level
nichts — 25.319 Kandidaten, **0** Subpixel — weil die Pack-Kunst von vor dem Kantenfix stammte;
der Neu-Export kam erst danach und wurde nur noch auf der Weltkarte getestet. Am 07.09. mit der
neu hochgerechneten Kunst gemessen: **76.941 gezeichnete Saum-Subpixel** im Level (max 1.013 je
Frame). User-Urteil: „die Kongs haben glatte Außenkanten". Damit ist die Kantenglättung
erstmals als wirksam belegt, und das negative Gesamturteil vom 12.08. ist gegenstandslos — es
galt einem Build, dem die passende Kunst fehlte.

**Fix 1 — halbtransparente Sprite-Texel mischten gegen die falsche Unterlage.** Wand 2 nimmt
die BG-Kachel als Grund unter dem Sprite. Steht ein **zweites Sprite** dazwischen, ist das die
falsche Unterlage: durch die weiche Kante schien der Hintergrund statt der Figur dahinter
(Dixies Haare vor Diddy). Die Zeilenpuffer behalten nur den Gewinner, das verdeckte Sprite ist
also gar nicht bekannt. Neues Flag `HdSpritePixel::MultiOpaque`, in `FetchSpriteTile` gesetzt
**bevor** das neuere Sprite das ältere überschreibt → `SpriteCount` Bit 3 → Wand 2 lässt
solche Pixel in Ruhe.
**Bekannte Nebenwirkung, zweimal beobachtet:** wo Sprites einander überlappen, ist die
Außenkante damit wieder hart — Krunchas Arm vor der Sonne in Gangplank, die Kongs
hintereinander. Das Abschalten ist die grobe Lösung; die richtige ist, das verdrängte Sprite
in `Sprites[3]` zu retten (Slot und Bit 3 gehören zusammen und sind frei) und **dagegen** zu
mischen. Als nächster Schritt vorgemerkt.

**Fix 2 — heller Saum an Dixies Haaren, nur unter Wasser.** Zwei Anläufe. Der erste (Saum von
nach Color Math in die Vor-Math-Hauptfarbe verschoben) änderte nichts am Bild, bleibt aber
drin: der Saum sitzt an einem Pixel, das der BG gewonnen hat, und muss dessen Math mitmachen.
**Die echte Ursache** fand sich erst nach der Rückmeldung „sieht aus wie vorher": die
Bottom-Suche akzeptierte eine BG-Ebene, die nur auf dem **Sub**-Screen liegt
(`MainScreenLayers | SubScreenLayers`). Unter der Wasserlinie schaltet DKC2 Main per HDMA auf
`$00`/`$04` und lässt BG1/BG2 nur auf Sub — die helle Sub-Kunst wurde damit zur „Unterlage"
hinter Dixie, obwohl auf dem Main-Screen etwas Dunkles steht. **Fix: `MainScreenLayers`-Gate**,
exakt dieselbe Korrektur, die Issue T am 17.07. einen Block weiter oben gebraucht hat.
**Merke:** jede „was liegt hinter diesem Pixel"-Frage gehört auf `MainScreenLayers` — nicht auf
`BgLayerMask`, nicht auf Main|Sub. Das war jetzt zweimal dieselbe Falle.
User-bestätigt am 07.09.: „der Saum unter Wasser ist weg". Das Gate sitzt nur in Wand 2, die
**Außen**kantenglättung läuft unter Wasser unverändert weiter (54.245 Subpixel gemessen).

**Messwerte:** `ms` max 6,53 bei 16,7 Budget, 0 Fehler-/Warnzeilen über vier Kontexte.

## [2026-08-12d] — S21: Kantenglättung für Sprites, beide Wände

Nur Mesen. **Vorher analysiert, nicht vermutet** — Messungen und Sichtvergleiche siehe
`project_status`; die Bilder liegen unter `Downloads\dkc2_kantenvergleich\`.

**Warum es zwei Änderungen sind:** die SNES entscheidet Sprite-Deckung auf dem 1×-Raster
(Farbindex 0 = nichts), die 4×-Kunst bringt ihren eigenen weichen Saum mit. Bisher ging beides
verloren — außerhalb der Silhouette wurde gar keine HD-Identität hinterlegt, und innerhalb
mischte ein halbtransparenter Texel gegen `nm*`, was an einem Sprite-Pixel die **SD-Sprite-Farbe
selbst** ist. Sprite gegen Sprite gemischt ergibt keine sichtbare Glättung. Im Detailbild sieht
man, dass Wand 2 **allein** sogar schlechter aussieht (dünner, fransig) — die beiden gehören
zusammen.

**Wand 1** (`SnesPpu.cpp`): `FetchSpriteTile` hinterlegt die OBJ-Kachelidentität jetzt auch an
nativ TRANSPARENTEN Pixeln; die nativen Puffer bleiben unverändert gegated, das emulierte Bild
ist bitgleich. Ein deckender Eintrag gewinnt immer (`NativeOpaque`), damit das transparente
Pixel eines später gezeichneten Sprites die Identität eines überlappenden nicht löscht.
`RenderSprites` erfasst diese Pixel in **Slot 2**, mit Fenstermaskierung, aber **ohne** die
Prioritätsentscheidung — die kann dort nicht fallen, weil die Tilemaps noch nicht komponiert
haben. Der Filter entscheidet sie gegen `MainScreenFlags & 0x0F`, das den echten Gewinner trägt.
Dazu: `_hdSpritePixelsCopy` wird jetzt je Scanline geleert — bisher unnötig, weil jeder Zugriff
durch `_spritePriority[x] < 4` geschützt war; der Saumpfad hat diesen Schutz nicht und würde
sonst die Kunst der Vorzeile über den Schirm schmieren.

**Wand 2** (`SnesHdVideoFilter.cpp`): ein Sprite-Gewinner bekommt jetzt eine Bottom-Kachel aus
`BgTiles[]`, genau wie ein BG-Gewinner. Damit mischt der bestehende Kompositionspfad
halbtransparente Sprite-Texel gegen die HD-Kunst des Hintergrunds statt gegen die SD-Sprite-Farbe.
Wo der Hintergrund keine HD-Kunst hat, bleibt das alte Verhalten.

Der Saum wird **nach** Color Math gemischt: die Math-Flags des Pixels gehören dem BG, der es
gewonnen hat, und DKC2 wendet auf OBJ nie Color Math an (jeder aufgezeichnete Kontext hat
`CMEnabled` mit `OBJ=0`). Die Umfärbung auf die lebende OBJ-Palette gilt für den Saum genauso —
sonst wäre er der einzige Teil einer Figur, der die Level-Tönung ignoriert.

**A/B-Schalter `SNES_HD_NO_SPRITE_EDGES=1`** schaltet beide Hälften ab (S20-Verhalten).
Neue Zähler im FRAME-Log: `sprEdge=<Pixel mit Saumkunst>/<tatsächlich gezeichnete Subpixel>`.

**Erwartung:** sichtbar nur bei Kunst, die MIT Kantenglättung hochgerechnet wurde. Kruncha
(25,5 % weiche Texel) profitiert sofort, die Kongs (0,7 %) erst nach dem Neu-Upscale.

**★ NACHTRAG nach dem ersten Spieltest: beide Wände wirken nur noch auf Kunst MIT
Referenzpalette.** Der User bestätigte den Gewinn bei Kruncha und den Kisten, meldete aber die
Laufzeit-Objekte auf dem Hub (Wespen, Piratenflagge, Fackeln) als „verwaschener". Das Log
zeigte, warum: im Level zeichnete Wand 1 **nichts** (25.319 Kandidaten, 0 Subpixel — die dortige
Kunst stammt von vor dem Kantenfix), auf der Weltkarte dagegen 6.194 Subpixel pro Frame, und
genau dort liegen die Laufzeit-Objekte. Deren Kunst ist vom laufenden Bild abgegriffen, trägt
also Hintergrundfarbe in den Randtexeln; sie nach außen zu verlängern schmiert diesen
Hintergrund ins Bild. Der Export entzieht solchen Kacheln ohnehin die Referenz — **„hat eine
Referenzpalette" trennt Laufzeit- von Galerie-Kunst also exakt** und ist jetzt Bedingung für
beide Wände. Kruncha behält den Gewinn; die Kartenschrift verliert ihren Saum mit (sie hat
ebenfalls keine Referenz), was der User als unkritisch eingestuft hat.

## [2026-08-12c] — Die verworfenen Kong-Kacheln waren nie fremd: der Mittelwert war es (UNGETESTET)

Nachtrag zum Eintrag darunter. Dort wurden 139 Kong-Kacheln aus dem Pack genommen, weil ihre
Kunst zu keiner Palette ihres eigenen Sprites passte. **Sie passte doch — die Statistik hat sie
verworfen.**

**Messung an den 174 aussortierten PNGs, gegen eine Kontrollgruppe referenzierter Kacheln
desselben Kongs:**

| | verworfen | Kontrolle |
|---|---|---|
| deckende Fläche | 32,8 % | 67,2 % |
| **Median**-Fehler zur eigenen Kong-Palette | **635** | 196 |
| Texel weiter als 1500 weg | 31,2 % | 9,6 % |
| Farbsättigung | 59 % | 82 % |

Die Sättigung erledigt die alte Grau-Rampen-Vermutung: die Kunst ist voll gefärbt, kein
Platzhalter. Und der Median liegt bequem **innerhalb** der Schwelle — es ist der **Mittelwert**,
den ein Schwanz von Ausreißern darüber zieht. Diese Ausreißer sind Texel auf einem
Farbübergang, die im 4×-Bild zwischen zwei Paletteneinträgen liegen und zu keinem passen. Auf
einer vollflächigen Kachel sind sie eine Minderheit, auf einer dünn besetzten Silhouettenkachel
ist fast alles Rand — daher trifft es genau die Randkacheln.

**Änderung, bewusst so klein wie möglich:**
1. **WELCHER Kandidat gewinnt, entscheidet weiter der normale Mittelwert.** Das trennt die
   Teile eines Composite-Frames und bleibt unangetastet — hier steckt die Lehre aus v1/v3.
2. Nur das Tor „ist das überhaupt die Kunst dieses Sprites?" urteilt auf einem **getrimmten
   Mittelwert** (schlechtestes Viertel der Texel fällt raus).
3. Die Abtastung weicht auf **jedes** Texel aus, wenn jedes zweite zu wenig deckende findet.
   Betrifft ausschließlich Kacheln, die heute ohnehin durchfallen.

**Gegengeprüft mit der ausgelieferten Funktion in Node, an den echten PNGs:**
**120 der 139 Kacheln bekommen ihre Referenz und damit ihre HD-Kunst zurück**, und **alle 300
Kontrollkacheln behalten exakt die Referenz, die sie heute haben** (0 verändert, 0 verloren).
Das ist die entscheidende Eigenschaft: der Eingriff kann nichts umwerten, was bereits sitzt.

19 Kacheln bleiben ohne Referenz und werden weiter verworfen — 4 davon haben selbst bei
dichtester Abtastung zu wenig deckende Texel.

**Nach dem nächsten Export** sollte `sprites/` rund 20.183 Dateien haben (statt 20.063), und der
inaktive Kong bleibt flackerfrei, weil die 120 Kacheln jetzt mit korrekter Referenz mitgedimmt
werden statt zu fehlen.

## [2026-08-12b] — Phase 3+4: die OAM-Slot-Nummer fällt aus dem Sprite-Schlüssel (UNGETESTET)

**Das Problem:** für Sprites ist `Key.PaletteIndex` die OAM-Palette**n-SLOT**-Nummer
(`SnesPpu.cpp:1086`), und ein Slot trägt keine Identität — DKC2s Allokator (`CODE_BB8A6F`)
vergibt den nächsten freien von acht. Dasselbe Sprite landet je nach Level in einer anderen
Zeile, und das Pack musste dieselbe Kunst einmal pro Slot ausliefern, in dem sie je
aufgezeichnet wurde: **31.243 Dateien für 19.825 verschiedene Kacheln.**

Seit der Umfärbung ist das unnötig: eine Kachel **mit Referenzpalette** wird von ihrer
Referenz auf die lebende Zeile umgerechnet, ist also in jedem Slot richtig. Eine Kopie genügt.

**Mesen (Build S20, `SnesHdData.h` + `SnesHdPackLoader.cpp`):**
- Neue Konstante `SnesHdSpriteAnyPalette = 0xFF`. Sprite-Kunst **mit** Referenz wird unter
  diesem Wildcard-Slot abgelegt, Kunst **ohne** Referenz behält ihren aufgezeichneten Slot —
  die kann nur unter der Zeile richtig sein, für die sie gebacken wurde.
- `GetMatchingTile` probiert weiter zuerst den exakten Slot und fällt erst dann auf die
  Wildcard zurück. Ein Pack im alten Format verhält sich damit **exakt wie vorher**.
- Der Loader überspringt weitere Slot-Varianten desselben Hashes, **bevor** er sie dekodiert,
  und meldet `(N redundant slot copies skipped)`.
- **Der Schlüssel selbst (`GetHashCode`/`operator==`) bleibt unangetastet** — bewusst: die
  Wildcard ist nur ein weiterer Slot-Wert, kein Sonderfall im Vergleich.
- Die Umfärbung liest den Live-Slot weiter aus der **PPU**-Information
  (`pixelInfo.Sprites[0]`), nicht aus dem Pack-Schlüssel; die Wildcard kann dort nicht
  ankommen.

**Viewer (Export):** Kacheln mit Referenz werden nur noch **einmal** geschrieben statt einmal
je Slot. Die `[sprites]`-Zeile weist die Zahl getrennt aus.

**Erwartung mit dem aktuell installierten Pack** (ohne Neuexport, nur neuer Mesen-Build):
`31.243` Dateien → `20.063` geladene Kacheln, Meldung `11180 redundant slot copies skipped`.
Nach einem Neuexport schrumpft `sprites/` auf dieselben 20.063 Dateien.

**★ Kompatibilität:** ein mit dieser Viewer-Version exportiertes Pack braucht **Mesen S20+**.
Auf S19 und älter fänden die zusammengelegten Kacheln nur noch in genau einem Slot statt.
Umgekehrt ist S20 mit alten Packs unkritisch.

## [2026-08-12] — v4 bestätigt; Kacheln ohne Referenz, die gedimmt gezeichnet werden, fliegen raus

**v4 ist im Spiel bestätigt:** das Sprite-Flimmern ist weg, die getönten Kisten bleiben getönt.
Übrig blieb eine Kleinigkeit — der **inaktive Partner-Kong** (der dem aktiven folgt und
abgedunkelt dargestellt wird) sprang im Idle gelegentlich auf die helle Form.

**Ursache, komplett offline aus `snes_hd_spritecap.txt`, dem Diag-Log und dem installierten
Pack ermittelt (kein zusätzlicher Spiellauf nötig):**
1. Die Abdunklung ist **eine eigene CGRAM-Palette**, kein Color Math: unter den 188
   aufgezeichneten Palettenzeilen gibt es **exakt zwei** Paare „B ist die eintragsweise
   gedimmte Kopie von A", beide mit **Faktor 0,70** — Diddy und Dixie. 7.629 Kacheln werden
   unter beiden Zeilen gezeichnet.
2. Davon hatten **139 Kacheln HD-Kunst, aber keine Referenzpalette**. Mesen lässt
   referenzlose Kunst unangetastet, also blieben sie hell, während das Spiel dimmte. Über die
   Animationsphasen wechselten referenzierte und referenzlose Kacheln — das Flackern.
3. **Für diese 139 ist keine Referenz ableitbar.** Gemessen: ihre bestpassenden Paletten sind
   *fremde* (Median-Fehler 434–816) — exakt die v3-Falle. Ein Pool aus den Paletten der
   Geschwisterkacheln desselben Sprites rettet nur ~30 %, die im spritecap aufgezeichneten
   Zeilen der Kachel nur 52 von 139.

**Lösung: für solche Kacheln gar keine Kunst ausliefern.** `findDimmedHashes()` erkennt beim
Einlesen des Spritecaps die gedimmten Palettenpaare (das CGRAM-Feld jeder `SPR`-Zeile wurde
bisher gelesen und weggeworfen) und merkt sich, welche Kacheln unter beiden Zeilen laufen.
Fehlt so einer Kachel die Referenz, überspringt der Export ihr PNG — in der Galerie-Schleife
wie im Laufzeit-Pfad, der Referenzen ohnehin grundsätzlich entzieht. Mesen rendert sie dann
nativ, und nativ ist unter *beiden* Paletten richtig. Konsole meldet die Zahl in der
`[sprpal]`- bzw. `[laufzeit]`-Zeile.

**Vorab verifiziert statt vermutet:** die 174 betroffenen PNGs wurden aus dem installierten
Pack in Quarantäne verschoben und der User hat gegengesehen — **kein Flimmern mehr am
abgedunkelten Kong.** Danach wurde die ausgelieferte `findDimmedHashes()` in Node gegen die
echte Aufzeichnung laufen gelassen: sie findet dieselben 2 Paare, dieselben 7.629 Kacheln und
verwirft **exakt dieselben 174 Dateien** (Differenz 0). Die 5.969 Kacheln mit Referenz bleiben
im Pack, die werden ja korrekt umgefärbt.

**Offen:** warum passt die Kunst dieser 139 Kacheln nicht zur Palette ihres eigenen Sprites?
Verdacht Grau-Rampen-Platzhalter beim Galerie-Rendern (`res.isGrey` fliegt aus dem
Kandidatenpool, die Kunst selbst aber nicht) — Vermutung, nicht gemessen.

**Spritecaps aus älteren Sitzungen** kennen die Dimm-Paare nicht; beim Wiederherstellen aus der
Datenbank warnt die Konsole und bittet um einmaliges Neuladen der Datei.

## [2026-08-10b] — Referenzwahl: drei Anläufe, zwei davon falsch (UNCOMMITTED, ungetestet)

Fortsetzung des Eintrags darunter. Phase 1 lieferte die Referenzpaletten aus, Phase 2 (Mesen,
Build S19) färbte damit um — und **die Kisten in Hot Head Hop waren korrekt getönt**, der
Mechanismus stimmt also. Gleichzeitig fing Dixie an zu flimmern. Die Suche danach ging dreimal
schief, bevor sie saß; das ist hier festgehalten, damit der Fehler nicht wiederkommt.

### ★ DIE ZENTRALE LEHRE

**Das Umfärben rechnet ÜBER DEN PALETTENINDEX**, nicht über Farbähnlichkeit:
`nächster Referenzeintrag i` → `live[i] − ref[i]`. Die Referenz muss deshalb **die Palette
sein, unter der die Kunst gebacken wurde** — nicht irgendeine, die die Pixel gut erklärt.
Sonst ist die Index-Zuordnung willkürlich, und das Ergebnis sind zufällige Farben statt einer
kleinen Abweichung. „Passt am besten" und „ist die richtige" sind hier nicht dasselbe.

### Die Anläufe

**v1 — Referenz = Primärpalette des besitzenden Sprites.** Ergebnis: 1,1 % der Kacheln trugen
eine Referenz, die ihre eigenen Pixel zu unter 35 % erklärt, konzentriert auf die beiden
Kong-Paletten. Im Spiel: Dixies Haare flimmerten. Zwei Ursachen — zusammengesetzte Sprites
zeichnen Teile eines Frames mit ihrer Sekundär-/Block2-Palette statt der primären, und die
Referenz wurde erst am Sprite-Ende hinter einem Aggregat-Wächter festgeschrieben, wodurch
Kunst und Referenz auseinanderlaufen konnten.

**v2 — Veto pro Kachel (<35 % Deckung) plus Referenzentzug für laufzeit-überschriebene Kunst.**
Ergebnis: besser, Haare ruhig, aber das Shirt flimmerte weiter. Ursache: die verbliebenen
falschen Referenzen sind *plausibel* und kommen durch jede Deckungsschwelle. Gemessen: nur
67,6 % der Kong-Kacheln hatten die bestpassende Palette, bei 19,4 % passte eine andere deutlich
besser (oft 3–4× kleinerer Fehler).

**v3 — beste Palette aus ALLEN 27 Kandidaten. ★ FEHLSCHLAG, deutlich schlimmer.** Fast alle
Sprites flimmerten, einzelne Kacheln in willkürlich falschen Farben. Genau der Fehler aus der
Lehre oben: eine farbarme Kachel wird von vielen fremden Paletten gut „erklärt", und dann ist
die Index-Zuordnung Zufall. **Diesen Weg nicht noch einmal einschlagen.**

**v4 — aktueller, ungetesteter Stand.** Kandidaten sind nur noch die Paletten *des jeweiligen
Sprites* (Primär, Sekundär, Block2) — jede semantisch gültig, die Bewertung entscheidet nur,
aus welchem Teil eines Frames die Kachel stammt. Referenz und PNG werden in **derselben
Schleifeniteration** vergeben, können also nicht mehr auseinanderlaufen. Ceiling
`MAX_REF_ERR = 1500` fängt Kunst ab, die gar nicht von diesem Sprite stammt.

### Wie es entschieden wurde

Ein A/B-Schalter in Mesen (`SNES_HD_NO_SPRITE_RECOLOR=1`) rendert Sprites exakt wie S18. Zwei
Läufe mit demselben Pack: mit Umfärbung flimmerte alles, ohne Umfärbung war alles ruhig
(196 Frames, `sprRecol` durchgehend 0, davon 163 mit HD-Sprites). Damit war die Ursache
bewiesen statt vermutet.

**Prozess-Lehre:** dieser Schalter hätte am ANFANG der Fehlersuche stehen müssen. Stattdessen
wurde zweimal an der Zuordnung geschraubt, ohne zu wissen, ob die Umfärbung überhaupt schuld
ist — und v3 hat die Lage dabei klar verschlechtert. Bei der nächsten unklaren Regression:
erst eine Messung bauen, die die Ursache eingrenzt, dann ändern.

## [2026-08-10] — `sprite_palettes.bin`: die Farben, unter denen ein Sprite gebacken wurde

Phase 1 von vier. Der Export legt eine neue Datei in den Pack, die zu jedem HD-Sprite-Tile die
16 Referenzfarben trägt. Im Spiel ändert sich damit noch nichts — Mesen liest die Datei erst in
Phase 2.

### Warum das nötig ist

Der Auslöser: in Hot Head Hop sind die Kisten mit HD-Pack in der Default-Farbe statt in der
Farbe des Levels; ohne HD-Pack stimmen sie. Die Disassembly erklärt es vollständig:

```
Level-Sprite-Daten → init-Command $8D <pal_index>      (sprite_property.cpp:40)
  → DATA_FD5FEE + pal_index*2 → 15 Farben in Bank FD   (tile.cpp:21, index.html:3440)
    → Allokator CODE_BB8A6F: 8 Slots ($0B64), Refcounts ($0B74)
      → DMA nach CGRAM $80 + Slot*16 + 1
        → Slot-Nummer in die OAM-Attributbits 9-11     (AND #$0E00)
```

Der **Inhalt** einer Sprite-Palette gehört also zum Sprite bzw. zu seinem Level-Eintrag, die
**CGRAM-Zeile** dagegen ist eine dynamische Zuteilung. Genau diese Zeile ist aber alles, was
Mesen zur Laufzeit sieht — und sie trägt keine Farbidentität. Der bisherige Umgang damit
(`index.html:12780`) war, jede beobachtete `(Hash, Slot)`-Kombination aus dem Spritecap
aufzuzeichnen und dieselbe Kunst pro Slot erneut zu schreiben. Gemessen am aktuellen Pack:
31.417 Sprite-PNGs für 19.964 verschiedene Hashes, also 1,57 Kopien pro Hash und bei voller
Abdeckung bis zu 8×. Abdeckung heißt hier außerdem: genug Level gespielt haben.

Mit der Referenzpalette kann Mesen stattdessen Referenz→Live umfärben — eine Kunst pro Sprite,
in jedem Level richtig eingefärbt, so wie es die Hardware macht.

### Was drin steckt

- **`resolveSpritePalettes()`** — die dreistufige Kaskade (kuratiert → localStorage-Override →
  ROM-Initscript) aus `buildSpriteGallery()` herausgezogen. Beide rufen jetzt dieselbe
  Funktion: eine zweite Kopie würde abdriften, und der Export würde eine Referenz ausliefern,
  unter der die Kunst nie gerendert wurde.
- **`getAnimPaletteMap()`** — cached den 2048-Typen-Initscript-Scan, den Galerie und Export
  beide brauchen. Wird beim ROM-Wechsel verworfen.
- **Wächter.** Die Kaskade kann heute anders antworten als beim SD-Export (Override geändert,
  kuratierter Eintrag ergänzt). Eine falsche Referenz würde Mesen von den richtigen Farben
  *weg* färben. Deshalb misst der Export an den tatsächlich geschriebenen Texeln, wie viel die
  Kandidatenpalette erklärt, und liefert sie nur bei ≥ 35 % Abdeckung aus. Gemessen wird pro
  Sprite, nicht pro Kachel — eine einzelne Kachel kann zu Recht nur aus Kantenpixeln bestehen.
  Fehlende Referenz ist harmlos: Mesen lässt die Kachel dann in Ruhe.
- **`animId`/`name`** werden aus den Container-Sprite-Sets in den Export durchgereicht; ohne sie
  ist das Sprite nicht identifizierbar.

### Format

```
uint8  version = 1
uint16 paletteCount
paletteCount × 16 × uint16le bgr555      (Index 0 = transparent)
uint32 entryCount
entryCount × { uint64le contentHash, uint16le paletteIndex }
```

Dedupliziert über den Paletteninhalt — viele Sprites teilen sich eine Palette. Round-Trip
getestet inklusive max-uint64-Hash und gesetztem High-Bit.

### Bekannte Lücke

Laufzeit-Kacheln (`spritemiss`, Weltkarten-Schrift, Skull Cart, Fackeln) bekommen **keine**
Referenz. Sie wurden vom Bildschirm erfasst und tragen die Live-Farben des Erfassungsmoments,
nicht eine ROM-Referenz — dafür bräuchte es die CGRAM zum Erfassungszeitpunkt. Diese Kacheln
verhalten sich weiter wie bisher.

## [2026-08-07b] — Cross-Gfxset-Wiederverwendung, und warum sie auf FARBEN schlüsseln muss

Beim Pack-Export wird jede geschriebene BG-Kachel indiziert; ein Durchlauf davor füllt bei
Overworld-/Schirm-Sets die Lücken, indem er dieselbe Kachel aus einem anderen Gfxset kopiert.
Kein zweiter Upscale. Er läuft **vor** `hashes.bin`, weil eine kopierte Kachel dort einen
Eintrag braucht — der Loader leitet den ContentHash aus (Gfxset, Layer, VRAM-Adresse) ab und
überspringt die Datei sonst wortlos (`SnesHdPackLoader.cpp:459`).

**Ergebnis im Spiel: Funkys BG2 läuft nach Monaten in HD.** `bg2/gfxset_09` (252 Dateien)
existierte vorher überhaupt nicht. Der Abgleich läuft über den Inhalts-Hash, nicht über den
Dateinamen — nötig, weil 152 der Kacheln bei Funky an anderen VRAM-Adressen liegen als bei
Mainbrace, woran das bloße Kopieren am 31.07. gescheitert war.

**Korrektur am selben Tag:** Der erste Schlüssel war `(ContentHash, Paletten-INDEX, Layer)` und
lieferte im Spiel ein paar graue Kacheln in Funkys blauem Himmel. Der Index ist nur eine
Nummer — welche Farben darin stehen, entscheidet die CGRAM des jeweiligen Schirms, und HD-Kunst
trägt die Farben des Spenders eingebacken. Der Schlüssel führt jetzt die **16 echten
CGRAM-Farben** der Zeile. Ohne CGRAM wird die Signatur absichtlich gfxset-eindeutig, es findet
dann also gar keine Übernahme statt: lieber eine Lücke als eine falsche Farbe.

Gegengeprüft: Funkys und Mainbrace' Palettenzeile 7 sind byte-identisch, die richtige Übernahme
überlebt den strengeren Schlüssel also. Nur die Fehlgriffe fallen weg.

Die Ausgabe schlüsselt jetzt je Set und Ebene auf — eine Gesamtzahl allein ist nicht auswertbar:
fehlende Spender sind harmlos auf einer Ebene, die absichtlich keinen Upscale bekommt
(BG1 des Ladeschirms ist Laufzeit-Text), und ein echter Fund auf einer, die HD sein sollte.

### Offen aus dem Mesen-Test

- **Soundeffekte hängen nach** — Effekt kommt Sekunden verspätet. Emulator, nicht Pack.
  Erste Eingrenzung: tritt es auch mit deaktiviertem HD-Pack auf?
- **HD-Sprites ignorieren Level-Farbeffekte** — in Hot Head Hop stechen alle HD-Kisten heraus,
  zu hell. SD-Sprites bekommen den Effekt. Verdacht auf den S4-Sprite-Pfad
  (`SnesHdVideoFilter.cpp:959ff`), Zusammenhang mit dem Kanten-Befund vom 06.08. prüfen.
- Ladeschirm `0x44` braucht einen Container-Eintrag, damit der Durchlauf ihn erreicht.

## [2026-08-07] — Sieben eigenständige Schirme im Haupt-Dropdown, mit Level-Ansicht

Die Schirme stehen jetzt dort, wo Level, Hintergründe und NPC-Shops stehen: ein Block
`── Screens ──` mit synthetischen IDs ab `SCREEN_ID_BASE = 512` — dasselbe Muster, das der
`── Backgrounds ──`-Block ab 256 schon benutzt. `loadLevel()` prüft den Schirm-Bereich **vor**
dem 256er-Bereich, weil der nach oben offen ist.

**Sie zeichnen in die Level-Ansicht**, nicht nur in den Katalog: die von
`buildOverworldCatalog()` gerenderten Ebenen werden nach absteigender Ebenennummer gestapelt
(BG2 zuerst, BG1 darüber) und auf `visibleRows` beschnitten. Der Katalog wird weiterhin
mitbefüllt, beide Ansichten funktionieren.

Nebenbei repariert: die Vor/Zurück-Knöpfe nahmen an, alles über 256 sei ein Hintergrund. Vom
ersten Schirm aus wäre „Zurück" auf ID 511 gelaufen — kein gültiger Eintrag, und
`currentLevelId` wäre auf einem nicht existierenden Wert stehen geblieben. Vier Stellen
(Knöpfe und Tastatur) prüfen jetzt den Schirm-Bereich zuerst.

**Sechs weitere Schirme eingetragen** (`0x40`–`0x45`), Adressen aus den Lua-Dumps gelesen und
**nur Ebenen übernommen, deren Bit in `mainScreenLayers`/`subScreenLayers` gesetzt ist**:
Bonus Find the Token / Destroy Them All / Collect the Stars, Title Screen, File Select,
Game Over. Alle sieben liegen mit VRAM **und CGRAM** in der Ground Truth (46 Gfxsets).

Ein eigenständiger Schirm hat keine Level-ID und damit **keinen ROM-Palette-Rückfall** — der
führt über die Overworld-Config des Levels. Ohne CGRAM-Dump scheiterte das vorher an einem
nichtssagenden „Cannot read properties of null". Die Meldung sagt jetzt, was zu tun ist.

### Bekannt und noch offen

- **Scroll wird ignoriert.** Ansicht und Export unterstellen 28 Zeilen ab Tilemap-Null. Die
  Dumps sagen anderes: Bonus/Ladeschirm `vscroll 1023` (= −1, harmlos), **PP-Raum BG2
  `hscroll 663`** = 151 px Versatz. Für die Anzeige kosmetisch, für den Export nicht — es
  entscheidet, welche Kacheln als sichtbar gelten. **Vor dem ersten Upscale zu beheben.**
- **BG1 des Ladeschirms wird nicht exportiert.** „SELECT GAME", drei Spielstände mit
  Zeit/Münzen/Prozent, vier Optionen — alles Laufzeit-Text, ein Dump ist eine Momentaufnahme.
  Ein Upscale davon ergäbe halb HD, halb SD mitten im Text. Die Schrift ist laut User eine
  **dritte, eigene** (weder Shop- noch Weltkartenschrift) und gehört in den Schrift-Workstream.
- **Bonusraum-Text ist die Weltkartenschrift und läuft im Spiel schon in HD** — er kommt über
  Sprites (`LayerIndex 4`, scope-frei), nicht über die BG-Ebene. Die 127 BG1-Kacheln je
  Bonusraum sind also im Wesentlichen die Kongs.
- **Game Over** ist der einzige Schirm mit einer 64×64-Tilemap (`wide` und `tall`); bisher gab
  es nur 32×64 und 64×32. Ungetestet, ob der Renderer die Kombination sauber liest.

## [2026-08-06b] — Eigenständige Schirme als Set-Art, erster Eintrag: Pirate Panics versteckter Raum

Neue `kind: 'screen'` neben `'shop'` und `'map'`: einzelne statische Schirme, die das Spiel
außerhalb des Levelbetriebs zeigt. Sie haben keine Level-ID und sind nur über die Set-Auswahl
erreichbar. Beim Zuschneiden verhalten sie sich wie Shops — sie scrollen nicht, also liegen
Zeilen 28–31 auch bei ihnen unterhalb der 224 sichtbaren Zeilen.

Erster Eintrag `0x3F` = **Pirate Panic, versteckter Raum**. Adressen stammen aus einem
Lua-Dump des lebenden PPU-Zustands (`screen_dump.lua`), nicht aus Vermutungen — und
übernommen wurden **nur Ebenen, deren Bit tatsächlich in `mainScreenLayers`/`subScreenLayers`
steht**. Die Registerdatei trägt daneben veraltete Basen des vorigen Schirms; wer die
einträgt, baut sich Phantomebenen. (Auf Gangplank Galleon stehen so die BG2/BG3-Basen des
Hubs, obwohl `main=$11` nur BG1 zeigt.)

**Gemessen an den Dumps, nicht geschätzt:**

| Ebene | distinkte Kacheln | schon im Pack |
|---|---|---|
| BG1 ($2000/$7000) | 657 | 5 |
| BG2 ($6000/$7800) | 254 | **254, alle an ihrer Adresse UND in ihrer Palette** |

Das Spiel lädt für den Raum nur das BG1-CHR-Fenster neu und lässt Pirate Panics BG2 stehen.
BG2 braucht deshalb **keine neue Kunst** — aber es muss trotzdem unter dem neuen Gfxset
liegen, weil `SnesHdData.h:476` Kacheln fremder Gfxsets blockt. Das ist der Funky-Fall in
seiner einfachen Form: bei Funky lagen 152 von 239 Kacheln an anderen Adressen, hier 0.

**Fallstrick, der eine Fehldiagnose gekostet hat:** Pack-Dateinamen führen die VRAM-Adresse
als Hex in **Kleinbuchstaben** (`60a0_P01.png`). Ein Vergleich mit großgeschriebenem Hex
trifft nur die reinen Ziffernadressen — hier meldete er 154 falsche Fehlstellen, während in
Wahrheit 255 von 255 vorhanden waren.

## [2026-08-06] — Parser gegen echte S18-Aufzeichnungen geprüft, toter sprpos-Block entfernt

### Die Kopfzeilen-Änderung ist jetzt belegt, nicht mehr nur plausibel

Die fünf Parser wurden **wörtlich aus `index.html` geschnitten** (Klammerzähler, der Strings,
Kommentare und Regex-Literale überspringt) und in Node gegen die echten Aufzeichnungen des
S18-Builds laufen gelassen — getestet ist damit der Code, der im Browser läuft, nicht eine
Kopie davon. Skripte im Scratchpad: `viewer_check.js`, `line_budget.js`, `syntax_check.js`.

| Datei | Größe | Ergebnis |
|---|---|---|
| `snes_hd_spritecap.txt` | 60,0 MB | 401 001 Zeilen, 35 963 Hashes, **0 verworfen** |
| `snes_hd_bgcap.txt` | 3,5 MB | 21 886 Zeilen, 5476 distinkte Tiles, **0 verworfen** |
| `snes_hd_spritemiss.txt` | 30,2 MB | 185 482 Zeilen, 52 531 (hash,pal), **0 verworfen** |
| `snes_hd_sprpos.txt` | 87,0 MB | 1 277 327 Positionen, **0 verworfen** |
| `snes_hd_oam.txt` | 197,7 MB | 66 628 Frames, 2 796 160 Einträge, **0 verworfen** |

**Der stärkere Beweis ist die Zeilenbilanz:** gelesen + verworfen + Dubletten + Kopfzeilen +
Leerzeilen == Zeilen der Datei, und das geht in **allen fünf** exakt auf. Bei OAM etwa
66 628 + 2 796 160 + 1 = 2 862 789. Damit ist nicht nur „nichts fälschlich verworfen" gezeigt,
sondern auch „nichts stillschweigend geschluckt" — die schwächere Aussage hätte ein Parser,
der Zeilen kommentarlos überspringt, ebenfalls erfüllt.

### Der tote sprpos-Gruppierungsblock ist raus (−141 Zeilen)

Nach dem Ausbau von `rebuildRuntimeObjects` (05.08.) blieben sieben Bausteine als geschlossene
Insel liegen: `RT_FRAME_WINDOW`, `RT_FRAME_GAP`, `rtClusterSpatial`, `rtOverlaps`, `rtHasStack`,
`rtSplitPhases`, `rtSplitStacks`. `rtSplitStacks` rief nur noch sich selbst; von außen kam
niemand mehr rein.

**Wofür der Pfad da war:** die Objekterkennung der sprpos-Ära. `sprpos` schrieb jede Kachel nur
einmal je Sitzung, kein Frame war je vollständig — Objekte mussten aus Nachbarschaft und einem
Zeitfenster *geraten* werden. Drei Schritte, von denen zwei nur die Nebenwirkung des ersten
aufräumten: das 120-Frame-Fenster setzte Wörter zusammen (`GU CH` → `GULCH`), stapelte dabei
aber zwei Levelnamen an derselben Stelle und jede Animationsphase einer Fackel auf alle
anderen — und `rtHasStack`/`rtSplitPhases`/`rtSplitStacks` nahmen das wieder auseinander.
S17 hat die Grundlage weggezogen: ein OAM-Eintrag **ist** ein Objekt, jeder Frame ist
vollständig. Eine Notiz im Code hält fest, warum der Block weg ist.

Geprüft nach dem Eingriff: Syntaxprüfung aller `<script>`-Blöcke über `vm.Script` (kompiliert,
führt nichts aus) und eine Restsuche über alle sieben Namen plus `runtimeObjects` —
Treffer nur noch in Kommentaren. **CRLF wurde erhalten**, sonst hätte der Diff die ganze Datei
als geändert gezeigt.

### Nebenbefund für den nächsten Workstream

`buildOamObjects()` schreibt `fontObjectsCache` bevor dessen `let`-Deklaration im Quelltext
steht. Das ist unkritisch — alle Aufrufer sitzen in Handlern, keiner läuft beim Seitenaufbau,
die temporale Totzone wird also nie berührt. Notiert, damit es bei einer künftigen Umsortierung
nicht übersehen wird.

## [2026-08-05d] — Die Schrift-Seite läuft auf OAM, die sprpos-Gruppierung ist weg

Aufräum-Bestandsaufnahme über die acht Recorder-Dateien. Ergebnis der Zählung:

| Datei | Größe | Leser |
|---|---|---|
| `oam` | 180,8 MB | Viewer (Objektmodell seit S17) |
| `sprpos` | 87,0 MB | **nur noch die Schrift-Seite** |
| `spritecap` | 58,6 MB | Viewer (Sprite-Paletten) |
| `spritemiss` | 29,7 MB | Viewer (liefert die Pixel) |
| `bgcap` | 3,5 MB | Viewer + Diagnose |
| `cgramcap` | 3,1 MB | **niemand** |
| `diag` / `context` | 0,3 MB / winzig | niemand im Code — aber die Menschen |

**Korrektur einer früheren Behauptung:** ich hatte `sprpos` als „Ergebnis ungenutzt" geführt.
Für die Galerie stimmte das, für die Schrift-Seite nicht — `fontObjects()` rief
`rebuildRuntimeObjects({ pinned, splitByPal, window: 120 })` und das waren die 3836 ms pro Laden.

**Migriert:** `fontObjects()` leitet seine Objekte jetzt aus `oamObjects` ab. Eine Eigenschaft
des alten Pfades musste nachgebaut werden — `splitByPal`: ein Levelname liegt auf Palette 6,
aber ein OAM-Indexlauf kann mehrere Paletten tragen (ein Name direkt neben einem Kong-Kopf
landet im selben Lauf), und `rtTextObjects` verwirft alles mit mehr als einer Palette. Jedes
Objekt wird deshalb auf seine P6-Zellen zurechtgeschnitten, mit Neu-Verankerung der
Koordinaten — sonst trüge die Leinwand die Lücke der anderen Palette und der Leser sähe
Phantom-Leerzeichen zwischen den Buchstaben.

**Danach war `rebuildRuntimeObjects` ohne Aufrufer** — 107 Zeilen tote Gruppierung samt
`runtimeObjects` entfernt. Der sprpos-**Loader** bleibt vorerst, damit vorhandene Aufzeichnungen
weiter laden; er fällt, sobald Mesen aufhört, die Datei zu schreiben.

Nebenbei: `buildOamObjects()` leert jetzt `fontObjectsCache`, sonst läse eine frische
Aufzeichnung noch durch den alten Cache.

**Vom User bestätigt:** Schrift-Reiter meldet `31/31 Zeichen erfasst · 31 in HD`. Die Wortliste
ist dünner geworden (23 P6-Objekte aus 1638), aber das liegt an der **Aufzeichnung**, nicht am
Umbau: die vorhandene OAM-Datei ist im Wesentlichen der Hub, wo immer nur ein Levelname
gleichzeitig steht. Die alte `sprpos`-Datei stammte aus einem Durchgang über alle Weltkarten
(71 263 Zeilen → 67 Textzeilen). Für einen künftigen Schrift-Upscale braucht es entsprechend
eine OAM-Aufzeichnung über alle Karten — kein Codethema.

### Parser vertragen die Sitzungs-Kopfzeilen von Mesen S18

Mesen S18 stempelt beim Öffnen jeder Recorder-Datei eine `=== SESSION … ===`-Zeile, damit sich
die Sitzungen im angehängten Log auseinanderhalten lassen. Alle fünf Parser (`parseSpriteCap`,
`parseBgCap`, `parseSpriteMiss`, `parseSprPos`, `parseOam`) überspringen sie jetzt — sonst
hätten sie sie als verworfene Zeilen gezählt und die Statistik verfälscht.

Der `sprpos`-**Loader** bleibt bewusst erhalten, obwohl Mesen die Datei nicht mehr schreibt:
vorhandene Aufzeichnungen sollen weiter ladbar sein. Er fällt erst, wenn feststeht, dass die
alte Datei nicht mehr gebraucht wird.

## [2026-08-05c] — Der Pack-Export las Tilemaps > 32 Kacheln falsch

Lockjaws Schiffswand kam in Mesen in HD an, aber **falsch angeordnet** — die Kunst war im
Viewer richtig, im Pack richtig, nur im Spiel saßen die Stücke an den falschen Stellen.

**Ursache:** eine SNES-Tilemap über 32×32 ist kein flaches Gitter, sondern zwei bzw. vier
**32×32-Screens hintereinander** zu je 1024 Einträgen. Die Tilemaps liegen im Container als
rohe VRAM-Kopie (`vram[offset + i]`, `index.html:10468`), also genau in diesem Layout — und
vier Exporter lasen sie mit `tilemapWords[tileY * tilesW + tileX]`. Für jede Kachel mit
`tileX >= 32` ist das der falsche Eintrag: die Kunst wird unter der Adresse einer **anderen**
Kachel abgelegt. Zur Laufzeit matcht sie dann sauber (`hashes.bin` leitet den Hash direkt aus
der VRAM-Adresse ab und war deshalb korrekt) und zeigt trotzdem das falsche Bild — genau das
beobachtete Symptom.

Sämtliche **Renderer** haben es immer schon richtig gemacht (`:1437`, `:1850`, `:6833`,
`:7049`), ebenso der BG1-Pack-Export (`:12022`). Deshalb sah die Wand im Viewer gut aus.
Betroffen waren nur die vier Exporter, die eine gespeicherte `*TilemapData` lesen. Neu:
`tilemapEntryIndex()` an allen vier Stellen.

Die Wand (64×32) traf es voll. Lockjaws BG3 ist 32×32 und war deshalb nie betroffen — was dazu
passt, dass BG3 in der Aufzeichnung **null** Misses hat.

**Nachtrag, erster Anlauf war falsch:** nicht jede gespeicherte Tilemap kommt aus VRAM. Pirate
Panics BG3 hat eine leere VRAM-Tilemap (die Scroll-Engine streamt Metatiles), deshalb setzt
`:10473` eine **virtuelle** Tilemap ein, aus ROM-Metatiles expandiert — **160×64, flaches
Array**. Screen-Offsets darauf lesen Müll: `bg3/gfxset_07` fiel von 67 Kacheln auf **2**, weil
jedes `tileX >= 32` auf einen Null-Eintrag zeigte und als leer übersprungen wurde. Genau die
Takelage von Pirate Panic. Eine echte SNES-Tilemap ist pro Achse nur 32 oder 64 Kacheln groß —
das ist jetzt der Test, alles andere gilt als rekonstruiert und wird flach gelesen.
Gegen die Renderer-Formel (`:1437`) geprüft: für 32×32, 64×32, 32×64 und 64×64 liefert die
Funktion **identische und bijektive** Indizes, für 160×64 bleibt sie flach.

### Median-Kacheln — versuchsweise, nur für Mainbrace

Mainbrace' Wolkenhimmel wirkt in Mesen „nicht wie aus einem Guss", im Viewer dagegen sauber.
Der Effekt ist alt, nicht neu. Zwei Verdächtige wurden ausgeschlossen und einer belegt:

**Ausgeschlossen — R3, der Palette-Transform.** `bg2/gfxset_37` verteilt sich auf drei
Palettenzeilen (P07: 273 Kacheln, P05: 36, P03: 7), und R3 rechnet je Zeile einen eigenen
Helligkeitsfaktor — verschiedene Faktoren nebeneinander hätten genau solche Blöcke ergeben.
Nachgerechnet aus `palettes.bin` und den bgcap-CGRAM-Feldern, exakt nach
`SnesHdVideoFilter.cpp:1288-1302`: **jede beobachtete Zeile ist identisch zur Referenz**
(G37 Zeile 6, G7 Zeilen 1–7, G3 Zeilen 1/4/5) → `if(!differs) continue` → der Transform läuft
gar nicht. Entlastet.

**Belegt — Kontextabhängigkeit des Upscalers.** BG2 geht als *ein* Bild durch das Modell,
wird aber kachelweise geschnitten. Dieselbe 8×8-Kachel steht im Bild oft vielfach, und weil
die Nachbarschaft jedes Mal anders ist, fällt das hochgerechnete Ergebnis jedes Mal anders aus:

| | Pirate Panic BG2 (Himmel) | Lockjaw BG2 (Decke) |
|---|---|---|
| Fläche aus wiederholten Kacheln | **81 %** | 18 % |
| häufigste Wiederholung | **128×** | 29× |
| Streuung der HD-Fassungen | Median 3,0/255, max **13,3** | Median 0,3, max **0,9** |
| Kacheln mit Streuung > 3/255 | **106 von 213** | **0 von 108** |

Der Export nahm bisher das **erste** Vorkommen und verwarf den Rest — im Spiel bekommt die
Kachel dann überall die Fassung, die für genau eine Position geglättet wurde. Deshalb sitzt der
Effekt an Kachelgrenzen mitten im Bild und nicht an den Tapetenkanten, und deshalb ist er im
Viewer unsichtbar (der zeigt das Bild am Stück).

**Versucht und wieder entfernt:** pixelweiser Median über alle Vorkommen einer Kachel, versuchs-
weise nur für Mainbrace. Hat funktioniert (gegen vier Fälle geprüft: Ausreißer ignoriert,
gerade Anzahl mittelt die beiden mittleren, identische Fassungen ergeben die Identität, Alpha
bleibt erhalten) und war **im Spiel trotzdem kaum zu sehen** — vom User getestet. Der Tile-Effekt
blieb.

**Warum die Obergrenze prinzipiell niedrig ist** — der Grund, es nicht doch stehenzulassen: der
Median korrigiert den Farb-Bias *innerhalb* einer Kachel. Der sichtbare Effekt sitzt aber auch
an den **Rändern**, und die sind mit keinem Verfahren zu retten, das eine Kachel genau einmal
speichert. Kachel A liegt einmal neben B und einmal neben C; die Glättung kann nur zu einer der
beiden passen. Ein Sonderpfad für ein einzelnes Gfxset war das nicht wert.

Der einzige Weg, der die Ursache trifft, wäre BG2 wie BG1 zu exportieren — gepolsterte
Einzelkacheln plus Cluster, Auswahl über `tileScore`. Kostet einen eigenen Upscale-Durchlauf je
Set. Steht als Kommentar im Code, falls der Effekt je stört.

### Ein ungespiegeltes Vorkommen schlägt jetzt ein gespiegeltes

Mainbrace' Wolkenhimmel (BG2) sah in Mesen stellenweise falsch angeordnet bzw. gespiegelt aus,
im Viewer dagegen richtig. Ausgelöst hat es die Untersuchung, bewiesen ist die Ursache nicht —
der Pack stammte aus dem oben beschriebenen kaputten Zwischenstand. Was die Untersuchung aber
zutage gefördert hat, ist eine echte Fragilität:

Die Dedup war **„erste gewinnt" pro `{Adresse}_{Palette}`**. Dieselbe Kachel steht in der
Tilemap oft vielfach, mal gespiegelt, mal nicht — bei einem Wolkenhimmel ist das die Regel.
Welches Vorkommen zuerst kommt, hängt an der **Scan-Reihenfolge**, und genau die hat der
Tilemap-Fix geändert. Traf es ein gespiegeltes Vorkommen, musste die Kunst per
Canvas-Transformation zurückgedreht werden, bevor sie ins Pack ging (Mesen spiegelt selbst zur
Laufzeit, `SnesHdVideoFilter.cpp:122-133`, der Pack muss also die kanonische Fassung tragen).

Ein **ungespiegeltes** Vorkommen braucht überhaupt keine Transformation und ist damit immer die
verlässlichere Quelle. Es darf jetzt ein bereits geschriebenes, gespiegeltes ersetzen. Danach
hängt das Ergebnis weder an der Scan-Reihenfolge noch daran, dass das Zurückdrehen stimmt.
Betrifft die vier Exporter BG2, Wand, BG3 und cmFg; BG1 läuft über einen eigenen Pfad und ist
unverändert.

### Der Color-Math-Vordergrund wurde im Katalog nie in HD gezeigt

`renderBgImageSection(grid, ssb, label, '#ffab40', scale)` — **ohne HD-Argument**, also immer
die native Quelle, auch wenn der Container die hochskalierte hielt. Wortgleiche Auslassung wie
bei der Schiffswand einen Eintrag weiter oben.

Wo die HD-Fassung liegt, hängt an der QUELLE, und die beiden Fälle sind nicht austauschbar:
ein BG1-gespeister Overlay (SSB-Honig) hat sein eigenes Bild in `hdPack.cmFg`, ein
BG3-gespeister (Lockjaws Wasser) hat gar keine eigene Kunst — die BG3-Kette trägt ihn bereits,
weshalb der Container für ihn auch keinen `cmFgBlob` speichert. Beide Zweige sind jetzt
verdrahtet.

Dazu eine Sicherung: `renderBgImageSection` bemisst die Leinwand am HD-Bild, die CSS-Größe aber
am SD-Bild — ein Paar mit abweichender Geometrie käme verzerrt heraus. Der BG3-Overlay wird
getrennt von `catalogData.bg3Image` zusammengesetzt und teilt dessen Maße nicht garantiert.
Passt der Faktor nicht (ganzzahlig, in beiden Achsen gleich), bleibt es bei SD und die Konsole
sagt warum.

### Keine vollständig transparenten Kacheln mehr im Pack

Mesen überspringt eine vollständig transparente HD-Kachel beim Matchen
(`SnesHdData.h:475`, `IsFullyTransparent`) und zeichnet die native — die ebenfalls transparent
ist. **Am Bild ändert sich dadurch nichts**, in beiden Fällen ist dort nichts. Was die Datei
sehr wohl ändert, ist die Diagnose: jede taucht in `snes_hd_bgcap.txt` als Miss auf. Lockjaws
BG2 lieferte 74 solcher Dateien, die für **148 von 232** aufgezeichneten Misses verantwortlich
waren und die echten Fälle zugedeckt haben. Der Export schreibt sie nicht mehr und meldet die
Zahl in der Konsole.

### Nebenbefund für jede künftige Log-Auswertung

`snes_hd_bgcap.txt` & Co. werden mit `fopen(path, "a")` geöffnet
(`SnesHdVideoFilter.cpp:1742`) — **die Logs hängen über Sitzungen hinweg an.** Die Datei hatte
21 828 Zeilen aus vielen Läufen; die aktuelle Sitzung war der letzte zusammenhängende
G3-Block mit 232 Zeilen. Wer die ganze Datei auswertet, misst Vergangenheit.

## [2026-08-05b] — Die zweite BG2-Ebene konnte nie HD werden

Lockjaw's Locker (`gfxset_03`) hat zwei BG2-Ebenen: Decke und **Schiffswand**. Nach dem
HD-Import war die Decke hochaufgelöst, die Wand blieb SD.

**Das ZIP war in Ordnung** — `bg2_wall.png` liegt darin, sauber hochgerechnet
(512×256 → 2048×1024), und das Manifest trägt seinen `bg2_wall`-Eintrag. Der Fehler war,
dass **niemand ihn gelesen hat**: `bg2_wall` kam im ganzen Viewer genau zweimal vor, beide
Male auf der Schreibseite des SD-Exports. Kein Import-Zweig, kein Anzeige-Zweig.

Die Speicherseite hat den Rest erledigt: der Wand-Blob wurde bei **jedem** Container-Save aus
der nativen Quelle neu gebaut, unter dem Kommentar `no HD version yet, always native res` —
richtig, als er geschrieben wurde, und still falsch geworden, sobald der SD-Export die Wand
mitschickte. Selbst wenn der Import sie eingelagert hätte, wäre sie beim nächsten Speichern
wieder überschrieben worden.

Der Rest der Kette war die ganze Zeit fertig: `hdPack.wall`/`wallGfxSet` existieren, der
Container führt `wallBlob`, und der Pack-Export leitet seine Kachelgröße aus der Bildbreite ab
(`srcTileSize = wallBitmap.width / tilesW`) — er hätte ein 4×-Bild ohne jede Änderung
verarbeitet. Es fehlten nur die zwei Enden.

**Behoben:**
- Import liest `manifest.bg2_wall` nach `hdPack.wall` (+ `wallGfxSet`), wie BG2/BG3.
- Container-Save nimmt **HD zuerst**, native Quelle nur als Rückfall.
- **Abwärts-Sperre:** `hdPack.wall` wird nach jedem Save freigegeben, der nächste Save fände
  also nur die native Quelle und würde die HD-Wand still herunterstufen. Ein gespeicherter
  Wand-Blob wird deshalb nie durch einen **kleineren** ersetzt. Dieselbe Absicht wie bei
  BG2/BG3, nur über die Auflösung ausgedrückt, weil es kein HD/SD-Kennzeichen gibt.
- Katalogansicht zeigt die HD-Wand (`renderBgImageSection` bekommt sie jetzt übergeben) und
  die Statuszeile nennt sie als `Wand` — sonst wäre es genau der Fall von 08-05a gewesen:
  korrekt importiert, korrekt gespeichert, auf dem Schirm trotzdem SD.

## [2026-08-05] — Die importierte Laufzeit-HD-Kunst war da, nur nie auf dem Schirm

Erster echter Rundweg für die Hub-Objekte (Fackeln, Flagge, Luftschiff): SD-Export →
Upscale → HD-Import. Der Import lief durch, die Galerie zeigte trotzdem weiter SD.

**Das ZIP war in Ordnung** — gegengeprüft: 49 PNGs plus `manifest.json` auf beiden Seiten,
identische Objektliste, HD exakt 4× (56×36 → 224×144), `scaleFactor` sauber auf 4
umgeschrieben. Die Schnittrechnung des Importers geht auf. Der Fehler lag ausschließlich
im Viewer, an **zwei** Stellen:

1. **Die Laufzeit-Galerie hatte überhaupt keinen HD-Pfad.** `buildRuntimeCard` rief immer
   `renderRuntimeObject` — den reinen SD-Renderer. `renderRuntimeObjectHd` existierte
   längst, war aber nur an die Schrift-Seite angeschlossen, und `ensureRuntimeHdBitmaps()`
   wurde von der Galerie nie aufgerufen: `hdRuntimeBitmaps` blieb `null`, also lief jede
   Karte in den SD-Zweig. Die HD-Kunst lag die ganze Zeit korrekt in `hdPack.runtimeTiles`.
2. **Der Re-Render nach dem Import feuerte nicht.** Import und Container-Laden prüften
   `if (runtimeObjects)` — das **alte sprpos-Modell**. Die Galerie läuft seit S17 über
   `oamObjects`; wer nur `snes_hd_oam.txt` lädt, hat `runtimeObjects === null`. Selbst der
   Abdeckungszähler („X schon HD") blieb deshalb stehen, bis man einen Filter anfasste.

**Behoben:** Checkbox **„HD zeigen"** in der Laufzeit-Toolbar (Gegenstück zur Schrift-Seite),
Dekodieren der Container-Kacheln beim ersten Aufbau der Galerie, und beide Wächter auf
`oamObjects || runtimeObjects`.

Damit gilt in der Galerie dieselbe Regel wie bei der Schrift: **wo HD fehlt, bleibt SD
stehen** — ein nur teilweise hochskaliertes Objekt bekommt einen orangen Rand, statt still
ganz oder gar nicht zu erscheinen. Die Animationsbilder laufen über denselben Renderer,
sonst wäre der Hover ab Bild 1 auf SD zurückgefallen. Die Leinwand trägt echte Pixel
(SD 1×, HD 4×), die CSS-Größe bleibt gleich — das Umschalten verschiebt das Raster nicht.

## [2026-08-04c] — Objekte mit Animationsbildern, Merkliste, und drei verworfene Versuche

Der Bilder-Umbau von 08-04b war ein **Rückschritt** und ist zurückgenommen. Er lieferte
Einzelbilder statt Objekten; die Fackeln, die vorher sauber als eine Karte mit neun Bildern
dastanden, zerfielen wieder. Der richtige Schluss war nicht, das Modell zu ersetzen, sondern
seinen *einen* Fehler zu beheben.

**Stand jetzt (und getestet):** OAM-Einträge werden je Frame über zusammenhängende
Indexläufe zu Momentaufnahmen gruppiert; Identität ist die **Struktur** (welche Zellen, wo,
Größe, Palette), die abweichenden **Inhalte sind die Animationsbilder**. Eine Karte je
Objekt, Animation beim Überfahren, Export je Bild als eigene Datei (`ID_f00.png` …) mit
`object`/`frame`/`frameCount` im Manifest — dieselbe Logik wie bei den Charakter-Sprites.

Am Hub bestätigt: **2285 Objekte, 81 animiert**, 254 ms. Vom User geprüft und benannt:

| ID | Objekt | |
|---|---|---|
| `G53-40x20-P0-77D8` | Fackelpaar Höhle | 9 Bilder |
| `G53-33x17-P0-CB35` | Fackelpaar Hütte | 8 Bilder |
| `G53-24x32-P0-C24E` | Flagge **mit Mast** | 4 Bilder |
| `G53-16x16-P0-8AE5` | Flagge animiert, ohne Mast | 10 Bilder |
| `G53-32x56-P2-C46A` | **Luftschiff** | 1 Bild, 13 Zellen |

### Drei Versuche, die Flagge automatisch zusammenzuführen — alle verworfen

Die beiden Flaggen-Karten teilen nachweislich **12 Kacheln**, gehören also zusammen. Keiner
der Ansätze hat das ohne Kollateralschaden geschafft:

1. **Verschmelzen über gemeinsame Kunst** → kettet transitiv über den Schirm: ein Klumpen
   `219x184` mit **868 Bildern**, der beide Fackelpaare gefressen hatte.
2. **Wachstumsbremse obendrauf** (eine Vereinigung darf das Objekt nicht vergrößern) → leckte
   trotzdem (`131x88`), und **die notierten IDs lösten nicht mehr auf**.
3. Davor schon: **Slot-Verfolgung über die Zeit** → zerlegt die Fackel in Flamme und Mast;
   **„eine Animation kehrt zurück"** → stuft auch die Kartenbuchstaben als zyklisch ein.

Die Verschmelzung ist **ganz entfernt**, mit einem Kommentar im Code, warum. Praktischer Weg
bis auf Weiteres: **beide Flaggen-Karten exportieren** — der Import beansprucht Kacheln per
Hash, Mast und Wehbilder landen beide im Pack. Dass die Vorschau die Flagge ohne Mast zeigt,
ändert am Ergebnis im Spiel nichts.

### ★ Merkliste

Weil keine Regel zuverlässig ein brauchbares Objekt von einem Bruchstück trennt, ist das
Urteil des Auges der einzige verlässliche Schritt — und muss deshalb einen Reload überleben.
Jede Karte hat einen **Stern**; die Merkliste liegt in IndexedDB und ist über die
Objekt-ID adressiert, die aus der Kunst abgeleitet und damit über Neuaufzeichnungen stabil
ist. Dazu Filter **„★ nur Merkliste"** und Knopf **„★ Merkliste exportieren"**, der
unabhängig von den Filtern arbeitet und fehlende IDs in der Konsole nennt.

## [2026-08-04b] — Das falsche Problem: nicht Objekte, sondern Bilder

Nach dem OAM-Umbau blieb die Ansicht unbefriedigend: die Flagge tauchte mehrfach auf und
keine Kachel zeigte die ganze Animation, Rauchwolken bewegten sich nicht, Wespen erschienen
verstreut. Ich habe daraufhin **drei** Verfahren für die Objekt-Identität gebaut und
gemessen — und alle drei scheitern, jedes anders:

| Identität | Fehler |
|---|---|
| **Struktur** (welche Zellen, wo) | Einzelzellen entarten: alles 16×16 auf P6 landet in einem Topf, sämtliche Kartenbuchstaben wurden „Phasen" eines Objekts |
| **Slot über die Zeit** | zerlegt die Fackel in Flamme und Mast; große Objekte verschmelzen (101×135 mit 197 „Phasen") |
| **„Animation kehrt zurück"** | stuft die Buchstaben ebenfalls als zyklisch ein — man läuft zum Level-Symbol zurück und sieht denselben Buchstaben |

Der Grund, warum keines funktioniert: **eine Animation ändert ihre OAM-Zusammensetzung**
(die wehende Flagge braucht mal mehr, mal weniger Einträge), und ein Slot wird
weiterverwendet. Es gibt keine verlässliche Objektgrenze in diesen Daten.

**Und sie wird auch nicht gebraucht.** Das Pack ist nach **Kachel-Hash** adressiert.
Instanzen, Positionen, Phasenreihenfolge, ja die Animation selbst ändern nichts am Ergebnis:
drei gleich aussehende Wespen brauchen ein Bild, eine Wespe mit fünf Posen braucht fünf.
Gebraucht wird schlicht **jedes unterschiedliche Bild einmal** — und ein OAM-Eintrag *ist*
per Definition ein zusammenhängendes Bild, die Einheit, die das Spiel selbst zeichnet.

Das ist dieselbe Form wie bei der Schrift-Seite: Wörter liefern dem Upscaler **Kontext**,
die Prüfliste sind die **Glyphen**. Hier liefert die Umgebung den Kontext, die Prüfliste sind
die **distinkten Bilder**. Die perfekte Objekt-Identität zu suchen war das falsche Problem —
sie hat nie beeinflusst, was produziert werden muss.

**Die Ansicht zeigt jetzt Bilder statt Objekte**, jedes mit einer **stabilen ID** aus seinem
Inhalt (`G53-16x16-P3-3424`) — kopierbar, über Sitzungen gleichbleibend, also als Handgriff
zum manuellen Aussortieren brauchbar. Dazu Suche nach ID oder Hash, Palettenfilter,
„8×8 ausblenden", und ein Zähler „N Bilder · davon HD · offen". Beim Überfahren zeigt die
Karte, **womit** das Bild exportiert wird: nicht der nackte Ausschnitt, sondern die ganze
OAM-Gruppe, in der es vorkam (im Mittel 10× so viel Fläche) — ein 8×8-Schnipsel allein
upscalet schlecht, und der Import beansprucht Kacheln ohnehin per Hash.

Gemessen am Hub: **240 distinkte Bilder** (226 zeichenbar), davon 42 ab 16 px. Darin die
Wespe als **5 Posen**, die Piratenflagge als ~14, die Rauchwolken als ~20. IDs eindeutig.
190 ms.

Entfernt: die gesamte Objekt-Identitätslogik (`buildOamObjects`, `oamPhaseTiles`, 95 Zeilen)
samt der Schalter *nur animierte*, *Einzelsprites aufteilen*, *Größe* und der Phasen-Vorschau.

## [2026-08-04] — Laufzeit-Objekte kommen jetzt aus OAM (S17)

Der bisherige Weg hat Objekte aus einer pixelweise abgetasteten, global deduplizierten
Bildschirmaufnahme **erraten**. `sprpos` schreibt jede Kachel genau einmal je Sitzung, kein
Frame ist also je vollständig — deshalb hing es am Frame-Fenster, ob ein Objekt überhaupt
erschien. Die Piratenflagge des Hubs war bei Fenster 1 da und bei 600 weg. Das war kein
Einstellungsproblem, die Information fehlte schlicht.

**Sie fehlte nur in unseren Dateien, nicht im Emulator.** `SpriteInfo` trägt `Index` — die
OAM-Nummer. Ein OAM-Eintrag **ist** ein Objekt (8×8 bis 64×64), vom Spiel so definiert,
mit eigener Position, Größe, Palette und Spiegelung.

**Mesen S17** schreibt `snes_hd_oam.txt`: je Frame ein Kopf plus eine Zeile je sichtbarem
Eintrag, mit allen Unterkachel-Hashes. Geschrieben wird nur bei **geänderter** sichtbarer
OAM-Belegung — ein stehender Schirm kostet einen Frame, eine Fackel einen je Phase.

**Die Gruppierungsregel ist keine Heuristik mehr.** Räumliche Überlappung scheitert (auf dem
Hub berühren sich Flagge, Kongs und Levelname und verschmelzen zu einem Block — gemessen,
es reproduzierte exakt die alten Klumpen). Ein Spiel legt die Sprites eines Objekts aber in
einem **zusammenhängenden OAM-Indexblock** ab. Danach gruppiert, fallen die Objekte einzeln
heraus.

**Identität = Struktur, Inhalt = Phase.** Ein Objekt wird über seine Zellen und deren Lage
identifiziert; wechseln nur die Kachelnummern, ist das eine **Phase** desselben Objekts.
Damit ist eine Fackel *ein* Eintrag mit 9 Phasen statt 9 unabhängiger Objekte, und der
Export verschickt alle Phasen als nummerierte Serie.

Gemessen an der Hub-Aufzeichnung (4264 Frames, 268 013 Einträge, **0 verworfen**):
**1638 Objekte in 163 ms** — der alte Weg brauchte 4800 ms für ein schlechteres Ergebnis.
Geometrie aller Phasen konsistent. Gerendert: Fackeln (9 Phasen), **wehende Piratenflagge**
(6), Torhaus mit beiden Fackeln (8), Rauchwolken — jeweils vollständig und getrennt.

**Aufgeräumt:** die Laufzeit-Toolbar verliert *Fenster*, *nach Palette trennen*,
*Stapel zeigen*, *Einzelkacheln aus*, *nur 1. Phase* und den Palettenfilter — alles davon
existierte nur, um die Rateverfahren zu bändigen. Übrig bleiben Gfxset, Größe,
*nur zeichenbare* und *nur animierte*. Karten zeigen die Animation beim Überfahren.

`sprpos` wird nur noch von der Schrift-Seite benutzt und kann entfallen, sobald diese
ebenfalls auf OAM steht — sie läuft und ihre Kunst liegt im Container, deshalb bewusst
nicht im selben Schritt angefasst.

## [2026-08-03] — Laufzeit-Sprites: die Weltkarten-Schrift kommt in den Container

Die Kartenschrift lief seit dem 31.07. in HD, aber **am Viewer vorbei**: erzeugt von zwei
Wegwerf-Skripten, die Glyphen lagen ausschließlich im Pack-Ordner. Ein Ordner-Neuaufbau
hätte sie gelöscht, und „nochmal upscalen" hätte bedeutet, die Skripte erneut zu schreiben.
Dieser Eintrag holt den Weg in den Viewer.

**Der Kern ist eine Beobachtung, keine neue Pipeline:** ein Wort von der Weltkarte
(`KREM QUAY`) ist strukturell dasselbe wie ein Sprite-Frame — ein Bild plus eine Liste von
(Hash, x, y)-Zellen. Es fehlte also nur eine neue *Quelle*, die in die vorhandene Kette
einspeist, nicht ein zweiter Strang daneben.

**Neu: Knopf „Laufzeit"** (Katalog-Toolbar) lädt `snes_hd_spritemiss.txt` (die Pixel:
32 VRAM-Bytes + 16 CGRAM-Farben je Kachel) und `snes_hd_sprpos.txt` (die Positionen) —
beide auf einmal, unterschieden **am Inhalt, nicht am Dateinamen**, weil beide Dateien
über Sitzungen fortgeschrieben und dabei umbenannt/kopiert werden. Persistiert im
vorhandenen IndexedDB-Store `recordings`, wie der Spritecap.

**Die Gruppierung war die eigentliche Arbeit.** Drei Schritte, jeder als Antwort auf einen
Defekt, der erst an den echten Aufzeichnungen sichtbar wurde (79 290 Positionszeilen):

1. **Fenster über Frames.** sprpos dedupliziert über (hash,x,y) und lässt pro Frame die
   Kacheln aus, deren VRAM sich mitten im Frame geändert hat (`SnesHdVideoFilter.cpp:1978`).
   **Kein einziger Frame enthält daher ein ganzes Wort** — „GLOOMY GULCH" verteilt sich über
   mehrere. Gruppierung pro Frame lieferte Fragmente wie `GU CH`.
2. **Räumliches Clustern**, 8×8-Kästen die sich berühren. Erledigt nebenbei die 8×16-Schrift
   ohne die alte (y, y+8)-Paarungsregel — genau die hatte am 31.07. den Apostroph und das
   `V` aussortiert, weil Satzzeichen einzeilig sind.
3. **Stapel trennen.** Zwei verschiedene Levelnamen an derselben Stelle innerhalb eines
   Fensters überlagern sich zu Buchstabensalat. Ein sauberes Objekt hat nie zwei Kacheln auf
   einer Position — wo doch, wird entlang von Lücken in den Frame-Nummern getrennt.

**Zeit ist bewusst KEINE Cluster-Dimension.** Die Aufsplittung passiert *innerhalb* eines
Wortes, eine Zeitbedingung zerlegt also Wörter statt sie zu trennen. Gemessen: 29 Objekte
mit ⌀ 3,9 Kacheln gegen 15 mit ⌀ 6,2.

Verifiziert **vor** dem Viewer-Code an den echten Daten (`scratchpad/final_algo.py`), danach
die JS-Portierung gegen dieselben Daten gegengerechnet (`js_smoke.js`): beide liefern
identisch **24 Objekte, die 63 Kartenschrift-Kacheln abdecken**; gerendert sind es lesbare
Wörter (`MONKEY`, `TARGET`, `K.ROOL`, `CAULDRON`). 707 ms für 79 290 Positionen.

**Neue Ansicht „⧉ Laufzeit"** in der Sprite-Galerie mit eigener Toolbar: Filter nach Gfxset
und Palette, „nur zeichenbare", Stapel ein/aus, Einzelkacheln aus (die upscalen schlecht),
und ein **Set-Cover-Vorschlag** — die kleinste Objektmenge, die jede sichtbare Kachel
abdeckt. Ausdrücklich ein Vorschlag: die Auswahl bleibt frei änderbar, und ein Zähler sagt,
wie viele Kacheln sie erreicht. Das **Fenster (30–600 Frames) ist einstellbar**, weil der
beste Wert davon abhängt, wie schnell die Karte durchlaufen wurde.

**Der Rundweg schließt sich:** SD-Export (`exportType: 'runtime'`, ein PNG je Objekt mit
8 px Rand) → Upscale → `Import HD` misst die Skalierung **am Bild statt am Manifest** und
schneidet sofort in hash-adressierte Kacheln → Container-Set `type:'spritemiss'` →
Pack-Export nach `sprites/{hash16}_P{pal}.png`.

Zwei Entscheidungen, die dabei bewusst anders sind als bei den Galerie-Sprites:
- **Geschnitten wird beim Import, nicht beim Export.** Die Einheit ist die Kachel, nicht das
  Objekt: derselbe Buchstabe steckt in vielen Wörtern, ganze Objekte zu speichern hieße,
  ihn mehrfach abzulegen und offenzulassen, welche Kopie gilt.
- **Die Palette kommt aus der Aufzeichnung, nicht aus dem Spritecap.** Die SPRMISS-Zeile
  trägt sie mit. Damit hängt dieser Zweig nicht am Spritecap und kann nicht mangels
  Aufzeichnung stillschweigend leer bleiben. Container-Import wie Pack-Export **mergen**,
  damit die Schrift heute und der Schädelwagen nächsten Monat nebeneinander bestehen.

### Nachtrag am selben Tag: S16 — der Positions-Recorder verlor systematisch Kacheln

Der erste Viewer-Test zeigte Wörter mit **halben Buchstaben** (`ANTICS` ohne obere Hälfte
von `C` und `S`, `FUNKY` ohne untere Hälfte des `Y`) und ein DK-Münz-Symbol, dem reihenweise
eine **Ecke** fehlte. Die Objekte meldeten dabei `missing = 0` — die Kacheln fehlten also
nicht an Pixeln, sondern **im Layout**: sie standen gar nicht erst in `sprpos`.

**Ursache in Mesen, nicht im Viewer.** `SnesPpu::RenderSprites` (`SnesPpu.cpp:809`) hinterlegt
die HD-Kachelinfo nur dort, wo `color != 0` — eine Sprite-Kachel existiert in `ScreenTiles`
also ausschließlich an ihren **deckenden** Pixeln. S15 tastete ein 8-Pixel-Raster ab, pro
Kachel genau einen Punkt; lag der auf einem transparenten Pixel, verschwand die Kachel
spurlos. Das trifft zwangsläufig die dünnen Stellen: Buchstabenhälften ohne Tinte in der
abgetasteten Zeile, und die Ecken runder Symbole, wo die Kunst leer ist.

**S16** tastet jeden Pixel ab und meldet den **Kachelursprung statt des Abtastpunkts** —
`OffsetX/OffsetY` sind der Versatz innerhalb der 8×8-Kachel, also ist der Ursprung
`(px - OffsetX, py - OffsetY)`. Dedup über `(hash, originX, originY)`: damit ist gleichgültig,
welcher Pixel getroffen wurde, und das Volumen bleibt bei etwa einer Zeile je Kachelinstanz.

Der Viewer erkennt eine Aufzeichnung im alten Rasterformat an ihrer Signatur (alle x auf
Vielfachen von 8, alle y auf demselben Rest) und sagt beim Laden, dass neu aufgezeichnet
werden muss — **die alte Datei vorher löschen**, Mesen hängt an.

### Zweiter Testlauf: Animationen, Überlappungen, und der Weg als Klumpen

Mit S16 waren die Buchstaben vollständig. Der Test zeigte drei weitere Fälle, die alle
denselben Kern haben — **mehrere Dinge im selben Bildbereich**:

1. **Animierte Objekte lagen übereinander** (Fackeln, Bienen, Rauchwolken, Krokodilmaul,
   Klubba-Symbol). Ein animiertes Sprite bemalt dieselben Positionen mit wechselndem Inhalt;
   im Fenster stapeln sich damit alle Phasen. Zeit trennt sie nicht — die Phasen liegen
   wenige Frames auseinander, enger als ein einzelnes Wort sich verteilt.
   **Neu `rtSplitPhases`:** Kacheln in der Reihenfolge ihres ersten Auftretens in Schichten
   legen, jede Kachel in die erste Schicht, in der sie nichts überlappt und nicht lange nach
   deren letztem Eintrag kommt. **Schicht 0 ist damit das Objekt, wie es zuerst erschien** —
   in sich stimmig und vollständig, und genau das genügt der Pipeline. Toolbar-Schalter
   „nur 1. Phase" (Standard an), Karten zeigen `▶1/3`.
2. **Zwei Levelnamen überlappten sich, ohne dieselbe Position zu belegen.** Seit S16 sind die
   Koordinaten echte Kachelursprünge, zwei Namen an fast derselben Stelle liegen also wenige
   Pixel versetzt — der alte Stapeltest auf *identische* Position sah nichts. Er prüft jetzt
   **Überlappung** (`|dx| < 8 && |dy| < 8`): zwei Kacheln EINES Objekts bedecken nie dieselben
   Pixel, Überlappung heißt also immer „zwei Dinge übereinander".
3. **Der Kartenweg verschluckte die Levelnamen.** Die Pfad-Sprites liegen lückenlos
   aneinander, reine Adjazenz kettet damit den halben Schirm zu einem Klumpen — und der
   Levelname obendrauf verschwand darin. **Geclustert wird jetzt innerhalb einer Palette:**
   eine OBJ-Kachel hat genau eine, die Schrift sitzt auf P6, der Weg nicht.
   Ergebnis: die Abdeckung der Kartenschrift stieg von **72 auf 95 von 96 Kacheln**.

Gemessen an der echten S16-Aufzeichnung: 3897 Objekte aus 60 006 Positionen in 638 ms,
**0 nicht trennbare Stapel**, 18 Objekte decken die Schrift ab (⌀ 7,1 Kacheln, breitestes
104 px). Gerendert sind es geschlossene Wörter — `BONUS BONANZA`, `KROCODILE`, `SWANKY'S`,
`KREMLAND`, `TOPSAIL` — und das DK-Symbol **einmal vollständig**.

Nebenbefund aus derselben Messung: die Datei hatte exakt 60 006 Zeilen, also den
Recorder-Deckel. Die Aufzeichnung brach mitten im Kartenlauf ab, spätere Karten waren nur
teilweise erfasst. **Deckel auf 200 000 angehoben** (~14 MB).

### Nachhaltigkeit: die Schrift als Ground Truth statt als Fundstück

Bis hierher war jeder Durchlauf Laufzeit-Archäologie: ablaufen, hinschauen, hoffen. Das
muss er nur EINMAL sein — die Kartenschrift ist eine **geschlossene Menge** (28 Glyphen plus
Satzzeichen, dieselben Kacheln auf allen Karten), und sie ist **überprüfbar**, weil die
Levelnamen im Klartext lesbar sind. Was fehlte, war das Speichern.

**Neu `font_groundtruth.js`** nach dem Muster von `vram_groundtruth.js`: `Zeichen →
(oberer Hash, unterer Hash)`. 28 Glyphen aus der Sitzung vom 31.07., dazu zwei heute
**aus dem Kontext abgeleitet** statt geraten:

- **`'`** = `E7B7C0F1CBBEE6C1`, einzeilig — steht in `SWANKY?S`, `LUBBA?S`, `KROW?S`,
  `JAW?S`, `OL?S`, `Y?S`. Sechs unabhängige Genitiv-Kontexte lassen nichts anderes zu.
- **`-`** = `BCF61FDA52C9D363`/`AF750CD8D7718ED8` — `HOT?H` ist HOT-HEAD HOP.

Beide waren am 31.07. **von Hand** ins Pack nachgeliefert worden, ohne dass jemals notiert
wurde, welches Zeichen welcher Hash ist. Jetzt steht es fest.

**`rtReadObjectText()`** liest ein Objekt als Text: erst nach y in Zeilen trennen (ein
Objekt kann `MONKEY MUSEUM` zweizeilig tragen), dann Spalten von 1–2 Kacheln nachschlagen.
Erkennt es weniger als die Hälfte, schweigt es — auf Palette 6 liegen auch die Kong-Köpfe,
und eine Reihe `?` ist keine Information. Die Karten tragen damit **Namen statt Kachelzahlen**.

**Knopf „🔤 Schrift-Status"** beantwortet „bin ich fertig?", ohne irgendetwas nachzuspielen:
je Glyphe aufgezeichnet/HD, alle gelesenen Namen, unbekannte Glyphen **mit dem Wort, in dem
sie stehen** (damit ist die nächste Zuordnung wieder eine Ableitung, keine Rateübung), und
welche Karten und Shops der Recorder nie gesehen hat — letzteres aus `OVERWORLD_SETS`
und der Aufzeichnung selbst, ohne erfundene Levelnamen-Liste.

Gegen die echte S16-Aufzeichnung geprüft: **96 Namen gelesen** (`GANGPLANK`, `CROCODILE`,
`KREMLAND`, `SWANKY'S`, `LOCKER!`, `KARNAGE!`, `TARGET`, `SHOWDOWN` …), nur noch
**4 unbekannte Glyphen-Vorkommen** statt über 20. Damit wird aus „alle Level ablaufen"
eine gezielte Restliste.

### HD-Anzeige, Aufräumen, und die drei restlichen Objekte

**Die HD-Kunst ist jetzt im Viewer sichtbar.** Die Schrift-Seite zeichnet wahlweise die
Kacheln aus dem Container statt der aufgezeichneten SD-Kacheln („HD zeigen", Standard an);
wo noch keine HD-Kachel liegt, bleibt die SD-Version stehen und das Wort bekommt einen
orangen Rahmen — man sieht also sofort, was fertig ist. Die Blobs werden einmal dekodiert
und zwischengespeichert.

**Absturz behoben.** `renderRuntimeObject` legte **pro Kachel ein Canvas-Element** an (über
1× sogar zwei). Beim Abschalten von „nur 1. Phase" vervielfacht sich die Objektzahl um die
Animationslänge — die Galerie erzeugte zehntausende Canvases und der Browser stand.
Jetzt ein Canvas je Objekt mit direkt geschriebenen Pixeln, Zoom über CSS. Dazu Kartenlimit
2000 → 400 und `rtCoveredKeys()` aus der Kartenschleife gehoben (wurde 2000× neu gebaut).

**Die Schrift-Seite lädt selbst.** Sie prüfte `runtimeObjects` — also die Gruppierung des
*Laufzeit*-Reiters — statt der Aufzeichnung, und blieb deshalb leer, wenn man direkt auf
Schrift ging. Sie fragt jetzt die Aufzeichnung ab und baut ihre eigene Gruppierung.

**🧹 Aufräumen** wirft aus der gespeicherten Aufzeichnung alles heraus, was dieser
Workstream nicht braucht. Ein Schirm bleibt, wenn er ein bekannter Karten-/Shop-Gfxset ist
**oder Kartenschrift enthält** — die zweite Regel rettet die Karten ohne HD-Kunst, die
`gfx=-1` melden und sonst wie Spielszenen aussähen (genau von so einem Schirm kam das V).
Gemessen: Positionen 260 019 → 76 603, Kacheln 51 510 → 2 996, Gruppieren 4779 → 950 ms,
weiterhin 106 lesbare Wörter. **Achtung:** der Schädelwagen lebt in einer Spielszene und
würde dabei verworfen — die Dateien in Downloads bleiben unangetastet.

**Das V ist gefunden** — in `CLAPPER'S CAVERN` (K. Rool's Keep, nicht Gloomy Gulch, wie ich
zuerst behauptet hatte). Nicht über gelesene Wörter, sondern über die Kacheln: die Zeile las
sich `C L _ P _ E R … C _ V _ R N`, C/R/N sitzen passend und das erste C hat denselben Hash
wie das C von CAVERN. Gerendert ein eindeutiges V. **31 Glyphen — das Alphabet ist komplett.**
Weil seine Nachbarn nie aufgezeichnet wurden, steht das V isoliert; deshalb neu: **Zeichen
ohne Beispielwort werden einzeln als 8×16-Glyphe exportiert** statt zu fehlen.

**Die drei restlichen Objekte sind alle in den Daten** — es fehlten nur die Einstellungen,
um sie zu finden. Nachgerendert und bestätigt:

| Objekt | Fenster | Palettentrennung | Filter |
|---|---|---|---|
| Lost-World-Steinweg | 120 | aus | G61, Palette 7, 1. Phase |
| Fackeln / Kartenanimationen | 120 | aus | Karten-Gfxset, Größe ≤ 32 px |
| Schädelwagen | **1** | aus | G-1, Palette 4, 1. Phase |

Dafür zwei neue Bedienelemente: **Fenster 1** („bewegte Objekte" — ein bewegtes Sprite ist in
einem einzelnen Frame vollständig, weil jeder Frame ihm neue Ursprünge gibt; ein statisches
braucht dagegen das Fenster) und ein **Größenfilter**, weil Fackeln 16×16 sind und zwischen
bildschirmgroßen Klumpen sonst untergehen.

### Eine Seite statt einer Werkzeugkiste

Rückmeldung nach dem Test: „aufgeblasen und nicht leicht verständlich". Zu Recht — für die
Schrift, eine abgeschlossene Sache, gab es nur den allgemeinen Objekt-Browser mit sechs
Filtern. **Neuer Reiter „🔤 Schrift"** mit genau zwei Abschnitten:

1. **Das Alphabet**, alphabetisch, jedes Zeichen gerendert, farbcodiert: grün = HD-Kunst im
   Container, orange = aufgezeichnet aber noch SD, rot = in der Aufzeichnung nicht enthalten.
2. **Die Beispielwörter für den Upscale** — die kleinste Auswahl, die jedes erfasste Zeichen
   mindestens einmal zeigt, mit Bild und gelesenem Text. Der Export-Knopf verschickt **genau
   diese** Wörter, es gibt nichts einzustellen.

Dazu die Klarstellung, warum der Palettenfilter „nicht funktionierte": **die Kong-Köpfe
liegen selbst auf Palette 6.** Die Palette trennt Text nicht von Nicht-Text — was das tut,
ist die Frage, ob die Glyphentabelle das Objekt LESEN kann. Genau das ist jetzt das Kriterium.

Ein Zählfehler dabei gefunden: die DK-Symbole heißen `[DK1]`/`[DK2]`, ein Zeichenlauf zerlegte
sie in `[`,`D`,`K`,`1`,`]`. Wird jetzt tokenisiert.

Ergebnis an der echten Aufzeichnung: **alle 30 Zeichen erfasst, 12 Wörter decken sie
vollständig ab** — `KROCODILE`, `SWANKY'S`, `GANGPLANK`, `LUBBA'S`, `HOT-H`, `A![DK1][DK2]`,
`MUDHO`, `KRAZY`, `FLYIN`, `JAW'S`, `QU`, `X`. Nichts bleibt offen.

Im Zuge dessen entfernt: „Aa Schrift-Filter", „🔤 Schrift-Status" und die 102-zeilige
`reportFontCoverage` — die Seite ersetzt sie. Der Hinweis auf nie besuchte Schirme steht
jetzt unten auf der Schrift-Seite, und nur solange oben noch etwas rot ist.

### Nachbesserung nach dem Test: die Restliste muss man auch SEHEN

Der Schrift-Status war richtig gerechnet und trotzdem unbrauchbar — die Liste ging in die
**Konsole**, in die Meldung nur Zahlen. Eine Restliste, die niemand sieht, ist keine.
Jetzt schreibt er in eine **Anzeige in der Seite**: nie aufgezeichnete Zeichen, aufgezeichnete
aber noch SD (die eigentliche Upscale-Restmenge), Zeichen ohne Tabelleneintrag **mit dem Wort,
in dem sie stehen**, und die Schirme, auf denen der Recorder nie war.

Zwei weitere Punkte aus demselben Test:

- **„Auswahl vorschlagen" war undurchschaubar.** Es rechnete ein Set-Cover über die gerade
  *sichtbaren* Objekte — ohne gesetzten Filter also über alle Gfxsets und Paletten, weshalb
  vor allem Kong-Köpfe vorgeschlagen wurden. Und es deckte auch Kacheln ab, die **längst
  HD sind**. Jetzt heißt es **„✨ Offenes vorschlagen"** und überspringt, was der Container
  schon hat; das Ergebnis erscheint als Liste mit den gelesenen Namen statt als
  Konsolenzeile. Dazu **„Aa Schrift-Filter"**: ein Klick stellt Palette 6, nur zeichenbare,
  nur 1. Phase, keine Einzelkacheln — damit der Vorschlag die Schrift meint und nicht alles.
- **Unbeschriftete Karten auf Palette 6 erklären sich jetzt selbst** („? nicht in der
  Schrifttabelle"). Es sind entweder Zeichen ohne Tabelleneintrag oder schlicht kein Text —
  die Kong-Köpfe liegen auf derselben Palette.

Was der Bericht mit der echten Aufzeichnung sagt: **alle 30 Glyphen sind aufgezeichnet**,
96 Namen gelesen, 4 Vorkommen ohne Tabelleneintrag, und **8 Schirme nie besucht**
(Cranky, Wrinkly, Swanky, Klubba, Krem Quay, Gloomy Gulch, K. Rool's Keep, The Flying Krock).

### Zwei Bugs, die auf dem Weg gefunden wurden

- **Der Container-ZIP-Roundtrip verlor Sprite-Metadaten.** `exportContainerAsZip` schrieb für
  Sprite-Sets nur `type/setId/animId/name/frameCount` + die Frame-PNGs; `meta`
  (offsetX/offsetY/**tiles[]**) und `scaleFactor` fielen heraus, der Re-Import stellte sie
  nicht her. Die Frames überlebten als Bilder, aber **ohne die Zuordnung Frame→Kachel lassen
  sie sich nie wieder ins Pack schneiden** — das ZIP-Backup war für Sprites also stumm
  unvollständig. Der IndexedDB-Pfad persistierte `meta` längst, nur dieser Weg nicht.
  Beide Seiten gefixt; ein ZIP ohne `meta` (alter Export) wird jetzt beim Import laut benannt,
  statt erst am Ende eines langen Pack-Exports aufzufallen.
- **„☑ Sichtbare wählen" leerte die Sprite-Galerie.** Die Auswahl-Knöpfe tragen die Klasse
  `cat-btn` nur wegen der Optik, haben aber kein `data-cat`. Der Kategorie-Handler lief für
  sie mit und setzte `activeCatFilter = undefined`, wonach jeder Kategorievergleich fehlschlug.
  Der Selektor greift jetzt nur noch auf `.cat-btn[data-cat]`.

## [2026-07-31] — CHR-Animationen auf Weltkarten und in Shops

Lost Worlds Rauchsäule war der letzte sichtbar in SD verbliebene Teil der Weltkarten. Die
128 aufgezeichneten Frames lagen seit gestern vor, konnten aber nirgends verarbeitet werden:
die S6b-Pipeline braucht zu jedem Anim-Frame seinen **Bildkontext** — den Ausschnitt, in dem
das Objekt im Spiel wirklich steht — und beide vorhandenen Kontext-Builder greifen auf
Dinge zu, die ein Shop- oder Kartenschirm nicht besitzt. `buildAnimOverlayContexts` liest
die Level-Laufzeit (`currentBgData.vram` + `ppu`), `buildAnimTerrainContext` das Map32-Raster
des Levels.

**Neu: `buildAnimOverworldContexts()`** — der dritte Fall, und der einfachste. Ein
Overworld-Schirm hat zwar keine Laufzeitdaten, dafür aber etwas Besseres: `buildOverworldCatalog`
hat jede Ebene bereits aus dem **echten VRAM-Dump des Schirms** gerendert und hält Dump,
Geometrie und fertige Leinwand fest. Der Kontext ist damit ein reiner Nachschlag auf
vorhandenen Daten, ohne jede Laufzeitabhängigkeit. Der Zellenlauf spiegelt `renderBgLayer`
inklusive der 32×32-Screen-Offsets, sonst läsen Hub, K. Rool's Keep (32×64) und Krem Quay
(64×32) die falschen Zellen.

Verifiziert gegen den echten Dump, bevor eine Zeile Exportcode lief: alle **22** Anim-Adressen
`$63A0`–`$6540` stehen in Lost Worlds BG1-Tilemap, als **ein** zusammenhängendes Objekt
(x 18–21, y 0–6). Der Trockenlauf liefert 1 Objekt, Ausschnitt 6×8 Kacheln (48×64 px, nach
dem Upscale 192×256), **8 Phasen → 8 Sheets, alle 128 aufgezeichneten Hashes abgedeckt**,
keine Einzelkachel-Fallbacks.

Auf dem Weg dorthin drei Stellen, an denen die Kette für Nicht-Level-Sets gerissen wäre:

- **Der Pack-Export hätte die Anim-Kacheln nie geschrieben.** Der Block lag im Rumpf der
  Schleife über `setsWithArrangement` — Sets mit Map32-Terrain. Shops und Karten haben per
  Definition keines, ihre Anim-Kacheln wären also stumm liegengeblieben. Der Block läuft
  jetzt als eigene Schleife über *alle* Sets mit Anim-Kacheln. Der Dedup-Schlüssel enthält
  dabei neu das Gfxset: Hashes sind zwar gfxset-unabhängig, Mesens striktes Scoping matcht
  aber nur innerhalb des erkannten Gfxsets, also braucht jedes Set seine eigene Kopie.
- **Der HD-Import hätte jede Anim-Zelle auf 8 px verkleinert.** Die Skalierungserkennung
  hängt an `tiles/`; ein Schirm-ZIP hat keine, also blieb `scaleFactor` auf der 1 aus dem
  Manifest — und genau diese Zahl ist die *Zielgröße* des Anim-Imports (`dst = 8 × scaleFactor`).
  Jetzt wird sie ersatzweise aus den Schirm-Ebenen gemessen (deren SD-Breite steht im
  Manifest), sonst aus dem laufenden `hdPack`; bleibt beides aus, warnt der Import laut.
- **Der Container-Save wäre sofort ausgestiegen.** `saveCurrentHDToContainer` beginnt mit
  `if (hdPack.tiles.size === 0) return 0`. Ein Schirm hat nie Map32-Kacheln, ein Nachimport
  nur der Anim-Frames auch nicht — beide sind hash-/ebenen-adressiert und aus nichts
  wiederherstellbar. Der Guard lässt jetzt auch Anim-Kacheln und Schirm-Ebenen passieren.

**Datenlage der übrigen gemeldeten Animationen** (aus `snes_hd_bgcap.txt` /
`snes_hd_spritemiss.txt` ausgezählt) — der Code deckt sie alle ab, aufgezeichnet ist bisher
nur die erste:

| Animation | Aufzeichnung | Weg |
|---|---|---|
| Lost World, Rauchsäule | **128 Frames, 22 Adressen** | dieser Pfad, bereit |
| Hub, blinkendes Kremland-Schild | **keine bgcap-Zeile für G53** | erst aufzeichnen |
| Hub, Fackeln | keine bgcap-Zeile; 415 Sprite-Hashes für G53 vorhanden | vermutlich Sprite-Pipeline |
| Swanky, Lichterleiste | **keine Zeile für G11**, weder BG noch Sprite | erst aufzeichnen |

Dass für den Hub *keine* BG-Misses auflaufen, obwohl er erkannt wird (`gfx=53`, drei
Kontextwechsel im Log), ist ein Hinweis, aber kein Beweis: entweder blinkt das Schild über
die **Palette** statt über CHR-DMA — dann erzeugt es prinzipiell keine Misses und gehört in
keine der beiden Pipelines — oder die Aufzeichnung war schlicht zu kurz.

## [2026-07-30] — Nachtrag: der Fingerprint-Fix war zunächst wirkungslos

Der Fix unten griff im Test nicht — Lost World stand weiter auf `gfx=-1`. Ursache war die
Herkunft des Flags: die Hash-Erzeugung las `animated` aus der **im Container gespeicherten**
`meta`, die aber aus einem Manifest von *vor* Einführung des Flags stammt. `undefined` ließ
alle Ebenen als stabil gelten, und die Referenzkacheln kamen weiter aus der Rauchsäule.

Jetzt wird `animated` aus `getOverworldLayers()` gelesen — die Registry ist die Autorität,
nicht der gespeicherte Datensatz. Damit wirkt es auch für Container, die vorher geschrieben
wurden; ein Neuimport ist nicht nötig, ein Pack-Export genügt.

**User-bestätigt:** Lost World jetzt `gfx=61`, Karte und geöffnetes Vulkanmaul durchgehend
in HD. Die Rauchsäule bleibt SD — erwartet, dafür fehlt noch die Anim-Pipeline.

*Lehre für künftige Flags: gespeicherte Metadaten sind für neu eingeführte Felder
unzuverlässig; immer aus der Registry ableiten.*

**Nebenergebnis, das der Fix erst möglich gemacht hat:** Weil der bgcap-Recorder auf
`ActiveGfxset >= 0` gegated ist, konnte er bei `gfx=-1` nichts aufzeichnen. Jetzt liegen
**128 Frames der Rauchsäule** vor — ~19 Kachelpositionen zwischen `$63B0` und `$6540`, alle
auf BG1/Palette 7, rund sieben Phasen je Position. Gleiche Struktur wie Hot Heads Lava.

## [2026-07-30] — Lost World fiel komplett auf SD zurück, sobald der Rauch sich bewegte

Im Test war die Karte in HD, solange die Rauchsäule in genau der Phase stand, die im
VRAM-Dump steckte. Bei jeder anderen Phase fiel **das ganze Bild** auf SD zurück — nicht
nur der Rauch. Das Diagnose-Log zeigt die Ursache eindeutig: die Signatur der Karte
erscheint 115-mal, und in **jedem** Frame steht `gfx=-1`.

Der Fingerprint schlug also fehl, und das strikte Gfxset-Scoping blockt bei `gfx=-1`
konsequenterweise *alle* HD-Kacheln des Schirms. Referenzkacheln waren aus der animierten
BG1-Ebene gewählt worden, deren Hashes sich mit jeder Animationsphase ändern.

Die Fingerprint-Auswahl bevorzugt eigentlich schon „stabile" Kacheln — nur wurde das Feld
`stable` für die Overworld-Einträge nie gesetzt, also waren alle Kandidaten gleichrangig
und die animierten kamen genauso infrage.

- `OVERWORLD_SETS` kennt jetzt `animated` je Ebene (gesetzt für Lost Worlds BG1).
- Die Hash-Einträge tragen `stable: !animated`, wodurch die Auswahl auf die statische
  Karte (BG2, 764 Kacheln) ausweicht.

*Nicht* behoben ist damit die Abdeckung der Rauchsäule selbst — dafür braucht es die
S6b-Anim-Pipeline mit einem Content-Hash je Frame. Neu ist nur, dass ihr Fehlen nicht mehr
den restlichen Schirm mitreißt.

## [2026-07-30] — Ordner-Export als experimentell gekennzeichnet

Der Export in einen Ordner ist auch nach den bisherigen Optimierungen unbrauchbar langsam
(über 2000 s veranschlagt) und belastet dabei das ganze System, während der ZIP-Weg für
dieselbe Datenmenge zügig durchläuft. Die Checkbox sagt das jetzt deutlich, statt eine
gleichwertige Alternative vorzutäuschen.

Der Grund liegt in der Bauart der File System Access API: Chromium legt pro Datei eine
Swap-Datei an und benennt sie beim Schließen um. Bei ~34 000 Dateien sind das über 100 000
Dateisystem-Operationen, die unter Windows zusätzlich den Virenscanner beschäftigen — der
ZIP-Weg schreibt dagegen **eine** Datei. Eine sinnvolle Lösung müsste die Dateimenge
angehen (nur Geändertes schreiben) statt das Schreiben selbst zu beschleunigen.

## [2026-07-30] — Die drei mehrschichtigen Schirme bekommen ihre fehlenden Ebenen

Zwölf der fünfzehn Schirme sind reines BG1 und liefen bereits. Drei nicht — und bei ihnen
fehlte jeweils der *größere* Teil des Bildes:

| Schirm | Ebene | Inhalt | Deckung |
|---|---|---|---|
| Crocodile Isle (Hub) | BG2 | grüner Himmel mit Wolkenbändern | 99,3 % |
| | BG3 (2bpp) | Wolkenbank am Inselfuß, Color-Math-Operand | 13,2 % |
| Funky's Flights II | BG2 | zweite Szenenebene | 100 % |
| Lost World | BG2 | **die eigentliche Karte** — Vulkan, Lava, Dschungel | 100 % |

Lost World ist der auffälligste Fall: dessen BG1 ist die animierte Rauchsäule (nur 6 %
Deckung, 85 Kacheln), die Karte selbst liegt auf BG2 mit 764 Kacheln. Bisher wurde also
ausschließlich der Rauch exportiert. Umgekehrt beim Hub: BG1 ist die Insel mit nur 40 %
Deckung, weil der Himmel dahinter durchscheinen soll — das sah nach einem Fehler aus, ist
aber korrekt.

- `OVERWORLD_SETS` bekommt ein optionales `extraLayers`. Da `owLayers[]` von Anfang an ein
  Array war, sind die Zusatzebenen reine **Daten** — Container, SD-Export, HD-Import und
  Pack-Export iterieren sie bereits und mussten nicht angefasst werden.
- Der Katalog zeigt jetzt eine Sektion pro Ebene, jede mit eigenem HD-Tausch.
- 2bpp wird durchgereicht (Hub-BG3): 8 Wörter statt 16 pro Kachel, 4 Farben pro
  Palettenzeile. Die Fingerprint-Auswahl überspringt Layer ≥ 2 ohnehin, da sie 4bpp
  voraussetzt — Hub-BG3 wird also korrekt nicht als Referenzkachel benutzt.
- **Funkys BG3 bleibt bewusst draußen:** das ist die Textschrift und gehört in die globale
  Font-Arbeit, nicht an ein einzelnes Gfxset gebunden.
- **Lost Worlds BG1 bleibt unvollständig, mit Absicht:** eine CHR-Animation, von der ein
  VRAM-Schnappschuss nur den gedumpten Frame enthält. Volle Abdeckung braucht die
  S6b-Anim-Pipeline, wo jeder Frame seinen eigenen Content-Hash bekommt.

## [2026-07-29] — NPC-Shops und Weltkarten: Katalog-Builder (Teil 1 von 4)

Shops und Weltkarten waren bisher vom HD-Pack ausgeschlossen. Sie haben im ROM
**keinen Gfxset** (Property-Typ `0x0004`/`0x0005` trägt keine Style-Daten) und kein
Map32-Terrain — sie sind reine Tilemap + CHR. Damit fallen sie durch den BG1-Pfad,
der part-getrieben ist (`set.tiles` mit Schlüsseln `"{gfxSet}_{partId}"`), passen aber
exakt auf den tilemap-getriebenen BG2-Pfad.

- **Neu: `buildOverworldCatalog(gfxSetIndex)`** — rendert den Schirm aus dem **echten
  VRAM+CGRAM-Dump**, nicht aus ROM-rekonstruierten Daten. Das ist kein Detail: der
  Pack-Export benennt jede Kachel nach ihrer VRAM-Adresse und schneidet sie aus genau
  diesem Bild, also müssen Bild und Tilemap aus derselben Quelle stammen, sonst werden
  Kacheln falsch beschriftet. Nebeneffekt: die Content-Hashes decken sich mit Mesens
  Laufzeit-VRAM.
- **Neu: `OVERWORLD_SETS`** — synthetische Gfxset-Indizes. Ein Scan aller 192 Level-IDs
  zeigt, dass das ROM nur `0x02`–`0x34` benutzt, also sind `0x35`+ frei. Die 5 Shops
  behalten ihre echten Sets `0x08`–`0x0C`.
  **Achtung:** die Karten-*Level*-IDs sind `0x30`–`0x38`, aber `0x30`–`0x34` sind echte
  Level-Gfxsets — die Karten dürfen also *nicht* nach ihrer Level-ID benannt werden.
- **`chr`/`tm`/`wide`/`tall` sind an die Dumps gepinnt, nicht aus `OVERWORLD_WORLDS`
  abgeleitet.** Die beiden decken sich für 14 von 15 Schirmen, aber der Config für
  **Lost World** beschreibt `$2000/$7800` — das ist zur Laufzeit dessen **BG2**; sein
  BG1 liegt bei `$6000/$7C00`. Eine falsche Basis verschiebt die Adressen des ganzen
  Schirms. Nachprüfbar mit `scratchpad/check_owconfig.py`.
  Ebenfalls aus den Dumps: drei Schirme sind nicht 32×32 — Hub und K. Rool's Keep sind
  32×64, Krem Quay ist 64×32.
- **Groundtruth trägt jetzt auch CGRAM** (`CGRAM_GROUND_TRUTH`, 39 Sets à 512 B). Das
  Spiel bearbeitet Paletten beim Laden nach (R3), die ROM-Rohpalette ist also nicht das,
  was auf dem Schirm steht. `VRAM_GROUND_TRUTH` blieb dabei unverändert — geprüft gegen
  `git show HEAD:`, alle 24 vorbestehenden Sets byte-identisch.
- **Entfernt: `gfxset_02`.** Der Dump vom 29.06. war keine Level-VRAM, sondern die
  Lost-World-Karte: alle 10 PPU-Register identisch mit `gfxset_3D`, 92,7 % der belegten
  Kacheln byte-gleich, und die Karte hat im ROM gar keinen Gfxset. Damals hatte
  `readCurrentGfxset()` auf der Karte den Restwert `$0539 = 0x02` gelesen. Dateien nach
  `dkc2_vram_dump\_mislabeled\` verschoben, nichts gelöscht. Der **echte** Gfxset 0x02
  (Web Woods Beta, Ghostly-Grove-Bonusräume) ist weiterhin ungedumpt.

**Verifiziert:** 13 der 15 Schirme rendern als reines BG1 vollständig (69–100 % Deckung,
67–110 Farben). Crankys Laden per Auge geprüft — Schilder, Preise, Fässer, alles korrekt.
Die zwei Ausnahmen sind bekannt und erwartet: **Hub** und **Lost World** komponieren
zusätzlich BG2 (Lost Worlds BG1 ist nur eine dünne Overlay-Ebene, 6 % Deckung), die
brauchen später einen Zwei-Ebenen-Pfad.

### Freigabe im Katalog (Teile 2–3, user-getestet)

- `scanGraphicsSets()` trägt die 15 Schirme als synthetische Sets nach (Marker
  `kind:'overworld'`). Keine Kollision: die Shop-Sets `0x08`–`0x0C` überspringt die
  ROM-Schleife ohnehin über `isNpcShop()`, die Karten liegen über dem ROM-Maximum
  `0x34`. **Bestätigt: 42 Sets statt 27.**
- `buildCatalogByGfxSet()` leitet Overworld-Sets als allererste Zeile um — vor jedem
  `style`-Zugriff.
- Anzeige über `renderBgImageSection(..., hdOw)`, also derselbe HD-Tausch wie bei BG2:
  nach einem HD-Import ersetzt die HD-Fassung das SD-Bild.

**Zwei Fehler, die erst der Test zeigte:**

1. **Es gibt zwei Katalog-Einstiegspunkte.** Neben `buildCatalogByGfxSet()` (Per-GfxSet)
   gibt es `buildCatalog()` (Per-Level), und der steigt bei `!currentTileParts` aus.
   Overworld-Level haben kein Map32 → `null` → die Katalogansicht behielt stumm das
   vorher geladene Level. Gefixt über den neuen Helfer `overworldSetForLevel(levelId)`.
   Dort muss `isNpcShop()` **zuerst** geprüft werden, weil `getOverworldIndex()` auch
   Shop-IDs auf ihre Welt abbildet — sonst landet Crankys Laden auf der Karte von Welt 0.
2. **`loadLevel()` hat drei Ausgänge.** Der Katalog wird erst am Funktionsende neu
   gebaut, der Overworld-Zweig kehrt aber vorher zurück. Folge: der Katalog aktualisierte
   sich beim Wechsel zu oder von einem Shop/einer Karte nicht. Derselbe Refresh-Block
   läuft jetzt auch dort, samt `selectedGfxSet`/`#catGfxSet`-Sync auf das synthetische
   Set (spiegelt, was der Normalpfad mit `style.graphics` tut).

**Ebenfalls gefixt, sonst hätte die Freigabe es ausgelöst:** die VBlank-Anim-Injektion im
Pack-Export dereferenzierte `setInfo.levels[0].style.vblankType` ungeprüft. Overworld-Sets
haben kein `style` → hätte den **gesamten** Pack-Export abgebrochen, sobald ein Shop im
Container liegt.

**User-bestätigt:** Katalogverhalten sauber, Wechsel in beide Richtungen aktualisiert
korrekt. Lost World zeigt wie vorhergesagt nur Rauchsäule und den Vulkaneingang
(Krokodilmaul), Rest transparent — die statische Karte liegt dort auf BG2.

**Hinweis zur Bedienung:** Das Set-Dropdown (`catGfxSetWrap`) ist im Standardmodus
„Per Level" ausgeblendet und erscheint erst über den Knopf **„Per Graphics Set"**. Nur
darüber erreichbar ist `Set 0x3E` (Krazy Kremland, zweiter Bildschirm) — dieser Schirm
hat keine eigene Level-ID, er teilt sich `0x33` mit dem ersten.

### Die `ow*`-Kette (Teil 4)

Der Katalog liefert **`owLayers[]`** statt eines einzelnen Bildes — heute genau ein Eintrag
für BG1. Alles dahinter iteriert dieses Array, damit der Hub (Himmel auf BG2, Wolken auf
BG3), Funkys BG2 und Lost Worlds BG2 später als *Daten* dazukommen und nicht als neue
Codepfade.

- **SD-Export:** `ow_bg{N}.png` + `manifest.owLayers[]` (chrBase, tilemapBase, Geometrie).
- **HD-Import:** → `hdPack.owLayers`, warnt wenn das Bild nicht hochskaliert wurde.
- **Container:** neues Feld `owBlobs`. Liegt nichts im Speicher, wird das Gespeicherte
  übernommen statt überschrieben — dieselbe Regel wie bei bg2/bg3, sonst hätte ein
  zweiter Save die importierte Kunst gelöscht (Bug 1 vom 2026-07-24 in neuer Verkleidung).
  `refreshContainerSetMetadata` brauchte nichts: es spreadet seit dem Juli-Fix den ganzen
  Datensatz.
- **Pack-Export:** schneidet nach dem BG2-Vorbild in `bg/bg{N}/gfxset_{DEZIMAL}/`.
  Die **Tilemap wird aus `vramSnapshot` neu abgeleitet**, nicht durch die ZIP geschleust —
  Bild und Tilemap müssen aus derselben VRAM stammen, sonst tragen Kacheln fremde Adressen.
  Die Kachelgröße kommt aus der Bild*breite*, weil die Höhe bei Shops beschnitten ist.
- **Content-Hashes:** Overworld-Sets hängen jetzt an `allHashSets`. Ohne die tragen die
  exportierten PNGs keinen ContentHash und sind für Mesen prinzipiell unauffindbar.
  Die **Fingerprints entstehen daraus automatisch**, weil die Auswahl auf denselben
  Hash-Einträgen aufbaut.

**Müllstreifen:** Tilemap-Zeilen 28–31 liegen unterhalb der 224 sichtbaren Zeilen. Nur bei
Shops abgeschnitten — Karten scrollen, dort wäre Material außerhalb des Startbildes sonst
verloren. Der gleiche Streifen existiert auch in Pirate Panics BG2; am bestehenden
BG2-Export wurde bewusst **nichts** geändert, um vorhandene Packs nicht zu verändern.

**Drei Blocker, die den Export sonst still hätten scheitern lassen:**
1. `exportCatalogAsZip` verlangte `currentTileParts` (Guard *und* Canvas-Anlage).
2. Der Fallback `buildBgImageFromCurrentLevel()` lieferte die Ebenen des zuletzt geladenen
   Levels, weil der Overworld-Zweig `currentBgData` nicht nullte — im Test landete Pirate
   Panics BG3 (1280×512) im Gangplank-ZIP. Wurzel gefixt, plus Sperre im Export.
3. `exportAsTexturePack` brach bei `setsWithArrangement.length === 0` komplett ab. Ein
   Container mit nur Shops/Karten hätte nie exportiert, mit irreführender Meldung.

## [2026-07-29] — Pack-Export wahlweise direkt in einen Ordner statt als ZIP

Der Weg ZIP erzeugen → warten → entpacken → nach Mesen kopieren kostete bei jedem Durchlauf
spürbar Zeit. Neue Checkbox **„Texture Pack direkt in einen Ordner schreiben (statt ZIP)"**
im Container-Panel: beim Export wird einmal ein Zielordner abgefragt, dann werden die
Dateien direkt hineingeschrieben.

- **Bewusst rein additiv:** Der komplette Export baut weiterhin denselben JSZip-Baum auf;
  nur der *letzte* Schritt entscheidet zwischen „ZIP herunterladen" und „Dateien schreiben".
  Die Option kann also nicht beeinflussen, *was* exportiert wird.
- **ZIP bleibt Standard.** Die Checkbox ist nicht vorausgewählt.
- Die Option erscheint nur, wo `showDirectoryPicker` existiert (Chromium). In anderen
  Browsern bleibt sie ausgeblendet, statt ein Versprechen zu geben, das nicht einlösbar ist.
- Bricht der Ordner-Weg ab — Auswahl abgebrochen, Rechte verweigert — fällt der Export
  automatisch auf die ZIP zurück, statt ohne Ergebnis zu enden.

**Nachtrag 1 (erster Test schlug fehl):** Die Ordnerabfrage kam nie, es wurde stumm eine ZIP
geladen. Ursache: `showDirectoryPicker()` verlangt eine *transiente Benutzeraktivierung*,
die wenige Sekunden nach dem Klick verfällt — der Aufruf stand aber am **Ende** eines
minutenlangen Exports und warf deshalb zuverlässig. Der Ordner wird jetzt **ganz am Anfang**
abgefragt, solange die Aktivierung frisch ist; das Schreibrecht gleich mit. Nebeneffekt:
man wählt den Ordner einmal vorne und der Export läuft danach ohne Rückfrage durch.

**Nachtrag 2 (zweiter Test: Ordner kam, brach aber mittendrin ab):** 6574 von 34044 Dateien
wurden geschrieben, dann fiel der Export auf die ZIP zurück. Abbruchstelle exakt bestimmt
(Vergleich der Dateizahlen je Ordner gegen die ZIP): `bg/bg1/gfxset_54`, Datei 53 von 800 —
alles davor deckungsgleich. Zwei Härtungen:

- Der Blob kommt jetzt direkt vom Eintrag aus `zip.forEach` statt über eine erneute
  `zip.file(path)`-Suche — ein Fehlermodus weniger, ohne Gegenwert.
- **Ein einzelner Schreibfehler wirft nicht mehr den ganzen Lauf weg.** Fehler werden je
  Datei gesammelt, der Pfad landet in der Konsole, und am Ende sagt eine Meldung, wie viele
  Dateien geschrieben wurden und welche fehlten. Erst über 200 Fehlern wird abgebrochen.

Die eigentliche Fehlerursache ist damit noch nicht bewiesen — der nächste Lauf nennt sie
beim Namen. Nebenbefund: Als Ziel war ein **früher entpackter Export** gewählt, erkennbar
an `bg2/gfxset_04` mit 64 statt 65 Dateien aus jenem älteren Lauf.

## [2026-07-30] — Spritecap bleibt gespeichert, Ordner-Export schreibt parallel

- **Spritecap überlebt jetzt einen Reload.** Bisher musste `snes_hd_spritecap.txt` in jeder
  Sitzung neu hochgeladen werden, und wer es vergaß, erfuhr das erst *am Ende* eines langen
  Exports — der dann ohne Sprite-Tiles herauskam. Die geparsten Daten liegen jetzt in
  IndexedDB (`recordings`-Store, DB-Version 2) und werden beim Start automatisch geladen.
  „Aktualisieren" heißt einfach: eine neue Datei wählen, sie überschreibt die alte. Der
  Knopf zeigt Anzahl und Ladedatum.
- **Fehlender Spritecap wird vor dem Export gemeldet**, nicht danach, und fragt, ob trotzdem
  exportiert werden soll.
- **Ordner-Export schreibt in Bündeln zu 24 parallel** statt streng nacheinander, und der
  Verzeichnis-Cache hält jetzt das *Promise* statt des fertigen Handles — vorher verfehlte
  ein paralleles Bündel den Cache geschlossen und lief die volle Elternkette fünfmal pro
  Datei ab. Der Fortschritt zeigt zusätzlich Dateien/Sekunde und geschätzte Restzeit.

**Ehrlicher Stand zum Ordner-Export:** Er ist deutlich langsamer als der ZIP-Weg, und das
ist noch nicht vollständig erklärt. Bekannt ist: der ZIP-Weg macht **einen** Durchlauf durch
alle Einträge, der Ordner-Weg dagegen pro Datei mehrere Dateisystem-Operationen — Chromium
legt für jedes `createWritable()` eine Swap-Datei an und benennt sie beim `close()` um, was
unter Windows zusätzlich den Virenscanner beschäftigt. Dazu kommt, dass jeder Eintrag über
`entry.async('blob')` aus der JSZip-Struktur zurückgelesen wird, obwohl er dort als Blob
hineingelegt wurde — ein vermeidbarer Umweg. **Der nächste Schritt wäre, für den Ordner-Weg
gar nicht erst über JSZip zu gehen**, sondern die Blobs beim Bauen parallel in einer flachen
Liste zu sammeln. Bis dahin bleibt die ZIP der verlässliche Weg; die Laufzeitausgabe in der
Konsole (`[export] folder write took …`) liefert die Messwerte dafür.

## [2026-07-30] — Nur der zuletzt importierte Shop/Karten-Schirm wurde in HD angezeigt

Nach dem Import mehrerer Schirme nacheinander zeigte die Katalogansicht nur noch beim
zuletzt importierten die HD-Fassung. Container und Pack-Export waren korrekt — es war reine
Anzeige.

- **Ursache:** `hdPack.owLayers` war nur nach *Ebene* geschlüsselt (`{1: …}`), nicht nach
  Gfxset. Jeder Import überschrieb also das BG1 des vorherigen Schirms, und die Anzeige
  prüfte zusätzlich gegen ein einzelnes `hdPack.owGfxSet`.
- **Fix:** `hdPack.owLayers[gfxSet][layer]`. Import und Container-Restore mergen jetzt pro
  Gfxset, die Anzeige schlägt über die `gfxSetIndex` des angezeigten Schirms nach.
  `owGfxSet` entfällt.

## [2026-07-24] — Container-Datenverlust: Save darf gespeicherte Kacheln nicht mehr löschen

Gefunden bei der Analyse eines Packs, in dem **1314 Kacheln fehlten**: `gfxset_07`
(Pirate Panic) komplett leer (0 statt 1239 PNGs) und `gfxset_03` bg2 601 statt 676 —
obwohl `hashes.bin` für beide die vollständigen Einträge enthielt. Metadaten also
intakt, nur die Bild-Blobs verschwunden.

*(Korrektur: `gfxset_04` sah mit 806 statt 1142 bg1-Adressen ebenfalls beschädigt aus,
ist es aber nicht — die fehlenden 336 sind das Honig-Overlay, das per Design in
`cmFg/gfxset_04` liegt. 806 + 336 = 1142, und alle 336 haben ihren Hash-Eintrag.)*

- **Problem:** `hdSaveSet()` ist ein Voll-`put()` des Datensatzes, und der Block am
  Ende von `saveCurrentHDToContainer()` **gibt die Bitmaps des gespeicherten Gfxsets
  absichtlich frei** (Speicherschonung über viele Importe hinweg). Zielt ein späterer
  Save auf dasselbe Set, findet der Gfxset-Filter nichts mehr im Speicher und schreibt
  `tiles: []` über die gespeicherte Kunst. Die einzige vorhandene Schutzprüfung
  (`hdPack.tiles.size === 0`) sieht `hdPack.tiles` nur als **Ganzes** und bleibt
  zufrieden, solange irgendein anderes Gfxset resident ist.
  Auslöser im Alltag: „Import HD" mit einer Sprite-ZIP, während ein Level ausgewählt
  ist — `hdPack.gfxSetIndex` ist dann leer, `activeGfxIdx` fällt auf `selectedGfxSet`
  dieses Levels zurück, und dessen Container-Eintrag wird geleert. Genau der vom User
  beobachtete Ablauf „Pirate Panic war HD → Sprites importiert → wieder SD".
- **Fix:** neuer Lese-Helper `hdGetSet()`; `saveCurrentHDToContainer()` vergleicht vor
  dem Schreiben mit dem gespeicherten Datensatz:
  - **0 Kacheln im Speicher, aber >0 im Container → harter Abbruch** (`return 0`,
    Konsole + Dialog). Dieser Fall ist nie legitim.
  - **weniger Kacheln als gespeichert → `confirm()`** mit Zahlen; Abbruch bei Nein.
    Ein absichtlich kleinerer Re-Import bleibt damit möglich, ein stiller Verlust nicht.
  - Die Blob-Konvertierung läuft erst **nach** der Prüfung (vorher wurden alle Bitmaps
    umsonst encodiert, bevor überhaupt klar war, ob gespeichert wird).
- **Gleiche Falle mitgeschlossen:** `hdPack.animTiles` wird nach jedem Save
  **geleert**, `bg2`/`bg3` werden geschlossen, `wallBlob`/`cmFgBlob` entstehen nur aus
  `currentBgData`/`catalogData` des gerade angezeigten Levels. Alle fünf werden jetzt
  aus dem gespeicherten Datensatz **übernommen**, wenn im Speicher nichts vorliegt,
  statt ihn zu nullen. Bei den Anim-Kacheln ist das besonders wichtig: sie sind
  hash-adressiert und lassen sich aus nichts anderem rekonstruieren.
- **Reparatur bestehender Container:** der Fix verhindert weiteren Verlust, stellt
  aber nichts wieder her — betroffene Sets müssen einmal neu per „Import HD"
  eingespielt werden.

### Ursache abgestellt: Import entscheidet, was gespeichert wird

Die Guards oben sind das Netz; das eigentliche Loch saß im Aufrufer.

- **Problem:** `importHDPackToContainer()` entschied per `hdPack.tiles.size > 0`, ob ein
  Level-Set gespeichert wird. `hdPack` ist aber ein **Sammler über die ganze Sitzung** —
  nach einem Sprite-Import liegen dort noch die Kacheln vorheriger Level. Der Level-Save
  feuerte also auch bei Sprite-ZIPs, und `activeGfxIdx` fiel mangels
  `hdPack.gfxSetIndex` auf das gerade **ausgewählte Level** zurück. Genau so wurde
  gfxset_07 geleert.
- **Fix:** `importHDPack()` gibt jetzt zurück, was es tatsächlich importiert hat
  (`{ kind: 'level' | 'sprites' | 'none', gfxSetIndex, tileCount }`) — die Verzweigung
  `manifest.exportType === 'sprites'` existierte ohnehin schon, ihr Ergebnis wurde nur
  weggeworfen. `importHDPackToContainer()` speichert Level-Sets nur noch bei
  `kind === 'level'`.

### Honig-Overlay (cmFg) kommt in die Upscale-Pipeline

Das Foreground-Overlay von Rambi Rumble (Honig, `cmFgSource === 'bg1'`) wurde zwar ins
Pack nach `cmFg/gfxset_XX/` geschnitten, war aber **nie Teil des SD-Exports** — es kam
also nie am Upscaler an, und die Kacheln blieben nativ. Gemessen: die 483 PNGs in
`cmFg/gfxset_04` decken 336 Adressen ab, und das sind exakt die 336 Adressen, die in
Rambi zur Laufzeit verfehlt werden.

- **SD-Export:** schreibt jetzt `cmfg.png` (natives Overlay-Bild) plus `manifest.cmFg`
  mit Quelle, Modus, Alpha und Subtract-Flag — genau wie `bg2.png`/`bg3.png`.
- **Import:** liest `manifest.cmFg.file` nach `hdPack.cmFg` und übernimmt die Metadaten;
  meldet den gemessenen Skalierungsfaktor und warnt, wenn das Overlay nicht
  hochskaliert wurde.
- **Container:** `saveCurrentHDToContainer()` bevorzugt jetzt `hdPack.cmFg`. Vorher
  gewann immer der native Redraw aus `currentFgData`/`catalogData`, d.h. ein
  importiertes HD-Overlay wurde beim Speichern sofort wieder überschrieben —
  `bg2`/`bg3` lesen aus genau diesem Grund schon lange aus `hdPack`.
- Der Pack-Export musste nicht angefasst werden: er leitet die Zellgröße aus der
  Bildbreite ab (`cmFgBitmap.width / tilesW`), ein 4×-Overlay passt also von selbst.
- **Mesen-Seite (Build S12):** der Loader scannt jetzt `cmFg/gfxset_XX/` und lädt die
  Kacheln als Layer 0. Sie sind gewöhnliche adress-adressierte BG1-Kacheln, und der
  Export schreibt ihre Content-Hashes ohnehin schon unter Layer 0 in `hashes.bin` —
  es braucht also weder einen neuen Key-Typ noch eine Renderer-Änderung.
  Vorabprüfung am vorhandenen Pack: 336/336 Adressen haben einen Hash-Eintrag,
  0 Dateinamen-Kollisionen mit `bg/bg1/gfxset_04`.
- **Rücknahme im Ernstfall:** der Ordner bleibt bewusst getrennt — `cmFg/` umbenennen
  stellt exakt das alte Verhalten wieder her.
- **Totes Gate entfernt (der Grund, warum `cmFg` beim Neuaufbau ganz ausfiel):**
  `buildCatalogByGfxSet()` cachte das BG1-Tilemap für Overlay-Level nur unter
  `fg.source === 'bg1' && ppu.bg1 && ppu.bg1.enabled`. `readPpuConfig()` schreibt
  `enabled` aber **nur auf bg2 und bg3** — `ppu.bg1.enabled` ist immer `undefined`, der
  Block lief also nie. Folge: `catalogData` trug weder `bg1TilemapData` noch die
  SSB-Felder in `ppuConfig`, und ein aus ZIPs aufgebauter Container (ohne geladenes
  Level) bekam für gfxset_04 einen Datensatz ohne beides. Der Pack-Export verlangt
  genau diese zwei Felder und übersprang `cmFg` daher komplett und lautlos
  (`total_cmfg_tiles: 0`). `fg.source === 'bg1'` identifiziert das Overlay-Level bereits
  — das ist der eigentliche Test, das Enable-Bit war nie einer.
  *(Der Befund war am 2026-07-22 als latent notiert und bewusst liegen gelassen, weil er
  den Mesen-Pack-Export verändert. Genau das ist jetzt erwünscht.)*

### KERNURSACHE: Anim-Sheets gingen 4× vorvergrößert in den Upscaler

Der eigentliche Grund, warum Anim-Kacheln im Spiel nativ aussahen — und er liegt **vor**
dem Viewer-Import, im SD-Export.

- **Messung (Blockgröße der uniformen Pixelblöcke im SD-Export):**

  | Ordner | Blockgröße |
  |---|---|
  | `tiles/` | **1** — echte native Pixel |
  | `clusters/` | **1** — echte native Pixel |
  | `animtiles/` | **4** — bereits 4× Nearest-Blowup |

- **Folge:** `buildAnimObjectSheet()` rendert mit `S = 4` und `imageSmoothingEnabled =
  false`. Das Upscale-Modell bekam also keine nativen Pixel, sondern einen fertigen
  Blowup, und konnte nur Blockkanten abrunden. Messbar: die Modellausgabe weicht bei
  `animtiles/` nur **4,2** von einer reinen NEAREST-Vergrößerung ab, bei `tiles/` und
  `clusters/` dagegen **10,3**. Anschließend rechnete der Import die 16×-Zelle wieder
  auf die 32px des Pack-Formats herunter und verwarf auch das noch.
- **Fix:** `S = 1`. Der Anim-Pfad entspricht jetzt exakt dem statischen: nativ raus,
  4× hochskalieren, Zelle 1:1 mit 32px übernehmen — nichts wird weggeworfen.
  `decodeBgCapTileCanvas()` gibt entsprechend natives 8×8 statt 32×32 zurück, und der
  Einzelkachel-Fallback `buildAnimPaddedCanvas()` baut 24×24 statt 96×96 (3×3 Zellen).
- **Import versteht jetzt alle drei Sheet-Formen** über die gemessene Zellgröße:
  8px (nativ, nicht upgescalt → Warnung), 32px (Sollfall, 1:1) und 128px (Altbestand
  aus 4×-Sheets, wird heruntergerechnet).
- **Alte ZIPs bleiben importierbar**, ihre Kacheln sind aber die schlechteren — die
  SD-Exporte müssen für volle Qualität einmal neu erzeugt und neu hochskaliert werden.
- **Die Colab-Routine ist unschuldig** und war es die ganze Zeit: sie erfasst
  `animtiles/` vollständig und rechnet sauber 4× hoch. Sie bekam nur schlechtes Futter.

### Anim-Kacheln: HD-Import konnte eine SD-Fassung nicht mehr ersetzen

Nachweis: die Anim-Kacheln im Pack wurden Zelle für Zelle gegen beide möglichen Quellen
gerechnet (Schnitt exakt wie im Import, mittlere RGB-Abweichung). Ergebnis gemischt —
**gfxset_20 (Hot Head) 790/790 aus dem HD-Sheet, gfxset_1D (Gusty) 99 von 105 aus dem
SD-Sheet.** Ein Magenta-Test (alle 1064 Kacheln eingefärbt) hatte zuvor bewiesen, dass
Mesen sie zeichnet — der Fehler lag also allein in der Kunst, die ins Pack kam.

- **Problem 1 — „wer zuerst da ist, gewinnt":** der Anim-Import übersprang jeden bereits
  vorhandenen Schlüssel (`if (hdPack.animTiles.has(key)) { animDup++; continue; }`).
  Lag eine Kachel schon aus einem SD-Import oder aus dem Container vor, konnte ein
  späterer HD-Import sie **nie** reparieren — er meldete sie nur als „Duplikat".
- **Fix:** jede Kachel merkt sich ihre Quellauflösung (`srcPx` = Quellpixel pro
  8×8-Zelle). Bei Kollision gewinnt die höhere Auflösung, die alte Bitmap wird
  geschlossen. Kacheln unbekannter Herkunft zählen als Minimum (Ziel-Zellgröße), damit
  ein echter HD-Import sie hebt, ein SD-Import eine bessere aber nicht überschreibt.
  `srcPx` wird im Container persistiert und beim Laden wiederhergestellt.
- **Problem 2 — `loadContainerToHDPack()` stellte Anim-Kacheln gar nicht wieder her:**
  nach „Laden" war `hdPack.animTiles` leer, ein anschließender Import hatte nichts zum
  Vergleichen, und der folgende Save schrieb die schlechtere Fassung in den Container.
  Sie werden jetzt über alle Sets hinweg zusammengeführt (hash-adressiert, also
  gfxset-unabhängig), bei Kollision nach derselben Auflösungsregel.
- **Problem 3 — nicht hochskalierte Sheets fielen nicht auf:** der SD-Export rendert
  Sheets bereits mit 4×, ein nicht upgescaltes Sheet misst also exakt die Ziel-Zellgröße
  und wurde 1:1 durchgereicht. Der Import warnt jetzt (Konsole + Dialog), wenn
  `src <= dst`, mit Nennung der betroffenen Sheet-Anzahl.
- **Entlastet:** die Colab-Upscale-Routine. Die vier HD-ZIPs enthalten `animtiles/`
  vollständig und 4× hochgerechnet (224×160 → 896×640 usw.), Manifest mit
  `scaleFactor: 4` und `upscaleModel`.

### Pack-Export liest Sprites aus dem Container statt aus dem Speicher

- **Problem:** die Sprite-Sektion von `exportAsTexturePack()` las `hdPack.sprites`,
  während der ganze übrige Export aus dem Container kommt. Ein Export ohne vorheriges
  „Import HD"/„Laden" in derselben Sitzung lieferte deshalb ein **leeres `sprites/`**,
  obwohl die Kunst im Container lag.
- **Fix:** Quelle sind jetzt die `sprite`/`mapicon`-Sets des Containers; `hdPack` ist nur
  noch Fallback für Sprites, die in dieser Sitzung importiert und noch nicht gespeichert
  wurden. Beide Quellen laufen über dieselbe normalisierte Struktur.
- **Speicher:** Frames bleiben Blobs und werden **einzeln** dekodiert und wieder
  freigegeben (`createImageBitmap` → `close()` im `finally`) — ein voller Container hat
  über 20 000 Frames.
- **Laufzeit:** vor dem Dekodieren wird geprüft, ob ein Frame überhaupt noch einen
  ungeschriebenen Hash beitragen kann. Da jeder Hash paketweit nur einmal geschrieben
  wird, sind die allermeisten späteren Frames redundant; ohne die Vorprüfung würde ihr
  Dekodieren den Export dominieren.

## [2026-07-22e] — Anim-Kacheln: ALLE beobachteten Layer exportieren, nicht nur den ersten

Gefunden beim Gegenlesen der Mesen-Seite (Schritt 5), bevor getestet wurde.

- **Problem:** `parseBgCap` dedupliziert global per Hash und behielt damit pro Hash
  nur den **zuerst gesehenen Layer**. Mesens Tile-Key enthält aber den Layer
  (`SnesHdTileKey::operator==`), und in Hot Head zeigen BG1 **und** BG2 auf dasselbe
  CHR-Fenster: **203 von 1110 Hashes in gfxset 0x20 kommen auf beiden Layern vor**
  (gfx37/29/4 dagegen praktisch gar nicht). Für die hätte im Spiel jeder Lookup auf
  dem jeweils anderen Layer ins Leere gegriffen — stilles Teil-HD, schwer zu
  diagnostizieren.
- **Fix:** `parseBgCap` führt jetzt `e.layers` = alle beobachteten Layer (aus
  `hashAddrKeys`, das die Layer ohnehin im Schlüssel trägt). Die Information wandert
  durch Sheet-Slices → Import → Container → Pack-Export, der pro Layer eine PNG
  schreibt. Der Dedup-Schlüssel des Exports enthält jetzt den Layer.
- Gleiche Bytes, also sind die Kopien exakt; für Sets mit nur einem Layer ändert
  sich nichts (gfxset 0x25 bleibt bei 7, 0x1D bei 39).
- **Nachbesserung (erster Test-Export zeigte weiter 510 statt 713):** die
  Layer-Information über den SD-Manifest-Weg zu führen reicht nicht. `layers[]`
  entsteht beim SD-Export, reist im Manifest durch den Upscaler und kommt erst beim
  Import an — ein Container, der VOR dem Fix gefüllt wurde, hat sie also nicht, und
  ein reiner Pack-Export kann sie nicht mehr herstellen. Ohne Gegenmaßnahme hätte
  der Fix ein komplettes Re-Upscale erzwungen.
  Deshalb leitet der Pack-Export die Layer jetzt **primär aus dem live geladenen
  `bgCapEntries` ab** (`animHashLayers`, Hash → alle beobachteten Layer); `layers[]`
  aus dem Container und der Einzel-Layer sind nur noch Fallback. Damit repariert ein
  einfacher Re-Export bestehende Container. Fehlt bgcap, warnt der Export explizit,
  statt still zu wenig zu schreiben.
- **Vorhersage am echten Pack verifiziert:** 797 Dateien → **1000** (+203), und die
  203 liegen ausnahmslos in gfxset 32 — deckt sich exakt mit der bgcap-Analyse
  (203 von 1110 Hashes auf beiden Layern; 0x25/0x1D/0x04 unberührt).
- **Pack muss neu exportiert werden** (mit geladenem BG-Anim), damit der Fix wirkt.

## [2026-07-22d] — S6b Schritt 4: Anim-Sheets importieren, persistieren und ins Pack exportieren

Bis hierher gab es `animTiles` **nur auf der Export-Seite** — `importHDPack` las den
Schlüssel nirgends, hochskalierte `animtiles/`-PNGs wurden also kommentarlos ignoriert.

- **4a Import (`importHDPack`):** liest `manifest.animTiles[].slices[]`, schneidet
  **jede** Zelle aus dem hochskalierten Objekt-Sheet und legt sie unter
  `hash_P{pal}` in `hdPack.animTiles` ab.
  - **Skalierung wird pro Sheet GEMESSEN, nicht angenommen** (`src = img.width /
    cropW`). Grund: der SD-Export rendert Sheets bereits mit `S = 4`
    (`buildAnimObjectSheet`), ein 4×-Upscale landet also bei **16× nativ**, während
    der statische Tile-Pfad bei 4× landet. Messen statt Annehmen hält beide
    Konventionen — und einen späteren nativen Export — ohne Format-Flag lauffähig.
  - **Un-Flip:** Sheets zeichnen Zellen in ihrer In-Game-Orientierung, damit das
    Objekt kohärent liest. Spiegeln ist eine Involution, also stellt dasselbe Flip
    erneut angewandt die kanonische Form her, die Mesen hasht.
  - Zielgröße `8 * scaleFactor` = 32 px, identisch zum Sprite-Pfad.
- **Container-Persistenz:** `animTiles` werden im Set-Record gespeichert, nach dem
  Speichern aus `hdPack` freigegeben (sie sind hash-keyed und tragen KEIN
  Gfxset-Präfix, könnten also nicht wie `tiles` gefiltert werden — ohne Freigabe
  würde der nächste Set-Save sie mitkopieren) und von `ensureGfxSetHDLoaded()`
  wieder geladen.
- **4b Pack-Export (`exportAsTexturePack`):** schreibt `h{hash16}_P{pal}.png` nach
  `bg/bg{layer+1}/gfxset_XX/`. Bewusst **nicht** über die `vramAddr`-Benennung: eine
  Animation schickt mehrere verschiedene Kacheln durch DIESELBE Adresse, die Adresse
  kann die Art also nicht identifizieren. Das `h`-Präfix sagt dem Mesen-Loader, die
  16 Hex-Ziffern direkt als Content-Hash zu lesen (Prinzip wie
  `sprites/{hash}_P{pal}.png`). Zähler `total_anim_tiles` im Manifest.
- **Verifikation gegen echte Daten** (Users 4×-Upscale von gfxset 0x20, 71 Sheets):
  136 zufällige Slices geschnitten, auf 8×8 heruntergerechnet und gegen die aus
  `snes_hd_bgcap.txt` decodierten nativen Bytes+CGRAM verglichen — **mittlere
  Kanalabweichung 1,8/255, alle 136 unter 25.** `col`/`row`/`src`-Ableitung stimmen.
  Einschränkung: in diesem Datensatz sind **alle** Slices ungeflippt, der Un-Flip-Pfad
  ist also nur logisch begründet, nicht durch Daten belegt.
- **NOCH OFFEN — Schritt 5 (Mesen):** `ParseTileFilename` in `SnesHdPackLoader.cpp`
  braucht den `h`-Präfix-Zweig (16 Hex → `Key.ContentHash` direkt, analog
  `ParseSpriteFilename`, Layer aus dem Ordner). **Bis dahin liegen die Anim-PNGs zwar
  im Pack, werden von Mesen aber nicht geladen.**

## [2026-07-22c] — S6b: Objekt-Set-Cover über alle Layer statt pro Layer

- **Problem (User-Test, Hot Head 0x20):** 113 PNGs, davon sichtbar unsaubere/doppelte.
  Console: `BG1: 3 Objekte — Phasen 14/13/15` (42 Sheets) und
  `BG2: 5 Objekte — Phasen 14/13/15/15/14` (71 Sheets).
- **Root Cause:** `selectAnimObjects` legte sein `covered`-Set **pro Layer-Kontext**
  neu an. BG1 und BG2 teilen sich in Hot Head das CHR-Fenster `$2010`–`$2190`, also
  deckte BG2 dieselben Adressen ein zweites Mal ab. Manifest-Auswertung zeigte
  vollständige Enthaltung: `L0_00 ⊂ L1_00` (61/61 Hashes), `L0_01 ⊂ L1_01` (46/46),
  `L0_02 ⊂ L1_02` (118/118) — **alle 42 BG1-Sheets überflüssig**, 14 PNG-Paare sogar
  byte-identisch (MD5), nur 99 von 113 Dateien überhaupt verschieden. Bei Mainbrace /
  Gusty / Rambi fiel es nicht auf, weil dort nur ein Layer animierte Tiles trägt.
- **Fix:** `selectAnimObjects(contexts, framesByAddr)` bekommt jetzt **alle** Kontexte
  auf einmal und führt ein einziges `covered`-Set. Kandidaten werden **größtes Objekt
  zuerst** abgearbeitet (echtes Greedy-Set-Cover), damit ein großes Objekt mehrere
  kleine mit denselben Adressen schlägt — sonst hinge das Ergebnis allein an der
  Layer-Reihenfolge. Rückgabe ist `Map(layer -> keptObjects)`.
- **Log:** ein Layer, der nichts Neues beiträgt, meldet das jetzt explizit
  (`alle N Vorkommen sind bereits über einen anderen Layer abgedeckt`) statt einer
  leeren Phasenliste.
- **Irreduzibler Rest bei Hot Head:** die Lava zerfällt im Level in räumlich getrennte
  kleine Komponenten (3×2 / 5×3 / 6×3) statt in ein großes Objekt wie Mainbraces
  Flagge, und ihr Zyklus ist mit 13–15 Phasen echt so lang. Beides ist keine
  Redundanz und bleibt.

## [2026-07-22b] — S6b: ein Sheet pro (Objekt, Phase) statt pro (Zelle, Frame) — 197 PNGs → 7

- **Problem (User-Test):** Der Terrain-Fix lieferte zwar korrekte Objekte (Mainbrace-
  Flagge komplett, Hot-Head-Blasen komplett), aber absurd viele PNGs: 197 für
  Mainbrace (6 erkannte Objekte!), 510 für Hot Head. Viele davon optisch identisch.
- **Root Cause:** `buildAnimClusterCanvas` erzeugte **ein PNG pro (Adresse, Hash)**:
  es rendert das *ganze* Objekt und tauscht darin **genau eine einzige 8×8-Zelle**
  gegen den Frame. Mainbrace = 30 Anim-Zellen × ~7 Phasen = 197 fast identische
  Flaggenbilder, die sich in je einer Kachel unterscheiden. Gemessen an den bgcap-
  Daten: G37/L0 hat 30 lückenlose Adressen `$2010`–`$21E0` (= die 6×5-Flagge) mit
  max. **7 distinkten Hashes je Adresse** — die Animation hat also **7 Phasen**.
- **Fix 1 — Phasen-Bündelung (`buildAnimObjectSheet`):** ein Sheet pro
  (Objekt, Phase), in dem **alle** Anim-Zellen gleichzeitig auf dieser Phase stehen.
  Zellen mit kürzerem Zyklus wiederholen sich (`phase % len`). Das Manifest trägt
  jetzt `slices[]` (ein Eintrag je Zelle mit `hash/pal/layer/addr/col/row/flip`)
  statt eines einzelnen `slice`. Nebeneffekt: der Upscaler sieht eine **echte**
  Animationsphase statt Phase 0 mit einer ausgetauschten Kachel.
- **Fix 2 — Objekt-Set-Cover (`selectAnimObjects`):** dasselbe Objekt kommt im Level
  mehrfach vor (Flagge 6×, Lava-Pools 125×/152×) und liefert byte-identische Sheets.
  Greedy: ein Objekt wird nur behalten, solange es eine noch nicht abgedeckte
  Adresse beiträgt. Log meldet die übersprungenen Wiederholungen.
- **Fix 3 — Frames pro ADRESSE, nicht pro (Layer, Adresse):** BG1 und BG2 teilen sich
  in manchen Leveln dasselbe CHR-Fenster (Hot Head: `$2010`–`$2190` auf L0 **und**
  L1, mit weitgehend identischen Hashes), und `parseBgCap` ordnet einen Hash dem
  zuerst gesehenen Layer zu. Eine Gruppierung pro Layer hätte eine Animation
  zerrissen; jetzt entscheidet allein die Adresse.
- **Nicht abgedeckte Hashes** (kein Kontext / Adresse außerhalb jedes Objekts) bekommen
  weiter ihre Einzelkachel mit transparentem Rand, damit kein Hash verloren geht.
- **Aufgeräumt:** `regionByCell`/`addrToCell` entfallen — die Objekte tragen ihre
  Region und Zellen jetzt selbst. `buildAnimClusterCanvas` ist ersetzt.
- **Befund, NICHT gefixt (Datenlage, kein Bug):** einzelne Frames zeigen fremde,
  schriftartige Kacheln im Lava-Kontext. Decodierung ist korrekt (valides 4bpp,
  Recorder-Re-Hash bestätigt): 26 Kacheln mit identischen oberen 3 Zeilen auf den
  zusammenhängenden Adressen `$20D0`–`$2260`, in einem engen Aufzeichnungsfenster —
  eine **andere Szene**, die dasselbe VRAM-Animationsfenster nachnutzt. Die Kacheln
  sind real und brauchen HD-Art, nur ihr Kontext im Sheet stimmt nicht. Automatische
  Aussortierung verworfen: der getestete Medoid-Ähnlichkeitsfilter markierte auch
  57 von 198 **legitimen** Mainbrace-Flaggen-Frames (die Flagge weht stark).
- **Test-Ergebnis (User, 2026-07-22):** Mainbrace 197 → **7 PNGs**, Flagge sauber
  und als Animation erkennbar. Gusty Glade **39 PNGs**, weiter über den
  `vram-tilemap`-Pfad, keine Regression. Rambi sauber. Hot Head 510 → **113 PNGs**.
- **OFFEN / bewusst akzeptiert — Hot Head (gfxset 0x20) ist noch nicht sauber:**
  113 PNGs sind zwar 4,5× weniger, aber immer noch viel für eine Lava-Animation,
  und ein Teil der Sheets sieht laut User weiterhin unsauber aus. Wir gehen erst mal
  damit weiter (Upscale-Test hat Vorrang). Zwei bekannte Treiber, noch nicht getrennt:
  (a) die oben beschriebenen **szenenfremden Kacheln** in `$20D0`–`$2260`, die im
  Lava-Kontext gerendert werden; (b) Hot Heads Objekte sind **klein und zahlreich**
  (3×2 und 5×3 Zellen, 125 auf BG1 / 152 auf BG2 vor dem Set-Cover), d.h. die
  55 Anim-Adressen verteilen sich auf viele kleine Komponenten statt auf ein großes
  Objekt wie Mainbraces Flagge — das Set-Cover braucht dann entsprechend viele
  Objekte, und jedes bringt seine eigene Phasenzahl (bis 15) mit. Nächster
  Diagnoseschritt, falls wir es nachschärfen: die `[animtiles] BG*:`-Zeile
  auswerten (Objektzahl × Phasen), um (a) gegen (b) zu trennen.

## [2026-07-22] — S6b Fix: BG1 wurde beim Objekt-Clustering IMMER übersprungen

- **Problem (User-Test S3+):** Mainbrace (gfxset 0x25) und Hot Head (0x20)
  exportierten 0 Objekt-Cluster, alle Anim-Frames landeten im transparenten
  Fallback (einzelne Kacheln mit transparentem Rand) — Console:
  `kein Layer-Kontext … 197 transparent-Fallback` bzw. `510 transparent-Fallback`.
- **Root Cause:** `buildAnimOverlayContexts` gated pro Layer auf `cfg.enabled` —
  aber **nur `ppu.bg2` und `ppu.bg3` tragen dieses Feld**, `ppu.bg1` hat es nie
  (Config-Konstruktion ~Z. 1326). `undefined` → `continue` → **jedes BG1-Objekt
  (Mainbrace-Flagge, Gusty-Blätter) wurde stumm übersprungen**, und da bei den
  getesteten Sets kein anderer Layer trug, war das Ergebnis `contexts == null`.
- **Fix:** kein Gate mehr auf `cfg.enabled`. Der Enable-Zustand wird aus TM/TS
  (`mainScreen | subScreen`, Bit 1<<layer) abgeleitet und nur noch **geloggt** —
  ein Layer ohne animierte Zellen fällt ohnehin unten raus, ein Versuch kostet
  also nichts und diese Fehlerklasse ist damit strukturell weg.
- **Neue Diagnose** wenn ein Layer 0 Anim-Adressen in seiner Tilemap findet:
  gesuchte vs. tatsächlich belegte CHR-Adressen (Sample + Range), `enabled`,
  `chrBase`, `tilemapBase`, Tilemap-Größe. Trennt die drei Fehlerfälle
  falscher Layer / falsche chrBase / Objekt nicht im Snapshot sichtbar.
- **Zweiter, EIGENTLICHER Root Cause (Test 2, Mainbrace):** auch mit gefixtem Gate
  0 Objekte — Diagnose: `chrBase=$2000, tilemapBase=$7800`, aber
  `Tilemap belegt: $2000 (1 distinkt)`, also **komplett leer**. Grund: BG1 ist in
  Mainbrace die **dynamische TERRAIN-Ebene**. Deren Tilemap steht nie im VRAM (die
  Scroll-Engine füllt sie zur Laufzeit aus den Level-Daten) — der VRAM-Snapshot ist
  dort null. Der Ansatz „lies die Tilemap aus dem VRAM" kann Terrain-Anim-Tiles
  also prinzipiell nie finden. Gusty funktionierte, weil die Blätter dort auf dem
  BG1-**Overlay** liegen (Tilemap statisch geladen) und das Terrain BG2 ist.
  bgcap ist unschuldig: 687 G37/L0-Einträge, Adressen `$2010`–`$21E0`, vollständig.
- **`buildAnimTerrainContext()` (neu):** Kontext für die Terrain-Ebene aus der
  Level-Map32-Karte statt aus dem VRAM. `tileArrangement` liefert pro 32×32-Part
  seine 16 8×8-Chars; `gfxData` wurde bei `terrainChrBase` aus dem VRAM extrahiert,
  also ist `terrainChrBase + gfxIndex*16` exakt die bgcap-Wortadresse. Über
  `currentTileMap` werden die Vorkommen im Level gefunden, Connected-Component
  darauf = ganzes Objekt (Flagge). Crops werden **on demand** aus
  `currentTileParts` komponiert — kein Riesen-Canvas für große Level.
  Part-Flip und Char-Flip werden korrekt verXORt (Zell-Position *und* Orientierung).
- **Refactor:** Connected-Component in `clusterAnimCells()` extrahiert (von beiden
  Buildern genutzt); Kontexte tragen jetzt `drawRegion(octx, region, cw, ch)` statt
  eines `baseCanvas`, damit VRAM- und Terrain-Quelle austauschbar sind. Log zeigt
  die Quelle: `BG1 (terrain): N Objekte …` bzw. `(vram-tilemap)`.
- **Latenter Nebenbefund (NICHT geändert):** `index.html:4894`
  (`fg.source === 'bg1' && ppu.bg1 && ppu.bg1.enabled`) ist aus demselben Grund
  toter Code — das BG1-Tilemap-Caching für SSB-Level läuft nie. Bewusst nicht
  mitgefixt, weil es den Mesen-Pack-Export verändern würde; separat prüfen.

## [2026-07-20d] — S6b Schritt 3+: Objekt-Cluster für ALLE Layer (nicht nur Gusty-Overlay)

- **`buildAnimOverlayContext` → `buildAnimOverlayContexts`** (pro Layer): der
  Kontext war fest auf Gustys BG1-**fg-overlay** verdrahtet, deshalb fielen
  Mainbrace-Flagge (BG1) und Hot-Head-Lava (BG2) in den transparenten Fallback
  und kamen zerstückelt raus. Jetzt wird die TATSÄCHLICHE Ebene der Anim-Tiles
  (aus dem bgcap-Layer: L0→BG1, L1→BG2, L2→BG3) via `renderBgLayer` +
  `currentPalette` frisch gerendert und darin geclustert. Ein Kontext pro Layer;
  jeder Anim-Frame wird über `contexts.get(entry.layer)` geroutet.
- Connected-Component erkennt so das ganze Objekt (Blatt/Flagge/Blase) auf
  seiner echten Ebene. Diagnose-Log jetzt pro Layer: `BG1: N Objekte — Größen …`.
- `padSource` → `object-cluster`.
- **Hinweis dynamisches Terrain (Hot Head BG2):** die BG2-Tilemap ist teils nicht
  statisch geladen — dort kann der Kontext dünn ausfallen (dann greift der
  transparente Fallback; opake Lava-Tiles skalieren einzeln trotzdem ok).

## [2026-07-20c] — S6b Schritt 3: SD-Export der Anim-Frames (Blatt-Cluster)

- **`exportCatalogAsZip()` exportiert die Anim-Frames des aktuellen Gfxsets** als
  ganze Blätter. Jeder Frame wird aus Bytes+CGRAM dekodiert (`drawTile8x8`),
  aber NICHT einzeln: einzelne 8×8-Kacheln sind winzige Fragmente (Gusty-Anims
  Ø 12 opake Pixel/64, teils ≤3) und für den Upscaler unbrauchbar. Stattdessen:
  - **`buildAnimOverlayContext()`** liest das LIVE BG1-Overlay-Tilemap
    (`currentBgData.vram` + `ppu.bg1`), findet die animierten Zellen und
    gruppiert räumlich zusammenhängende per Connected-Component (8er-Nachbar-
    schaft) zu **ganzen Blättern** (keine Schnittabfälle). Diagnose-Log:
    Blätter-Anzahl + Größen.
  - **`buildAnimClusterCanvas()`** rendert jeden Frame IN seinem Blatt-Crop
    (Bounding-Box + 1 Ring) aus dem echten Overlay-Bild (`currentFgData`) —
    die Nachbar-Blattteile geben dem Upscaler Kontext; die Mitte trägt die
    aktuelle Frame-Variante (in In-Game-Flip).
  - Manifest `animTiles[]` trägt `slice{centerCol,centerRow,cropW,cropH,
    flipH,flipV}` → Schritt 4 schneidet die Mitte hash-keyed zurück und
    un-flippt zur kanonischen Hash-Orientierung.
  - Fallback: transparentes Padding pro Kachel (`buildAnimPaddedCanvas`), falls
    kein Overlay-Kontext (Level ohne Blätter-Overlay geladen).
- Dateiname `animtile_{hash16}_L{layer}_P{pal}.png`, Ordner `animtiles/`.
- **Kontext:** Erster Versuch Self-Mirror, dann Sprite-Stil (transparent) —
  beide verworfen: einzelne Fragmente reichen nicht (User-Test). Blätter müssen
  als zusammenhängende Einheit hochskaliert werden.
- **Ausstehend:** Schritt 4 (`exportAsTexturePack` → `h{hash16}_P{pal}.png`,
  Mitte aus Cluster schneiden+un-flippen), Schritt 5 (Mesen `h`-Präfix). 2bpp
  BG3 später.

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
