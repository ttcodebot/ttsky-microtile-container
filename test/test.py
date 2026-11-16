# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# The micro tile at select value 0 is the micro tile test module (a counter / input mirror).
# The other three are projects of their own: this test only checks that the container
# isolates them from the selected micro tile.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

COUNTER = 0


async def start(dut):
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = COUNTER
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)


@cocotb.test()
async def test_loopback(dut):
    """While in reset, the counter micro tile mirrors ui_in to uo_out."""
    await start(dut)

    for i in list(range(0, 256, 5)) + [255]:
        dut.ui_in.value = i
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == i
    assert dut.uio_oe.value == 0
    assert dut.uio_out.value == 0


@cocotb.test()
async def test_counter(dut):
    """Out of reset, the counter micro tile outputs a counter on uo_out."""
    await start(dut)

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
    """A micro tile that is not selected gets no clock and is held in reset."""
    await start(dut)

    # Run the counter for a while
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 20)
    assert int(dut.uo_out.value) >= 16

    for other in range(1, 4):
        # Select another micro tile: the counter loses its clock and goes into reset
        dut.uio_in.value = other
        await ClockCycles(dut.clk, 20)

        # Back to the counter: it starts from zero
        dut.uio_in.value = COUNTER
        await ClockCycles(dut.clk, 2)
        first = int(dut.uo_out.value)
        assert first <= 2
        await ClockCycles(dut.clk, 10)
        assert int(dut.uo_out.value) == first + 10
