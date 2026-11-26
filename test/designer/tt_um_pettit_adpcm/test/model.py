# SPDX-License-Identifier: Apache-2.0
"""Cycle-exact model of tt_um_pettit_adpcm: step(ui) is one rising clock
edge with rst_n high (after a reset of 16 clocks or more) and returns the
uo_out the chip shows after it.  value() is the predictor as a number, valid
whenever the bit counter is 0."""

SD = 5


class Model:
    def __init__(self):
        self.ramp = 0
        self.sync = 0
        self.pend = 0
        self.pred = 0           # shifted full of zeros by the reset
        self.step = 0
        self.phase = 0
        self.init = 1
        self.cy = 0
        self.duty = 16          # mid-scale, set by the reset
        self.acc = self.extra = 0
        self.pwm = None

    def value(self):
        return self.pred

    def step_clock(self, ui):
        sgn, m, strobe = ui >> 3 & 1, ui & 7, ui >> 4 & 1
        i = self.ramp & 15
        last, first = i == 15, i == 0
        rise = (self.sync >> 1 & 1) and not (self.sync >> 2 & 1)
        phase = self.phase
        k, en, sub = {1: (3, 1, sgn), 2: (0, m >> 2 & 1, sgn), 3: (1, m >> 1 & 1, sgn), 4: (2, m & 1, sgn),
                      5: ((~m & 3) if m & 4 else 4, 1, 0 if m & 4 else 1)}.get(phase, (0, 0, 0))
        tap = (self.step >> k & 1) if i + k < 16 else 0
        to_pred, to_step = 1 <= phase <= 4, phase == 5
        a = (self.step if to_step else self.pred) & 1
        b = en & (tap ^ sub)
        cin = (en & sub) if first else self.cy
        s = a ^ b ^ cin
        cout = (a & b) | (a & cin) | (b & cin)

        zero = self.ramp == 0
        load = zero and not self.init
        pwm = 0 if zero else int(self.ramp <= self.duty + self.extra)
        if load:
            t = self.acc + (self.pred >> (11 - SD) & ((1 << SD) - 1))
            self.extra, self.acc = t >> SD, t & ((1 << SD) - 1)
            self.duty = self.pred >> 11

        pin = (1 if last else 0) if self.init else (s if to_pred else self.pred & 1)
        sin = (1 if i == 4 else 0) if self.init else (s if to_step else self.step & 1)
        self.pred = pin << 15 | self.pred >> 1
        self.step = sin << 15 | self.step >> 1
        if rise:
            self.pend = 1
        if last:
            if self.init:
                self.phase = 0
            elif phase == 0:
                if self.pend:
                    self.phase = 1
                    if not rise:
                        self.pend = 0
            else:
                self.phase = 0 if phase == 5 else phase + 1
            self.init = 0
        self.ramp = (self.ramp + 1) & 31
        self.sync = (self.sync << 1 | strobe) & 7
        self.cy = cout
        self.pwm = pwm
        busy = 1 if self.pend or self.phase else 0
        return pwm << 7 | (pwm ^ 1) << 6 | busy << 5 | self.duty
