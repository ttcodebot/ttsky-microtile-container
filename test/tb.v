`default_nettype none
`timescale 1ns / 1ps

/* The container under test (RTL, or the gate level netlist with the micro tile netlists), and
   next to it the reference model: the container RTL with the micro tile RTL from their
   repositories (modules renamed to ref_*). Both get the same inputs; test.py compares them.
*/
module tb ();

  // Dump the signals to a FST file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
  wire [7:0] ref_uo_out;
  wire [7:0] ref_uio_out;
  wire [7:0] ref_uio_oe;
`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  `TOP_MODULE user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

  `REF_TOP_MODULE ref_project (
      .ui_in  (ui_in),
      .uo_out (ref_uo_out),
      .uio_in (uio_in),
      .uio_out(ref_uio_out),
      .uio_oe (ref_uio_oe),
      .ena    (ena),
      .clk    (clk),
      .rst_n  (rst_n)
  );

endmodule
