## How it works

A synthetic design used to measure how much logic fits in a micro tile: five stages of four flip-flops with an adder and mixing logic, plus five extra
flip-flops. It has no use other than filling the micro tile.

## How to test

Hold `rst_n` low for a clock cycle, then clock it: `uo_out` shows a pseudo random sequence that depends on `ui_in`.

## External hardware

None
