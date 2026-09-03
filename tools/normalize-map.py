#!/usr/bin/env python3

"""
Script to normalize the nvram map files:
  - One entry per line.
  - Indent with 2 spaces.
  - Convert name of `_note` attribute to `_notes`.

Usage:
    normalize-map.py mapname.map.json
    normalize-map.py *.map.json

File format updates
-------------------
* v0.9:
    - new _metadata.validation

* v0.8:
    - checksum8/checksum16 objects can have a checksum property
    - new 'bool' encoding

* v0.7:
    - add `platform` metadata
    - start/end/offsets hex values no longer deprecated (and are now preferred)

* v0.6:
    - move metadata properties into a separate `_metadata` section

* v0.5:
    - introduce `dipsw` encoding and `_values` metadata property

* v0.4:
    - introduce new `_nibble` property

* v0.3:
    - convert start/end values stored as hex strings to decimal values
    - introduce new `null` attribute for `ch` encoding

* v0.2:
    - remove "packed"=true and replace "packed"=false with "nibble"="low"
"""

import json
import sys
from collections import OrderedDict

# global to hold required file format for last converted file
file_format = 0.0


def minimum_file_format(v):
    global file_format

    if file_format < v:
        file_format = v


def map_convert(pairs):
    global file_format

    result = OrderedDict()
    for k, v in pairs:
        if k == '_note':
            k = '_notes'

        # set minimum file format based on appearance of certain keys
        if k == '_fileformat':
            minimum_file_format(v)
        elif k == 'validation':
            # _metadata.validation added in v0.9
            minimum_file_format(0.9)
        elif k == 'checksum':
            # checksum attribute for checksum8/checksum16 objects added in v0.8
            minimum_file_format(0.8)
        elif k == 'encoding' and v == 'bool':
            minimum_file_format(0.8)
        elif k == 'platform':
            # metadata "platform" introduced in v0.7
            minimum_file_format(0.7)
        elif k == '_nibble':
            # global "_nibble" introduced in v0.4
            minimum_file_format(0.4)
        elif k == 'nibble':
            # "nibble" is only valid in v0.2 and later
            minimum_file_format(0.2)
        elif k == 'null':
            # "null" is only valid in v0.3 and later
            minimum_file_format(0.3)
        elif k == '_values' or (k == 'encoding' and v == 'dipsw'):
            # "_values" appeared in v0.5 along with "dipsw" encoding
            minimum_file_format(0.5)

        if k == 'version' and type(v) is float:
            v = int(v * 10)

        if k == 'packed':
            # as of v0.2, "packed" attribute deprecated in favor of "nibble"
            if not v:
                # replace packed=false with nibble=low
                result['nibble'] = 'low'
                minimum_file_format(0.2)
            # silently remove default packed=true
        else:
            result[k] = v

    return result


def create_metadata(map_data: OrderedDict):
    """
    Move all underscore-prefixed properties (other than `_notes` and `_fileformat`) to
    a new `_metadata` property.

    :param map_data: map to convert (converted in-place)
    :return:
    """
    if '_metadata' not in map_data:
        map_data['_metadata'] = OrderedDict()

    delete_keys = []
    for key, entry in map_data.items():
        if key.startswith('_'):
            if key not in ['_notes', '_fileformat', '_metadata']:
                # remove leading underscore from key when adding to _metadata
                delete_keys.append(key)
                map_data['_metadata'][key[1:]] = entry
        else:
            map_data[key] = entry

    # delete keys moved to _metadata
    for key in delete_keys:
        del map_data[key]

    for entry in ['_metadata', '_fileformat', '_notes']:
        if entry in map_data:
            map_data.move_to_end(entry, last=False)

    # keep version as first property of _metadata
    map_data['_metadata'].move_to_end('version', last=False)


def rename_last_game(map_data: OrderedDict):
    # move last_game into game_state
    if 'last_game' in map_data:
        if 'game_state' not in map_data:
            map_data['game_state'] = OrderedDict()
        map_data['game_state']['scores'] = map_data['last_game']
        for index, entry in enumerate(map_data['game_state']['scores']):
            if 'label' not in entry:
                # make sure entry has a label
                entry['label'] = 'Player %u' % (index + 1)
                entry.move_to_end('label', last=False)
        del map_data['last_game']

        # make sure game_state is at the top of the file
        for entry in ['game_state', '_metadata', '_fileformat', '_notes']:
            if entry in map_data:
                map_data.move_to_end(entry, last=False)


exitcode = 0
for filename in sys.argv[1:]:
    file_format = 0.6       # default to 0.6, first _fileformat with _metadata property
    try:
        data = json.load(open(filename, 'r'), object_pairs_hook=map_convert)
        data['_fileformat'] = file_format
        create_metadata(data)
        rename_last_game(data)
        with open(filename, 'w') as outfile:
            outfile.write(json.dumps(data, indent=2))
            # add trailing newline to match `jq` output
            outfile.write('\n')
    except json.decoder.JSONDecodeError as e:
        print("JSON decode error(s) for %s:\n%s\n" % (filename, str(e)))
        # at least one JSON file was improperly formatted
        exitcode = 1

raise SystemExit(exitcode)
