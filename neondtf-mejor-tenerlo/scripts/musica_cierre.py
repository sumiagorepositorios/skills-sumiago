"""Música y efectos del cierre de Sumiago (7 s). Salida: out/musica_cierre.wav"""
import os
import numpy as np, wave
SR = 44100
DURS = [7.0]
import itertools
starts = [0] + list(itertools.accumulate(DURS))[:-1]
DUR = sum(DURS)
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(1)
BPM = 120; B = 60 / BPM

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[:j - i] * gain
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return e

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.001, 0.16) * 1.0
def hat():
    n = int(0.08 * SR); x = rng.normal(0, 1, n); x = np.diff(x, prepend=0)
    return x * env(n, 0.001, 0.02) * 0.18
def clap():
    n = int(0.25 * SR); x = rng.normal(0, 1, n); x = np.diff(x, prepend=0)
    return x * env(n, 0.002, 0.07) * 0.28
def saw(freq, n):
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 8))
    return s
def bass(freq, dur):
    n = int(dur * SR)
    return saw(freq, n) * env(n, 0.005, dur * 0.6) * 0.22
def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.3 * t)) + 0.4 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return s * e * 0.035
def pluck(freq, dur=0.25):
    n = int(dur * SR)
    return saw(freq, n) * env(n, 0.002, 0.07) * 0.07
def whoosh(dur=0.5, up=True):
    n = int(dur * SR); x = rng.normal(0, 1, n)
    # simple moving-average lowpass with sweeping window
    out = np.zeros(n); acc = 0
    t = np.arange(n) / n
    k = 0.02 + 0.5 * (t if up else 1 - t)
    for i in range(n):
        acc += k[i] * (x[i] - acc); out[i] = acc
    e = np.sin(np.pi * t) ** 2
    return out * e * 0.5
def click():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2200 * t) + rng.normal(0, 0.5, n)) * env(n, 0.0005, 0.008) * 0.5
def ding():
    n = int(0.8 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 1975.5 * t)) * env(n, 0.002, 0.25) * 0.16
def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 300 + 900 * t / 0.12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.05) * 0.25
def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 200 * (8 ** (t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.06 + rng.normal(0, 1, n) * 0.04 * (t / dur)
    return s * (t / dur) ** 1.5
def impact():
    n = int(1.2 * SR); t = np.arange(n) / SR
    f = 30 + 80 * np.exp(-t * 10)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.9 + rng.normal(0, 1, n) * 0.15 * np.exp(-t * 12)) * env(n, 0.001, 0.4)


for b in range(4):
    t0 = b * 2.0; ch = [[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7]][b]
    add(pad(ch, 2.0), t0, 1.3)
    for s in range(8):
        add(pluck(ch[s % 3] * 2, 0.3), t0 + s * 0.25, 0.45, (-0.4 if s % 2 else 0.4))
    if b >= 1:
        for q in range(4): add(kick(), t0 + q * 0.5, 0.45); add(hat(), t0 + q * 0.5 + 0.25, 0.7)
add(whoosh(0.6), 0.0, 1.0); add(impact(), 3.45, 0.7); add(ding(), 4.3, 1.0); add(pop(), 4.6, 1.0)
st = np.stack([L, R], 1); t = np.arange(N) / SR
st *= np.clip((DUR - t) / 1.0, 0, 1)[:, None]; st = np.tanh(st * 1.3) * 0.85; st /= np.abs(st).max() / 0.9
w = wave.open(os.path.join(os.getcwd(), "out", "musica_cierre.wav"), "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
