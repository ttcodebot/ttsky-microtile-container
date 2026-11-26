import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_reset_and_diamond(dut):
    dut.clk.value = 0
    dut.ui_in.value = 0  # Mode 00: diamond
    dut.rst_n.value = 0
    cocotb.start_soon(Clock(dut.clk, 200, unit="ns").start(start_high=False))

    await RisingEdge(dut.clk)
    await Timer(50, unit="ns")
    assert int(dut.uo_out.value) == 0x88, "Reset should center both axes"

    dut.rst_n.value = 1

    for index, expected in enumerate((0x80, 0x80, 0x91, 0x91, 0xA2)):
        await RisingEdge(dut.clk)
        await Timer(50, unit="ns")
        actual = int(dut.uo_out.value)
        assert actual == expected, (
            f"Sample {index}: expected 0x{expected:02X}, got 0x{actual:02X}"
        )
