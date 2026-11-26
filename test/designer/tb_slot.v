`default_nettype none
`timescale 1ns / 1ps

/* The container with one micro tile selected (uio_in = SLOT), seen through the pins of a micro
   tile (clk, rst_n, ui_in, uo_out), so that the micro tile's own test can drive it unchanged.
*/
module tb ();

  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  reg clk;
  reg rst_n;
  reg [7:0] ui_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
  wire VPWR = 1'b1;
  wire VGND = 1'b0;

  `TOP_MODULE user_project (
      .VPWR   (VPWR),
      .VGND   (VGND),
      .ui_in  (ui_in),
      .uo_out (uo_out),
      .uio_in (8'd`SLOT),
      .uio_out(uio_out),
      .uio_oe (uio_oe),
      .ena    (1'b1),
      .clk    (clk),
      .rst_n  (rst_n)
  );

endmodule
