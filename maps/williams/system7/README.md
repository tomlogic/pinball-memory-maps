# Williams System 7

## Game Status

The byte at 0xC9 holds the game status:

| value | when |
|---|---|
| 0x00 | game in progress |
| 0x01 | attract mode after power-on; on some games also after a game |
| 0x02 | attract mode after a game has ended (not on every game) |
| 0xFF | Firepower II only: during each end-of-ball bonus count |

Firepower II (`fpwr2_l2`) writes 0xFF to this byte for 0.2 to 1.2 seconds
at the end of every ball, so reading it as a `bool` gives one false "game
over" per ball on that game.  The 10KB generic map masks the byte with 0x03
and treats 1 and 2 as game over, the same approach as the System 6 maps
(see GitHub issue #171).

Measured with headless PinMAME, sampling the byte on every emulated frame
through complete games:

| ROM | map | 0xFF between balls | after a game | `bool` rule | masked rule |
|---|---|---|---|---|---|
| `fpwr2_l2` | generic-10KB | every ball | 2 | one false rise per ball | one rise per game |
| `pharo_l2` | generic-10KB | never | 1 (1, then 2 four seconds later on a cabinet) | one rise per game | same |
| `jngld_l2` | generic-10KB | never | 1 | one rise per game | same |
| `strlt_l1` | generic-12KB | never | 2 | one rise per game | same |
| `lsrcu_l2` | lsrcu_l2 | never | 2 | one rise per game | same |

The masked rule gives the right answer on all five.  The 12KB generic map
and `lsrcu_l2` still use `bool`: it was correct on the one ROM measured for
each.  The other ROMs of both generic maps were not measured.

evilwraith confirmed the `fpwr2_l2`, `pharo_l2` and `jngld_l2` rows on a
cabinet (see the pull request for this change).  On Pharaoh, 0x58 counts
down in BCD on the last ball, so "ball in play is 0" is not a substitute
for this byte there.

A restart (Start pressed during a game) does not raise `game_over` on any
of the five.  Star Light can show 1 for about four seconds at the end of a
game before settling on 2.

## Banked RAM

The platform files describe CPU addresses 0x0000-0x00FF as a bank onto the
first 256 bytes of RAM at 0x1000.  `game_state` uses the 0x00xx addresses.
A reader that takes bytes from a flat copy of the CPU address space,
without following the bank, sees zeros there for the whole session.  The
same bytes are at 0x1000 plus the address.
