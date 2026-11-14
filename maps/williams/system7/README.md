# Williams System 7

## Game Status

The byte at 0xC9 holds the game status:

| value | when |
|---|---|
| 0x00 | game in progress |
| 0x01 | attract mode after power-on |
| 0x02 | attract mode after a game has ended |
| 0xFF | during each end-of-ball bonus count (0.1 to 1.2 seconds per drain) |

Reading it as a `bool` gives one false "game over" for every ball.  The
10KB generic map masks the byte with 0x03 and treats 1 and 2 as game over,
the same approach as the System 6 maps (see GitHub issue #171).  With that
rule `game_over` rises once per game, and it agrees with "ball in play is
0" (low nibble of 0x58) on every snapshot of the test games.

Measured on `fpwr2_l2`, `pharo_l2` and `jngld_l2` with headless PinMAME:
one-, two- and four-player games and a mid-game restart.  A restart (Start
pressed during a game) goes straight from ball N to ball 1 with scores
zeroed; `game_over` does not rise.

The 12KB generic map and `lsrcu_l2` use the same byte but were not
measured, so they are unchanged.

## Banked RAM

The platform files describe CPU addresses 0x0000-0x00FF as a bank onto the
first 256 bytes of RAM at 0x1000.  `game_state` uses the 0x00xx addresses.
A reader that takes bytes from a flat copy of the CPU address space,
without following the bank, sees zeros there for the whole session
(PinMAME's `memory_find_base` behaves this way for System 7).  The same
bytes are at 0x1000 plus the address.
