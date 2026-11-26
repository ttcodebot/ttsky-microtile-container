# Micro tile tests through the container

Each micro tile's own cocotb test, copied unchanged from its repository at the commit the container uses, run on the gate level netlist of the container (plus the four micro tile netlists) with that micro tile selected. [tb_slot.v](tb_slot.v) ties `uio_in` to the select value and exposes the micro tile pins (`clk`, `rst_n`, `ui_in`, `uo_out`) under the names the tests use.

| Slot | Directory | Copied from |
| ---- | --------- | ----------- |
| 0 | `tt_um_pettit_micro/test/` | kdp1965/ttsky26e-um-pettit-micro f3eada4 `test/test.py`, `test/model.py` |
| 1 | `tt_um_MaligayangPasko/test/` | alexandercoabad/MaligayangPasko_micro f72cb64 `test/test.py`, `test/model.py` |
| 2 | `tt_um_pettit_adpcm/test/`, `tools/` | kdp1965/ttsky26e-um-pettit-adpcm 6a6bf8a `test/test.py`, `test/model.py`, `tools/uadpcm.py` |
| 3 | `tt_um_xy_spirograph/test/` | Astr0K/ttsky-xy-spirograph 9a1c0b1 `test/test.py` |

```sh
cp ../../tt_submission/tt_um_micro_tiles_ttsky26e_1.v ../gate_level_netlist.v
make GATES=yes SLOT=0
```
