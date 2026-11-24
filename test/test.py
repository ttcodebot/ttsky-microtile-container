# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# Four micro tiles with uio pins (test/micro_tiles.json, written by assemble_uio.py), either
#   bidirectional (tiles: micro_uio<N>): uio_in, uio_out, uio_oe on container pins uio[N+1:2], or
#   fixed direction (tiles: micro_i<A>o<B>): uio_in on uio[A+1:2], uio_out on uio[A+B+1:A+2], constant uio_oe, or
#   direction register (tiles: micro_io<N>): uio_in, uio_out on uio[N+1:2]; the container's uio_oe register is
#   cleared in reset and loads ui_in[N-1:0] on the first clock after reset.
# Every micro tile is a combinational loopback while in reset:
#     uo_out = {ui_in[7:A], uio_in} ^ K, uio_out = ui_in[7:8-B] ^ K[7:8-B], uio_oe = ui_in[N-1:0] (bidirectional)
# so one model checks every pin of every micro tile through the container. The micro tile at
# select value 0 counts on uo_out (xor K) and uio_out when out of reset.

import json
import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

SPEC = json.load(open(os.path.join(os.path.dirname(__file__), "micro_tiles.json")))
KIND = SPEC.get("kind", "bidir" if SPEC.get("bidir", True) else "split")
BIDIR = KIND == "bidir"
REG = KIND == "reg"
A = SPEC.get("n_in", SPEC["n"])  # uio inputs of a micro tile
B = SPEC.get("n_out", SPEC["n"])  # uio outputs of a micro tile
KS = SPEC["k"]
CONNECT = SPEC.get("connect_uio", True)  # False: day-0 container, micro tile uio pins not connected
# Day-0 micro tiles do not use uio (outputs tied to 0); while in reset uo_out = ui_in ^ K
NO_UIO = [not CONNECT or d for d in SPEC.get("day0", [False] * 4)]
IMASK = (1 << A) - 1
OMASK = (1 << B) - 1
OUT_SHIFT = 2 + A if KIND == "split" else 2  # container pin of uio_out[0]
FIXED_OE = OMASK << OUT_SHIFT if KIND == "split" else 0  # uio_oe in reset (bidirectional: set by ui_in)
COUNTER = 0


def loopback(k, ui, uio, sel=None):
    """uo_out, uio_oe, uio_out of the container while micro tile with constant k is selected and in reset"""
    if sel is not None and NO_UIO[sel]:
        return ui ^ k, FIXED_OE if CONNECT else 0, 0
    u = (uio >> 2) & IMASK
    uo = ((((ui >> A) << A) | u) ^ k) & 0xFF
    oe = (ui & IMASK) << 2 if BIDIR else FIXED_OE
    out = (((ui >> (8 - B)) ^ (k >> (8 - B))) & OMASK) << OUT_SHIFT
    return uo, oe, out


async def start(dut):
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = COUNTER
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)


@cocotb.test()
async def test_loopback(dut):
    """Every pin of every micro tile, through the container: 300 random vectors per micro tile."""
    await start(dut)
    rng = random.Random(2)
    for sel, k in enumerate(KS):
        for _ in range(300):
            ui = rng.randrange(256)
            uio = (rng.randrange(64) << 2) | sel
            dut.ui_in.value = ui
            dut.uio_in.value = uio
            await Timer(1, unit="us")
            uo, oe, out = loopback(k, ui, uio, sel)
            assert dut.uo_out.value == uo, f"micro tile {sel}: uo_out {int(dut.uo_out.value):02x} != {uo:02x}"
            assert dut.uio_oe.value == oe, f"micro tile {sel}: uio_oe {int(dut.uio_oe.value):02x} != {oe:02x}"
            assert dut.uio_out.value == out, f"micro tile {sel}: uio_out {int(dut.uio_out.value):02x} != {out:02x}"
        dut._log.info(f"micro tile {sel} ({SPEC['macros'][sel]}): 300 vectors pass")


@cocotb.test()
async def test_counter(dut):
    """Out of reset, the counter micro tile counts on uo_out (xor K) and uio_out."""
    await start(dut)
    k = KS[COUNTER]
    dut.ui_in.value = 0 if KIND == "split" else OMASK  # all its uio pins outputs (register: loaded at reset release)
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    for i in range(300):
        assert dut.uo_out.value == (i & 0xFF) ^ k
        if NO_UIO[COUNTER]:
            assert dut.uio_out.value == 0
            assert dut.uio_oe.value == (FIXED_OE if CONNECT else 0)
        else:
            assert dut.uio_out.value == (i & OMASK) << OUT_SHIFT
            assert dut.uio_oe.value == (FIXED_OE if KIND == "split" else OMASK << 2)
        await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_isolation(dut):
    """A micro tile that is not selected gets no clock and is held in reset."""
    await start(dut)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 20)
    assert int(dut.uo_out.value) ^ KS[COUNTER] >= 16

    for other in range(1, 4):
        # Select another micro tile: the counter loses its clock and goes into reset
        dut.uio_in.value = other
        await ClockCycles(dut.clk, 20)

        # Back to the counter: it starts from zero
        dut.uio_in.value = COUNTER
        await ClockCycles(dut.clk, 2)
        first = int(dut.uo_out.value) ^ KS[COUNTER]
        assert first <= 2
        await ClockCycles(dut.clk, 10)
        assert int(dut.uo_out.value) ^ KS[COUNTER] == first + 10


@cocotb.test(skip=not REG or not CONNECT)
async def test_oe_register(dut):
    """Direction register: all inputs in reset, loads ui_in at reset release, only for the micro tile selected then."""
    await start(dut)
    for sel, pattern in [(0, 0b101101), (2, 0b010011), (3, 0b111111), (1, 0b000001)]:
        pattern &= OMASK
        dut.uio_in.value = sel
        dut.rst_n.value = 0
        dut.ui_in.value = pattern
        await ClockCycles(dut.clk, 3)
        assert dut.uio_oe.value == 0, "uio_oe must be 0 (all inputs) while in reset"
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)
        assert dut.uio_oe.value == pattern << 2
        dut.ui_in.value = ~pattern & 0xFF  # later changes of ui_in do not change the directions
        await ClockCycles(dut.clk, 5)
        assert dut.uio_oe.value == pattern << 2
        dut.uio_in.value = (sel + 1) % 4  # another micro tile: all inputs
        await Timer(1, unit="us")
        assert dut.uio_oe.value == 0
        dut.uio_in.value = sel
        await Timer(1, unit="us")
        assert dut.uio_oe.value == pattern << 2
        dut._log.info(f"micro tile {sel}: oe {pattern:06b} pass")
