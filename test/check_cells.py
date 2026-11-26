# SPDX-License-Identifier: Apache-2.0

"""Cell name check for a micro tile container, on the final GDS.

The shuttle merges every project GDS into one layout, where cells are shared by name. When Magic
writes the container, it keeps each micro tile's GDS as it is but renames the standard cells inside
it with a short prefix per macro file (e.g. A2_sky130_fd_sc_hd__inv_1), so that they do not clash
with the container's own copies. This fails unless:
  - the container GDS has exactly one top cell, the container;
  - every cell is the container, one of the micro tile top cells, a PDK standard cell
    (sky130_fd_sc_hd__*), or a prefixed copy of one (<prefix>_sky130_fd_sc_hd__*), each prefix used
    under one micro tile only (so no micro tile brings a cell of its own that could clash with
    another project or another micro tile);
  - every standard cell and every prefixed copy is geometrically identical to the PDK cell (XOR of
    all layers is empty), so that sharing it by name with the rest of the chip changes nothing.

Usage: check_cells.py <container gds> <container top> <pdk std cell gds> <micro tile top> [<micro tile top> ...]
"""

import re
import sys

import klayout.db as pya

gds, top_name, pdk_gds, *micro = sys.argv[1:]
STD_PREFIX = "sky130_fd_sc_hd__"

layout = pya.Layout()
layout.read(gds)
pdk = pya.Layout()
pdk.read(pdk_gds)
ok = True

tops = [c.name for c in layout.top_cells()]
print(f"top cells: {tops}")
if tops != [top_name]:
    print(f"ERROR: expected one top cell {top_name}")
    ok = False

names = [c.name for c in layout.each_cell()]
if len(names) != len(set(names)):
    print("ERROR: duplicate cell names")
    ok = False
COPY = re.compile(r"^([A-Za-z0-9]+)_(" + STD_PREFIX + r".*)$")
std = sorted(n for n in names if n.startswith(STD_PREFIX))
copies = sorted(n for n in names if COPY.match(n))
other = sorted(n for n in names if not n.startswith(STD_PREFIX) and not COPY.match(n))
prefixes = sorted({COPY.match(n).group(1) for n in copies})
print(f"{len(names)} cells: {len(std)} standard cells, {len(copies)} prefixed copies (prefixes {prefixes}), others: {other}")
if sorted(other) != sorted([top_name, *micro]):
    print(f"ERROR: the other cells should be exactly {sorted([top_name, *micro])}")
    ok = False

# Which micro tile uses which standard cell (for the report)
users = {}
for inst_top in [top_name, *micro]:
    cell = layout.cell(inst_top)
    if cell is None:
        continue
    for child in cell.each_child_cell():
        users.setdefault(layout.cell(child).name, set()).add(inst_top)


def flat_region(ly, cell, layer_index):
    return pya.Region(cell.begin_shapes_rec(layer_index)).merged()


# Each prefix belongs to one micro tile
for inst_top in micro:
    cell = layout.cell(inst_top)
    if cell is None:
        print(f"ERROR: micro tile {inst_top} not found")
        ok = False
        continue
    used = sorted({COPY.match(layout.cell(c).name).group(1) for c in cell.each_child_cell() if COPY.match(layout.cell(c).name)})
    print(f"{inst_top}: {len(list(cell.each_child_cell()))} child cells, prefixes {used}")
owners = {}
for inst_top in micro:
    cell = layout.cell(inst_top)
    for c in cell.each_child_cell() if cell else []:
        m = COPY.match(layout.cell(c).name)
        if m:
            owners.setdefault(m.group(1), set()).add(inst_top)
for prefix, who in sorted(owners.items()):
    if len(who) != 1:
        print(f"ERROR: prefix {prefix} is used by {sorted(who)}")
        ok = False
for n in copies:
    if COPY.match(n).group(1) not in owners:
        print(f"ERROR: {n} is not used by a micro tile")
        ok = False

different = []
for name in std + copies:
    ref = pdk.cell(COPY.match(name).group(2) if COPY.match(name) else name)
    if ref is None:
        print(f"ERROR: {name} is not a PDK standard cell")
        ok = False
        continue
    cell = layout.cell(name)
    layers = set()
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        layers.add((info.layer, info.datatype))
    for li in pdk.layer_indexes():
        info = pdk.get_info(li)
        layers.add((info.layer, info.datatype))
    for layer, datatype in sorted(layers):
        a_li = layout.find_layer(layer, datatype)
        b_li = pdk.find_layer(layer, datatype)
        a = flat_region(layout, cell, a_li) if a_li is not None else pya.Region()
        b = flat_region(pdk, ref, b_li) if b_li is not None else pya.Region()
        if layout.dbu != pdk.dbu:
            b = b.transformed(pya.ICplxTrans(pdk.dbu / layout.dbu))
        if not (a ^ b).is_empty():
            different.append(f"{name} layer {layer}/{datatype} (used by {sorted(users.get(name, []))})")
            break

print(f"{len(std) + len(copies)} standard cells and copies compared with {pdk_gds}: {len(different)} differ")
for d in different:
    print(f"ERROR: {d}")
ok &= not different

print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
