<!---
This file is used to generate your project datasheet.
-->

## How it works

A 640x480 @ 60 Hz VGA picture (25.175 MHz pixel clock, 2 bits per colour channel, TinyVGA Pmod
pinout) drawn with combinational logic from the pixel counters, no frame buffer. The design is
for the **micro tile** (`tiles: "micro"`: clk, rst_n, 8 inputs, 8 outputs, about 300 gates or 80
flip-flops). Hardened with the Tiny Tapeout flow it is 34 flip-flops and 339 cells in total
(excluding fill and tap cells), at 90.2 % utilisation, with the DRC, the 17 precheck tests and the
gate-level test all passing.

The picture is an 80 x 60 grid of 8-pixel cells:

- **Tree**: four stacked tiers of a fir tree (eight rows each, rows 16..47). The half-width grows
  one cell a row, and each tier starts four cells narrower than the last row of the tier above,
  so the tiers look like skirts. The edge cells are darker green, the needles are striped, and
  the brown trunk is four cells wide.
- **Star**: a small diamond on top (rows 12..15) that blinks through four colours (dark red, red,
  yellow, orange), changing about every 0.27 s.
- **Lights**: every fourth cell inside the tree is a light whose colour cycles
  (red, yellow, white, cyan) with the frame count.
- **Snow**: 4x4-pixel flakes fall in the night sky, one in every fourth 8-pixel column, each
  column with its own phase, one cell every four frames, wrapping every 128 pixels. The ground
  (rows 52..59) is snow.
- **Greeting**: **MALIGAYANG PASKO!** in red (or green, see the inputs) on the snow: 17 characters of a 3x5-cell font with a
  5-cell-wide M, one cell between characters.
- Nothing is stored: the picture comes from the counters, a tier rule, a star rule, a glyph table
  and a few XORs.

Inputs (all low, or left unconnected, gives the plain scene):

| Pin | Name | Effect when high |
|-----|------|------------------|
| `ui[0]` | PAUSE | freezes the frame counter, and with it the snow, the lights and the star |
| `ui[1]` | SNOW_OFF | hides the falling snow |
| `ui[2]` | SKY_BLACK | black sky instead of dark blue |
| `ui[3]` | TEXT_GREEN | greeting in green instead of red |
| `ui[7:4]` | unused | |

The outputs are registered, so the picture is one clock late relative to the sync pulses.

The earlier 1x1 version of this project (full scene, `MERRY CHRISTMAS!` and `MALIGAYANG PASKO!` in an
8x8 font, 523 lines of Verilog) does not fit a micro tile; this version keeps the tree, the lights, the
star, the snow and the greeting in a smaller font.

## How to test

Connect a TinyVGA PMOD and a VGA monitor, apply a 25.175 MHz clock and release reset.
A Christmas tree with a blinking star, falling snow and the greeting on the snow should appear.
Set `ui[1]` high to hide the snow, `ui[2]` for a black sky, `ui[3]` for a green greeting, and `ui[0]` to freeze the animation.

## External hardware

TinyVGA PMOD (https://github.com/mole99/tiny-vga) and a VGA monitor.
