#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""uadpcm.py - the uADPCM codec of tt_um_pettit_adpcm: encoder, reference
decoder and the .ua stream file.  No dependencies.  (audio2ua.py is the
front end that takes mp3 / m4a / wma / MIDI and prepares the audio; this
file is the codec itself.)

uADPCM is a 4-bit adaptive differential PCM: every code moves a 16-bit
predictor by a multiple of a step size, and the step size follows the codes,
growing after large ones and shrinking after small ones.  Both updates are
shifts and adds of the step, so a bit-serial datapath does them with one
full adder.  16-bit unsigned predictor (reset 0x8000), 16-bit step (reset
16), code {sign, m[2:0]}:

    pred -/+= step>>3 + (m2 ? step : 0) + (m1 ? step>>1 : 0) + (m0 ? step>>2 : 0)
    step  = m2 ? step + (step >> (3 - m[1:0]))       x 1.125, 1.25, 1.5, 2
               : step - (step >> 4)                  x 0.94; stops at 15 by itself

The decoder has no clamps: the ENCODER never emits a code that would take
the predictor outside 0..65535 or the step past 65535.

    uadpcm.py encode IN.wav OUT.ua [--seconds S] [--start S] [--gain G]
        IN.wav: 16-bit PCM, first channel, at the rate it is to play at
        OUT.ua: 'uADP', u32 samples, u32 rate (little-endian), then two
                codes a byte, low nibble first
    uadpcm.py decode IN.ua OUT.wav          exactly what the chip will play
    uadpcm.py snr IN.wav [--seconds S]      SNR of uADPCM, and of standard
                                            IMA ADPCM for comparison
"""
import struct
import sys
import wave

MASK = 0xFFFF
PRED0, STEP0 = 0x8000, 16


def delta_of(step, m):
    return (step >> 3) + (step if m & 4 else 0) + (step >> 1 if m & 2 else 0) + (step >> 2 if m & 1 else 0)


def next_step(step, m):
    """The step after magnitude m; may exceed 16 bits (the encoder refuses those)."""
    if not m & 4:
        return step - (step >> 4)
    return step + (step >> (3 - (m & 3)))


def decode(codes, pred=PRED0, step=STEP0):
    """Codes (0..15) to unsigned 16-bit samples, exactly as the chip (wrapping)."""
    out = []
    for c in codes:
        d = delta_of(step, c & 7)
        pred = (pred - d if c & 8 else pred + d) & MASK
        step = next_step(step, c & 7) & MASK
        out.append(pred)
    return out


def encode(samples, pred=PRED0, step=STEP0):
    """Unsigned 16-bit samples to codes: the code whose result is nearest,
    among those that keep the predictor and the step in range."""
    codes = []
    for s in samples:
        best = None
        for m in range(8):
            ns = next_step(step, m)
            if ns > MASK:
                continue
            d = delta_of(step, m)
            for sign in (0, 8):
                p = pred - d if sign else pred + d
                if 0 <= p <= MASK:
                    e = abs(p - s)
                    if best is None or e < best[0]:
                        best = (e, sign | m, p, ns)
        _, c, pred, step = best
        codes.append(c)
    return codes


# ------------------------------------------- IMA ADPCM, for the comparison
_IMA_STEP = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97,
             107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724,
             796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026,
             4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500,
             20350, 22385, 24623, 27086, 29794, 32767]
_IMA_INDEX = [-1, -1, -1, -1, 2, 4, 6, 8]


def ima_roundtrip(samples):
    """Signed 16-bit samples through a plain IMA encoder and decoder."""
    pred, idx, out = samples[0], 0, []
    for s in samples:
        st = _IMA_STEP[idx]
        diff, nib = s - pred, 0
        if diff < 0:
            nib, diff = 8, -diff
        if diff >= st:
            nib |= 4
            diff -= st
        if diff >= st >> 1:
            nib |= 2
            diff -= st >> 1
        if diff >= st >> 2:
            nib |= 1
        d = delta_of(st, nib & 7)
        pred = max(-32768, min(32767, pred - d if nib & 8 else pred + d))
        idx = max(0, min(88, idx + _IMA_INDEX[nib & 7]))
        out.append(pred)
    return out


def read_audio(path, start_s=0.0, seconds=None):
    """(rate, signed 16-bit samples) from a 16-bit PCM .wav, first channel."""
    with wave.open(path, "rb") as w:
        assert w.getsampwidth() == 2, "16-bit PCM WAV only"
        rate, ch = w.getframerate(), w.getnchannels()
        w.setpos(int(start_s * rate))
        n = w.getnframes() - int(start_s * rate) if seconds is None else int(seconds * rate)
        raw = w.readframes(n)
    return rate, [v[0] for v in struct.iter_unpack("<" + "h" * ch, raw)]


# ------------------------------------------------------------- file formats
def write_ua(path, codes, rate):
    if len(codes) & 1:
        codes = codes + [0]
    body = bytes(codes[i] | codes[i + 1] << 4 for i in range(0, len(codes), 2))
    open(path, "wb").write(b"uADP" + struct.pack("<II", len(codes), rate) + body)


def read_ua(path):
    blob = open(path, "rb").read()
    assert blob[:4] == b"uADP"
    n, rate = struct.unpack_from("<II", blob, 4)
    return rate, [(blob[12 + (i >> 1)] >> (4 * (i & 1))) & 15 for i in range(n)]


def write_wav(path, rate, signed):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<%dh" % len(signed), *signed))


def snr_db(ref, got):
    import math
    sig = sum(r * r for r in ref)
    err = sum((r - g) ** 2 for r, g in zip(ref, got))
    return 10 * math.log10(sig / err) if err else float("inf")


def _opt(name, default=None):
    return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "decode":
        rate, codes = read_ua(sys.argv[2])
        write_wav(sys.argv[3], rate, [p - 32768 for p in decode(codes)])
        print("%s: %d samples at %d Hz" % (sys.argv[3], len(codes), rate))
        return
    rate, pcm = read_audio(sys.argv[2], _opt("--start", 0.0), _opt("--seconds"))
    gain = _opt("--gain", 1.0)
    target = [max(0, min(MASK, int(round(s * gain)) + 32768)) for s in pcm]
    codes = encode(target)
    got = decode(codes)
    if cmd == "encode":
        write_ua(sys.argv[3], codes, rate)
        print("%s: %d samples at %d Hz (%.1f s), SNR %.1f dB" % (sys.argv[3], len(codes), rate, len(codes) / rate,
                                                                  snr_db([t - 32768 for t in target], [g - 32768 for g in got])))
    elif cmd == "snr":
        ref = [t - 32768 for t in target]
        print("uADPCM %.1f dB, IMA %.1f dB over %d samples" % (snr_db(ref, [g - 32768 for g in got]),
                                                              snr_db(ref, ima_roundtrip(ref)), len(ref)))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
