/*
 * tt_um_micro_uio6_b: micro tile with 6 uio pins (synthetic capacity design, 4 stages + 0 bits, with uio).
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_micro_uio6_b (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [5:0] uio_in,   // IOs: Input path
    output wire [5:0] uio_out,  // IOs: Output path
    output wire [5:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // While in reset: a combinational loopback through every pin
  localparam [7:0] K = 8'h3c;
  wire [7:0] lb_uo = {ui_in[7:6], uio_in} ^ K;
  wire [5:0] lb_oe = ui_in[5:0];
  wire [5:0] lb_out = ui_in[7:2] ^ K[7:2];

  localparam N = 4;

  reg [3:0] s[0:N-1];
  wire [7:0] uio8 = {2'b0, uio_in};
  wire [7:0] fb = {s[N-1], s[N-2]} ^ ui_in ^ uio8;

  integer i;
  always @(posedge clk) begin
    if (!rst_n) begin
      for (i = 0; i < N; i = i + 1) s[i] <= 4'd1 + i[3:0] * 4'd7;
    end else begin
      s[0] <= fb[3:0] + fb[7:4];
      for (i = 1; i < N; i = i + 1)
        s[i] <= (s[i-1] + {s[i][0], s[i][3:1]}) ^ (s[(i*5+3)%N] & {4{ui_in[i%8]}});
    end
  end

  wire [7:0] run_uo = {s[N-1], s[N/2]} ^ {s[N/3], s[0]};
  wire [7:0] run_uio = {s[1], s[2]} ^ {s[3], s[N-1]};
  wire [7:0] run_oe = {s[2], s[N-2]};

  assign uo_out  = rst_n ? run_uo : lb_uo;
  assign uio_out = rst_n ? run_uio[5:0] : lb_out;
  assign uio_oe  = rst_n ? run_oe[5:0] : lb_oe;

endmodule
