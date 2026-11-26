# SPDX-License-Identifier: Apache-2.0
"""Cycle-exact model of tt_um_pettit_micro: step(ui) is one rising clock edge
with rst_n high and returns the uo_out the chip shows after it."""


class Model:
    def __init__(self):
        self.hc = self.vc = self.t = 0

    @staticmethod
    def tri(w, top):
        """4 bits under bit `top` of w, inverted when bit `top` is set."""
        v = (w >> (top - 4)) & 15
        return v ^ 15 if (w >> top) & 1 else v

    def pixel(self, ui):
        hc, vc, t = self.hc, self.vc, self.t
        scene = (ui & 7) ^ (0 if ui >> 3 & 1 else t >> 8)
        sier, nodither = scene >> 2, ui >> 4 & 1
        x, y = (hc >> 1) & 255, (vc >> 1) & 255
        v = ((x ^ y, x & y, y, x | y)[scene & 3] + t) & 255
        chk = (hc ^ vc) & 1
        if sier and (x & v) != 0 and chk:
            return 0, 0, 0
        w9 = v << 1                      # so that tri() can take bits [4:1]
        r4, g4, b4 = self.tri(w9, 8), self.tri(w9, 7), self.tri(w9, 6) ^ 15
        thr = 3 if nodither else chk << 1 | (vc & 1)
        return [(c >> 2) + 1 if (c & 3) > thr and c >> 2 != 3 else c >> 2 for c in (r4, g4, b4)]

    def step(self, ui):
        hc, vc = self.hc, self.vc
        hs_n = 0 if 656 <= hc < 752 else 1
        vs_n = 0 if vc in (490, 491) else 1
        r, g, b = self.pixel(ui) if hc < 640 and vc < 480 else (0, 0, 0)
        out = (hs_n << 7 | (b & 1) << 6 | (g & 1) << 5 | (r & 1) << 4 |
               vs_n << 3 | (b >> 1) << 2 | (g >> 1) << 1 | (r >> 1))
        self.hc = 0 if hc == 799 else hc + 1
        if hc == 799:
            self.vc = 0 if vc == 524 else vc + 1
            if vc == 524 and not ui >> 5 & 1:
                self.t = (self.t + 1) & 2047
        return out
