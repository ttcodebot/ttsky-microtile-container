/*
 * tt_um_micro_uio6_cnt: micro tile with 6 uio pins (counter with uio).
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_micro_uio6_cnt (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [5:0] uio_in,   // IOs: Input path
    output wire [5:0] uio_out,  // IOs: Output path
    output wire [5:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // While in reset: a combinational loopback through every pin
  localparam [7:0] K = 8'h00;
  wire [7:0] lb_uo = {ui_in[7:6], uio_in} ^ K;
  wire [5:0] lb_oe = ui_in[5:0];
  wire [5:0] lb_out = ui_in[7:2] ^ K[7:2];

  reg rst_n_i;
  reg [7:0] cnt;

  always @(posedge clk or negedge rst_n)
    if (~rst_n) rst_n_i <= 1'b0;
    else rst_n_i <= 1'b1;

  always @(posedge clk or negedge rst_n_i)
    if (~rst_n_i) cnt <= 0;
    else cnt <= cnt + 1;

  assign uo_out  = rst_n ? cnt ^ K : lb_uo;
  assign uio_out = rst_n ? cnt[5:0] : lb_out;
  assign uio_oe  = lb_oe;

endmodule
