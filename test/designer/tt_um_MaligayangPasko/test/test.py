# SPDX-FileCopyrightText: © 2026 Alexander Co Abad
# SPDX-License-Identifier: Apache-2.0
"""Every clock of a few frames against the cycle-exact model (model.py), with the pause input
toggled on the way and the three display options (ui_in[3:1]) switched by a fixed pseudo-random
pattern, plus the VGA timing measured from the sync pins alone.  FRAMES=n in the
environment (default 3).  Frame 2 is written to frame.png when Pillow is installed."""

import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

from model import Model, colour, pack

H_TOTAL, V_TOTAL = 800, 525


@cocotb.test()
async def test_video(dut):
    frames = int(os.environ.get("FRAMES", "3"))
    cocotb.start_soon(Clock(dut.clk, 40, unit="ns").start())   # 25 MHz

    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    # In the RTL simulation start the frame counter at 47, so that three frames cover star colours 2 and 3
    # and the light cycling.  The gate-level netlist has no such name; it starts at 0.
    model = Model()
    try:
        dut.user_project.t.value = 47
        model.t = 47
    except Exception:                     # no such signal in the gate-level netlist
        pass
    errors = 0
    hs_fall, vs_fall, hs_low, vs_low = [], [], 0, 0
    prev = 0xFF
    pic = {}
    rng = random.Random(2026)
    pattern = 0
    seen = set()                            # option bits seen to change a pixel
    for n in range(frames * H_TOTAL * V_TOTAL + 2 * H_TOTAL):
        # pause (ui_in[0]) is high for the last 20 lines of the second frame, so the frame counter skips one step
        line = n // H_TOTAL
        if n % (8 * H_TOTAL) == 0:          # a new option pattern every 8 lines
            pattern = rng.randrange(8)
        # the first two frames run with all options off (the plain scene, frame 2 is saved as frame.png),
        # the later ones with the pattern
        ui = (pattern << 1) if line >= 2 * V_TOTAL else 0
        ui |= 1 if (V_TOTAL + 505 <= line < 2 * V_TOTAL) else 0
        dut.ui_in.value = ui
        await FallingEdge(dut.clk)          # ui_in is seen by the next rising edge
        if n % 61 == 0 and n < 3 * H_TOTAL * V_TOTAL:    # sample: does each option bit change this pixel?
            m, h, v = model, model.hc, model.vc
            for b in range(1, 4):
                if h < 640 and v < 480 and colour(h, v, m.t, ui) != colour(h, v, m.t, ui ^ (1 << b)):
                    seen.add(b)
        expect = model.step(ui)
        got = dut.uo_out.value
        if not got.is_resolvable or int(got) != expect:
            errors += 1
            if errors <= 10:
                dut._log.error(f"clock {n} (line {n // H_TOTAL % V_TOTAL}, col {n % H_TOTAL}): "
                               f"uo_out {got} expected {expect:08b}")
            continue
        got = int(got)
        if prev & 0x80 and not got & 0x80:
            hs_fall.append(n)
        if prev & 0x08 and not got & 0x08:
            vs_fall.append(n)
        hs_low += not got & 0x80
        vs_low += not got & 0x08
        prev = got
        f, c = divmod(n, H_TOTAL * V_TOTAL)
        if f == 1 and c % H_TOTAL < 640 and c // H_TOTAL < 480:
            pic[c] = got

    dut._log.info(f"{n + 1} clocks, {errors} mismatches, frame counter {model.t}")
    assert errors == 0
    want = set(range(1, 4))
    assert want <= seen, f"option bits that never changed a sampled pixel: {want - seen}"
    # timing from the pins: 800 clocks a line with 96 of sync, 525 lines a frame with 2 of sync
    assert all(b - a == H_TOTAL for a, b in zip(hs_fall, hs_fall[1:]))
    assert all(b - a == H_TOTAL * V_TOTAL for a, b in zip(vs_fall, vs_fall[1:]))
    assert len(vs_fall) == frames
    assert hs_low == 96 * len(hs_fall)
    assert vs_low == 2 * H_TOTAL * len(vs_fall)
    # the picture is not blank: several colours are used
    assert len({v & 0x77 for v in pic.values()}) >= 6

    try:
        from PIL import Image
        im = Image.new("RGB", (640, 480))
        px = im.load()
        for c, v in pic.items():
            r, g, b = (v & 1) << 1 | (v >> 4) & 1, (v >> 1 & 1) << 1 | (v >> 5) & 1, (v >> 2 & 1) << 1 | (v >> 6) & 1
            px[c % H_TOTAL, c // H_TOTAL] = (r * 85, g * 85, b * 85)
        im.save("frame.png")
    except ImportError:
        pass
