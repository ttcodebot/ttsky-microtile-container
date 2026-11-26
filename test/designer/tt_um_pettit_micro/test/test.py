# SPDX-FileCopyrightText: © 2026 Ken Pettit
# SPDX-License-Identifier: Apache-2.0
"""Every clock of a few frames against the cycle-exact model (model.py), with
ui_in changing on the way so that each mode is drawn, plus the VGA timing
measured from the sync pins alone.  FRAMES=n in the environment (default 3)."""

import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

from model import Model

H_TOTAL, V_TOTAL = 800, 525
# a new ui_in every 20 lines: each scene, hold, no dither, and the unused inputs
UI_SEQ = [0, 1, 2, 3, 4, 5, 6, 7, 0x08, 0x0D, 0x10, 0x13, 0x16, 0xC0, 0xDF]


@cocotb.test()
async def test_video(dut):
    frames = int(os.environ.get("FRAMES", "3"))
    cocotb.start_soon(Clock(dut.clk, 40, unit="ns").start())   # 25 MHz

    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    model = Model()
    errors = 0
    hs_fall, vs_fall, hs_low, vs_low = [], [], 0, 0
    prev = 0xFF
    for n in range(frames * H_TOTAL * V_TOTAL + 2 * H_TOTAL):
        if n % (20 * H_TOTAL) == 0:
            ui = UI_SEQ[(n // (20 * H_TOTAL)) % len(UI_SEQ)]
            # the frame counter stops for the second frame's wrap only
            if n // (H_TOTAL * V_TOTAL) == 1 and (n // H_TOTAL) % V_TOTAL >= 500:
                ui |= 0x20
            dut.ui_in.value = ui
        await FallingEdge(dut.clk)          # ui_in is seen by the next rising edge
        expect = model.step(ui)
        got = dut.uo_out.value
        if not got.is_resolvable or int(got) != expect:
            errors += 1
            if errors <= 10:
                dut._log.error(f"clock {n} (line {n // H_TOTAL % V_TOTAL}, col {n % H_TOTAL}, ui {ui:#04x}): "
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

    dut._log.info(f"{n + 1} clocks, {errors} mismatches, frame counter {model.t}")
    assert errors == 0
    # timing from the pins: 800 clocks a line with 96 of sync, 525 lines a frame with 2 of sync
    assert all(b - a == H_TOTAL for a, b in zip(hs_fall, hs_fall[1:]))
    assert all(b - a == H_TOTAL * V_TOTAL for a, b in zip(vs_fall, vs_fall[1:]))
    assert len(vs_fall) == frames
    assert hs_low == 96 * len(hs_fall)
    assert vs_low == 2 * H_TOTAL * len(vs_fall)
    assert model.t == frames - 1 if frames >= 2 else model.t == frames
