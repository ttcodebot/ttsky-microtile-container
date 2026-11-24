## How it works

Four micro tile projects with 3 uio inputs and 3 uio outputs each, combined into a single Tiny Tapeout tile.

`uio_in[1:0]` selects the active micro tile. It gets `clk`, `rst_n`, `ui_in` and `uio_in[4:2]`, and drives `uo_out` and `uio_out[7:5]` (always outputs). The others get no clock and are held in reset.

## How to test

Select a micro tile with `uio[1:0]`, then follow the instructions of that micro tile.

## External hardware

None
