## How it works

Four micro tile projects, combined into a single Tiny Tapeout tile.

Each micro tile is a separately hardened 70.38 x 51.68 um macro with a reduced interface: `clk`, `rst_n`, `ui_in[7:0]` and `uo_out[7:0]`. The container places four of them, and muxes the tile's pins to the selected one. The other micro tiles get no clock and are held in reset.

| `uio[1:0]` | Micro tile | Author | Macro |
| ---------- | ---------- | ------ | ----- |
| 0 | [Micro tile test (sky130A)](tt_um_micro_test/info.md) | Tiny Tapeout | `tt_um_micro_test` |
| 1 | [Micro tile capacity test](tt_um_micro_dense/info.md) | Tiny Tapeout | `tt_um_micro_dense` |
| 2 | [Wokwi micro tile 0497](tt_um_wokwi_463380823859050497/info.md) | Tiny Tapeout | `tt_um_wokwi_463380823859050497` |
| 3 | [Wokwi micro tile 7361](tt_um_wokwi_459285910800527361/info.md) | Tiny Tapeout | `tt_um_wokwi_459285910800527361` |

## How to test

Select a micro tile with `uio[1:0]`, then follow the instructions of that micro tile.

## External hardware

None
