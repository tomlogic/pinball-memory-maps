# Data East RAM Mapping

## Adjustment checksum (version 3 and 3b)

Data East version 3 games keep their machine adjustments from `0x1E00` and protect them with a
plain 8-bit sum -- not complemented -- stored in a single byte elsewhere in NVRAM. A write to any
byte of the block that does not update that check byte is discarded at the next boot: the ROM
resets the whole of NVRAM to factory. That is the failure this documents, first seen as Free Play
set from outside the service menu never holding.

Every version 3 game shares one checksum routine, so both the block length and the check byte can
be read out of the ROM rather than guessed:

```
4F           clra
F6 hh ll     ldab $hhll        ; block length, a constant in ROM
CE 1E 00     ldx  #$1E00
AB 00        loop: adda 0,x
08                 inx
5A                 decb
26 FA              bne loop
39           rts
...          caller: jsr/bsr <routine> ; B7 aa aa   <- staa, the check byte
```

To extract it for a new ROM: search the CPU ROMs for `AB 00 08 5A 26 FA 39`, step back six bytes
to the `ldab`, read the count at the address it names, then find the `jsr`/`bsr` to the routine
and take the `staa` that follows. Exclude the sound and display ROMs when resolving the count
address, or a sound ROM will answer for the CPU companion and give a nonsense length.

The check byte is often nowhere near the block (`0x1FBD`, `0x1FD0`, `0x1FD8`, `0x1FDD` on the
later games), which is why searching an NVRAM image for a sum adjacent to the adjustments finds
nothing on most of the family.

| block | check | games |
|---|---|---|
| 0x1E00-0x1E42 | 0x1EDE | bttf_a21, bttf_a28 (see note) |
| 0x1E00-0x1E44 | 0x1EDE | simp_a27 |
| 0x1E00-0x1E45 | 0x1FC0 | trek_117, trek_120, trek_201 |
| 0x1E00-0x1E46 | 0x1EFE | ckpt_a17 |
| 0x1E00-0x1E47 | 0x1EFE | btmn_106 |
| 0x1E00-0x1E48 | 0x1EFE | tmnt_104 |
| 0x1E00-0x1E56 | 0x1FD8 | jupk_305, jupk_501, jupk_513 |
| 0x1E00-0x1E59 | 0x1FC0 | lw3_200, lw3_208 (and aar_101), stwr_101, stwr_103 |
| 0x1E00-0x1E5A | 0x1FBD | batmanf |
| 0x1E00-0x1E5A | 0x1FDD | gnr_300 |
| 0x1E00-0x1E5B | 0x1FDD | baywatch, frankst, lah_113, mav_200, maverick, tomy_400 |
| 0x1E00-0x1E5D | 0x1FD0 | rab_130 |
| 0x1E00-0x1E5D | 0x1FDD | rab_320, wwfr_106 |
| 0x1E00-0x1E60 | 0x1FDD | tftc_400 |
| 0x1E00-0x1E67 | 0x1EDA | hook_408 |

tmnt_104 and hook_408 were measured live on a cabinet first (a 2 Hz tap of RAM across operator-menu
changes: Free Play moved the sum by one, Balls Per Game by two); the ROM procedure reproduces both
exactly, which is what validates it. Every other value above was read from the ROM, and each was
checked against saved NVRAM where a cabinet had that game.

**Revisions within a map do not always agree.** The length is a per-build constant, so where one
map covers several ROMs they can differ by a byte or two: bttf_a28 sums one byte more than
bttf_a27 and bttf_g27, mav_100 one less than mav_200, simp_a20 one less than simp_a27. Each map
declares the value for the ROM it is named after unless a different revision was confirmed against
hardware, and says so in its notes. A mismatch is safe rather than destructive: a writer must
refuse a region that does not validate.

Version 1 and version 2 games do not contain this routine and keep their adjustments elsewhere
(`0x078D` and `0x1F8D`/`0x1F47` for Free Play); nothing is declared for them.
