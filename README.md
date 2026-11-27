![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# Micro tile container for sky130A

An experimental Tiny Tapeout 1x1 project that holds four _micro tiles_: small, separately hardened macros with a reduced interface (`clk`, `rst_n`, `ui_in[7:0]`, `uo_out[7:0]`). `uio[1:0]` selects the active micro tile.

- [Read the documentation for project](docs/info.md)
- Micro tile project: https://github.com/ttcodebot/ttsky-microtile

## Floorplan

The tile is 161.00 x 111.52 um. Each micro tile is 70.38 x 51.68 um.

| Instance | Macro                | Location (um)  | Orientation | Micro tile outline (um) |
| -------- | -------------------- | -------------- | ----------- | ----------------------- |
| `proj1`  | `tt_micro_tile_slot` | (0, 0)         | N           | (0, 0)                  |
| `proj2`  | `tt_micro_tile_slot` | (89.58, 0)     | FN          | (90.62, 0)              |
| `proj3`  | `tt_micro_tile_slot` | (0, 53.04)     | N           | (0, 53.04)              |
| `proj4`  | `tt_micro_tile_slot` | (89.58, 53.04) | FN          | (90.62, 53.04)          |

- The slot macro (`micro_container.py placeholder` in tt-support-tools) is the micro tile outline plus 1.04 um beyond its pin edge for the jumpers; its origin is the micro tile's.
- The right column is mirrored (FN), so all pins face the channel in the middle of the tile.
- DRC by construction: inside a micro tile's outline the container draws nothing on li1-met3 but copies of the pins (and the power vias, inside the power stripes). Each pin is extended straight out of the slot, and the jumper (via3, met4 bridge, via3, met3 landing pad) starts 0.4 um outside it. Container li1/met1/met2/met3 keep 0.17/0.28/0.28/0.4 um (the wide-metal spacing) from every slot outline (`ROUTING_OBSTRUCTIONS`, slot LEF), and the two slots of a column are 1.36 um apart (more than nwell.2a, 1.27 um). So any micro tile that is DRC clean on its own, with its pins and power stripes at the template positions, is DRC clean in the container.
- The mux logic is placed in the channel and in the row above the micro tiles, right below the pins of the container.

## Power

A micro tile brings out `VPWR` and `VGND` on four horizontal met3 stripes. The container has the usual vertical met4 stripes, at a 22.08 um pitch, placed so that every micro tile gets three stripes of each net and the channel one of each. They run right over the micro tiles, and wherever a met4 stripe crosses a met3 stripe of the same net there is a via3 array.

The crossing is orthogonal, so nothing has to be aligned between the container and the micro tiles, and it needs no custom PDN script. The stock LibreLane macro grid connects `PDN_VERTICAL_LAYER` to `PDN_HORIZONTAL_LAYER`, so the configuration sets `PDN_HORIZONTAL_LAYER` to `met3` (the container has no horizontal stripes of its own) and lists the micro tiles in `PDN_MACRO_CONNECTIONS`. See [src/config.json](src/config.json).

## Verification

The container is an ordinary 1x1 project: the `gds` workflow uses the stock Tiny Tapeout actions and the stock precheck.

- LVS (Magic + Netgen) runs with the micro tiles as black boxes: it checks that the `VPWR` and `VGND` pins of every micro tile are on the power nets of the container, not what is inside the micro tile.
- [test/trace_power.py](test/trace_power.py) checks the final GDS without any abstraction, as a step of the `gds` workflow. It follows the metal and vias from the `VPWR` and `VGND` pins of the container, and fails unless they reach every standard cell rail of every micro tile.
- The `lvs-full-gds` branch runs LVS on a layout extracted from the final GDS, transistors of the micro tiles included (`MAGIC_EXT_USE_GDS`, `LVS_INCLUDE_MARCO_NETLISTS`).

## Updating the micro tiles

The hardened views of the micro tiles are in [macros](macros): GDS, LEF, gate level netlist (`.v`), powered netlist (`.pnl.v`) and RTL (`rtl/`). `tt_um_micro_test` comes from the `GDS_logs` artifact of the micro tile project (`runs/wokwi/final`); [macros/rename.py](macros/rename.py) makes the three renamed copies.
