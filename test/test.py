# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

MICRO_TILES = 4


async def start(dut):
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)


@cocotb.test()
async def test_loopback(dut):
    """While in reset, the selected micro tile mirrors ui_in to uo_out."""
    await start(dut)

    for sel in range(MICRO_TILES):
        dut._log.info(f"Testing loopback of micro tile {sel}")
        dut.uio_in.value = sel
        dut.rst_n.value = 0
        await ClockCycles(dut.clk, 1)
        for i in list(range(0, 256, 5)) + [255]:
            dut.ui_in.value = i
            await ClockCycles(dut.clk, 1)
            assert dut.uo_out.value == i
    assert dut.uio_oe.value == 0
    assert dut.uio_out.value == 0


@cocotb.test()
async def test_counter(dut):
    """Out of reset, the selected micro tile outputs a counter on uo_out."""
    await start(dut)

    for sel in range(MICRO_TILES):
        dut._log.info(f"Testing counter of micro tile {sel}")
        dut.uio_in.value = sel
        dut.ui_in.value = 0
        dut.rst_n.value = 0
        await ClockCycles(dut.clk, 10)
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        for i in range(256):
            assert dut.uo_out.value == i
            await ClockCycles(dut.clk, 1)

        for i in range(5):
            assert dut.uo_out.value == i
            await ClockCycles(dut.clk, 1)
        dut.rst_n.value = 0
        await ClockCycles(dut.clk, 2)
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == 0


@cocotb.test()
async def test_isolation(dut):
    """A micro tile that is not selected gets no clock: its counter stays in reset."""
    await start(dut)

    # Run the counter of micro tile 0 for a while
    dut.uio_in.value = 0
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 20)
    assert dut.uo_out.value != 0

    # Micro tile 1 was held in reset all along, and starts counting from zero
    dut.uio_in.value = 1
    await ClockCycles(dut.clk, 2)
    first = int(dut.uo_out.value)
    assert first <= 2
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == first + 10
