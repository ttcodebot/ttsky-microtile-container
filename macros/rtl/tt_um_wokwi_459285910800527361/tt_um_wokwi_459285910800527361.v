/* Automatically generated from https://wokwi.com/projects/459285910800527361 */

`default_nettype none

// verilator lint_off UNUSEDSIGNAL
// verilator lint_off PINCONNECTEMPTY

module tt_um_wokwi_459285910800527361(
  input  wire [7:0] ui_in,    // Dedicated inputs
  output wire [7:0] uo_out,    // Dedicated outputs
  input clk,
  input rst_n
);
  wire net1 = clk;
  wire net2 = rst_n;
  wire net3 = ui_in[0];
  wire net4 = ui_in[1];
  wire net5 = ui_in[2];
  wire net6 = ui_in[3];
  wire net7 = ui_in[4];
  wire net8 = ui_in[5];
  wire net9 = ui_in[6];
  wire net10 = ui_in[7];
  wire net11;
  wire net12;
  wire net13;
  wire net14;
  wire net15;
  wire net16;
  wire net17;
  wire net18;
  wire net19 = 1'b0;
  wire net20 = 1'b1;
  wire net21 = 1'b1;
  wire net22 = 1'b0;
  wire net23 = 1'b1;
  wire net24;
  wire net25;
  wire net26;
  wire net27;
  wire net28;
  wire net29;
  wire net30;
  wire net31 = 1'b0;
  wire net32 = 1'b0;
  wire net33 = 1'b0;
  wire net34;
  wire net35;
  wire net36;
  wire net37;
  wire net38;
  wire net39;
  wire net40;
  wire net41;
  wire net42;
  wire net43;
  wire net44;
  wire net45;
  wire net46;
  wire net47;
  wire net48;
  wire net49;
  wire net50;
  wire net51;
  wire net52;
  wire net53;
  wire net54;
  wire net55;
  wire net56;
  wire net57;
  wire net58;
  wire net59;
  wire net60;
  wire net61;
  wire net62;
  wire net63;
  wire net64;
  wire net65;
  wire net66;
  wire net67;
  wire net68 = 1'b0;
  wire net69 = 1'b0;
  wire net70 = 1'b0;
  wire net71 = 1'b0;
  wire net72 = 1'b0;
  wire net73 = 1'b0;

  assign uo_out[0] = net11;
  assign uo_out[1] = net12;
  assign uo_out[2] = net13;
  assign uo_out[3] = net14;
  assign uo_out[4] = net15;
  assign uo_out[5] = net16;
  assign uo_out[6] = net17;
  assign uo_out[7] = net18;

  dffr_cell flop1 (
    .d (net24),
    .clk (net1),
    .r (net25),
    .q (net11),
    .notq (net24)
  );
  dffr_cell flop2 (
    .d (net26),
    .clk (net1),
    .r (net25),
    .q (net12),
    .notq ()
  );
  dffr_cell flop3 (
    .d (net27),
    .clk (net1),
    .r (net25),
    .q (net13),
    .notq ()
  );
  dffr_cell flop4 (
    .d (net28),
    .clk (net1),
    .r (net25),
    .q (net14),
    .notq ()
  );
  not_cell not1 (
    .in (net2),
    .out (net25)
  );
  xor_cell xor1 (
    .a (net12),
    .b (net11),
    .out (net26)
  );
  and_cell and1 (
    .a (net11),
    .b (net12),
    .out (net29)
  );
  xor_cell xor3 (
    .a (net13),
    .b (net29),
    .out (net27)
  );
  and_cell and2 (
    .a (net29),
    .b (net13),
    .out (net30)
  );
  xor_cell xor4 (
    .a (net14),
    .b (net30),
    .out (net28)
  );
  and_cell and5 (
    .a (net34),
    .b (net35),
    .out (net36)
  );
  and_cell and4 (
    .a (net3),
    .b (net4),
    .out (net34)
  );
  dffr_cell flop5 (
    .d (net37),
    .clk (net1),
    .r (net25),
    .q (net38),
    .notq ()
  );
  dffr_cell flop6 (
    .d (net39),
    .clk (net1),
    .r (net25),
    .q (net40),
    .notq ()
  );
  dffr_cell flop7 (
    .d (net41),
    .clk (net1),
    .r (net25),
    .q (net42),
    .notq ()
  );
  dffr_cell flop8 (
    .d (net43),
    .clk (net1),
    .r (net25),
    .q (net44),
    .notq ()
  );
  dffr_cell flop9 (
    .d (net45),
    .clk (net1),
    .r (net25),
    .q (net46),
    .notq ()
  );
  dffr_cell flop10 (
    .d (net47),
    .clk (net1),
    .r (net25),
    .q (net48),
    .notq ()
  );
  dffr_cell flop11 (
    .d (net49),
    .clk (net1),
    .r (net25),
    .q (net50),
    .notq ()
  );
  dffr_cell flop12 (
    .d (net51),
    .clk (net1),
    .r (net25),
    .q (net52),
    .notq ()
  );
  and_cell and7 (
    .a (net53),
    .b (net5),
    .out (net54)
  );
  and_cell and8 (
    .a (net55),
    .b (net4),
    .out (net53)
  );
  not_cell not2 (
    .in (net5),
    .out (net35)
  );
  not_cell not4 (
    .in (net3),
    .out (net55)
  );
  and_cell and9 (
    .a (net34),
    .b (net5),
    .out (net56)
  );
  not_cell not3 (
    .in (net10),
    .out (net57)
  );
  and_cell and10 (
    .a (net38),
    .b (net58),
    .out (net59)
  );
  and_cell and11 (
    .a (net40),
    .b (net58),
    .out (net60)
  );
  and_cell and12 (
    .a (net42),
    .b (net58),
    .out (net61)
  );
  and_cell and13 (
    .a (net44),
    .b (net58),
    .out (net62)
  );
  and_cell and14 (
    .a (net56),
    .b (net10),
    .out (net58)
  );
  and_cell and15 (
    .a (net57),
    .b (net56),
    .out (net63)
  );
  and_cell and16 (
    .a (net46),
    .b (net63),
    .out (net64)
  );
  and_cell and17 (
    .a (net48),
    .b (net63),
    .out (net65)
  );
  and_cell and18 (
    .a (net50),
    .b (net63),
    .out (net66)
  );
  and_cell and19 (
    .a (net52),
    .b (net63),
    .out (net67)
  );
  or_cell or1 (
    .a (net64),
    .b (net59),
    .out (net15)
  );
  or_cell or2 (
    .a (net65),
    .b (net60),
    .out (net16)
  );
  or_cell or3 (
    .a (net66),
    .b (net61),
    .out (net17)
  );
  or_cell or4 (
    .a (net67),
    .b (net62),
    .out (net18)
  );
  mux_cell mux1 (
    .a (net38),
    .b (net6),
    .sel (net36),
    .out (net37)
  );
  mux_cell mux2 (
    .a (net40),
    .b (net7),
    .sel (net36),
    .out (net39)
  );
  mux_cell mux3 (
    .a (net42),
    .b (net8),
    .sel (net36),
    .out (net41)
  );
  mux_cell mux4 (
    .a (net44),
    .b (net9),
    .sel (net36),
    .out (net43)
  );
  mux_cell mux5 (
    .a (net46),
    .b (net6),
    .sel (net54),
    .out (net45)
  );
  mux_cell mux6 (
    .a (net48),
    .b (net7),
    .sel (net54),
    .out (net47)
  );
  mux_cell mux7 (
    .a (net50),
    .b (net8),
    .sel (net54),
    .out (net49)
  );
  mux_cell mux8 (
    .a (net52),
    .b (net9),
    .sel (net54),
    .out (net51)
  );
endmodule
