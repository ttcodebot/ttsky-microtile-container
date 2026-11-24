# SPDX-License-Identifier: Apache-2.0

"""Assemble a micro tile container whose micro tiles have N uio pins (tiles: micro_uio<N>).

Usage: python assemble_uio.py <spec.yaml>   (run from the root of the container repo)

    top_module: tt_um_micro_tiles_uio6
    title: "Micro tiles with 6 uio pins"
    shuttle: ttsky26e
    pdk: sky130A
    slots: [[0, 0], [90.62, 0], [0, 51.68], [90.62, 51.68]]   # proj1..proj4; the right column is mirrored
    micro_tiles:            # in select order (uio_in[1:0] = 0, 1, 2, 3)
      - repo: owner/name    # a CI build: the tt_submission artifact of gds run <run>
        run: 123456
      - local: /path/to/project   # or a local build: runs/wokwi/final of that project dir

The container gives the selected micro tile clk, rst_n, ui_in and uio_in[2+N-1:2], and muxes its uo_out,
uio_out and uio_oe to uo_out, uio_out[2+N-1:2] and uio_oe[2+N-1:2]. uio[1:0] stay inputs: they select.
Micro tiles with fixed directions (tiles: micro_i<A>o<B>, no uio_oe) get uio_in[A+1:2]; their uio_out drives
uio_out[A+B+1:A+2], and the container's uio_oe is constant (1 on those B pins).
Writes macros/, src/project.v, the MACROS section of src/config.json, info.yaml, test/micro_tiles.mk and
test/micro_tiles.json (N and the loopback constant K of every micro tile, for test.py).
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

spec = yaml.safe_load(open(sys.argv[1]))
top = spec["top_module"]
tiles = spec["micro_tiles"]
slots = spec["slots"]
pdk_name = spec.get("pdk", "sky130A")
netlist_kind = "pnl" if pdk_name == "sky130A" else "nl"
assert len(tiles) == 4

macros_dir = pathlib.Path("macros")
shutil.rmtree(macros_dir, ignore_errors=True)
(macros_dir / "rtl").mkdir(parents=True)

entries = []
for index, tile in enumerate(tiles):
    tmp = pathlib.Path(tempfile.mkdtemp())
    if "run" in tile:
        subprocess.run(
            ["gh", "run", "download", str(tile["run"]), "-R", tile["repo"], "-n", "tt_submission", "-D", str(tmp)],
            check=True,
        )
        info = yaml.safe_load(open(tmp / "info.yaml"))
        src_dir = tmp / "src"
        sub = tmp / "tt_submission"
        project = info["project"]
        macro = project["top_module"]
        views = {"gds": sub / f"{macro}.gds", "lef": sub / f"{macro}.lef", "v": sub / f"{macro}.v"}
        provenance = f"{tile['repo']} run {tile['run']}"
    else:
        proj = pathlib.Path(tile["local"])
        info = yaml.safe_load(open(proj / "info.yaml"))
        src_dir = proj / "src"
        project = info["project"]
        macro = project["top_module"]
        final = proj / "runs" / "wokwi" / "final"
        views = {
            "gds": final / "gds" / f"{macro}.gds",
            "lef": final / "lef" / f"{macro}.lef",
            "v": final / netlist_kind / f"{macro}.{netlist_kind}.v",
        }
        provenance = f"local {proj}"
    m = re.fullmatch(r"micro_uio(\d)", project["tiles"]) or re.fullmatch(r"micro_r(\d)", project["tiles"])
    m_io = re.fullmatch(r"micro_i(\d)o(\d)", project["tiles"])
    m_reg = re.fullmatch(r"micro_io(\d)", project["tiles"])
    if m:
        n = (int(m.group(1)), int(m.group(1)), "bidir")
    elif m_io:
        n = (int(m_io.group(1)), int(m_io.group(2)), "split")
    elif m_reg:
        n = (int(m_reg.group(1)), int(m_reg.group(1)), "reg")
    else:
        raise AssertionError(f"{macro} is not a micro tile with uio pins")
    assert macro != top and macro not in [e["macro"] for e in entries], f"duplicate macro {macro}"
    shutil.copy(views["gds"], macros_dir / f"{macro}.gds")
    shutil.copy(views["lef"], macros_dir / f"{macro}.lef")
    shutil.copy(views["v"], macros_dir / f"{macro}.pnl.v")
    rtl_dir = macros_dir / "rtl" / macro
    rtl_dir.mkdir()
    for source in project["source_files"]:
        shutil.copy(src_dir / source, rtl_dir / pathlib.Path(source).name)
    rtl = (rtl_dir / project["source_files"][0]).read_text()
    k = int(re.search(r"localparam \[7:0\] K = 8'h([0-9a-fA-F]+);", rtl).group(1), 16)
    day0 = "Day-0 micro tile: uio not used" in rtl
    entries.append(
        {"index": index, "macro": macro, "n": n, "k": k, "day0": day0, "sources": project["source_files"], "from": provenance}
    )
    shutil.rmtree(tmp)

ns = {e["n"] for e in entries}
assert len(ns) == 1, f"micro tiles with different uio interfaces: {ns}"
n_in, n_out, kind = ns.pop()
bidir = kind == "bidir"
n = n_in + n_out if kind == "split" else n_in
assert 1 <= n <= 6
hi = 2 + n - 1  # top uio bit used
pad = 6 - n


def padded(expr, low=2):
    return "{" + (f"{pad}'b0, " if pad else "") + expr + f", {low}'b0}}"


if bidir:
    oe_decl = f"  wire [{n - 1}:0] uio_oe_proj[3:0];\n"
    out_assign = f"""  assign uio_out = {padded("uio_out_proj[sel]")};
  assign uio_oe  = {padded("uio_oe_proj[sel]")};"""
    out_doc = f"uio_out[{hi}:2] and uio_oe[{hi}:2]. uio[1:0] are always inputs."
elif kind == "reg":
    # One direction register for all four slots (only one micro tile is active at a time).
    # Cleared while rst_n is low (all inputs); on the first clock after reset it loads ui_in[N-1:0]
    # and the select value. It only drives uio_oe while that micro tile stays selected.
    oe_decl = f"""  reg [{n - 1}:0] oe_q;
  reg [1:0] oe_sel;
  reg oe_armed;
  always @(posedge clk) begin
    if (!rst_n) begin
      oe_q <= {n}'h0;
      oe_armed <= 1'b1;
    end else if (oe_armed) begin
      oe_q <= ui_in[{n - 1}:0];
      oe_sel <= sel;
      oe_armed <= 1'b0;
    end
  end
"""
    out_assign = f"""  assign uio_out = {padded("uio_out_proj[sel]")};
  assign uio_oe  = {padded(f"oe_sel == sel ? oe_q : {n}'h0")};"""
    out_doc = f"uio_out[{hi}:2]; uio_oe[{hi}:2] comes from a register loaded from ui_in[{n - 1}:0] at reset release."
else:
    oe_decl = ""
    oe_mask = ((1 << n_out) - 1) << (2 + n_in)
    out_assign = f"""  assign uio_out = {padded("uio_out_proj[sel]", 2 + n_in)};
  assign uio_oe  = 8'h{oe_mask:02x};"""
    out_doc = f"uio_out[{hi}:{2 + n_in}]. uio[{1 + n_in}:0] are inputs, uio[{hi}:{2 + n_in}] outputs."


# Options: gate = inputs besides clk / rst_n that only the selected micro tile sees (default ui_in and uio_in);
# connect_uio: false = a day-0 container that leaves the micro tiles' uio pins unconnected (uio_out / uio_oe 0).
gate = spec.get("gate", ["ui_in", "uio_in"])
connect_uio = spec.get("connect_uio", True)
if not connect_uio:
    oe_decl = ""
    out_assign = """  assign uio_out = 8'h00;
  assign uio_oe  = 8'h00;"""
    out_doc = "nothing else: the micro tiles' uio pins are not connected, uio_out and uio_oe are 0."


def instance(e):
    i = e["index"]
    ui = f"sel == {i} ? ui_in : 8'h00" if "ui_in" in gate else "ui_in"
    uio = f"sel == {i} ? uio_in[{1 + n_in}:2] : {n_in}'h0" if "uio_in" in gate else f"uio_in[{1 + n_in}:2]"
    if not connect_uio:
        uio_ports = "      .uio_in (),\n      .uio_out()" + (",\n      .uio_oe ()" if bidir else "")
    else:
        uio_ports = f"      .uio_in ({uio}),\n      .uio_out(uio_out_proj[{i}])" + (
            f",\n      .uio_oe (uio_oe_proj[{i}])" if bidir else ""
        )
    return f"""  {e['macro']} proj{i + 1} (
      .rst_n  (sel == {i} ? rst_n : 1'b0),
      .clk    (sel == {i} ? clk : 1'b0),
      .ui_in  ({ui}),
      .uo_out (uo_out_proj[{i}]),
{uio_ports}
  );
"""


instances = "\n".join(instance(e) for e in entries)
if not connect_uio:
    unused = "ena, uio_in[7:2], 1'b0"
else:
    unused = f"ena, uio_in[7:{2 + n_in}], 1'b0" if 2 + n_in <= 7 else "ena, 1'b0"
pathlib.Path("src/project.v").write_text(
    f"""/*
 * Copyright (c) 2024 Tiny Tapeout
 * SPDX-License-Identifier: Apache-2.0
 *
 * Generated by assemble_uio.py, do not edit.
 */

`default_nettype none

// Container for four micro tile projects with {n} uio pins each. uio_in[1:0] selects the active
// one: only the selected micro tile gets clk, rst_n, ui_in and uio_in[{1 + n_in}:2], and drives uo_out,
// {out_doc}
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
  wire [{n_out - 1}:0] uio_out_proj[3:0];
{oe_decl}
  assign uo_out  = uo_out_proj[sel];
{out_assign}

{instances}
  // List all unused inputs to prevent warnings
  wire _unused = &{{{unused}}};

endmodule
"""
)

macros = {
    e["macro"]: {
        "instances": {
            f"proj{e['index'] + 1}": {"location": slots[e["index"]], "orientation": "N" if e["index"] % 2 == 0 else "FN"}
        },
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
# Spec option config: {KEY: value} replaces the value of an existing key of src/config.json (or adds it)
for key, value in spec.get("config", {}).items():
    new = f'"{key}": {json.dumps(value)}'
    text, count = re.subn(rf'"{key}": [^\n]*?(?=,?\n)', lambda m: new, text, count=1)
    if not count:
        text = text.replace('"MACROS": {', f'{new},\n\n  "MACROS": {{', 1)
config.write_text(text)

info_path = pathlib.Path("info.yaml")
text = info_path.read_text()
text = re.sub(r"  title: .*", f'  title:        "{spec["title"]}"', text, count=1)
text = re.sub(r"  top_module: .*", f'  top_module:  "{top}"', text, count=1)
for i in range(2, 8):
    if kind != "split":
        label = f"micro tile bidir[{i - 2}]" if i <= hi else ""
    else:
        label = f"micro tile in[{i - 2}]" if i < 2 + n_in else f"micro tile out[{i - 2 - n_in}]" if i <= hi else ""
    text = re.sub(rf'  uio\[{i}\]: *"[^"]*"', f'  uio[{i}]: "{label}"', text)
info_path.write_text(text)

rtl_list = " ".join(f"$(MACROS_DIR)/rtl/{e['macro']}/{s}" for e in entries for s in e["sources"])
pathlib.Path("test/micro_tiles.mk").write_text(
    "# Generated by assemble_uio.py, do not edit.\n"
    f"TOP_MODULE = {top}\n"
    f"MACROS = {' '.join(e['macro'] for e in entries)}\n"
    f"MACROS_RTL = {rtl_list}\n"
)
pathlib.Path("test/micro_tiles.json").write_text(
    json.dumps({"n": n, "kind": kind, "bidir": bidir, "n_in": n_in, "n_out": n_out, "connect_uio": connect_uio, "gate": gate, "k": [e["k"] for e in entries], "day0": [e["day0"] for e in entries], "macros": [e["macro"] for e in entries], "from": [e["from"] for e in entries]}, indent=2)
    + "\n"
)
print("assembled", top, f"(N = {n}) from", ", ".join(e["macro"] for e in entries))
