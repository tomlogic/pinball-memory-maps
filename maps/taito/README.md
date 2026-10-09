# Taito do Brasil

8080 CPU (a Z80 on Rowamet's Heavy Metal, `maps/rowamet/heavymtl.map.json`). PinMAME saves one 256-byte
battery-backed window as the `.nv` file: at `0x4000` on the 1980–85 boards (platform `taito`), at `0x1000` on the
1979 board (platform `taito-1979`). The display DMA and the command DMA sit **inside** that window, so the player
scores, ball in play, credits display and the firmware's flags are all in the image. Everything below was read from
the ROM code and checked against live NVRAM captures on an AtGames ALP4K running Visual Pinball Standalone.

There is no checksum and no mirror, so nothing is declared under `_metadata.validation`. The firmware's integrity
rules are BCD validity and minimums, described below.

## Maps

| map | firmware | sets | strongest evidence |
|---|---|---|---|
| `vortex` | 1981–85 | 29 | live games on Vortex and Mr. Black (one- and four-player); images of sharkt, cosmic, stest |
| `drakor` | 1980 | 3 | live games on Drakor and Meteor (one- and four-player) |
| `obaoba` | 1979 code on 1980 hardware | 2 | live games on Oba-Oba (one- and four-player) |
| `shock` | 1979 | 2 | live game and three images of Shock |
| `rowamet/heavymtl` | 1981–85 (Vortex's, on a Z80) | 1 | live game on Heavy Metal |

Sets listed without an image are there because their ROM references every declared address the same way as the
measured set in their family: the ten-byte settings copy from ROM, the high-score compare loop, the credits-to-display
copy, the replay routine and the game-over write. Each map's `_notes` says which sets are which. Not mapped: `football`
(ROM lost).

## Layout (offsets into the window; the 1979 board moves the display and command areas to +00/+10)

| offset | holds | how it was established |
|---|---|---|
| `+50` … | audits, 16-bit little-endian binary counters — see below | live |
| `+70` … `+78` | nine operator settings, BCD — see below | the service menu steps an editor over them; the operator sheets name them |
| `+79` … `+7B` | high score, BCD, **most-significant first** | compare loop walks it MSB-first against the score; shown on the P1 display in attract |
| `+7F` | credits, BCD | `LDA 407F / STA 408D` copies it to the display; counted coin by coin live |
| `+80` … `+8B` | P1–P4 scores, 3 BCD bytes each, **least-significant first** | `segMap` in the driver; Drakor's display `00 00 67` beside its high score `67 00 00` |
| `+8C` | ball in play | live |
| `+8D` / `+8F` | credits display / player count (swapped on the 1979-derived firmware) | live; the reset path refuses to resume with players ≥ 5 |
| `+8E` | match digit; cycles 0–9 during play | live |
| `+9E` | current player, **one bit per player** (1, 2, 4, 8; 0 in attract) | live in four-player games on Mr. Black, Drakor, Meteor and Oba-Oba; every generation's code rotates it right until carry to get the number (Vortex `0x0445`, Drakor `0x05C9`, Shock/Oba-Oba `0x0CBE`). Declared `bits` with values 1–4 |
| `+9F` bit 0 | game over | live; written by the reset path when it declines to resume |
| `+9F` bit 1 | tilt; set at the tilt, cleared when the next ball starts | live on all four families |
| `+F4` … `+FF` | the last game's final display, once the game is over (1980–85 window only) | live; the attract alternates the display between it and the high score |

The 1979 board: display `+00`, ball `+0C`, players `+0D`, match `+0E`, credits display `+0F`, current player `+1E`,
flags `+1F`, settings `+F0`, high score `+F9`, credits `+FF`.

**Resume.** The firmware deliberately resumes a game in progress after a reset, so an image saved mid-game holds that
game: game over clear and a ball in play. The maps describe the image as it is.

### The nine settings

Named from two operator sheets, Shock (1979) and Cosmic (1981); each sheet's default column matches its game's image
byte for byte.

| # | offset | label | allowed | default |
|---|---|---|---|---|
| 1 | `+70` | balls per game | 03–05 | 05 |
| 2 | `+71` | coinage code ("Fichas/Partida"; Cosmic: "Crédito/Partida") — **coinage is here, not on DIPs**; the digits' meaning is not on either sheet | 11–14 | 11 |
| 3 | `+72` | maximum credits (credits are clamped to it at boot) | 01–09 | 06 |
| 4 | `+73` | incentive ("Incentivo") | 01, 11–14 | **01** on the 1981–85 sets and shock, **04** on drakor, meteort, fireact and the Oba-Oba sets |
| 5 | `+74` | replay level 1 ("1º Score"), ×10,000 | 15–99 (Shock); fixed values (Cosmic) | per game, 17 (gemini1) to 50 (drakor) |
| 6 | `+75` | replay level 2, skipped if equal to 5 | as 5 | as 5 |
| 7 | `+76` | extra-ball score ("Bola Extra Score"), skipped if equal to **6**; what passing it does is per game, see below | as 5 | as 5 |
| 8 | `+77` | specials per game | 01–05 | 05 |
| 9 | `+78` | credits for beating the high score | 01–03 (Shock), 01–02 (Cosmic) | **01** on the 1981–85 sets and fireact, **02** on drakor, meteort, the Oba-Oba sets and shock |

Defaults are each set's own factory table, read from its ROM — the ten bytes at `0x1FF4` (`0x1BF4` on the
1979-derived firmware) that the reset path copies in when a settings byte is not BCD; the tenth is the high score's
leading byte. A map declares a default only where all its sets agree. `min`, `max` and `default` are stored values:
settings 5–7 declare `scale: 10000`, so their limits are 15 and 99.

The eight "Adjust" DIP switches (CODE 0–7 on the sheets) are not settings. They are the BCD keypad for entering a value
in the service menu (CODE 0–3 = second digit 1/2/4/8, CODE 4–7 = first digit), and left raised they select game rules
and, on the 1981–85 firmware, the replay levels (below). A walk-through of the service menu is the VPForums Taito
ball-count procedure (https://www.vpforums.org/index.php?app=tutorials&article=89).

**No checksum.** The integrity rule is BCD validity: at reset every settings byte goes through `DAA`, and one non-BCD
byte restores all nine from ROM. Write adjustments as BCD. The high score is reloaded from a ROM minimum if it reads
lower.

## Settings 5–7 are not adjustable on the 1981–85 firmware

Every set in the Vortex map, Heavy Metal and Fire Action rebuild `+74..+76` from ROM: the base at `0x1FF8-0x1FFA` plus
a BCD offset from a seven-entry table (`0x1FD8`; `0x1F00` on fireact), indexed by CODE 5–7 (input `0x2806`, which PinMAME
maps to DIP bank 0; CODE 5 is the low bit). On Mr. Black (`0x026F`) it runs at reset, at each step of the attract cycle
(`0x03E9` into the settings validation, which ends in the call at `0x0192`) and when a player is added (`0x0861`): levels
written into NVRAM in attract were back at 39/39/39 within six seconds, three times.

The Cosmic sheet says the same: settings 5–7 take "only fixed values", the replay level is "automatically set from the
switches at every game start, no more manual adjustment", and its table of eight CODE 5–7 combinations (350K–850K) is
Cosmic's row below exactly. So these maps do not declare settings 5–7; the Drakor, Oba-Oba and Shock maps, whose
firmware has no such routine, do (set and played live on Oba-Oba, Drakor and Meteor). Fire Action is in the Drakor map
and has the routine; written values are not expected to last there, which has not been tested.

Replay level in thousands, by CODE 5–7 value, read from each ROM:

| sets | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| gemini1 | 170 | 230 | 310 | 370 | 440 | 560 | 610 | 710 |
| ladylukt, vegast | 260 | 290 | 330 | 380 | 440 | 490 | 520 | 630 |
| titan, titan1 | 270 | 300 | 340 | 390 | 410 | 470 | 500 | 550 |
| sureshot | 280 | 300 | 330 | 360 | 400 | 450 | 500 | 600 |
| cavnegro, cavnegr1, cavnegr2 | 290 | 350 | 410 | 470 | 530 | 590 | 690 | 750 |
| hawkman, zarza1 | 300 | 330 | 360 | 400 | 450 | 500 | 550 | 600 |
| rally | 300 | 350 | 400 | 450 | 500 | 570 | 650 | 750 |
| vortex, heavymtl | 300 | 340 | 390 | 450 | 490 | 530 | 590 | 630 |
| cosmic | 350 | 410 | 470 | 540 | 620 | 700 | 790 | 850 |
| gemini | 350 | 410 | 490 | 550 | 620 | 740 | 790 | 890 |
| sharkt | 350 | 400 | 460 | 520 | 610 | 690 | 760 | 840 |
| stest, gork | 350 | 430 | 490 | 530 | 590 | 650 | 720 | 810 |
| fireact | 360 | 400 | 440 | 480 | 520 | 560 | 600 | 640 |
| lunelle | 390 | 430 | 490 | 550 | 630 | 670 | 730 | 850 |
| mrblack, mrblack1, fireactd, polar, snake, voleybal | 390 | 450 | 490 | 550 | 600 | 630 | 670 | 750 |
| hawkman1 | 410 | 470 | 540 | 620 | 700 | 790 | 850 | 980 |
| sshuttle, sshuttl1 | 450 | 500 | 550 | 600 | 650 | 700 | 750 | 800 |
| zarza | 450 | 590 | 650 | 750 | 850 | 890 | 930 | 990 |

The Shock sheet instead lets CODE 5 and 6 change the *default* level (250K, 350K, 400K) that a forced reset restores;
that is not verified in the code.

## Setting 7 is a per-game hook

The shared score-level routine (Vortex `0x0DBB`, Drakor `0x0E56`, Shock/Oba-Oba `0x0A5E`) treats setting 7 as a third
threshold: skipped when it equals replay level 2, otherwise once per player per game it jumps through a vector
(`0x1FCC`; `0x1BCC` on the 1979 code) into the game's own ROM. Read from every set on file:

| hook | sets |
|---|---|
| returns immediately — the setting does nothing | vortex, heavymtl, cosmic, sharkt, stest, sureshot, gemini, gemini1, ladylukt, vegast, titan, titan1, zarza, zarza1, hawkman, hawkman1, lunelle, rally, snake, gork, voleybal, mrblack, mrblack1, fireactd, sshuttle, sshuttl1, polar |
| starts a sound and returns | drakor (live: a 427,232 game with the level at 180,000 gave no extra ball) |
| game-specific code | shock, obaoba, obaoba1, obaobao, meteort, fireact, cavnegro, cavnegr1, cavnegr2 |

On obaoba and meteort the hook awards an extra ball. In the captures every player who passed the level — five times on
Oba-Oba, three on Meteor, including later players of four-player games — was served the same ball again after the
drain, and no one else was, apart from one tilted ball. The ball number does not change for the extra ball. The other
hooks in that row have not been traced. Cosmic is in the first row even though its own sheet names the setting.

## Audits

16-bit little-endian **binary** counters from `+50`, which the firmware's statistics display walks two bytes at a time
(Vortex `0x08BB`). Identified from live captures:

| offset | counter | maps | evidence |
|---|---|---|---|
| `+52` | play time, in ~64 s ticks | all but shock | ticks only during a game; the statistics display divides it by games played |
| `+54` | powered-on time, in ~64 s ticks | all but shock | ticks in attract too (Vortex: 44, 108, 173, 237, 301 s) |
| `+56` | coins | all but shock | one tick per coin, on the poll the credit rose |
| `+5C` | games played | all but shock | once per player started, as each credit is consumed — four ticks for a four-player start on Mr. Black, Drakor, Meteor and Oba-Oba |
| `+5E` | credits awarded | drakor, obaoba | one tick per credit the game gives: replay levels for whichever player is up (Oba-Oba, Meteor), a won match (Drakor), the credits for beating the high score (Oba-Oba). Drakor's award routine increments it at `0x0612` |
| `+60` | replays awarded | drakor, obaoba | in step with `+5E` for every replay-level award (nine on Oba-Oba, six on Meteor); did not move for the match credit on Drakor or the high-score credits on Oba-Oba. The score-level check hands the award routine this address (Drakor `0x0E6F`) |
| `+64` | high-score credits awarded | obaoba | 0 → 2 across a 605,893 game against a 580,000 high score (setting 9 = 2). One before/after observation |

On the 1981–85 firmware the replay path hands the award routine `+60` as Drakor's does (Vortex `0x0DD4`), and the
routine then increments `+5A` (`0x0F22`) where Drakor's increments `+5E`. That is from the code only: no capture on
that firmware includes a credit award, so neither is declared there. Not measured on the 1979 window (Shock).

## Not established

- What "Incentivo" means, and why the 1980 firmware's factory value (04) is outside the set the two sheets allow.
- Audits `+50`, `+58`, `+5A`: zero in every capture, including Oba-Oba sessions with coins through chutes 2 and 3,
  replays at both levels, extra balls by score and a beaten high score. `+62` and `+66` onward also stayed zero.
