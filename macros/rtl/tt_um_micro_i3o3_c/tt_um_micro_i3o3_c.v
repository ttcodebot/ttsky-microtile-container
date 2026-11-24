/*
 * tt_um_micro_i3o3_c: micro tile with 3 uio inputs and 3 uio outputs (counter with uio).
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_micro_i3o3_c (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [2:0] uio_in,   // uio inputs (container pins uio[4:2])
    output wire [2:0] uio_out,  // uio outputs (container pins uio[7:5])
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // While in reset: a combinational loopback through every pin
  localparam [7:0] K = 8'h5a;
  wire [7:0] lb_uo = {ui_in[7:3], uio_in} ^ K;
  wire [2:0] lb_out = ui_in[7:5] ^ K[7:5];

  reg rst_n_i;
  reg [7:0] cnt;

  always @(posedge clk or negedge rst_n)
    if (~rst_n) rst_n_i <= 1'b0;
    else rst_n_i <= 1'b1;

  always @(posedge clk or negedge rst_n_i)
    if (~rst_n_i) cnt <= 0;
    else cnt <= cnt + 1;

  assign uo_out  = rst_n ? cnt ^ K : lb_uo;
  assign uio_out = rst_n ? cnt[2:0] : lb_out;

endmodule
