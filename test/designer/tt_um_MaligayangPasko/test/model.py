"""Cycle-exact reference model of tt_um_MaligayangPasko, written from the
description of the picture (cell grid, tier rule, star shape, glyphs), not from the RTL expressions."""

H_TOTAL, V_TOTAL = 800, 525

GLYPHS = {  # 3x5 cells, one string per row
    "A": ["###", "#.#", "###", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"], "I": ["###", ".#.", ".#.", ".#.", "###"],
    "G": ["###", "#..", "#.#", "#.#", "###"], "Y": ["#.#", "#.#", "###", ".#.", ".#."],
    "N": ["###", "#.#", "#.#", "#.#", "#.#"], "P": ["###", "#.#", "###", "#..", "#.."],
    "S": ["###", "#..", "###", "..#", "###"], "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "!": [".#.", ".#.", ".#.", "...", ".#."],
}
M5 = ["#...#", "##.##", "#.#.#", "#...#", "#...#"]    # the M is 5 cells wide, columns 6..10
TEXT = "MALIGAYANG PASKO!"          # 17 characters, rows 53..57; the other 16 at pitch 4 from column 12

RED, GREEN, YELLOW, WHITE, CYAN = 0b110000, 0b001100, 0b111100, 0b111111, 0b001111
LIGHTS = [RED, YELLOW, WHITE, CYAN]


def pack(rgb):
    """rgb = RRGGBB (two bits each) -> uo_out = {hs, B0, G0, R0, vs, B1, G1, R1} without the sync bits"""
    r1, r0, g1, g0, b1, b0 = [(rgb >> s) & 1 for s in (5, 4, 3, 2, 1, 0)]
    return (b0 << 6) | (g0 << 5) | (r0 << 4) | (b1 << 2) | (g1 << 1) | r1


# ui_in bits: 0 pause (handled in step), 1..3 display options, all low = the plain scene
SNOW_OFF, SKY_BLACK, TEXT_GRN = (1 << b for b in range(1, 4))


def colour(hc, vc, t, ui=0):
    cx, cy = hc // 8, vc // 8                                 # 80 x 60 cells of 8 pixels
    dx = (39 - cx) if cx < 40 else (cx - 40)                  # distance from the centre line
    in_tree = edge = False
    if 16 <= cy <= 47:                                        # four tiers of eight rows
        hw = 1 + 4 * ((cy - 16) // 8) + cy % 8
        in_tree, edge = dx <= hw, dx == hw
    if 12 <= cy <= 15:                                        # small diamond star on rows 12..15
        sdy = 0 if cy in (13, 14) else 1
        if dx + sdy <= 1:
            return [0b100000, 0b110000, 0b111100, 0b110100][(t >> 4) & 3]
    if in_tree and not edge and ((cx ^ cy) & 1) and (((cx >> 1) ^ (cy >> 1)) & 1):   # light
        lc = (((cx >> 2) & 1) << 1 | ((cy >> 2) & 1)) ^ ((t >> 4) & 3)
        return LIGHTS[lc]
    if edge:
        return 0b000100
    if in_tree:
        return 0b001100 if cy & 1 else 0b001000
    if 48 <= cy <= 51 and dx <= 1:                            # trunk
        return 0b100100
    if cy >= 52:                                              # snow on the ground, with the greeting on it
        if 53 <= cy <= 57:
            ink = GREEN if ui & TEXT_GRN else RED
            if 6 <= cx <= 10 and M5[cy - 53][cx - 6] == "#":
                return ink
            o = cx - 12
            if 0 <= o < 64 and o % 4 < 3:
                ch = TEXT[1 + o // 4]
                if ch != " " and GLYPHS[ch][cy - 53][o % 4] == "#":
                    return ink
        return WHITE
    ph = ((cx >> 3) & 0xF) ^ ((((cx >> 3) & 3) << 2) | ((cx >> 5) & 3))
    if not ui & SNOW_OFF and (cx & 3) == 1 and not (hc & 4) and not (vc & 4) and ((((cy & 0xF) + ph) & 0xF) == ((t >> 2) & 0xF)):
        return WHITE
    return 0 if ui & SKY_BLACK else 0b000001


class Model:
    def __init__(self):
        self.hc = self.vc = self.t = 0

    def step(self, ui):
        """One rising clock edge (reset released): returns uo_out after the edge."""
        hc, vc, t = self.hc, self.vc, self.t
        active = hc < 640 and vc < 480
        hs_n = 0 if 656 <= hc < 752 else 1
        vs_n = 0 if vc in (490, 491) else 1
        out = pack(colour(hc, vc, t, ui)) if active else 0
        out |= (hs_n << 7) | (vs_n << 3)
        if hc == H_TOTAL - 1:
            self.hc = 0
            if vc == V_TOTAL - 1:
                self.vc = 0
                if not (ui & 1):
                    self.t = (t + 1) & 63
            else:
                self.vc = vc + 1
        else:
            self.hc = hc + 1
        return out
