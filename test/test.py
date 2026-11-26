# SPDX-FileCopyrightText: © 2026 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

"""Container test: the design under test (in the gate level test, the container netlist plus the
four micro tile netlists) runs next to a reference model made of the container RTL and the RTL
of each micro tile, taken unchanged from its repository (tb.v, make_ref.py). Every clock, every
output bit that the reference knows (0 or 1) must match. Inputs and resets are random (seeded).

  test_slots      each micro tile in turn: select it, random ui_in, random resets (RESETS clocks),
                  then a long run without resets (LONG clocks, more than one 640x480 VGA frame)
  test_switching  random selection changes, with random ui_in and resets (SWITCH clocks)
  test_isolation  the outputs of the micro tiles that are not selected are forced to random
                  values: uo_out must not change; their clk, rst_n and ui_in must stay 0
                  (ISOLATION clocks per slot)

From the environment: SEED (default 2026), RESETS (50000), LONG (450000), SWITCH (100000),
ISOLATION (5000).
"""

import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.handle import Force, Release
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, Timer

SEED = int(os.environ.get("SEED", "2026"))
RESETS = int(os.environ.get("RESETS", "50000"))
LONG = int(os.environ.get("LONG", "450000"))
SWITCH = int(os.environ.get("SWITCH", "100000"))
ISOLATION = int(os.environ.get("ISOLATION", "5000"))
PERIOD_NS = 100
SLOTS = 4
INSTANCES = ["proj1", "proj2", "proj3", "proj4"]  # slot i is proj<i+1> (src/project.v)
NAMES = ["Micro Munch", "Maligayang Pasko", "Micro ADPCM", "XY Spirograph"]


class Stats:
    def __init__(self, dut, name):
        self.dut = dut
        self.name = name
        self.cycles = 0  # clocks compared
        self.full = 0  # clocks where the reference knew all 8 bits
        self.bits = 0  # bits compared
        self.mismatches = 0  # clocks with at least one wrong bit
        self.logged = 0
        self.values = set()  # distinct reference outputs
        self.prev = None
        self.vsync = 0  # falling edges of uo_out[3] (VSYNC of the VGA micro tiles): frames

    def check(self, where=""):
        dut = self.dut
        ref = str(dut.ref_uo_out.value).upper()
        got = str(dut.uo_out.value).upper()
        self.cycles += 1
        known = [i for i, r in enumerate(ref) if r in "01"]
        self.bits += len(known)
        self.full += len(known) == 8
        self.values.add(ref)
        if self.prev is not None and self.prev[4] == "1" and ref[4] == "0":
            self.vsync += 1
        self.prev = ref
        bad = [i for i in known if got[i] != ref[i]]
        if str(dut.uio_oe.value) != "00000000" or str(dut.uio_out.value) != "00000000":
            bad.append("uio")
        if bad:
            self.mismatches += 1
            if self.logged < 10:
                self.logged += 1
                dut._log.error(
                    f"{self.name} clock {self.cycles} {where}: uo_out {got}, reference {ref}, "
                    f"uio_out {dut.uio_out.value}, uio_oe {dut.uio_oe.value}"
                )

    def report(self):
        self.dut._log.info(
            f"{self.name}: {self.cycles} clocks compared ({self.full} with all 8 reference bits known), "
            f"{self.bits} bits, {self.mismatches} mismatching clocks; "
            f"{len(self.values)} distinct outputs, {self.vsync} falling edges on uo_out[3]"
        )


class Stimulus:
    """Random ui_in that holds each value for a random number of clocks (so slow inputs such as
    strobes and mode pins are exercised too), and random resets of 1 to 40 clocks, on average
    one every 1 / reset_rate clocks."""

    def __init__(self, rng, reset_rate=1 / 3000):
        self.rng = rng
        self.reset_rate = reset_rate
        self.ui = 0
        self.hold = 0
        self.reset = 0

    def step(self, dut):
        rng = self.rng
        if self.hold == 0:
            self.ui = rng.randrange(256)
            self.hold = rng.choice([1, 1, 2, 4, 16, 64, 256, 1024])
        self.hold -= 1
        if self.reset == 0 and rng.random() < self.reset_rate:
            self.reset = rng.randint(1, 40)
        rst_n = 0 if self.reset else 1
        self.reset = max(0, self.reset - 1)
        dut.ui_in.value = self.ui
        dut.rst_n.value = rst_n


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)


async def select(dut, rng, slot, reset_clocks=20):
    """Select a micro tile (random values on the unused uio_in[7:2]) and reset it."""
    await FallingEdge(dut.clk)
    dut.uio_in.value = slot | (rng.randrange(64) << 2)
    dut.rst_n.value = 0
    for _ in range(reset_clocks):
        dut.ui_in.value = rng.randrange(256)
        await FallingEdge(dut.clk)
    dut.rst_n.value = 1


@cocotb.test()
async def test_slots(dut):
    """Each micro tile, selected on its own, against its RTL."""
    await start(dut)
    failed = []
    for slot in range(SLOTS):
        rng = random.Random(SEED * 16 + slot)
        await select(dut, rng, slot)
        stats = Stats(dut, f"slot {slot} ({NAMES[slot]})")
        stim = Stimulus(rng)
        for n in range(RESETS + LONG):
            if n == RESETS:  # the long run: no more resets
                stim.reset_rate = 0
            await FallingEdge(dut.clk)
            stats.check()
            stim.step(dut)
            if n % 997 == 0:  # the unused uio_in bits must not matter
                dut.uio_in.value = slot | (rng.randrange(64) << 2)
        stats.report()
        if stats.mismatches or stats.full < (RESETS + LONG) // 2:
            failed.append(slot)
    assert not failed, f"slots with mismatches or too few known reference outputs: {failed}"


@cocotb.test()
async def test_switching(dut):
    """Random selection changes, at random times, with random inputs and resets."""
    await start(dut)
    rng = random.Random(SEED * 16 + 8)
    # Bring every micro tile out of reset once, so that all of them have a known state
    for slot in range(SLOTS):
        await select(dut, rng, slot)
        await ClockCycles(dut.clk, 50)
    stats = Stats(dut, "switching")
    stim = Stimulus(rng)
    slot, switches, left = 0, 0, 0
    seen = set()
    for _ in range(SWITCH):
        await FallingEdge(dut.clk)
        stats.check(f"(slot {slot})")
        if left == 0:
            slot = rng.randrange(SLOTS)
            seen.add(slot)
            left = rng.choice([1, 1, 2, 3, 5, 10, 20, 50, 100, 300, 1000, 3000])
            switches += 1
        left -= 1
        dut.uio_in.value = slot | (rng.randrange(64) << 2)
        stim.step(dut)
    stats.report()
    dut._log.info(f"{switches} selections, slots seen: {sorted(seen)}")
    assert seen == set(range(SLOTS))
    assert stats.mismatches == 0
    assert stats.full > SWITCH // 2


@cocotb.test()
async def test_isolation(dut):
    """The micro tiles that are not selected cannot reach uo_out, and see only zeros."""
    await start(dut)
    rng = random.Random(SEED * 16 + 9)
    container = dut.user_project
    for slot in range(SLOTS):
        await select(dut, rng, slot)
        others = [INSTANCES[i] for i in range(SLOTS) if i != slot]
        stats = Stats(dut, f"isolation, slot {slot} selected")
        stim = Stimulus(rng)
        zeros_ok = True
        for n in range(ISOLATION):
            # While clk is high: the micro tiles that are not selected see clk, rst_n, ui_in = 0
            await RisingEdge(dut.clk)
            await Timer(PERIOD_NS // 4, unit="ns")
            for name in others:
                inst = getattr(container, name)
                pins = (str(inst.clk.value), str(inst.rst_n.value), str(inst.ui_in.value))
                if pins != ("0", "0", "00000000"):
                    zeros_ok = False
                    if n < 10:
                        dut._log.error(f"{name} is not selected but sees clk, rst_n, ui_in = {pins}")
            await FallingEdge(dut.clk)
            stats.check()
            for name in others:
                getattr(container, name).uo_out.value = Force(rng.randrange(256))
            stim.step(dut)
        for name in others:
            getattr(container, name).uo_out.value = Release()
        stats.report()
        assert stats.mismatches == 0
        assert zeros_ok
