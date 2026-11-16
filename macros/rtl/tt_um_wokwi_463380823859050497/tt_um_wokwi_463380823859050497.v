/* Automatically generated from https://wokwi.com/projects/463380823859050497 */

`default_nettype none

// verilator lint_off UNUSEDSIGNAL
// verilator lint_off PINCONNECTEMPTY

module tt_um_wokwi_463380823859050497(
  input  wire [7:0] ui_in,    // Dedicated inputs
  output wire [7:0] uo_out,    // Dedicated outputs
  input clk,
  input rst_n
);
  wire net1 = clk;
  wire net2 = rst_n;
  wire net3 = ui_in[3];
  wire net4 = ui_in[4];
  wire net5 = ui_in[5];
  wire net6 = ui_in[6];
  wire net7 = ui_in[7];
  wire net8;
  wire net9;
  wire net10;
  wire net11;
  wire net12;
  wire net13;
  wire net14;
  wire net15;
  wire net16;
  wire net17;
  wire net18;
  wire net19;
  wire net20;
  wire net21;
  wire net22;
  wire net23;
  wire net24;
  wire net25;
  wire net26;
  wire net27;
  wire net28;
  wire net29;
  wire net30;
  wire net31;
  wire net32;
  wire net33;
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
  wire net68;
  wire net69;
  wire net70;
  wire net71;
  wire net72;
  wire net73;
  wire net74;
  wire net75;
  wire net76;
  wire net77;
  wire net78;
  wire net79;
  wire net80;
  wire net81;
  wire net82;
  wire net83;
  wire net84;
  wire net85;
  wire net86;
  wire net87;
  wire net88;
  wire net89;
  wire net90;
  wire net91;
  wire net92;
  wire net93;
  wire net94;
  wire net95;
  wire net96;
  wire net97;
  wire net98;
  wire net99;
  wire net100;
  wire net101;
  wire net102;
  wire net103;
  wire net104;
  wire net105;
  wire net106;
  wire net107;
  wire net108;
  wire net109;
  wire net110;
  wire net111;
  wire net112;
  wire net113 = 1'b1;
  wire net114 = 1'b1;
  wire net115 = 1'b0;
  wire net116 = 1'b1;
  wire net117 = 1'b0;
  wire net118;
  wire net119;
  wire net120;
  wire net121;
  wire net122;
  wire net123;
  wire net124;
  wire net125;
  wire net126;
  wire net127;
  wire net128;
  wire net129;
  wire net130;
  wire net131;
  wire net132;
  wire net133;
  wire net134;
  wire net135;
  wire net136;
  wire net137;

  assign uo_out[0] = net8;
  assign uo_out[1] = net9;
  assign uo_out[2] = net10;
  assign uo_out[3] = net11;
  assign uo_out[4] = net12;
  assign uo_out[5] = net13;
  assign uo_out[6] = net14;
  assign uo_out[7] = 0;

  buffer_cell input_w (
    .in (net15),
    .out (net16)
  );
  not_cell input_not_w (
    .in (net15),
    .out (net17)
  );
  buffer_cell input_x (
    .in (net18),
    .out (net19)
  );
  not_cell input_not_x (
    .in (net18),
    .out (net20)
  );
  buffer_cell input_y (
    .in (net21),
    .out (net22)
  );
  not_cell input_not_y (
    .in (net21),
    .out (net23)
  );
  buffer_cell input_z (
    .in (net24),
    .out (net25)
  );
  not_cell input_not_z (
    .in (net24),
    .out (net26)
  );
  and_cell gate_and_0 (
    .a (net17),
    .b (net20),
    .out (net27)
  );
  and_cell gate_and_1 (
    .a (net22),
    .b (net25),
    .out (net28)
  );
  and_cell gate_and_2 (
    .a (net16),
    .b (net20),
    .out (net29)
  );
  and_cell gate_and_3 (
    .a (net23),
    .b (net26),
    .out (net30)
  );
  and_cell gate_and_4 (
    .a (net16),
    .b (net20),
    .out (net31)
  );
  and_cell gate_and_5 (
    .a (net23),
    .b (net26),
    .out (net32)
  );
  and_cell gate_and_6 (
    .a (net17),
    .b (net19),
    .out (net33)
  );
  and_cell gate_and_7 (
    .a (net23),
    .b (net26),
    .out (net34)
  );
  and_cell gate_and_8 (
    .a (net17),
    .b (net20),
    .out (net35)
  );
  and_cell gate_and_9 (
    .a (net22),
    .b (net26),
    .out (net36)
  );
  and_cell gate_and_10 (
    .a (net16),
    .b (net20),
    .out (net37)
  );
  and_cell gate_and_11 (
    .a (net23),
    .b (net26),
    .out (net38)
  );
  and_cell gate_and_12 (
    .a (net17),
    .b (net22),
    .out (net39)
  );
  and_cell gate_and_13 (
    .a (net26),
    .b (net26),
    .out (net40)
  );
  and_cell gate_and_14 (
    .a (net17),
    .b (net20),
    .out (net41)
  );
  and_cell gate_and_15 (
    .a (net25),
    .b (net25),
    .out (net42)
  );
  and_cell gate_and_16 (
    .a (net17),
    .b (net19),
    .out (net43)
  );
  and_cell gate_and_17 (
    .a (net26),
    .b (net26),
    .out (net44)
  );
  and_cell gate_and_18 (
    .a (net17),
    .b (net20),
    .out (net45)
  );
  and_cell gate_and_19 (
    .a (net22),
    .b (net22),
    .out (net46)
  );
  and_cell gate_and_20 (
    .a (net17),
    .b (net19),
    .out (net47)
  );
  and_cell gate_and_21 (
    .a (net23),
    .b (net25),
    .out (net48)
  );
  and_cell gate_and_22 (
    .a (net20),
    .b (net23),
    .out (net49)
  );
  and_cell gate_and_23 (
    .a (net26),
    .b (net26),
    .out (net50)
  );
  and_cell gate_and_24 (
    .a (net17),
    .b (net23),
    .out (net51)
  );
  and_cell gate_and_25 (
    .a (net25),
    .b (net25),
    .out (net52)
  );
  and_cell gate_and_26 (
    .a (net17),
    .b (net22),
    .out (net53)
  );
  and_cell gate_and_27 (
    .a (net26),
    .b (net26),
    .out (net54)
  );
  and_cell gate_and_28 (
    .a (net20),
    .b (net23),
    .out (net55)
  );
  and_cell gate_and_29 (
    .a (net26),
    .b (net26),
    .out (net56)
  );
  and_cell gate_and_30 (
    .a (net17),
    .b (net23),
    .out (net57)
  );
  and_cell gate_and_31 (
    .a (net25),
    .b (net25),
    .out (net58)
  );
  and_cell gate_and_32 (
    .a (net17),
    .b (net20),
    .out (net59)
  );
  and_cell gate_and_33 (
    .a (net17),
    .b (net22),
    .out (net60)
  );
  and_cell gate_and_34 (
    .a (net26),
    .b (net26),
    .out (net61)
  );
  and_cell gate_and_35 (
    .a (net20),
    .b (net23),
    .out (net62)
  );
  and_cell gate_and_36 (
    .a (net26),
    .b (net26),
    .out (net63)
  );
  and_cell gate_and_37 (
    .a (net17),
    .b (net23),
    .out (net64)
  );
  and_cell gate_and_38 (
    .a (net25),
    .b (net25),
    .out (net65)
  );
  and_cell gate_and_39 (
    .a (net17),
    .b (net19),
    .out (net66)
  );
  and_cell gate_and_40 (
    .a (net22),
    .b (net26),
    .out (net67)
  );
  and_cell gate_and_41 (
    .a (net20),
    .b (net23),
    .out (net68)
  );
  and_cell gate_and_42 (
    .a (net26),
    .b (net26),
    .out (net69)
  );
  and_cell gate_and_43 (
    .a (net17),
    .b (net20),
    .out (net70)
  );
  and_cell gate_and_44 (
    .a (net25),
    .b (net25),
    .out (net71)
  );
  and_cell gate_and_45 (
    .a (net27),
    .b (net28),
    .out (net72)
  );
  and_cell gate_and_46 (
    .a (net29),
    .b (net30),
    .out (net73)
  );
  and_cell gate_and_47 (
    .a (net31),
    .b (net32),
    .out (net74)
  );
  and_cell gate_and_48 (
    .a (net33),
    .b (net34),
    .out (net75)
  );
  and_cell gate_and_49 (
    .a (net35),
    .b (net36),
    .out (net76)
  );
  and_cell gate_and_50 (
    .a (net37),
    .b (net38),
    .out (net77)
  );
  and_cell gate_and_51 (
    .a (net39),
    .b (net40),
    .out (net78)
  );
  and_cell gate_and_52 (
    .a (net41),
    .b (net42),
    .out (net79)
  );
  and_cell gate_and_53 (
    .a (net43),
    .b (net44),
    .out (net80)
  );
  and_cell gate_and_54 (
    .a (net45),
    .b (net46),
    .out (net81)
  );
  and_cell gate_and_55 (
    .a (net47),
    .b (net48),
    .out (net82)
  );
  and_cell gate_and_56 (
    .a (net49),
    .b (net50),
    .out (net83)
  );
  and_cell gate_and_57 (
    .a (net51),
    .b (net52),
    .out (net84)
  );
  and_cell gate_and_58 (
    .a (net53),
    .b (net54),
    .out (net85)
  );
  and_cell gate_and_59 (
    .a (net55),
    .b (net56),
    .out (net86)
  );
  and_cell gate_and_60 (
    .a (net57),
    .b (net58),
    .out (net87)
  );
  and_cell gate_and_61 (
    .a (net60),
    .b (net61),
    .out (net88)
  );
  and_cell gate_and_62 (
    .a (net62),
    .b (net63),
    .out (net89)
  );
  and_cell gate_and_63 (
    .a (net64),
    .b (net65),
    .out (net90)
  );
  and_cell gate_and_64 (
    .a (net67),
    .b (net66),
    .out (net91)
  );
  and_cell gate_and_65 (
    .a (net68),
    .b (net69),
    .out (net92)
  );
  and_cell gate_and_66 (
    .a (net70),
    .b (net71),
    .out (net93)
  );
  or_cell gate_or_0 (
    .a (net72),
    .b (net73),
    .out (net94)
  );
  or_cell gate_or_1 (
    .a (net74),
    .b (net75),
    .out (net95)
  );
  or_cell gate_or_2 (
    .a (net76),
    .b (net76),
    .out (net96)
  );
  or_cell gate_or_3 (
    .a (net77),
    .b (net78),
    .out (net97)
  );
  or_cell gate_or_4 (
    .a (net79),
    .b (net80),
    .out (net98)
  );
  or_cell gate_or_5 (
    .a (net81),
    .b (net82),
    .out (net99)
  );
  or_cell gate_or_6 (
    .a (net83),
    .b (net83),
    .out (net100)
  );
  or_cell gate_or_7 (
    .a (net84),
    .b (net85),
    .out (net101)
  );
  or_cell gate_or_8 (
    .a (net86),
    .b (net86),
    .out (net102)
  );
  or_cell gate_or_9 (
    .a (net87),
    .b (net59),
    .out (net103)
  );
  or_cell gate_or_10 (
    .a (net88),
    .b (net89),
    .out (net104)
  );
  or_cell gate_or_11 (
    .a (net90),
    .b (net91),
    .out (net105)
  );
  or_cell gate_or_12 (
    .a (net92),
    .b (net93),
    .out (net106)
  );
  or_cell gate_or_13 (
    .a (net95),
    .b (net96),
    .out (net107)
  );
  or_cell gate_or_14 (
    .a (net97),
    .b (net98),
    .out (net108)
  );
  or_cell gate_or_15 (
    .a (net99),
    .b (net100),
    .out (net109)
  );
  or_cell gate_or_16 (
    .a (net102),
    .b (net101),
    .out (net110)
  );
  or_cell gate_or_17 (
    .a (net103),
    .b (net104),
    .out (net111)
  );
  or_cell gate_or_18 (
    .a (net105),
    .b (net106),
    .out (net112)
  );
  buffer_cell output_A (
    .in (net94),
    .out (net8)
  );
  buffer_cell output_B (
    .in (net107),
    .out (net9)
  );
  buffer_cell output_C (
    .in (net108),
    .out (net10)
  );
  buffer_cell output_D (
    .in (net109),
    .out (net11)
  );
  buffer_cell output_E (
    .in (net110),
    .out (net12)
  );
  buffer_cell output_F (
    .in (net111),
    .out (net13)
  );
  buffer_cell output_G (
    .in (net112),
    .out (net14)
  );
  dffr_cell flop1 (
    .d (net118),
    .clk (net1),
    .r (net119),
    .q (net120),
    .notq (net121)
  );
  dffr_cell flop2 (
    .d (net122),
    .clk (net1),
    .r (net119),
    .q (net123),
    .notq ()
  );
  dffr_cell flop3 (
    .d (net124),
    .clk (net1),
    .r (net119),
    .q (net125),
    .notq ()
  );
  dffr_cell flop4 (
    .d (net126),
    .clk (net1),
    .r (net119),
    .q (net127),
    .notq (net128)
  );
  and_cell and1 (
    .a (net129),
    .b (net130),
    .out (net118)
  );
  and_cell and2 (
    .a (net129),
    .b (net131),
    .out (net122)
  );
  and_cell and3 (
    .a (net129),
    .b (net132),
    .out (net124)
  );
  and_cell and4 (
    .a (net129),
    .b (net128),
    .out (net126)
  );
  and_cell and5 (
    .a (net123),
    .b (net133),
    .out (net134)
  );
  and_cell and6 (
    .a (net125),
    .b (net127),
    .out (net133)
  );
  and_cell and7 (
    .a (net123),
    .b (net121),
    .out (net135)
  );
  and_cell and8 (
    .a (net125),
    .b (net135),
    .out (net136)
  );
  and_cell and9 (
    .a (net127),
    .b (net136),
    .out (net137)
  );
  xor_cell xor1 (
    .a (net134),
    .b (net120),
    .out (net130)
  );
  xor_cell xor2 (
    .a (net133),
    .b (net123),
    .out (net131)
  );
  xor_cell xor3 (
    .a (net127),
    .b (net125),
    .out (net132)
  );
  not_cell not1 (
    .in (net137),
    .out (net129)
  );
  mux_cell mux1 (
    .a (net120),
    .b (net4),
    .sel (net3),
    .out (net15)
  );
  mux_cell mux2 (
    .a (net123),
    .b (net5),
    .sel (net3),
    .out (net18)
  );
  mux_cell mux3 (
    .a (net125),
    .b (net6),
    .sel (net3),
    .out (net21)
  );
  mux_cell mux4 (
    .a (net127),
    .b (net7),
    .sel (net3),
    .out (net24)
  );
  not_cell not2 (
    .in (net2),
    .out (net119)
  );
endmodule
