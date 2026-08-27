# Williams System 6

## HSTD display
At the end of the game, the machine alternates one of the player score
displays with the current High Score To Date (HSTD).  It backs that
player score up at 0x70.

I originally assumed it always shows the HSTD in the Player 1 position,
but during Visual Pinball testing with Algar, I witnessed it using
the Player 3 and Player 4 positions.

If attempting to read scores from memory during "game over", it will be
important to watch for the HSTD taking the place of an actual player's
score in any position.  We could encode this in the map somehow, using
the lamp matrix.  When bitmask 0x80 at address 0x17 is set, the game is
showing the HSTD.

Later eras of games display the HSTD in all player positions, which
makes it easier to detect.

Note: Firepower (and possibly other games) doesn't back up the tens
digit to 0x72, so the game always shows 00 for that player's score
during attract mode.

## Game Status

Games set bits of the byte at 0x78 to indicate things like game over, tilt,
extra ball, and playfield qualified.  We originally used bit 0 to identify
a "game over" state, but Wes Smith reported (see GitHub issue #171) that
the game writes 0xFF to 0x78 between balls which will trigger an early
game over.

One possible solution is to look at the bottom two bits (bit 1 is tilt)
and only accept a true "game over" when they's set to `01`.  Another
solution is to compare `current_ball` to 0 since we're reading display
memory, and it's set to zero from the match sequence.  But that display
remains set to ` 3` when match is disabled.
