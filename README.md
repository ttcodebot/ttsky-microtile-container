![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# Micro tiles group 1 (sky130A, TTSKY26e trial)

An experimental Tiny Tapeout 1x1 project that holds four different _micro tiles_: small, separately hardened macros with a reduced interface (`clk`, `rst_n`, `ui_in[7:0]`, `uo_out[7:0]`). `uio[1:0]` selects the active micro tile.

- [Read the documentation for project](docs/info.md)
- The floorplan, the power hand-off and the checks are described on the `main` branch.

## How this container is put together

Each micro tile is built in its own repository (here: branches of https://github.com/ttcodebot/ttsky-microtile) with the micro tile flavour of the Tiny Tapeout GDS action. The container takes the `tt_submission` artifact of each build, the same artifact an ordinary project submits to a shuttle.

1. List the four builds in [microtiles.yaml](microtiles.yaml) (repository and id of the `gds` workflow run), in select order.
2. Run `python assemble.py`. It downloads the artifacts and generates everything that depends on the micro tiles:
   - `macros/`: GDS, LEF and powered netlist of every micro tile, its `commit_id.json` and `pdk.json`, and its sources (for the RTL simulation);
   - `src/project.v` (the mux) and the `MACROS` section of `src/config.json`;
   - `docs/info.md` and `docs/<micro tile>/info.yaml` + `info.md`, the documentation of every micro tile;
   - `subprojects.json`, the list of micro tiles in the format the shuttle repository and the Tiny Tapeout index use for project groups;
   - `test/micro_tiles.mk`, the macro lists for the testbench.
3. Commit and push. The `gds` workflow hardens the container with the stock Tiny Tapeout actions, checks the power connection of every micro tile on the final GDS ([test/trace_power.py](test/trace_power.py)) and runs the stock precheck.
