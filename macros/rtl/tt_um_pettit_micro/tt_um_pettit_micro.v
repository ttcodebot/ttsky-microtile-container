/*
 * Copyright (c) 2026 Ken Pettit
 * SPDX-License-Identifier: Apache-2.0
 *
 * tt_um_pettit_micro - a VGA demo for the Tiny Tapeout micro tile
 * (70.38 x 51.68 um of sky130: about 80 flops' worth of room, and only
 * clk, rst_n, ui_in and uo_out).
 *
 * 640x480 at 60 Hz from a 25.175 MHz clock (25 MHz works on most monitors),
 * 2 bits per colour on the TinyVGA Pmod pinout, ordered dither to make the
 * 2 bits look like 4.  One 8-bit adder draws everything:
 *
 *     v = op(x, y) + t        x, y in 2-pixel units, t = the frame count
 *
 * and v goes through a palette of three triangle waves.  op is one of
 *     x ^ y   "munching squares" (PDP-1, 1962) in colour
 *     x & y   a Sierpinski gasket of colour steps
 *     x | y   its complement
 *     y       a scrolling gradient
 * and (x & v) == 0 can be laid over any of them as a mask: a Sierpinski
 * carpet at full brightness on the stippled picture.  That is eight scenes;
 * the top of the frame counter steps through them every 4.3 seconds.
 */

`default_nettype none

module tt_um_pettit_micro (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire [2:0] sel      = ui_in[2:0];   // scene (added to the automatic one)
  wire       hold     = ui_in[3];     // stop stepping through the scenes
  wire       nodither = ui_in[4];     // plain 2-bit colour
  wire       pause    = ui_in[5];     // freeze the animation

  // ---------------------------------------------------------------- timing
  // H: 640 visible, 16 front porch, 96 sync, 48 back porch = 800
  // V: 480 visible, 10 front porch,  2 sync, 33 back porch = 525
  reg [9:0] hc;
  reg [9:0] vc;
  reg [10:0] t;               // frame counter: [7:0] animates, [10:8] is the scene

  wire h_end = (hc == 10'd799);
  wire v_end = (vc == 10'd524);

  always @(posedge clk) begin
    if (!rst_n) begin
      hc <= 10'd0;
      vc <= 10'd0;
      t  <= 11'd0;
    end else begin
      hc <= h_end ? 10'd0 : hc + 10'd1;
      if (h_end) begin
        vc <= v_end ? 10'd0 : vc + 10'd1;
        if (v_end && !pause) t <= t + 11'd1;
      end
    end
  end

  wire hs_n   = ~((hc[9:4] >= 6'd41) && (hc[9:4] < 6'd47));   // 656 .. 751
  wire vs_n   = ~(vc[9:1] == 9'd245);                         // 490, 491
  wire active = ~(hc[9] & (hc[8] | hc[7])) &                  // hc < 640
                ~(vc[9] | (&vc[8:5]));                        // vc < 480

  // --------------------------------------------------------------- picture
  wire [7:0] x = hc[8:1];
  wire [7:0] y = vc[8:1];

  wire [2:0] scene = sel ^ (hold ? 3'd0 : t[10:8]);
  wire [1:0] op    = scene[1:0];
  wire       sier  = scene[2];

  wire [7:0] p = (op == 2'd0) ? x ^ y :
                 (op == 2'd1) ? x & y :
                 (op == 2'd2) ? y     :
                                x | y;
  wire [7:0] v = p + t[7:0];

  // Sierpinski: where x and v share a 1 bit the picture is stippled to half
  // brightness, which leaves the carpet at full brightness
  wire       hit = ~|(x & v);
  wire       chk = hc[0] ^ vc[0];
  wire       off = sier & ~hit & chk;

  // palette: three triangle waves of v, an octave apart
  wire [3:0] r4 = v[7] ? ~v[6:3] : v[6:3];
  wire [3:0] g4 = v[6] ? ~v[5:2] : v[5:2];
  wire [3:0] b4 = v[5] ?  v[4:1] : ~v[4:1];

  // 2x2 ordered dither of 4 bits down to 2
  wire [1:0] thr = nodither ? 2'd3 : {chk, vc[0]};

  function [1:0] dith(input [3:0] c, input [1:0] th);
    dith = ((c[1:0] > th) && (c[3:2] != 2'd3)) ? c[3:2] + 2'd1 : c[3:2];
  endfunction

  wire       show = active & ~off;
  wire [1:0] r = dith(r4, thr);
  wire [1:0] g = dith(g4, thr);
  wire [1:0] b = dith(b4, thr);

  // ---------------------------------------------------------------- output
  // TinyVGA Pmod: uo[0]=R1 [1]=G1 [2]=B1 [3]=VS [4]=R0 [5]=G0 [6]=B0 [7]=HS
  reg [7:0] out;
  always @(posedge clk) begin
    out <= {hs_n, show ? {b[0], g[0], r[0]} : 3'b000,
            vs_n, show ? {b[1], g[1], r[1]} : 3'b000};
  end
  assign uo_out = out;

endmodule
