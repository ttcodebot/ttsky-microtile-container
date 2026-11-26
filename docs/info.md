## How it works

Four micro tile projects, combined into a single Tiny Tapeout tile.

Each micro tile is a separately hardened 70.38 x 51.68 um macro with a reduced interface: `clk`, `rst_n`, `ui_in[7:0]` and `uo_out[7:0]`. The container places four of them and connects the tile's pins to the one selected with `uio_in[1:0]`. The other micro tiles get no clock, no inputs and a low `rst_n`, so they stop. `uio` are always inputs (`uio_oe = 0`); `uio_in[7:2]` are not used.

| `uio_in[1:0]` | Micro tile | Author | Macro |
| ------------- | ---------- | ------ | ----- |
| 0 | [Micro Munch (VGA demo in a micro tile)](tt_um_pettit_micro/info.md) | Ken Pettit | `tt_um_pettit_micro` |
| 1 | [Maligayang Pasko! (Christmas tree in a micro tile)](tt_um_MaligayangPasko/info.md) | Alexander Co Abad | `tt_um_MaligayangPasko` |
| 2 | [Micro ADPCM (streaming audio decoder in a micro tile)](tt_um_pettit_adpcm/info.md) | Ken Pettit | `tt_um_pettit_adpcm` |
| 3 | [XY Spirograph](tt_um_xy_spirograph/info.md) | Luis Xavier Jauregui de la Rosa | `tt_um_xy_spirograph` |

## Micro tiles

### 0: Micro Munch (VGA demo in a micro tile)

- Select: `uio_in[1:0] = 0` (00)
- Author: Ken Pettit
- Macro: `tt_um_pettit_micro`
- Repository: <https://github.com/kdp1965/ttsky26e-um-pettit-micro>, commit [`f3eada4`](https://github.com/kdp1965/ttsky26e-um-pettit-micro/tree/f3eada4402ffa58e3f15b4e383f3de742fb19516)
- Clock: 25.175 MHz
- Eight scenes of munching squares and Sierpinski carpets on VGA from 39 flops

| Pin | `ui_in` | `uo_out` |
| --- | ------- | -------- |
| 0 | SCENE[0] | R1 |
| 1 | SCENE[1] | G1 |
| 2 | SCENE[2] (Sierpinski mask) | B1 |
| 3 | HOLD (stop stepping through the scenes) | VSYNC |
| 4 | NO_DITHER | R0 |
| 5 | PAUSE | G0 |
| 6 | - | B0 |
| 7 | - | HSYNC |

Full documentation: [tt_um_pettit_micro/info.md](tt_um_pettit_micro/info.md)

### 1: Maligayang Pasko! (Christmas tree in a micro tile)

- Select: `uio_in[1:0] = 1` (01)
- Author: Alexander Co Abad
- Macro: `tt_um_MaligayangPasko`
- Repository: <https://github.com/alexandercoabad/MaligayangPasko_micro>, commit [`f72cb64`](https://github.com/alexandercoabad/MaligayangPasko_micro/tree/f72cb64a2e6fd89058bffdf5468fa2e9af0f7183)
- Clock: 25.175 MHz
- VGA pixel-art Christmas tree with a blinking star, colour-cycling lights and the greeting MALIGAYANG PASKO!, in a micro tile

| Pin | `ui_in` | `uo_out` |
| --- | ------- | -------- |
| 0 | PAUSE (freeze snow, lights and star) | R1 |
| 1 | SNOW_OFF (hide the falling snow) | G1 |
| 2 | SKY_BLACK (black sky instead of dark blue) | B1 |
| 3 | TEXT_GREEN (green greeting instead of red) | VSync |
| 4 | - | R0 |
| 5 | - | G0 |
| 6 | - | B0 |
| 7 | - | HSync |

Full documentation: [tt_um_MaligayangPasko/info.md](tt_um_MaligayangPasko/info.md)

### 2: Micro ADPCM (streaming audio decoder in a micro tile)

- Select: `uio_in[1:0] = 2` (10)
- Author: Ken Pettit
- Macro: `tt_um_pettit_adpcm`
- Repository: <https://github.com/kdp1965/ttsky26e-um-pettit-adpcm>, commit [`6a6bf8a`](https://github.com/kdp1965/ttsky26e-um-pettit-adpcm/tree/6a6bf8acfcbec1eb1ebf71ea4518a915047d021c)
- Clock: 32 MHz
- A bit-serial 4-bit ADPCM decoder with 1 MHz PWM, fed by the host one code a sample

| Pin | `ui_in` | `uo_out` |
| --- | ------- | -------- |
| 0 | CODE[0] | DUTY[0] |
| 1 | CODE[1] | DUTY[1] |
| 2 | CODE[2] | DUTY[2] |
| 3 | CODE[3] (sign) | DUTY[3] |
| 4 | STROBE (rising edge: a new code) | DUTY[4] |
| 5 | - | BUSY |
| 6 | - | PWM audio, inverted |
| 7 | - | PWM audio (1 MHz) |

Full documentation: [tt_um_pettit_adpcm/info.md](tt_um_pettit_adpcm/info.md)

### 3: XY Spirograph

- Select: `uio_in[1:0] = 3` (11)
- Author: Luis Xavier Jauregui de la Rosa
- Macro: `tt_um_xy_spirograph`
- Repository: <https://github.com/Astr0K/ttsky-xy-spirograph>, commit [`9a1c0b1`](https://github.com/Astr0K/ttsky-xy-spirograph/tree/9a1c0b1e17c80be9323680ab5453e0334013f07e)
- Clock: 64 kHz
- Draws four selectable patterns on an XY oscilloscope using two external 4-bit R-2R DACs.

| Pin | `ui_in` | `uo_out` |
| --- | ------- | -------- |
| 0 | Pattern select bit 0 (LSB) | X DAC bit 0 (LSB) |
| 1 | Pattern select bit 1 (MSB) | X DAC bit 1 |
| 2 | - | X DAC bit 2 |
| 3 | - | X DAC bit 3 (MSB) |
| 4 | - | Y DAC bit 0 (LSB) |
| 5 | - | Y DAC bit 1 |
| 6 | - | Y DAC bit 2 |
| 7 | - | Y DAC bit 3 (MSB) |

Full documentation: [tt_um_xy_spirograph/info.md](tt_um_xy_spirograph/info.md)

## How to test

Set `uio_in[1:0]` to the select value of a micro tile, then follow the instructions of that micro tile: `ui_in`, `uo_out`, `clk` and `rst_n` are its pins. Set the clock to the frequency that micro tile wants. A micro tile that is selected again continues from where it stopped (its clock was stopped), so reset it after selecting it.

## External hardware

See each micro tile.
