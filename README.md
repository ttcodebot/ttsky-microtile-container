![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# Micro tiles TTSKY26e group 1 (sky130A)

A Tiny Tapeout 1x1 project that holds four community _micro tiles_ submitted for TTSKY26e: small, separately hardened macros with a reduced interface (`clk`, `rst_n`, `ui_in[7:0]`, `uo_out[7:0]`). `uio_in[1:0]` selects the active micro tile.

| `uio_in[1:0]` | Micro tile | Repository | Commit |
| ------------- | ---------- | ---------- | ------ |
| 0 | Micro Munch | https://github.com/kdp1965/ttsky26e-um-pettit-micro | f3eada4 |
| 1 | Maligayang Pasko! | https://github.com/alexandercoabad/MaligayangPasko_micro | f72cb64 |
| 2 | Micro ADPCM | https://github.com/kdp1965/ttsky26e-um-pettit-adpcm | 6a6bf8a |
| 3 | XY Spirograph | https://github.com/Astr0K/ttsky-xy-spirograph | 9a1c0b1 |

- [Read the documentation for project](docs/info.md)
- The floorplan, the power hand-off and the checks are described on the `main` branch.

## How this container is put together

Each micro tile is built in its own repository with the stock Tiny Tapeout GDS action (`tiles: "micro"` in its `info.yaml`). The container takes the `tt_submission` artifact of each build, the same artifact an ordinary project submits to a shuttle.

1. List the four builds in [microtiles.yaml](microtiles.yaml) (repository and id of the `gds` workflow run), in select order.
2. Run `python assemble.py`. It downloads the artifacts and generates everything that depends on the micro tiles:
   - `macros/`: GDS, LEF and powered netlist of every micro tile, its `commit_id.json` and `pdk.json`, and its sources (for the RTL simulation);
   - `src/project.v` (the mux) and the `MACROS` section of `src/config.json`;
   - `docs/info.md` and `docs/<micro tile>/`, the documentation of every micro tile;
   - `subprojects.json`, the list of micro tiles in the format the shuttle repository and the Tiny Tapeout index use for project groups;
   - `test/micro_tiles.mk`, the macro lists for the testbench.
3. Commit and push. The `gds` workflow hardens the container with the stock Tiny Tapeout actions, checks the power connection of every micro tile on the final GDS ([test/trace_power.py](test/trace_power.py)), runs the stock precheck and the gate level tests.

## Tests

- [test/test.py](test/test.py) (stock `test` and `gl_test` workflows): the container, in the gate level test its netlist plus the four micro tile netlists, against a reference made of the container RTL and the RTL of each micro tile from its repository. Every clock, seeded random inputs and resets: each micro tile on its own, random selection changes, and isolation (the outputs of the micro tiles that are not selected are forced to random values).
- [test/designer](test/designer) (`designer_gl_test` job): each micro tile's own cocotb test, unchanged, run through the container gate level netlist with that micro tile selected.
