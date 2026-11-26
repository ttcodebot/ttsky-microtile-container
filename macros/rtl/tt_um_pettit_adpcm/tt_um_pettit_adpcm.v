/*
 * Copyright (c) 2026 Ken Pettit
 * SPDX-License-Identifier: Apache-2.0
 *
 * tt_um_pettit_adpcm - a streaming ADPCM decoder with a 1 MHz PWM output,
 * for the Tiny Tapeout micro tile (70.38 x 51.68 um of sky130; clk, rst_n,
 * ui_in and uo_out only).
 *
 * The host (the RP2350: a PIO state machine fed by DMA) puts a 4-bit code on
 * ui[3:0] and raises the strobe ui[4], once a sample.  The codec ("uADPCM",
 * tools/uadpcm.py) is an adaptive differential PCM whose two updates are
 * shifts and adds of the step size, with no table.  For a code {sgn, m[2:0]},
 * a 16-bit predictor (0x8000 after reset) and a 16-bit step (16 after reset):
 *
 *     pred -/+= step>>3 + (m2 ? step : 0) + (m1 ? step>>1 : 0) + (m0 ? step>>2 : 0)
 *     step   = m2 ? step + (step >> (3 - m[1:0])) : step - (step >> 4)
 *
 * Everything is bit-serial.  The 16-bit predictor and the 16-bit step
 * are two shift registers that rotate all the time, least significant bit
 * first, once every 16 clocks; one full adder adds (or subtracts) a tap of
 * the step register, which is the step shifted right, to whichever register
 * is being updated as it goes by.  A sample is five such passes, 80 clocks.
 * There are no clamps: the encoder never emits a code that would overflow.
 *
 * With a 32 MHz clock two rotations are one 1 MHz PWM period.  At its start
 * the registers are back in place and the top 5 bits of the predictor are
 * taken as the duty; the next 5 feed a first-order sigma-delta whose carry
 * lengthens the pulse by one clock.  In reset the output toggles every
 * clock, which is mid-scale too.  uo[6] is the complement of the PWM.
 */

`default_nettype none

module tt_um_pettit_adpcm #(
    parameter SD = 5            // sigma-delta bits below the 5 PWM bits
) (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset (16 clocks or more)
);

  wire       sgn    = ui_in[3];     // the code: held by the host until the next one
  wire [2:0] m      = ui_in[2:0];
  wire       strobe = ui_in[4];     // rising edge: a new code is on ui[3:0]

  // ----------------------------------------------------------------- time
  reg  [4:0] ramp;                  // the PWM period; ramp[3:0] is the bit going by
  wire [3:0] i     = ramp[3:0];
  wire       last  = &i;            // the last bit of a pass
  wire       first = ~|i;

  // ---------------------------------------------------------- the strobe
  reg [2:0] sync;
  reg       pend;                   // a code is waiting for the next pass
  wire      rise = sync[1] & ~sync[2];

  // --------------------------------------------------------- the datapath
  reg [15:0] pred, step;
  reg  [2:0] phase;                 // 0 idle, 1..4 the predictor's passes, 5 the step's
  reg        init;                  // the pass after reset: loads 0x8000 and 16
  reg        cy;

  // idle passes add nothing to the predictor, which is the same as leaving it
  wire to_step = (phase == 3'd5);
  wire to_pred = ~to_step;

  // this pass: add or subtract step >> k, or nothing
  reg [2:0] k;
  reg       en, sub;
  always @* begin
    case (phase)
      3'd1:    begin k = 3'd3; en = 1'b1; sub = sgn; end
      3'd2:    begin k = 3'd0; en = m[2]; sub = sgn; end
      3'd3:    begin k = 3'd1; en = m[1]; sub = sgn; end
      3'd4:    begin k = 3'd2; en = m[0]; sub = sgn; end
      3'd5:    begin k = m[2] ? {1'b0, ~m[1:0]} : 3'd4; en = 1'b1; sub = ~m[2]; end
      default: begin k = 3'd0; en = 1'b0; sub = 1'b0; end
    endcase
  end

  // bit i + k of the step is at step[k]; past bit 15 it is 0
  wire [4:0] ik   = {1'b0, i} + {2'b00, k};
  wire       tap  = step[k] & ~ik[4];
  wire       a    = to_step ? step[0] : pred[0];
  wire       b    = en & (tap ^ sub);
  wire       cin  = first ? (en & sub) : cy;
  wire       sum  = a ^ b ^ cin;
  wire       cout = (a & b) | (a & cin) | (b & cin);

  always @(posedge clk) begin
    ramp <= rst_n ? ramp + 5'd1 : 5'd0;
    sync <= {sync[1:0], strobe};
    cy   <= cout;

    pred <= {init ? last       : (to_pred ? sum : pred[0]), pred[15:1]};
    step <= {init ? (i == 4'd4) : (to_step ? sum : step[0]), step[15:1]};

    if (!rst_n) begin
      init  <= 1'b1;
      phase <= 3'd0;
      pend  <= 1'b0;
    end else begin
      if (rise) pend <= 1'b1;
      if (last) begin
        init <= 1'b0;
        if (init)               phase <= 3'd0;
        else if (phase == 3'd0) begin
          if (pend) begin
            phase <= 3'd1;
            if (!rise) pend <= 1'b0;
          end
        end else                phase <= (phase == 3'd5) ? 3'd0 : phase + 3'd1;
      end
    end
  end

  // ------------------------------------------------------------------ PWM
  reg [4:0]    duty;
  reg [SD-1:0] acc;
  reg          extra;
  reg          pwm;
  wire         zero = (ramp == 5'd0);
  wire         load = zero & ~init;     // not before the constants are in
  always @(posedge clk) begin
    if (!rst_n) begin
      {extra, acc} <= {(SD + 1) {1'b0}};
      duty         <= 5'd16;
    end else if (load) begin
      {extra, acc} <= {1'b0, acc} + {1'b0, pred[10:11-SD]};
      duty         <= pred[15:11];
    end
    // High from ramp 1 for duty (+1) clocks.  In reset the output toggles
    // every clock: half the clock's frequency at 50%, which a low-pass filter
    // cannot tell from the mid-scale PWM that follows, so going into reset
    // and coming out of it are silent.
    pwm <= rst_n ? (~zero & ({1'b0, ramp} <= {1'b0, duty} + {5'd0, extra})) : ~pwm;
  end

  // uo[7] PWM (the audio Pmod's pin), uo[6] its complement (a speaker
  // between the two sees twice the swing), uo[5] busy, uo[4:0] the duty
  assign uo_out = {pwm, ~pwm, pend | (phase != 3'd0), duty};

endmodule
