# Stern SAM RAM Mapping

## Introduction

Stern SAM games (2006–2014: Spider-Man through The Walking Dead) run an ARM AT91 CPU
with 128 KB of battery-backed NVRAM mapped at `0x02100000`. PinMAME exposes an 80 MB
CPU image, but everything a map needs sits in two windows: NVRAM, and the working
RAM around `0x00030000` (`0x00030000`–`0x0003FFFF` on most games; AC/DC Pro keeps
player and status just below it, at `0x0002EEC0`). The platform file's *Main RAM* entry is 1 MB so that maps may read the working
RAM; widening it permits reads and changes nothing about how any field decodes.

Everything in these maps that is not attributed to a disassembly was measured live:
a 2 Hz tap of CPU RAM and NVRAM recorded on a cabinet across an operator-menu
session, coins, and at least one full game with a mid-ball tilt, then each
declaration was checked against every sample of its recording. Since November 2026
most of the NVRAM side is read from the ROM image instead (adjustments, high-score and
champion records, scores), and the working-RAM fields of the games no cabinet recorded
come from headless libpinmame games of the same ROM (coins, a two-player game, two
tilts), whose status values every map's `game_over` and `tilted` were also checked
against. Per-map `_notes` record what is specific to that game and how it was found;
this file holds what the games share.

Two things move between games and must never be copied from one map to another:
the score slots and the CPU-side counters (player, ball, status). Two things are
shared by every game measured: the player count at `0x02110900` and the credit
counter at `0x0211100C`.

## Non-Volatile Storage

### Machine adjustments

From `0x02102008` NVRAM holds an array of 8-byte adjustment records:

```
+0  32-bit little-endian value
+4  check byte: 0xFF minus the 8-bit sum of the four value bytes
+5  0xFF 0xFF 0xFF
```

Every record in every image examined satisfies the check byte. A write that changes
the value without updating the check byte is silently discarded when the ROM next
reads its adjustments, so the maps declare each written record as `checksum8` with
`end` on the check byte (the checksum is adjacent, so the standard tail form applies).

The array is in the ROM's own order, not the service-menu order. A full sweep of the
Standard Adjustments on `st_161hc` (every visible adjustment changed once in menu
order with the tap running) gave this mapping from menu number to record index:

| Standard Adjustment | record |
|---|---|
| #1–#12 | 10–21 in order |
| #13, #14 | 23, 22 |
| #15–#18 | 24–27 |
| #19, #20 | 29, 28 |
| #21 Balls Per Game, #22 Tilt Warnings, #23 Credit Limit | 30, 31, 32 |
| #38 Free Play | 33 |
| #44–#46 | 34–36 |
| #48 Ball Save Time – #53 | 37–42 |
| #55–#58 | 43–46 |
| #24 Allow High Scores | 47 |
| #31–#35 Grand Champion, High Score #1–#4 thresholds | 48–52 |
| #25–#30, #36 | 53–59 |
| #37 HSTD Reset Count | 60 |
| #62–#64 | 61–63 |
| system group #43, #41, #61, #54, #42, #60, #39, #59, #47, #40 | 0–9 |

Two array layouts exist, and which one a game uses is a property of the ROM revision
rather than of the game. On the *offset-0* family Free Play is record 33 and the
mapping above applies directly: avr_200, avs_170, bbh_170, bdk_294, csi_240,
fg_1200af, nba_802, st_161h, tf_180, trn_174h, twd_156, twenty4_150, xmn_151h. On the
*+2* family two records are inserted somewhere before record 30 and everything
measured sits exactly two later -- Free Play 35, Balls Per Game 32, Credit Limit 34,
Ball Save Time 39: acd_170h, im_185ve, im_186, im_186ve, mtl_170h, mtl_180, mtl_180h,
smanve_101, st_162, st_162h, twd_160h. Note that Star Trek and The Walking Dead appear
in both lists -- st_161h and twd_156 are offset-0 while st_162/st_162h and twd_160h are
+2 -- so the layout must be established per ROM and never carried across a revision. On both
families Balls Per Game is three records below Free Play and Credit Limit one below,
which is how `ball_count` and `max_credits` were placed on games where only Free Play
was toggled; on every game where the menu was later exercised the rule held.

Multi-option adjustments store an option code: Replay Type is NONE=0, FIXED=1,
DYNAMIC=2, AUTO=3. (The sweep table above had #39 Language and #40 Player Language
Select swapped; the ROM and a cabinet's menu put Language at record 6, ID 7.)

#### Adjustments from the ROM

The ROM describes every adjustment, so `adjustments` can be generated rather than swept.
Every SAM map has its A.1 and A.2 sections from the ROM:

- A descriptor table, 32 bytes per adjustment ID: record address, base default, min, max,
  step, a pointer to the name, and a display type. The ID is the entry's position. Most
  ROMs keep the records from `0x02102008`; early World Poker Tour (before 1.40) and Pirates
  of the Caribbean (before 3.00) keep them from `0x02100BC4`.
- A display-type table: per type, the option names (as message IDs) and the formatter
  that prints the values some settings show as words (Ball Save Time 0 is NO BALL SAVES
  and 16 AUTO, Match Percentage 11 is OFF, ...). Game Pricing's names are the run of
  pricing messages from AUSTRALIA 1, with CUSTOM at its maximum.
- The A.1 menu order as a list of IDs. The newest ROMs leave IDs 11 and 12 (the two
  records of the *+2* family) out of it.
- A.2 is not a list in the ROM, and the menu hides some IDs (Star Trek: Fixture On and
  Off; Spider-Man VE 1.00: IDs 114-117; Pirates: 78-80), so the A.2 items in the maps are
  the IDs the service menu showed when it was walked in libpinmame.

A factory reset applies an install preset after the base defaults (Player Language
Select becomes YES; Spider-Man's replay levels and high-score defaults rise), so the
defaults in the maps are a factory-fresh NVRAM's. Game-specific displays are game code
that the boot copies to RAM at `0x010xxxxx`; their formatters were read from a RAM dump
of the booted game, which gives the values they print as words (Spider-Man VE's Locks
From Plunger 0 NONE, 4 UNLIMITED). Values such a formatter prints through SAM's own format strings
(`%u%P1/ST/ND/RD/TH/% MULTIBALL`) stay plain numbers. Best Combo Champion stores its
N-way count in the record's high half (`0x00050001` shows 5-WAY), so it is declared as
the two bytes at +2.

Master volume is *not* an adjustment record. It is a single byte (0–63, factory 40;
52 on AC/DC LE) with a complement check byte immediately after it, at a per-ROM
address. Each address below was measured by pressing volume up in attract (libpinmame)
and diffing the NVRAM: the byte and its check byte moved and nothing else did. The
ROM's volume setter (`cmp rN, #63 ; movcs rN, #63`, then the address from the literal
pool) gives the same address on every one of them. Adjustment #47 Music Volume (1–15)
is a different setting.

| address | games |
|---|---|
| `0x02110204` | mtl_180, mtl_180h, twd_160h |
| `0x02110248` | acd_170, acd_170h, im_185ve, im_186, im_186ve, st_162, st_162h |
| `0x0211024C` | bdk_294, csi_240, fg_1200af, nba_802, twenty4_150 |
| `0x02110250` | avr_200, avs_170, bbh_170, mtl_170h, smanve_101, st_161h, tf_180, trn_174h, twd_156, xmn_151h |

### Audits

Audits are 16-byte records (around `0x021023D0` on the games examined):

```
+0   32-bit little-endian value
+4   32-bit, always zero in every sample
+8   copy of the value
+12  check byte: 0xFF minus the 8-bit sum of the first twelve bytes
+13  0xFF 0xFF 0xFF
```

The value and its copy change in the same sample, with the check byte valid
throughout; live counters (play time) tick during the game. The dword at +4 never
left zero across two full games, so it is not a WPC-style in-game accumulator. A
writer must update the value, the copy and the check byte together.

### Credits

`0x0211100C`, one byte, on all twenty games measured: it rises with coins and falls
by one at each game start.

### Scores

Scores are little-endian integers in NVRAM, four per game. Both the slot address and
the spacing between players are per ROM, so neither may be carried from one map to
another:

| slot address | spacing | games |
|---|---|---|
| `0x021109E4` | 4 | avs_170, im_185ve, im_186, im_186ve, mtl_170h, smanve_101, st_162, tf_180, trn_174h, twd_156, xmn_151h |
| `0x021109E4` | 8 | avr_200, bbh_170, fg_1200af, nba_802, twenty4_150 |
| `0x021109F0` | 8 | bdk_294, csi_240 |
| `0x02110A0C` | 4 | st_161h, st_162h |
| `0x02110A24` | 8 | acd_170, acd_170h, mtl_180, mtl_180h |
| `0x02110A9C` | 8 | twd_160h |

Eight-byte spacing does not by itself mean an eight-byte score: several of the games
above pair it with a 32-byte champion record, whose score cannot be wider than four
bytes, so the extra four bytes are padding there. The games whose champion records do
carry a 64-bit score (see below) are all in the 8-byte group, which is suggestive but
not proof -- a live slot's width has not been measured on any game. The slots are
declared as four bytes except on the games with 36-byte champion records (below),
which declare eight.

A recurring false positive when searching for score slots is a *scaled set* in CPU
RAM: four values each roughly a quarter of the previous one, which is display scratch,
not the score.

### Champion records

High scores and mode champions are 32-byte records (36 on some later ROMs):

```
+0            name, null-terminated, 0xFF fill to the score
+24           little-endian score: 4 bytes on a 32-byte record, 8 on a 36-byte record
+28  / +32    checksum16: 0xFFFF minus the 16-bit sum of the preceding bytes, little-endian
+30  / +34    two slack bytes
```

The record begins at the *name* on every game measured, and the score is at +24 on
every high-score and mode-champion record but one; the 36-byte form does not move the
score. (The exception is Spider-Man VE's Best Combo Champion, which
keeps a one-byte combo count at +0x1A instead of a score at +24.) The checksum is what
establishes that framing: taking the records to start at the name validates all five
high scores on every image checked, and taking them to start at the score validates
none. Two maps had been framed the other way and so paired each name with the
following record's score, which reported the Grand Champion's points against the
first-place player's initials; both are corrected.

The record size is what sets the score width. On a 32-byte record the checksum16
occupies +28 and +29, so the score physically cannot be wider than the four bytes at
+24. On a 36-byte record the checksum moves to +32, and the eight bytes from +24 to
+31 are **all score**: the champion score on those games is a 64-bit little-endian
integer.

That was settled by poking the NVRAM and reading the ROM's own attract display back,
on mtl_180h. The Grand Champion record held `JDB` with 75,000,000. Editing a pair of
bytes that leaves the byte sum -- and so the checksum -- unchanged avoids having to
recompute anything:

| bytes changed | attract display |
|---|---|
| none | 75,000,000 |
| +27 -= 1, +28 = 1 | 4,353,190,080 |
| +27 -= 2, +29 = 1, +31 = 1 | 72,058,693,591,001,280 |

The second reading proves +28 carries 2^32; the third proves the field runs all the
way to +31, since 72,058,693,591,001,280 is exactly the eight-byte little-endian
value and no shorter read produces it. The ROM also wrote the record back
byte-identical on exit, so it round-trips the wide value rather than normalising it.
(Credit to @tomlogic, who ran the first of these independently and reported the same
4,353,190,080.)

Note that the champion-threshold tables on these same games still store their
thresholds as 4-byte values with a complement check byte, so the widening is in the
stored record only. That mismatch is why the extra bytes could not be settled by
inspection: they read zero in all 163 captured records, because no score had ever
exceeded 2^32.

Only `acd_170`, `acd_170h`, `mtl_180`, `mtl_180h` and `twd_160h` have 36-byte
records, so only those declare `length` 8; every other game keeps 4. It applies to
mode champions as well as high scores on those games -- the records are the same
form, and the checksum validates at +32 in all 50 mode-champion records across the
four of them an image was available for, with `+28..+31` zero throughout. The
handful of champions that hold a counter rather than a score (Combo Champion, The
Walking Dead's Walkers Killed Champion) are untouched. This is a
property of the record size, checkable per game from the checksum position, not
something to assume for SAM generally. Whether the *live* score slots in working RAM
widen to match is a separate question and is **not** established -- see the spacing
table above.

Declared as `checksum16` with `length` 30 (or 34). The name field takes the
10-letter names Standard Adjustment #36 allows, so initials are declared as `ch`
with `null: terminate` and `length` 11. Record order matches the default-threshold
table (`0x021022A8` on Iron Man, `0x021024F8` on Metallica, stride 0x18) and the
attract display, which is how mode-champion labels were assigned where the records
held only factory initials; an operator champion reset copies the thresholds into
the records and keeps the initials.

## Working RAM

### Player and ball

The current player and current ball are adjacent bytes in CPU RAM, player low and
ball high, at a per-ROM address (`0x00032438/9` Transformers, `0x00034DB8/9` Iron Man
VE, `0x00037714/5` Iron Man 1.86 non-VE — the two 1.86 ROMs differ). They were found
by behaviour, not value: over a multi-player game the player byte completes 1→2→3→…
once per ball and wraps to 1 in the same sample the ball steps, which separates the
pair from carry bytes of 32-bit counters that also count 1, 2, 3.

The ball never returns to 0 after a game: it parks at the last value through attract
and drops to 1 when the next game starts. Consumers detecting a game's end must use
the status byte below, and a new game is the ball wrapping down to 1.

### Status byte

On every game measured one byte near the ball counter is a status byte: player + 0x32
on most, + 0x2C on Family Guy, World Poker Tour and Pirates, + 0x18 on Shrek, + 0x34 on
Spider-Man 2.10-2.40, + 0x48 on Wheel of Fortune. It reads `01` in attract from
power-up; in a game a base value (`12`, `13` or `14` by game) and, while ball serves,
modes and animations run, other values (`26`, `28`, `40`, `43`, `4C`, `5F`, `61`, `7B`,
...); from the tilt to the next ball served the base value plus 2 (`14`, `15` or `16`);
and `01` again at the moment the game ends. The maps decode it as:

- `game_over`: no bit above 0x01 set (mask 0xFE, inverted), i.e. the byte is `00` or `01`.
- `tilted`: the tilt value alone, an enum over mask 0x1F (0x3F on Mustang, whose `B5`
  equals `15` under 0x1F; 0x7F on X-Men and Rolling Stones, `55`).

A few maps keep a narrower bit test that held on every sample of their recording and
of a cabinet game (bdk_294, mtl_*, smanve_101, twd_160h: `tilted` bit 0x04 or 0x02;
bbh_170, bdk_294, csi_240, im_*, mtl_*: `game_over` mask 0x12, 0x14, 0x30 or 0x38).
Family Guy's `game_over` is a separate byte (`0x00032E04`: 05 in attract, 00 in a game).

Single bits of the status byte misread a full game, because mode values carry them:
Avatar's `40`/`45`, Avengers' `61`, TRON's `4D` and X-Men's `28` read as game over under
mask 0x12, and Big Buck Hunter's `34`/`3F`/`56`/`6F`, Iron Man's `72` and TRON's `5F`
(while tilt warnings come in) as tilted under bit 0x04 or 0x02. Bytes elsewhere did
worse on a cabinet, and were replaced by the status byte:

| game | old field | on a cabinet |
|---|---|---|
| acd_170h | `game_over` `0x00034C7E` | flips 64/00 every few seconds in play |
| acd_170h | `tilted` `0x00038D24` inverted | reads tilted in attract after power-up |
| nba_802 | `game_over` `0x0003FF83` | game over for 6 s after a tilted ball drained |
| nba_802 | `tilted` `0x0003FF6B` | set at each ball launch, never at the tilt |
| st_162 | `game_over` `0x00032652` | stays 02 after the game ends |
| st_162h | `game_over` `0x0003BA3E` | 0 after power-up until a game has ended |
| st_162h | `tilted` `0x0003310B` | also set for a moment at each tilt warning |
| twd_156 | `game_over` `0x00035E48` | 0 after power-up until a game has ended |
| twenty4_150 | `game_over` `0x02102A3C` (NVRAM) | keeps 1 when a game is cut off by power-off |

### Tilt warnings

The tilt-warning counter (`0x0003893C` on 24, `0x000390BC` on CSI, declared as
`tilt_warnings`) counts warnings within a ball and clears at the next ball. It is not a
tilt flag: with the factory setting of two warnings the counter reaches 2 at the second
warning and the third hit tilts, so the ball is still live at 2.

### How the game state was checked

Each `game_over` and `tilted` comes from a headless libpinmame game of the ROM (two
players, three balls, two tilts, RAM sampled throughout) and, where the map says so, a
cabinet game: two players, a mechanical tilt on player 1's first ball, flippers until the
game ends, with the declared fields and any candidate bytes logged at every change and
the final scores and records compared with the DMD. Headless runs miss values (a game
that never ends headless never shows the return to `01`), and an NVRAM byte survives a
game cut off by power-off, so a field is trusted only after a full game on a cabinet.
