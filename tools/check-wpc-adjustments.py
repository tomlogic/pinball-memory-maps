#!/usr/bin/env python3
"""Check the adjustments of every Williams WPC map against the WPC adjustment layout.

WPC keeps each adjustment as a 16-bit word, in table order, after the
"Adjustments" checksum16 block start.  So all 2-byte adjustments start on one
parity, and all 1-byte adjustments (the word's low byte) sit on the other.
The check also makes sure that each adjustment is inside the block, that no
two adjustments overlap, and that a default is inside min and max.  The items
in OUTSIDE_BLOCK are stored outside the block, so the block and parity rules
do not apply to them.

Usage: tools/check-wpc-adjustments.py [map.json ...]
With no arguments, it checks maps/williams/wpc/*.map.json.  Exit status 1
when a map fails.
"""

import glob
import json
import os
import sys

# (map file, section, item) of adjustments that the ROM stores outside the block.
OUTSIDE_BLOCK = {
    ("rs_l6c.map.json", "A.2 Feature Adjustments", "27"),
    ("rs_l6c.map.json", "A.2 Feature Adjustments", "28"),
}


def item_size(item):
    if item.get("encoding") == "enum":
        return 1
    return item.get("length", 1)


def check(path):
    errors = []
    with open(path) as f:
        m = json.load(f)
    adjustments = m.get("adjustments")
    if not adjustments:
        return errors
    block = next((c for c in m.get("checksum16", []) if c.get("label") == "Adjustments"), None)
    if block is None:
        return [f"{path}: has adjustments but no checksum16 block labeled Adjustments"]
    word_parity = (block["start"] + 2) % 2
    used = {}
    for section, items in adjustments.items():
        for code, item in items.items():
            where = f"{path}: {section} {code} {item.get('label', '')} @{item['start']}"
            size = item_size(item)
            want = word_parity if size == 2 else 1 - word_parity
            end = item["start"] + size - 1
            if (os.path.basename(path), section, code) not in OUTSIDE_BLOCK:
                if item["start"] % 2 != want:
                    errors.append(f"{where}: a {size}-byte adjustment must start on an "
                                  f"{'odd' if want else 'even'} address")
                if item["start"] < block["start"] or end > block["end"]:
                    errors.append(f"{where}: outside the Adjustments block {block['start']}-{block['end']}")
            for a in range(item["start"], end + 1):
                if a in used:
                    errors.append(f"{where}: overlaps {used[a]}")
                    break
                used[a] = f"{section} {code}"
            lo, hi, d = item.get("min"), item.get("max"), item.get("default")
            if None not in (lo, hi, d) and not lo <= d <= hi:
                errors.append(f"{where}: default {d} is outside {lo}-{hi}")
    return errors


def main(paths):
    paths = paths or sorted(glob.glob("maps/williams/wpc/*.map.json"))
    errors = [e for p in paths for e in check(p)]
    for e in errors:
        print(e)
    print(f"Checked {len(paths)} WPC maps: {len(errors)} problem(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
