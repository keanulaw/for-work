"""Synthesize meme sound effects (no downloads, no AI). Writes 48 kHz stereo WAVs.
Usage: python3 scripts/meme_sfx.py <out_dir>
"""
import os, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=0.3):
    e = np.ones(n)
    na, nr = int(SR * a), int(SR * r)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def lowpass(x, cutoff):
    # one-pole, cutoff may be an array for sweeps
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y, prev = np.empty_like(x), 0.0
    for i, v in enumerate(x):
        prev = (1 - a[i]) * v + a[i] * prev
        y[i] = prev
    return y


def reverb(x, wet=0.3, decay=1.2):
    ir_t = t(decay)
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 5 / decay)
    n = len(x) + len(ir) - 1
    tail = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n) * wet / 12
    return np.concatenate([x, np.zeros(len(ir) - 1)]) + tail


def vine_boom():
    x = t(1.2)
    f = 38 + 70 * np.exp(-x * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s = np.tanh(s * 3) * np.exp(-x * 2.6)
    click = rng.standard_normal(len(x)) * np.exp(-x * 120) * 0.4
    return reverb(s + click, 0.5, 1.4)


def whoosh():
    x = t(0.55)
    n = rng.standard_normal(len(x))
    sweep = 300 + 5000 * np.sin(np.pi * x / x[-1]) ** 2
    return lowpass(n, sweep) * np.sin(np.pi * x / x[-1]) ** 1.5 * 2.2


def riser():
    x = t(2.0)
    n = lowpass(rng.standard_normal(len(x)), 200 + 6000 * (x / x[-1]) ** 2)
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (x / x[-1]) ** 2) / SR) * 0.25
    return (n * 1.5 + tone) * (x / x[-1]) ** 2


def record_scratch():
    x = t(0.45)
    speed = np.where(x < 0.18, 1 - x / 0.18 * 2.2, -1.2 + (x - 0.18) * 4)
    ph = np.cumsum(np.abs(speed)) / SR
    n = rng.standard_normal(len(x))
    s = lowpass(n, 800 + 3500 * np.abs(speed)) * (0.6 + 0.4 * np.sin(2 * np.pi * 180 * ph * 20))
    return s * env(len(x), 0.002, 0.1) * 2


def airhorn():
    x = t(1.1)
    out = np.zeros(len(x))
    for f in (466, 554, 698):
        ph = 2 * np.pi * f * x * (1 + 0.004 * np.sin(2 * np.pi * 6 * x))
        out += 2 * (ph / (2 * np.pi) % 1) - 1
    out = lowpass(out / 3, 3500)
    gate = (np.sin(2 * np.pi * 7.5 * x) > -0.6).astype(float)
    return np.tanh(out * gate * 2.5) * env(len(x), 0.01, 0.25) * 0.8


def ding():
    x = t(1.4)
    s = sum(np.sin(2 * np.pi * f * x) * np.exp(-x * d) * a for f, d, a in ((1760, 3, 1), (2637, 4, 0.5), (3520, 6, 0.3)))
    return s * 0.5


def sad_trombone():
    parts = []
    for i, f in enumerate((392, 370, 349, 330)):
        d = 0.42 if i < 3 else 1.1
        x = t(d)
        vib = 1 + (0.012 * np.sin(2 * np.pi * 5.5 * x) if i == 3 else 0)
        ph = 2 * np.pi * f * np.cumsum(vib) / SR
        s = sum(np.sin(k * ph) / k for k in range(1, 8))
        parts.append(lowpass(s, 1800) * env(len(x), 0.03, 0.12 if i < 3 else 0.5))
    return np.concatenate(parts) * 0.5


def bass_drop():
    x = t(1.6)
    f = 140 * np.exp(-x * 2.2) + 32
    s = np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 2.5)
    return s * np.exp(-x * 1.4) * 0.9


def write(path, mono):
    mono = mono / max(1e-9, np.abs(mono).max()) * 0.89
    data = (np.stack([mono, mono], 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for fn in (vine_boom, whoosh, riser, record_scratch, airhorn, ding, sad_trombone, bass_drop):
        write(os.path.join(out, fn.__name__ + ".wav"), fn())
        print(fn.__name__)
