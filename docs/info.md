<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Four micro tile projects, combined into a single Tiny Tapeout tile.

Each micro tile is a separately hardened 70.38 x 51.68 um macro with a reduced interface: `clk`, `rst_n`, `ui_in[7:0]` and `uo_out[7:0]`. The container places four of them, and muxes the tile's pins to the selected one. The other micro tiles get no clock and are held in reset.

### Selecting the active project

Use `uio[1:0]` to select the active micro tile project.

| `uio[1:0]` | Micro tile          |
| ---------- | ------------------- |
| 0          | `tt_um_micro_test`  |
| 1          | `tt_um_micro_proj2` |
| 2          | `tt_um_micro_proj3` |
| 3          | `tt_um_micro_proj4` |

### The micro tiles

All four micro tiles are copies of the micro tile test module (https://github.com/ttcodebot/ttsky-microtile). It has two modes of operation:

1. Mirroring the input pins to the output pins (when `rst_n` is low).
2. Outputting an 8-bit counter on the output pins (when `rst_n` is high).

## How to test

1. Select a micro tile with `uio[1:0]`.
2. Set `rst_n` low and observe that the input pins (`ui_in`) are output on the output pins (`uo_out`).
3. Set `rst_n` high and observe that the counter is output on the output pins (`uo_out`).

## External hardware

None
