# SPDX-License-Identifier: Apache-2.0

"""Assemble a micro tile container from micro tile CI builds (prototype of the container generator).

Usage: python assemble.py   (run from the root of the container repo; needs the gh CLI and PyYAML)

Input: microtiles.yaml

    top_module: tt_um_micro_tiles_group_1
    title: "Micro tiles group 1"
    shuttle: ttsky26e
    micro_tiles:           # in select order (uio_in[1:0] = 0, 1, 2, 3)
      - repo: owner/name
        run: 123456        # id of the gds workflow run that built the micro tile

For every micro tile it downloads the `tt_submission` artifact of that run (the same artifact a
1x1 project submits) and writes:

    macros/<macro>.gds, .lef, .pnl.v      hardened views (the .v of a sky130 submission is the powered netlist)
    macros/<macro>.commit_id.json, .pdk.json   provenance
    macros/rtl/<macro>/                   sources, for the RTL simulation of the container
    docs/<macro>/info.yaml, info.md       the micro tile's own documentation
    docs/info.md                          list of the micro tiles
    subprojects.json                      what the shuttle repo needs next to the container
    src/project.v, src/config.json        mux and macro placement (config.json: MACROS only)
    info.yaml                             top module, title, source list
    test/micro_tiles.mk                   macro and source lists for the testbench
"""

import json
import pathlib
import re
import shutil
import subprocess
import tempfile

import yaml

SLOTS = [  # instance name, location, orientation
    ("proj1", [0, 0], "N"),
    ("proj2", [90.62, 0], "FN"),
    ("proj3", [0, 51.68], "N"),
    ("proj4", [90.62, 51.68], "FN"),
]
PIN_KEYS = [f"{bus}[{i}]" for bus in ("ui", "uo") for i in range(8)]

spec = yaml.safe_load(open("microtiles.yaml"))
top = spec["top_module"]
tiles = spec["micro_tiles"]
assert len(tiles) == len(SLOTS), "this container holds exactly four micro tiles"

macros_dir = pathlib.Path("macros")
shutil.rmtree(macros_dir, ignore_errors=True)
(macros_dir / "rtl").mkdir(parents=True)
for old in pathlib.Path("docs").iterdir():
    if old.is_dir():
        shutil.rmtree(old)

entries = []
for index, tile in enumerate(tiles):
    tmp = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(
        ["gh", "run", "download", str(tile["run"]), "-R", tile["repo"], "-n", "tt_submission", "-D", str(tmp)],
        check=True,
    )
    info = yaml.safe_load(open(tmp / "info.yaml"))
    project = info["project"]
    macro = project.get("top_module") or f"tt_um_wokwi_{project['wokwi_id']}"
    assert project["tiles"] == "micro", f"{macro} is not a micro tile"
    assert macro != top and macro not in [e["macro"] for e in entries], f"duplicate macro {macro}"
    sub = tmp / "tt_submission"
    commit = json.load(open(sub / "commit_id.json"))
    pdk = json.load(open(sub / "pdk.json"))

    shutil.copy(sub / f"{macro}.gds", macros_dir / f"{macro}.gds")
    shutil.copy(sub / f"{macro}.lef", macros_dir / f"{macro}.lef")
    shutil.copy(sub / f"{macro}.v", macros_dir / f"{macro}.pnl.v")
    shutil.copy(sub / "commit_id.json", macros_dir / f"{macro}.commit_id.json")
    shutil.copy(sub / "pdk.json", macros_dir / f"{macro}.pdk.json")
    rtl_dir = macros_dir / "rtl" / macro
    rtl_dir.mkdir()
    sources = project.get("source_files") or [f"{macro}.v", "cells.v"]
    for source in sources:
        shutil.copy(tmp / "src" / source, rtl_dir / pathlib.Path(source).name)

    docs_dir = pathlib.Path("docs") / macro
    shutil.copytree(tmp / "docs", docs_dir)
    shutil.copy(tmp / "info.yaml", docs_dir / "info.yaml")

    pinout = info.get("pinout", {})
    entries.append(
        {
            "index": index,
            "macro": macro,
            "sources": [pathlib.Path(s).name for s in sources],
            "pdk": pdk,
            "sub": {
                "macro": macro,
                "title": project["title"],
                "author": project["author"],
                "discord": project.get("discord", ""),
                "description": project["description"],
                "clock_hz": project.get("clock_hz", 0),
                "repo": commit["repo"],
                "commit": commit["commit"],
                "pinout": {k: pinout.get(k, "") for k in PIN_KEYS},
            },
        }
    )
    shutil.rmtree(tmp)

flows = {(e["pdk"]["FLOW_VERSION"], e["pdk"]["PDK_VERSION"]) for e in entries}
assert len(flows) == 1, f"micro tiles were built with different flows: {flows}"

# subprojects.json, in the format of the TTIHP25a subtile groups
with open("subprojects.json", "w") as f:
    json.dump(
        {"shuttle": spec["shuttle"], "index_bits": 2, "projects": {str(e["index"]): e["sub"] for e in entries}},
        f,
        indent=2,
    )
    f.write("\n")

# docs/info.md
rows = "\n".join(
    f"| {e['index']} | [{e['sub']['title']}]({e['macro']}/info.md) | {e['sub']['author']} | `{e['macro']}` |" for e in entries
)


def clock_text(hz):
    if not hz:
        return "not applicable"
    return f"{hz / 1e6:g} MHz" if hz >= 1e6 else f"{hz / 1e3:g} kHz"


def tile_section(e):
    sub = e["sub"]
    repo = sub["repo"]
    commit = sub["commit"]
    pins = "\n".join(
        f"| {i} | {sub['pinout'][f'ui[{i}]'] or '-'} | {sub['pinout'][f'uo[{i}]'] or '-'} |" for i in range(8)
    )
    return f"""### {e['index']}: {sub['title']}

- Select: `uio_in[1:0] = {e['index']}` ({e['index']:02b})
- Author: {sub['author']}
- Macro: `{e['macro']}`
- Repository: <{repo}>, commit [`{commit[:7]}`]({repo}/tree/{commit})
- Clock: {clock_text(sub['clock_hz'])}
- {sub['description']}

| Pin | `ui_in` | `uo_out` |
| --- | ------- | -------- |
{pins}

Full documentation: [{e['macro']}/info.md]({e['macro']}/info.md)
"""


sections = "\n".join(tile_section(e) for e in entries)
pathlib.Path("docs/info.md").write_text(
    f"""## How it works

Four micro tile projects, combined into a single Tiny Tapeout tile.

Each micro tile is a separately hardened 70.38 x 51.68 um macro with a reduced interface: `clk`, `rst_n`, `ui_in[7:0]` and `uo_out[7:0]`. The container places four of them and connects the tile's pins to the one selected with `uio_in[1:0]`. The other micro tiles get no clock, no inputs and a low `rst_n`, so they stop. `uio` are always inputs (`uio_oe = 0`); `uio_in[7:2]` are not used.

| `uio_in[1:0]` | Micro tile | Author | Macro |
| ------------- | ---------- | ------ | ----- |
{rows}

## Micro tiles

{sections}
## How to test

Set `uio_in[1:0]` to the select value of a micro tile, then follow the instructions of that micro tile: `ui_in`, `uo_out`, `clk` and `rst_n` are its pins. Set the clock to the frequency that micro tile wants. A micro tile that is selected again continues from where it stopped (its clock was stopped), so reset it after selecting it.

## External hardware

See each micro tile.
"""
)

# src/project.v
instances = "\n".join(
    f"""  {e['macro']} {SLOTS[e['index']][0]} (
      .rst_n (sel == {e['index']} ? rst_n : 1'b0),
      .clk   (sel == {e['index']} ? clk : 1'b0),
      .ui_in (sel == {e['index']} ? ui_in : 8'h00),
      .uo_out(uo_out_proj[{e['index']}])
  );
"""
    for e in entries
)
pathlib.Path("src/project.v").write_text(
    f"""/*
 * Copyright (c) 2024 Tiny Tapeout
 * SPDX-License-Identifier: Apache-2.0
 *
 * Generated by assemble.py from microtiles.yaml, do not edit.
 */

`default_nettype none

// Container for four micro tile projects. uio_in[1:0] selects the active one:
// only the selected micro tile gets clk, rst_n and ui_in, and drives uo_out.
module {top} (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire [1:0] sel = uio_in[1:0];
  wire [7:0] uo_out_proj[3:0];

  assign uo_out  = uo_out_proj[sel];
  assign uio_out = 0;
  assign uio_oe  = 0;

{instances}
  // List all unused inputs to prevent warnings
  wire _unused = &{{ena, uio_in[7:2], 1'b0}};

endmodule
"""
)

# src/config.json: replace the MACROS section, keep everything else (the file has repeated "//" keys)
macros = {
    e["macro"]: {
        "instances": {SLOTS[e["index"]][0]: {"location": SLOTS[e["index"]][1], "orientation": SLOTS[e["index"]][2]}},
        "gds": [f"dir::../macros/{e['macro']}.gds"],
        "lef": [f"dir::../macros/{e['macro']}.lef"],
        "pnl": [f"dir::../macros/{e['macro']}.pnl.v"],
    }
    for e in entries
}
macros_text = json.dumps(macros, indent=2).replace("\n", "\n  ")
config = pathlib.Path("src/config.json")
text = config.read_text()
text, count = re.subn(r'"MACROS": \{.*?\n  \},\n', lambda m: f'"MACROS": {macros_text},\n', text, flags=re.S)
assert count == 1
config.write_text(text)

# info.yaml
info_path = pathlib.Path("info.yaml")
text = info_path.read_text()
text = re.sub(r'  title: .*', f'  title:        "{spec["title"]}"', text, count=1)
text = re.sub(r'  top_module: .*', f'  top_module:  "{top}"', text, count=1)
info_path.write_text(text)

# test/micro_tiles.mk
rtl = []
seen = set()
for e in entries:
    for source in e["sources"]:
        # Wokwi projects all come with the same cells.v
        if source == "cells.v" and source in seen:
            continue
        seen.add(source)
        rtl.append(f"$(MACROS_DIR)/rtl/{e['macro']}/{source}")
pathlib.Path("test/micro_tiles.mk").write_text(
    "# Generated by assemble.py from microtiles.yaml, do not edit.\n"
    f"TOP_MODULE = {top}\n"
    f"MACROS = {' '.join(e['macro'] for e in entries)}\n"
    f"MACROS_RTL = {' '.join(rtl)}\n"
)
print("assembled", top, "from", ", ".join(e["macro"] for e in entries))
