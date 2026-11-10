# SPDX-License-Identifier: Apache-2.0
# Author: Uri Shaked

# This script prepares three more copies of the tt_um_micro_test micro tile under different
# names, so the container can be tested with four distinct macros.
#
# Usage: python rename.py   (run from this directory, needs the klayout Python package)

import klayout.db as pya

SOURCE = "tt_um_micro_test"

with open(f"{SOURCE}.lef", "r") as f:
    lef_data = f.read()
with open(f"{SOURCE}.v", "r") as f:
    nl_data = f.read()
with open(f"{SOURCE}.pnl.v", "r") as f:
    pnl_data = f.read()
with open(f"rtl/{SOURCE}.v", "r") as f:
    rtl_data = f.read()

for i in range(2, 5):
    name = f"tt_um_micro_proj{i}"

    layout = pya.Layout()
    layout.read(f"{SOURCE}.gds")
    top_cell = layout.top_cell()
    assert top_cell.name == SOURCE
    top_cell.name = name
    layout.write(f"{name}.gds")

    with open(f"{name}.lef", "w") as f:
        f.write(lef_data.replace(SOURCE, name))
    with open(f"{name}.v", "w") as f:
        f.write(nl_data.replace(SOURCE, name))
    with open(f"{name}.pnl.v", "w") as f:
        f.write(pnl_data.replace(SOURCE, name))
    with open(f"rtl/{name}.v", "w") as f:
        f.write(rtl_data.replace(SOURCE, name))
