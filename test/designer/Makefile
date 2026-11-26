# Each micro tile's own cocotb test (copied unchanged from its repository, see README.md), run
# through the container: gate level netlist of the container plus the four micro tile netlists,
# with uio_in[1:0] tied to the select value of that micro tile.
#
#   make GATES=yes SLOT=<0..3>     (needs ../gate_level_netlist.v, as the gl_test workflow copies it)

SIM ?= icarus
FST ?= -fst
TOPLEVEL_LANG ?= verilog
SLOT ?= 0
MACROS_DIR = $(PWD)/../../macros
include ../micro_tiles.mk

MACRO_0 = $(word 1,$(MACROS))
MACRO_1 = $(word 2,$(MACROS))
MACRO_2 = $(word 3,$(MACROS))
MACRO_3 = $(word 4,$(MACROS))
MACRO = $(MACRO_$(SLOT))
ifeq ($(MACRO),)
$(error SLOT must be 0, 1, 2 or 3)
endif

ifneq ($(GATES),yes)
$(error the designer tests run on the gate level netlist only: make GATES=yes SLOT=$(SLOT))
endif

SIM_BUILD       = sim_build/slot$(SLOT)
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
COMPILE_ARGS    += -DTOP_MODULE=$(TOP_MODULE)
COMPILE_ARGS    += -DSLOT=$(SLOT)
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
VERILOG_SOURCES += $(PWD)/../gate_level_netlist.v
VERILOG_SOURCES += $(patsubst %,$(MACROS_DIR)/%.pnl.v,$(MACROS))
VERILOG_SOURCES += $(PWD)/tb_slot.v
TOPLEVEL = tb

# The micro tile's test module (test.py and its model.py)
export PYTHONPATH := $(PWD)/$(MACRO)/test:$(PYTHONPATH)
COCOTB_TEST_MODULES = test
COCOTB_RESULTS_FILE = results_slot$(SLOT).xml
export COCOTB_RESULTS_FILE

include $(shell cocotb-config --makefiles)/Makefile.sim
