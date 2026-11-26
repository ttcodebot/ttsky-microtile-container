`default_nettype none

module tt_um_xy_spirograph (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] ui_in,
    output reg  [7:0] uo_out
);
    reg [5:0] phase;
    reg [1:0] mode_meta, mode;
    wire [5:0] phase2 = phase << 1;
    wire [5:0] phase3 = phase2 + phase;

    // Fold the top half of the phase ramp back toward zero.
    function [3:0] triangle;
        input [5:0] angle;
        begin
            triangle = angle[4:1] ^ {4{angle[5]}};
        end
    endfunction

    // X coordinates of a four-point star. Y follows a quarter-turn later.
    function [3:0] star_axis;
        input [3:0] index;
        begin
            case (index)
                0: star_axis = 15;
                1, 15: star_axis = 13;
                2, 14: star_axis = 10;
                3, 13: star_axis = 9;
                4, 12: star_axis = 8;
                5, 11: star_axis = 7;
                6, 10: star_axis = 6;
                7, 9: star_axis = 3;
                8: star_axis = 1;
                default: star_axis = 8;
            endcase
        end
    endfunction

    always @(posedge clk) begin
        if (!rst_n) begin
            phase <= 0;
            mode_meta <= 0;
            mode <= 0;
            uo_out <= 8'h88;
        end else begin
            phase <= phase + 6'd1;
            mode_meta <= ui_in[1:0];
            mode <= mode_meta;
            case (mode)
                2'b00: uo_out <= {triangle(phase + 6'd16), triangle(phase)};
                2'b01: uo_out <= {triangle(phase2 + 6'd16), triangle(phase)};
                2'b10: uo_out <= {triangle(phase3), triangle(phase2)};
                2'b11: uo_out <= {star_axis(phase[5:2] + 4'd4), star_axis(phase[5:2])};
            endcase
        end
    end
endmodule

`default_nettype wire
