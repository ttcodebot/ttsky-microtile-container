# SPDX-FileCopyrightText: © 2026 Ken Pettit
# SPDX-License-Identifier: Apache-2.0
"""A test signal (a sweep with a changing loudness, and silence) is encoded
by tools/uadpcm.py and streamed into the chip the way the host does it, one
code and a strobe every PERIOD clocks.  Checked:

  - every clock of uo_out against the cycle-exact model (model.py);
  - the model's predictor after every sample against the codec's reference
    decoder (uadpcm.decode), so chip == model == what the encoder assumed;
  - the PWM: its high time over 1024 clocks of the last sample, held, against
    the predictor's top 10 bits.

SAMPLES (default 3000) and PERIOD (default 128 clocks; 1024 is 31250 Hz) from
the environment."""

import math
import os
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import uadpcm  # noqa: E402
from model import Model  # noqa: E402


def test_signal(n):
    """Unsigned 16-bit samples: a rising sweep, loud then quiet, then silence, then a full-scale burst."""
    out, ph = [], 0.0
    for j in range(n):
        x = j / n
        ph += 2 * math.pi * (0.002 + 0.12 * x)
        amp = 30000 * (1 - x / 0.6) ** 2 if x < 0.6 else 0 if x < 0.75 else 32700
        out.append(41000 if j >= n - 40 else int(32768 + amp * math.sin(ph)))
    return out


@cocotb.test()
async def test_stream(dut):
    samples = int(os.environ.get("SAMPLES", "3000"))
    period = int(os.environ.get("PERIOD", "128"))
    cocotb.start_soon(Clock(dut.clk, 32, unit="ns").start())   # 31.25 MHz

    target = test_signal(samples)
    codes = uadpcm.encode(target)
    ref = uadpcm.decode(codes)
    assert len(set(codes)) >= 14, "the test signal should use nearly every code"

    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 20)
    # in reset: mid-scale duty on uo[4:0], no code pending
    assert str(dut.uo_out.value)[2:] == "010000", f"uo_out in reset: {dut.uo_out.value}"
    if os.environ.get("GATES") != "yes":
        # ... and the PWM pin toggles every clock, uo[6] its complement (the
        # flop powers up either way; in the RTL simulation it is given a value)
        dut.user_project.pwm.value = 0
        seen = []
        for _ in range(8):
            await FallingEdge(dut.clk)
            seen.append(int(dut.uo_out.value) >> 6)
        assert seen in ([1, 2] * 4, [2, 1] * 4), f"uo[7:6] in reset: {seen}"
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    model = Model()
    errors = checked = high = 0
    ui = 0
    total = samples * period + 4096             # the last sample is held for 4096 clocks
    for n in range(total):
        j, ph = divmod(n, period)
        if j < samples:
            if ph == 0:
                ui = codes[j]                   # the code, strobe low
            elif ph == 3:
                ui = codes[j] | 0x10            # strobe high
            elif ph == 3 + period // 2:
                ui = codes[j]
        dut.ui_in.value = ui
        await FallingEdge(dut.clk)              # ui_in is seen by the next rising edge
        expect = model.step_clock(ui)
        got = dut.uo_out.value
        if expect is not None:
            checked += 1
            if not got.is_resolvable or int(got) != expect:
                errors += 1
                if errors <= 10:
                    dut._log.error(f"clock {n} (sample {j}): uo_out {got} expected {expect:08b}")
                continue
            if n >= total - 1024:
                high += int(got) >> 7
        # the end of a sample period: its code is decoded (16 clocks of waiting at most, then 80)
        if ph == period - 1 and j < samples:
            # rotate the model's registers into place to read the predictor
            rot = model.ramp & 15
            p = ((model.pred >> (16 - rot)) | (model.pred << rot)) & 0xFFFF if rot else model.pred
            if p != ref[j]:
                errors += 1
                if errors <= 10:
                    dut._log.error(f"sample {j}: predictor {p}, the reference decoder says {ref[j]}")

    dut._log.info(f"{samples} samples, {checked} clocks checked, {errors} mismatches; "
                  f"last sample {ref[-1]}: PWM high {high} of 1024 clocks, top 10 bits {ref[-1] >> 6}")
    assert errors == 0
    assert checked > total * 0.99
    assert abs(high - (ref[-1] >> 6)) <= 1
