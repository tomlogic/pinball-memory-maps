# Stern SAM RAM Mapping

## Introduction

Stern SAM games (2006–2014: Spider-Man through The Walking Dead) run an ARM AT91 CPU
with 128 KB of battery-backed NVRAM mapped at `0x02100000`. PinMAME exposes an 80 MB
CPU image, but everything a map needs sits in two windows: NVRAM, and the 64 KB of
working RAM at `0x00030000`–`0x0003FFFF` (the rest of the image is constant across a
game). The platform file's *Main RAM* entry is 1 MB so that maps may read the working
RAM; widening it permits reads and changes nothing about how any field decodes.

Everything in these maps that is not attributed to a disassembly was measured live:
a 2 Hz tap of CPU RAM and NVRAM recorded on a cabinet across an operator-menu
session, coins, and at least one full game with a mid-ball tilt, then each
declaration was checked against every sample of its recording. Per-map `_notes`
record what is specific to that game; this file holds what the games share.

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
| system group #43, #41, #61, #54, #42, #60, #40, #59, #47, #39 | 0–9 |

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

Multi-option adjustments store an option code, and the display order is not the
numeric order: Replay Type on Star Trek is NONE=0, FIXED=1, DYNAMIC=2, AUTO=3 while
the menu lists AUTO first. Only codes that were stepped through with the tap running
are named in the maps.

Master volume is *not* an adjustment record. It is a single byte (0–63, factory 40)
with a complement check byte immediately after it, at a per-ROM address:
`0x02110250` on most games, `0x0211024C` on NBA, `0x02110248` on Iron Man,
`0x02110204` on The Walking Dead LE (`twd_156` uses `0x02110250`). Adjustment #47
Music Volume (1–15) is a different setting.

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
| `0x02110A24` | 8 | acd_170h, mtl_180, mtl_180h |
| `0x02110A9C` | 8 | twd_160h |

Eight-byte spacing does not by itself mean an eight-byte score: several of the games
above pair it with a four-byte champion record, so the extra four bytes are padding
there. Where the champion record also grows (see below) the score really is wider.

A recurring false positive when searching for score slots is a *scaled set* in CPU
RAM: four values each roughly a quarter of the previous one, which is display scratch,
not the score.

### Champion records

High scores and mode champions are 32-byte records (36 on some later ROMs):

```
+0            name, null-terminated, 0xFF fill to the score
+24           4-byte little-endian score (36-byte records add four more bytes here; see below)
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

On a 36-byte record the checksum sits at +32, so four bytes sit between the 4-byte
score at +24 and the checksum. What they are for is **not established**. They read
zero in every image captured (163 records across acd_170, acd_170h, mtl_180, mtl_180h
and twd_160h), and those are the same games whose live score slots move to 8-byte
spacing, which is what a 64-bit score would look like below 2^32. Against that
reading, the champion-threshold tables on the same games store their thresholds as
4-byte values with a complement check byte -- the format a 32-bit score would be
compared against. The score is declared as four bytes on every game until a value
above 2^32 is observed or the ROM settles it; nothing in the maps depends on the
question, since both readings decode identically for every score seen so far.

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

### Status bitfield

On most games the byte 0x31 past the ball counter is a status bitfield: it reads 1
through attract and other values through a game, and the value while tilted differs
from the value in play by one bit for exactly the samples between the tilt and the end
of the tilted ball, during which the player's score is frozen. 17 of the
23 games with a `game_over` declaration use that byte:

| games | game_over | tilted |
|---|---|---|
| avr_200, avs_170, bbh_170, bdk_294, smanve_101, trn_174h, xmn_151h | mask 0x12 inverted | mask 0x04 |
| im_185ve, im_186, im_186ve | mask 0x14 inverted | mask 0x02 |
| mtl_180, mtl_180h | mask 0x30 inverted | enum over mask 0x06 |
| csi_240 | mask 0x12 inverted | mask 0x02 at 0x000390BC (tilt-warning counter) |
| mtl_170h | mask 0x38 inverted | mask 0x04 |
| st_161h | mask 0xFE inverted | enum over mask 0x1F, value 21 only |
| tf_180 | mask 0xFE inverted | mask 0x04 |
| twd_160h | mask 0xFE inverted | mask 0x02 |

No single bit is common to every in-play value across games, and the tilt bit is `0x04`
on some ROMs and `0x02` on others, so each map declares the narrowest expression that
holds on every sample of its own recording rather than a shared decoding. The values
actually observed for a game -- what it reads in attract, at game start, at ball start,
in play and while tilted -- are recorded in that map's `_notes`, along with the size of
the recording they came from.

The remaining games do not use that byte and keep game over, tilt, or both elsewhere:

| game | game_over | tilted |
|---|---|---|
| acd_170h | `0x00034C7E`, whole byte | whole byte, inverted at 0x00038D24 |
| fg_1200af | `0x00032E04`, whole byte | not present |
| nba_802 | `0x0003FF83`, whole byte | whole byte at 0x0003FF6B |
| st_162h | `0x0003BA3E`, whole byte | whole byte at 0x0003310B |
| twd_156 | `0x00035E48`, whole byte | not present |
| twenty4_150 | `0x02102A3C`, whole byte, inverted | mask 0x02 at 0x0003893C (tilt-warning counter) |

Contributions that decode the individual bits are welcome; the recordings behind each
row are described in the maps' notes.

### Tilt warnings

Where mapped, the tilt-warning counter is a CPU RAM byte that counts plumb-bob
closures within a ball (`0x0003893C` on 24, `0x000390BC` on CSI); with the factory
setting of two warnings, tilted is that counter reaching 2.
