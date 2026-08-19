# Pinball Memory Maps

### Sponsorship
A special thanks to [Scorbit](https://scorbit.io/) for sponsoring Tom
Collins to work on this project starting in June 2025.

### Description
The initial goal of this project was to document the contents of the `.nv`
files PinMAME (the solid state pinball machine ROM emulator) uses to store
the contents of a game's non-volatile RAM.  At a  basic level, it's useful
to know how a game stores its high scores so  other programs (like a game
launcher) can parse and display that information.

Going further and documenting adjustments and audits allows for the
development of alternate interfaces (like a web browser) to view audits
and change game settings without using the service menu.

This project started in October 2015, and should be considered "beta"
quality.  As people map more games, the file format may change to
support additional requirements.  We are working toward a "1.0" file 
format version that should reduce the number of changes moving foward.

Starting in 2025, it transitioned to include mapping of all RAM for a game,
including the volatile RAM that isn't stored in `.nv` files, and isn't 
maintained by battery backup in physical games.

I chose to use [JSON](http://json.org) as a simple yet flexible file
format for this project.  If necessary, other projects should be able to
convert the map files to alternate formats.  The JSON website describes
the file format and includes links to parsing libraries in many
programming languages.

For this repository, we're formatting JSON files with each entry on its
own line, and 2 spaces for indentation.  You can get this formatting using
either `jq` or `python`:

- jq: `jq --indent 2 --ascii-output . romname.map.json`
- python: `json.dumps()` with the setting `indent=2`

```
    print(json.dumps(json.load(open('romname.map.json', 'r')), indent=2))
```

We're using the `--ascii-output` option to `jq` so it's consistent with the
Python output of bytes values 0x80 to 0xFF.  For example, `hs_l4.map.json`
encodes a 0xC4 byte in the default attract text as `\u00C4`.

The script `tools/reformat-json.sh` can reformat one (or all) of the JSON
files using `jq`.  The script `tools/normalize-map.py` uses Python to do
the same formatting as `jq`, but also normalizes maps to the latest format.

[Project home](https://github.com/tomlogic/pinball-memory-maps)

_Note that this project was renamed to pinball-memory-maps from 
pinmame-nvram-maps in August 2026._

## License

As of August 2026, these Pinball Memory Maps are made available under the
[Open Database License](http://opendatacommons.org/licenses/odbl/1.0/).
Any rights in individual contents of the database are licensed under the
[Database Contents License](http://opendatacommons.org/licenses/dbcl/1.0/).

This project was previously licensed under the GNU Lesser General Public 
License v3.0 (LGPL).  Since that license is more appropriate for code than
data, it now applies to code in the `tools/` directory.  LGPL requires that
derived works be licensed under the same license, but works that only link
to it do not fall under this restriction.

My intent is for the map files (`.map.json`) to remain open and for
everyone to benefit from updates, yet allow for their use in
closed-source projects with attribution.  Please include a GitHub link
to the original project (or your fork of it), along with the description,
"This program makes use of content from the Pinball Memory Maps project."

## Sample Code

My preference is to keep this project dedicated to just the JSON files
so other projects can incorporate it as a git submodule.

A [related project](https://github.com/tomlogic/py-pinmame-nvmaps)
currently includes a Python program (`nvram_parser.py`) that works as a
standalone application to dump a parsed `.nv` file, or as a class
(ParseNVRAM) you can use from other programs.

There is also a [Rust library](https://github.com/francisdb/pinmame-nvram) 
for reading and writing nvram files that uses the maps from this project.

## Mapping New Games

Start PinMAME and write down all the high scores, and then exit. 
Open the game's `.nv` file in a hex editor and search for the initials. 
It should be possible to find each set of initials, with the
corresponding score nearby.

For adjustments, make a list of each setting, its default value, the
range of accepted values, and whether certain values have special
meaning (like *OFF* or *DISABLED*).  I make use of a modified version of
PinMAME that monitors an address range and dumps any changes it detects
to that range.  It's a simple matter to change a setting and see the
modified location in the NVRAM file.

Audits are a bit more difficult, and I intend to build a tool to modify
portions of the NVRAM file to aid in matching audits to file locations.

## Map Index

The file `index.json` is a simple dictionary that maps PinMAME romset names
to their corresponding map file (which may be valid for multiple ROMs).
Implementations can use it for lookups  instead of parsing the entire list
of maps.

- The dictionary will have a single entry for a given ROM (i.e., the
  repository won't have multiple maps for a ROM).
- The map filename can be in a relative subdirectory, using `/` as the
  directory separator (e.g., `"maps/williams/wpc/dm_lx4.map.json"`).
- Use `tools/update-index.py` to automatically update the index.

## Data Freshness

The file `last-updated.json` records when the map data last changed, and where
to download that exact revision.  Projects that keep a local cache of this
repository can poll it instead of re-fetching everything:

```json
{
  "_note": "Automatically generated by tools/update-last-updated.sh",
  "commit": "aab556e3059f4463740293e01531b2f9d817ed89",
  "last_updated": 1787018567,
  "last_updated_iso": "2026-08-18T02:02:47Z",
  "tarball_url": "https://github.com/tomlogic/pinball-memory-maps/archive/aab556e3059f4463740293e01531b2f9d817ed89.tar.gz",
  "zipball_url": "https://github.com/tomlogic/pinball-memory-maps/archive/aab556e3059f4463740293e01531b2f9d817ed89.zip"
}
```

- `last_updated` is a Unix epoch timestamp, and `last_updated_iso` is the
  same moment in UTC for human readers.
- `commit` is the commit that made the change, and `tarball_url` and
  `zipball_url` point at that commit rather than at a branch.  Nothing after
  it touched a `*.json` file, so those archives hold the current map data and
  their contents never change out from under a cached copy.
- Both archives unpack into a single top-level directory named
  `pinball-memory-maps-<commit>`, which callers will usually want to strip.
  The tarball is roughly a third the size of the zip.
- Only `*.json` files count.  A commit that only touches the README or the
  scripts in `tools/` leaves these values alone.

The file is regenerated by `.github/workflows/last-updated.yml` on every push
to `main` that changes a `*.json` file.  Run `tools/update-last-updated.sh` to
preview it locally; it builds the URLs from your `origin` remote, so set
`GITHUB_REPOSITORY=owner/name` if you are working in a fork.

Polling it does not consume the GitHub REST API rate limit (60 requests per
hour for unauthenticated clients), because neither `raw.githubusercontent.com`
nor the archive URLs are part of that API:

    https://raw.githubusercontent.com/tomlogic/pinball-memory-maps/main/last-updated.json

That URL honors `If-None-Match`, so an unchanged file costs only a `304 Not
Modified`.

## Listing of PinMAME ROM sets

The file `romnames.json` is a simple dictionary with PinMAME romset names 
as the key (e.g., "hs_l4") and a value with a human-readable description
(e.g., "High Speed (L-4)").

You can update the contents of that file by piping the output of
`pinmame -listfull` through the `tools/update-romnames.py` script.

## Platform Files

Starting with `_fileformat` v0.7, each map references a "platform" file
that primarily describes the memory layout for the game.  The top-level
`platforms/` directory holds these JSON files, and the map file's
`_metadata` section has a `platform` property with the name of that file
without the `.json` extension (e.g., "williams-system11").

The platform file has the following properties:

- **_notes**: Optional notes about the hardware platform.
- **cpu**: Optional string describing the hardware's CPU.
- **endian**: Set to either `"big"` (default) or `"little"` to indicate the 
  default byte order of multibyte values.
  Refers to which end of the number is stored first.  For example, a
  `bcd`-encoded score of 123,450 is the byte sequence 0x12, 0x34, 0x50 if
  big-endian, and 0x50 0x34 0x12 if little-endian.
- **memory_layout**: A list of dictionaries describing RAM regions for the 
  given hardware.

### Memory Layout Entries
- **label**: Optional description of the memory for human reference.
- **_notes**: Optional notes about this section of `memory_layout`.
- **type**: Either "ram" (for volatile memory) or "nvram" (for non-volatile
  memory stored in PinMAME's `.nv` file for the romset).
- **address**: The base CPU address used to access the memory contents.
- **size**: The number of addresses covered by the device.
- **nibble**: Set to `"both"` (default for 8-bit memory), `"high"`, or 
  `"low"` to identify which 4-bit nibble to use from each address.  Some 
  games (e.g., Williams System 7, Gottlieb System 80B, Stern M-100) used
  4-bit NVRAM, so only half of each byte is valid.
  `"both"` indicates use of the full 8 bits/byte.  Set to `"low"` to use
  the lower 4 bits of the byte or `high` to use the upper 4 bits of the byte. 
  The `bcd` sequence `0x12 0x34 0x56` translates to `123456` when `nibble` is
  `both`, `246` when `nibble` is `low` and `135` when `nibble` is `high`.
  Robowars has an example of a `nibble=low` `ch` field, where the sequence
  `0x04 0x01 0x04 0x02 0x04 0x03` translates to `0x41 0x42 0x43` which is the
  string `"ABC"`.
  The `bally-stern-6800` platform uses `nibble=high` and Williams System 4-7
  use `nibble=low`.

## Maps File Format

The JSON file is essentially a big dictionary or associative array, with
the following key/value pairs.  It may help to review one or more of the
included files as an example of the file format while reading this
section of the documentation.

In cases where this specification isn't clear, please use existing maps
or the Python library as a guide.

Numbers can appear as decimal values (`1234`) or hexadecimal values
inside of strings (`"0x4D2"`).  `_fileformat` v0.3 deprecated usage of
hexadecimal strings except for the `mask` attribute, but it was undeprecated
for v0.7 when locations represented memory addresses from the CPU's 
perspective, not just offsets into the `.nv` file.

### Metadata

Starting with fileformat v0.6, all metadata fields other than `_fileformat`
and `_notes` are now part of a `_metadata` attribute.

Note that keys starting with underscore and the `_metadata` attribute 
describe the map itself and provide defaults for later entries.

- **_notes**: Notes about the map, possibly indicating who created it or
  portions of the map that may not be entirely correct.  Can be a string
  or an array of strings.
- **_fileformat** _(required)_: A `float` indicating the file's format.

#### _metadata Properties

- **version** _(required)_: A `float` indicating the map's version.
- **roms** _(required)_: A list of PinMAME ROMs that use this map.
  version.  See Version History at the end of this README for changes.
- **free_only**: A list of PinMAME ROMs that only support "home" use.  If
  a ROM is in this list, it's always Free Play, and it's safe to ignore 
  `game_state` fields of `credits`, `max_credits`, and `free_play` as they 
  don't make sense in this context.
- **copyright**: Original author of the map, possibly a list of people
  who have contributed to the map.
- **license**: All files from this project are covered by the LGPL license.
  Modified map files, or maps created using an existing map as a starting
  point are also covered by that license.
- **platform**: Identifies the hardware platform (e.g., Williams WPC) for 
  the ROMs covered by this map.  This is a string that corresponds to a
  JSON file in the top-level `platforms/` directory.  See the Platform 
  section above for details on what's covered in that file.
- **char_map**: Characters to use for the `ch` encoding instead of a straight 
  ASCII table.  See Whirlwind (`whirl_l3.map.json`) as an example.
- **values**: A dictionary for value lists used by multiple entries.  Added
  to `_fileformat` v0.5 to support long lists of pricing options that apply
  to multiple sets of DIP switches.  The `value` property for an entry can
  reference a key to this dictionary instead of having a full list.


### Descriptors

The map file contains objects describing regions of memory and how to
interpret them.  They're comprised of the following key/value pairs:

- **_notes**: Notes for someone maintaining the map; not displayed when
  parsing memory.  Can be a string or a list of strings.

- **encoding** _(required)_ must be one of the following:
  - `"enum"`: An enumerated type where the byte at `start` is used as an
    index into a list of strings provided in `values`.
  - `"int"`: A (possibly) multibyte integer, where each byte is multiplied
    by a power of 256.  The byte sequence `0x12 0x34` would translate to the
    decimal value `4660`.
  - `"bits"`: Same decoding as `"int"`, but used to sum select integers from
    the list in `values`.
  - `"bool"`: Same decoding as `"int"`, but all non-zero values equate to
    `true` and zero is `false`.  Inverts the logic if the optional property
    `invert` is set to `true` (zero is `true` and non-zero is `false`).
  - `"bcd"`: A binary-coded decimal value, where each byte represents two
    decimal digits of a number.  The byte sequence `0x12 0x34` would translate
    to the decimal value `1234`.  When converting BCD values, treat the
    nibbles 0xA to 0xF as 0 numerically, or a space for display purposes.
  - `"ch"`: A sequence of 7-bit ASCII characters that may be shortened by a
    null byte (0x00) terminator based on the `"null"` attribute for the entry.
    If the map has `char_map` metadata, all bytes (including 0x00) are
	indexes into that string.
  - `"raw"`: A series of raw bytes, useful for extracting data yet to be
    decoded or that requires custom processing.
  - `"dipsw"`: A special encoding where `offsets` is a list of DIP switch
    numbers (indexed starting with 1) that combine to form an index into
    the `values` list for the entry.  See the "DIP Switches" section for
    details.
  - `"wpc_rtc"`: A special type for a real-time clock value
    from a WPC game, stored as a sequence of 7 bytes.  Starts with a
    two-byte year (2015 is `0x07 0xDF`), month (1-12), day of month (1-31),
    day of the week (0-6, 0=Sunday), hour (0-23) and minute (0-59).

- You must specify the location of data in memory one or more of the
  following directives:
  - **start**: Address of the first byte/nibble to interpret.  In the past, 
    this was the same as the `.nv` file offset.  Starting with `_fileformat` 
    v0.7, it's the CPU's address and can reference any entry in the platform
    file's `memory_layout` section.
    Default behavior is to use that single byte/nibble unless the `end`
    or `length` keys are present.  Either `start` or `offsets` are required.
  - **end**: Address of the last byte/nibble to interpret.  Its value
    must be greater than or equal to `start`. 
  - **length**: Number of bytes/nibbles to interpret, must be at least 1 
    (default).
  - **offsets**: Alternative to using start/end or start/length when addresses
    aren't contiguous.  List of addresses to use.  Either `start` or `offsets`
    are required.  For `dipsw` encoding, this is actually a list of switch
    numbers.

- These properties provide additional encoding details.
  - **endian**: Overrides the platform's `endian` setting.
  - **nibble**: Overrides the platform's `nibble` setting for the platform's
    Memory Layout section corresponding to the first address of the 
    descriptor.
  - **null**: Used for `"ch"` encodings to specify null (0x00) byte handling.
      For `truncate` and `terminate`, ignore all bytes after the null.
    - `"ignore"`: Ignore (skip over) null bytes.  Default setting.
    - `"truncate"`: A null can shorten the string, but won't be present for
      strings that fill the allotted space.
    - `"terminate"`: Null bytes are always present and terminate the string.

- These properties are only related to displaying the value, independently of
  how it's actually stored in memory.
  - **label**: A label describing this descriptor. 
  - **short_label**: An optional, abbreviated label for use when space is
    limited (like in a game launcher on a DMD). 
  - **values**: A list of strings or integers, used for the `enum` encoding
    (starting at index 0) and the `bits` encoding, as values for bit 0, 1, 2,
    etc.  Starting in `_fileformat` v0.5, this property can be a string that
    references a list stored in the `values` metadata property for the map.
  - **special_values**: A set of key/value pairs for a numeric field where some
    values have special meaning (for example, `{"0": "OFF"}`).
  - **units**: Used to indicate that a field contains a time value as either a
    number of `"seconds"` or `"minutes"`, and should be displayed as `HH:MM:SS`.
  - **suffix**: A string to append to the value (e.g., `"M"` if the value
    represents millions).
  - **scale**: A numeric multiplier for a decoded `int`, `bcd`, or `bits`.
  - **offset**: A numeric value to add to a decoded `int`, `bcd`, or `bits`
    value before displaying it.  Applied after `scale`.
  - **mask**: A mask to apply to each byte before processing.  For example, a
    mask of `"0x5F"` converts lowercase initials to uppercase and a mask of
    `"0x0F"` clears the upper four bits.
  - **invert**: Only used for `bool` encoding.  Defaults to `false`.  If
    set to `true`, treat a value of zero as `true` and non-zero as `false`.

- Encodings can include properties that describe limitations imposed on
  adjustments in the service menu, or just ranges that the ROM considers
  invalid.  These all pertain to the stored value, exclusive of any `scale`
  or `offset`.
  - **default**: The factory default value.
    Used for the **initials** entry of a high score to indicate the value
    for an unused entry (e.g., `"   "` on WPC, `"\u0000\u0000\u0000"` on
    Gottlieb System 80).  Defaults to `0` unless specified.
  - **min** and **max**: The valid range of values.
  - **multiple_of**: Enforce a subset of values between `min` and `max`.
    Defaults to `1` (all values allowed) unless specified.

#### Encoding/Property Cheat Sheet

| property       | bcd/int | bool | bits | ch  | enum | raw | wpc_rtc | dipsw |
|----------------|:-------:|:----:|:----:|:---:|:----:|:---:|:-------:|:-----:|
| start          |    X    |  X   |  X   |  X  |  X   |  X  |    X    |       |
| end            |    X    |  X   |  X   |  X  |      |  X  |    X    |       |
| length         |    X    |  X   |  X   |  X  |      |  X  |    X    |       |
| offsets        |    X    |  X   |  X   |  X  |      |  X  |    X    |   X   |
| endian         |    X    |  X   |  X   |     |      |     |         |       |
| nibble         |    X    |  X   |  X   |  X  |  X   |  X  |    X    |       |
| mask           |    X    |  X   |  X   |  X  |  X   |  X  |    X    |       |
| null           |         |      |      |  X  |      |     |         |       |
| special_values |    X    |      |      |     |      |     |         |       |
| values         |         |      |  X   |     |  X   |     |         |   X   |
| offset         |    X    |  X   |  X   |     |      |     |         |       |
| scale          |    X    |  X   |  X   |     |      |     |         |       |
| suffix         |    X    |      |  X   |     |      |     |         |       |
| units          |    X    |      |  X   |     |      |     |         |       |
| invert         |         |  X   |      |     |      |     |         |       |

##### Encoding Notes
- The `enum` encoding is intended for single-byte values.
- The `bool` encoding always resolves to either `true` or `false`.
- The `bcd`, `bits`, `bool`, and `int` encodings convert bytes into a numeric
  value that is modified by properties such as `offset`, `scale`, `suffix`,
  and `units`.
- `dipsw`, `raw`, and `wpc_rtc` are special encodings.

##### Property Notes
- The `null` property only applies to `ch` encoding.
- The `values` property is a list of values, starting with an index of 0.
- The `special_values` property is a dictionary of integers (as strings)
  and a string to override display of a specific integer.  A common example
  would be replacing a 0 with the word OFF (represented as
  `"special_values": { "0": "OFF" }}`).

### File Map

Keys that don't start with an underscore typically have groups of
**descriptors** as their values.

- **last_played**: A descriptor (likely with a `wpc_rtc` encoding) with a
  date stamp of when PinMAME last saved the `.nv` file.
- **high_scores**: The traditional high score table that would usually
  start with the Grand Champion and then proceed through First Place to
  Fourth Place.  An array of objects with the following key/value pairs:
  - **label**: A label describing the score (e.g., `"Grand Champion"`).
  - **short_label**: An abbreviated label (e.g., `"GC"`).
  - **initials**: Descriptor of where the high score's initials are stored
    in memory.
  - **score**: Descriptor of where the high score's score is stored in
    memory.
- **mode_champions**: Another array of descriptors with recognition of
  other in-game accomplishments.
- **adjustments**: An object of key/value pairs for groupings of
  adjustments, where the key describes the group (e.g. `"A.1 Standard
  Adjustments"`) and the value is another object of key/value pairs
  for that grouping.  In that inner object, the keys are typically the
  numbers from the service menu (`"01"`) and the values are the
  corresponding descriptor.
- **audits**: Same as `adjustments`, but for the game's audits (also
  referred to as "Bookkeeping").
- **game_state**: A collection of memory areas used during a game to store
  the state of the game (e.g., player #, ball #, progressive jackpot value,
  etc.).  See the Game State section for a list of this section's properties.
- **dip_switches**: A special section detailing DIP switch options for the
  game.  See the "DIP Switches" section below for details.

### Game State

The Game State section (`game_state`) contains information about the current
game in progress.

#### Key Fields
This should be considered a priority when mapping a game.

- **scores**: A list of entries representing player scores from the current
    game or the game that just finished.
- **current_player**: A number representing the current player (1-6).  Values 
    of 0 or larger than `player_count` are an indication that there isn't a
    game in progress (i.e., in attract mode).
- **player_count**: Number of players in the current game (1-6), or the game 
    that just finished.
- **current_ball**: Current ball number (typically 1-5).  Values of 0 or
    larger than `ball_count` are an indication that there isn't a game in
    progress.
- **ball_count**: Number of balls per game.
- **extra_balls**: Number of unplayed extra balls for the current player.

#### Extra Information
These fields can provide useful information, but are considered a lower
priority.

- **final_scores**: In the "Game Over" state, Bally AS-2518-35 games store
    the results of the previous game at a separate memory address than the
    scores when a game is in progress.  Use this entry in place of `scores`
    when `game_over` is `true`.
- **credits**: Current number of credits on the game.
- **max_credits**: Maximum number of credits possible on the game.
- **volume**: Current volume setting.  Entry should have a min/max value
    so it's possible to represent the volume as a percentage, and to know
    the valid range for making changes.
- **replay**: Current score needed to achieve a replay.
- **match**: The (typically) 2-digit "match" score from the last game.
- **bonus**: Unmultiplied, end-of-ball bonus for current ball.
- **bonusX**: Multiplier for `bonus`.  There currently isn't a method of
    representing complex bonus amounts (e.g., different mode bonuses, and
    a mix of multiplied and unmultiplied values).
- **eb_on_this_ball**: Number of extra balls the current player earned on
    the current ball.
- **tilt_warnings**: Number of tilt warnings received on the current ball.

The following should use an encoding of `bool`:
- **free_play**: Whether the game is configured for Free Play.
- **game_over**: Whether the game is in progress (false) or over (true).
- **tilted**: Current player has tilted their ball.

### DIP Switches

PinMAME stores DIP Switch values in the last six bytes of the `.nv` file.
The first byte represents SW1 to SW8, with SW1 in the least significant bit.
The second byte is SW9 to SW16, etc.  The fifth and sixth bytes are typically
used for switches on sound boards.  These map files reference them as SW33 to
SW40 and SW41 to SW48.

The `dip_switches` section of the file describes the settings for individual
switches or groups of switches, stored as a dictionary with a key that is
typically the switch number (e.g., "3") or a switch range (e.g., "1-5").

Each DIP switch descriptor has the following properties:
- A `label` describing the option controlled by the switch(es).
- An `encoding` of `dipsw`.
- An `offsets` property to hold a list of switch numbers.
- A `values` property.  The `values` can be a list, or a string that
  references a shared list in the `values` metadata.

The index into the value list is the result of combining switch values
where OFF=0 and ON=1.  The first entry in `offsets` is the most-significant
bit when combining multiple switch values.

Example with entries for a single switch and group of two switches.

| SW1 | Special           |
|-----|:------------------|
| OFF | Awards Replay     |
| ON  | Awards Extra Ball |

| SW2 | SW3 | Maximum Credits |
|-----|-----|:----------------|
| OFF | OFF | 5               |
| OFF | ON  | 10              |
| ON  | OFF | 15              |
| ON  | ON  | 20              |

```json
{
  "1": {
    "label": "Special",
    "offsets": [
      1
    ],
    "values": [
      "Awards Replay",
      "Awards Extra Ball"
    ]
  },
  "2-3": {
    "label": "Maximum Credits",
    "offsets": [
      2,
      3
    ],
    "values": [
      5,
      10,
      15,
      20
    ]
  }
}
```

See `gottlieb/victory.map.json` as a full example of DIP switch documentation.

### Checksums

The objects used for the last two entries in the map are
slightly different from the other descriptors.  They have the required
`start` field, require either an inclusive `end` (preferred) or `length`, and
`label` is optional.  They introduce a new, optional `groupings` key used to
treat a single descriptor as a list of groupings-sized ranges.

(For example, on WPC games, the audits are a series of 6-byte entries, each 
with an 8-bit checksum as the last byte.)

As of file format v0.7, these objects allow for non-adjacent checksums via
a `checksum` field to represent the checksum's address.  The original 
behavior (followed when `checksum` isn't present) is to extract the 
checksum byte from the end of the `start` to `end` range.  If `checksum` is 
present, `start` to `end` describe only the bytes checksummed.

(For example, on Williams System 11 games, the single byte credit field 
has a checksum that appears in a non-adjacent address.)

- **checksum8**: An array of memory regions protected by an 8-bit
  checksum.  The last byte of the range is set so that the low byte from
  the sum of all bytes in the range is `0xFF`.
- **checksum16**: An array of memory regions protected by a 16-bit
  checksum.  The last two bytes of the range are the 16-bit result of
  subtracting all prior bytes in the range from `0xFFFF`.

### Version History
- v0.1: Initial Version
- v0.2: Deprecate `packed` attribute in favor of `nibble`.
- v0.3: Deprecate usage of hex strings for `start`, `end` and `offsets`.
        Add the `null` attribute for entries with `ch` encoding.
- v0.4: Add global `_nibble` to apply to all entries.
- v0.5: Add `dipsw` encoding and `_values` metadata.
- v0.6: Move all top-level metadata attributes other than `_notes` and
        `_fileformat` into a new `_metadata` attribute with the leading
        underscore removed.
        Deprecate `last_game` attribute in favor of `game_state.scores`.
- v0.7: Add `platform` metadata property.
- v0.8: Add `checksum` property to checksum8/checksum16 objects to allow
        for non-adjacent checksums (needed for Credits on System 11).
        Add `bool` encoding and `invert` property.  Rename `attract` to 
        `game_over`; add `final_scores` to `game_state`.
