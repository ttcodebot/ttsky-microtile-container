/*
 * Copyright (c) 2026 Alexander Co Abad
 * SPDX-License-Identifier: Apache-2.0
 *
 * Maligayang Pasko - a pixel-art Christmas tree on VGA, for the Tiny Tapeout
 * micro tile (clk, rst_n, ui_in, uo_out only).
 *
 * 640x480 at 60 Hz from a 25.175 MHz clock, 2 bits per colour on the TinyVGA
 * Pmod pinout.  The picture is an 80 x 60 grid of 8-pixel cells drawn with
 * combinational logic only, no frame buffer:
 *   - a star on top that blinks through four colours, a four-tier fir tree
 *     with darker edges, striped needles and colour-cycling lights, a trunk
 *     and a snow-covered ground
 *   - snow falling in the night sky
 *   - "MALIGAYANG PASKO!" in red (or green) on the snow, a 3x5-cell font of 12 glyphs
 */

`default_nettype none

module tt_um_MaligayangPasko (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // inputs: all low (or unconnected pulled low) is the plain scene
  wire pause     = ui_in[0];    // freeze the animation (snow, lights and star)
  wire snow_off  = ui_in[1];    // hide the falling snow
  wire sky_black = ui_in[2];    // black sky instead of dark blue
  wire text_grn  = ui_in[3];    // greeting in green instead of red

  // ui_in[7:4] are not used: tie them off so that the linter does not warn (no logic is generated)
  wire _unused = &{ui_in[7:4], 1'b0};

  // ---------------------------------------------------------------- timing
  // H: 640 visible, 16 front porch, 96 sync, 48 back porch = 800
  // V: 480 visible, 10 front porch,  2 sync, 33 back porch = 525
  reg [9:0] hc;
  reg [9:0] vc;
  reg [5:0] t;                  // frame counter

  wire h_end = (hc == 10'd799);
  wire v_end = (vc == 10'd524);

  always @(posedge clk) begin
    if (!rst_n) begin
      hc <= 10'd0;
      vc <= 10'd0;
      t  <= 6'd0;
    end else begin
      hc <= h_end ? 10'd0 : hc + 10'd1;
      if (h_end) begin
        vc <= v_end ? 10'd0 : vc + 10'd1;
        if (v_end && !pause) t <= t + 6'd1;
      end
    end
  end

  wire hs_n   = ~((hc[9:4] >= 6'd41) && (hc[9:4] < 6'd47));   // 656 .. 751
  wire vs_n   = ~(vc[9:1] == 9'd245);                         // 490, 491
  wire active = ~(hc[9] & (hc[8] | hc[7])) &                  // hc < 640
                ~(vc[9] | (&vc[8:5]));                        // vc < 480

  // ------------------------------------------------------------------ grid
  // 80 x 60 cells of 8 pixels.  Rows: 12..15 star, 16..47 tree (4 tiers of 8 rows),
  // 48..51 trunk, 52..59 snow on the ground; the sky is above and beside the tree.
  wire [6:0] cx = hc[9:3];
  wire [5:0] cy = vc[8:3];
  wire [2:0] r  = cy[2:0];                 // row inside a tier

  // distance from the centre line (between columns 39 and 40)
  wire [6:0] u  = cx - 7'd40;
  wire [5:0] dx = u[6] ? ~u[5:0] : u[5:0];

  // tree: half-width in cells = 1 + 4 * tier + row in tier, tier = cy[5:3] - 2
  wire [4:0] hw       = {cy[5:3], 2'b00} - 5'd7 + {2'b00, r};
  wire [6:0] tdiff    = {2'b00, hw} - {1'b0, dx};
  wire       tree_row = cy[5] ^ cy[4];                   // rows 16..47
  wire       in_tree  = tree_row & ~tdiff[6];
  wire       edge_c   = in_tree & (tdiff[5:0] == 6'd0);

  wire center2 = (dx[5:1] == 5'd0);                      // columns 38..41
  wire trunk   = (cy[5:2] == 4'b1100) & center2;         // rows 48..51, four cells wide
  wire ground  = cy[5] & cy[4] & (cy[3] | cy[2]);        // rows 52..59

  // star: a small diamond of cells on rows 12..15 that blinks and cycles through four colours
  wire star = (cy[5:2] == 4'b0011) & center2 & (~dx[0] | (cy[1] ^ cy[0]));

  // "MALIGAYANG PASKO!": 17 characters, rows 53..57.  M is 5 cells wide (columns 6..10);
  // the other 16 characters are 3 cells wide at a pitch of 4 starting at column 12.
  wire [4:0] ci   = cx[6:2] - 5'd3;        // 0..15 for columns 12..75
  wire [1:0] ccol = cx[1:0];               // 0..2 (3 is the gap)
  wire [2:0] crow = cy[2:0];               // glyph rows are 53..57 (crow 5, 6, 7, 0, 1)
  reg  [3:0] gid;
  always @* begin
    case (ci[3:0])
      4'd0: gid = 4'd1;  4'd1: gid = 4'd2;  4'd2: gid = 4'd3;  4'd3: gid = 4'd4;  4'd4: gid = 4'd1;
      4'd5: gid = 4'd5;  4'd6: gid = 4'd1;  4'd7: gid = 4'd6;  4'd8: gid = 4'd4;
      4'd10: gid = 4'd7; 4'd11: gid = 4'd1; 4'd12: gid = 4'd8; 4'd13: gid = 4'd9; 4'd14: gid = 4'd10;
      4'd15: gid = 4'd11;
      default: gid = 4'd15;                // blank
    endcase
  end
  // Glyphs stored LSB-left (bit 0 = left column) to avoid column subtraction
  reg [14:0] gl;
  always @* begin
    case (gid)
      4'd1:  gl = 15'b101_101_111_101_111;   // A
      4'd2:  gl = 15'b111_001_001_001_001;   // L
      4'd3:  gl = 15'b111_010_010_010_111;   // I
      4'd4:  gl = 15'b111_101_101_001_111;   // G
      4'd5:  gl = 15'b010_010_111_101_101;   // Y
      4'd6:  gl = 15'b101_101_101_101_111;   // N
      4'd7:  gl = 15'b001_001_111_101_111;   // P
      4'd8:  gl = 15'b111_100_111_001_111;   // S
      4'd9:  gl = 15'b101_101_011_101_101;   // K
      4'd10: gl = 15'b111_101_101_101_111;   // O
      4'd11: gl = 15'b010_000_010_010_010;   // !
      default: gl = 15'b000_000_000_000_000;
    endcase
  end
  reg [2:0] gr;
  reg [4:0] mr;                            // M stored LSB-left
  always @* begin
    case (crow)
      3'd5: begin gr = gl[2:0];   mr = 5'b10001; end  // row 53
      3'd6: begin gr = gl[5:3];   mr = 5'b11011; end  // row 54
      3'd7: begin gr = gl[8:6];   mr = 5'b10101; end  // row 55
      3'd0: begin gr = gl[11:9];  mr = 5'b10001; end  // row 56
      3'd1: begin gr = gl[14:12]; mr = 5'b10001; end  // row 57
      default: begin gr = 3'b000; mr = 5'b00000; end
    endcase
  end
  wire [6:0] mx     = cx - 7'd6;
  wire       m_area = (mx[6:3] == 4'd0) & (~mx[2] | (~mx[1] & ~mx[0]));
  wire       text   = ground & ((m_area & mr[mx[2:0]]) | (~ci[4] & (ccol != 2'd3) & gr[ccol]));

  // lights: every fourth cell inside the tree, the colour cycles with the frame count
  wire light = in_tree & ~edge_c & (&(cx[1:0] ^ cy[1:0]));
  wire [1:0] lc = {cx[2], cy[2]} ^ t[5:4];

  // falling snow: a 4x4 pixel flake in every fourth 8-pixel column, falling monotonically downward
  wire [3:0] ph    = cx[6:3] ^ {cx[4:3], cx[6:5]};
  wire       snow  = ~snow_off & (cx[1:0] == 2'b01) & ~hc[2] & ~vc[2] & ((cy[3:0] + ph) == t[5:2]);

  // ----------------------------------------------------------------- colour
  reg [5:0] rgb;                // {R1 R0 G1 G0 B1 B0}
  always @* begin
    if (star) begin
      case (t[5:4])
        2'd0:    rgb = 6'b10_00_00;     // dark red (almost off)
        2'd1:    rgb = 6'b11_00_00;     // red
        2'd2:    rgb = 6'b11_11_00;     // yellow
        default: rgb = 6'b11_01_00;     // orange
      endcase
    end
    else if (light)         rgb = (lc == 2'd0) ? 6'b11_00_00 :
                                  (lc == 2'd1) ? 6'b11_11_00 :
                                  (lc == 2'd2) ? 6'b11_11_11 : 6'b00_11_11;
    else if (edge_c)        rgb = 6'b00_01_00;
    else if (in_tree)       rgb = cy[0] ? 6'b00_11_00 : 6'b00_10_00;
    else if (trunk)         rgb = 6'b10_01_00;
    else if (text)          rgb = {{2{~text_grn}}, {2{text_grn}}, 2'b00};
    else if (ground | snow) rgb = 6'b11_11_11;
    else                    rgb = {5'b00000, ~sky_black};
  end

  // ---------------------------------------------------------------- output
  // TinyVGA Pmod: uo[0]=R1 [1]=G1 [2]=B1 [3]=VS [4]=R0 [5]=G0 [6]=B0 [7]=HS
  reg [7:0] out;
  always @(posedge clk) begin
    out <= {hs_n, active ? {rgb[0], rgb[2], rgb[4]} : 3'b000,
            vs_n, active ? {rgb[1], rgb[3], rgb[5]} : 3'b000};
  end
  assign uo_out = out;

endmodule
