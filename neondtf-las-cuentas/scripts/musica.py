import os
import numpy as np, wave
SR = 44100
DURS = [4.1, 6.8, 4.3, 5.7, 3.5, 6.5, 5.6, 8.0, 7.0]
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


S = starts
def tick():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * env(n, 0.0005, 0.006) * 0.25
def drone(f0, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = saw(f0, n) * 0.5 + np.sin(2 * np.pi * f0 * 1.005 * t)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.3)
    return s * e * 0.06
prog = [(110.0, [220, 261.6, 329.6]), (87.31, [174.6, 220, 261.6]), (130.81, [261.6, 329.6, 392]), (98.0, [196, 246.9, 293.7])]
arp = {0: [440, 523.3, 659.3, 523.3], 1: [349.2, 440, 523.3, 440], 2: [523.3, 659.3, 784, 659.3], 3: [392, 493.9, 587.3, 493.9]}
def section(t):
    if t < S[1]: return "intro"
    if t < S[3]: return "tense"
    return "full"
bar = 4 * B
for b in range(int(DUR / bar) + 1):
    t0 = b * bar; ci = b % 4; root, chord = prog[ci]
    sec0 = section(t0)
    if sec0 in ("intro", "tense", "dark"):
        add(drone(55.0, bar), t0, 1.0)
        add(pad([220, 261.6, 329.6], bar), t0, 0.7)
    elif sec0 == "hit":
        pass
    else:
        add(pad(chord, bar), t0, 1.0 if sec0 == "full" else 1.3)
    for q in range(4):
        tb = t0 + q * B
        if tb >= DUR: break
        sec = section(tb)
        if sec in ("intro", "tense", "dark"):
            add(tick(), tb, 1.0); add(tick(), tb + B / 2, 0.6 if sec != "dark" else 1.0)
            if sec == "dark": add(tick(), tb + B / 4, 0.5); add(tick(), tb + 3 * B / 4, 0.5)
            if sec != "intro" and q in (0, 2): add(kick(), tb, 0.55)
        elif sec == "full":
            add(kick(), tb, 0.9); add(hat(), tb + B / 2, 1.0, 0.3); add(hat(), tb + 3 * B / 4, 0.5, -0.3)
            if q in (1, 3): add(clap(), tb, 1.0)
            add(bass(root, B * 0.45), tb + B / 2, 1.0); add(bass(root, B * 0.3), tb, 0.6)
            for s in range(4):
                add(pluck(arp[ci][(q * 4 + s) % 4]), tb + s * B / 4, 0.7, (-0.4 if s % 2 else 0.4))
        elif sec == "break":
            if q == 0: add(kick(), tb, 0.4)
            for s in range(2):
                add(pluck(arp[ci][(q * 2 + s) % 4]), tb + s * B / 2, 0.5)

def blip(f):
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * env(n, 0.001, 0.02) * 0.18
for k in range(int(3.0 / 0.14)): add(blip(900 + (k * 137) % 700), 0.6 + k * 0.14, 0.8)
add(ding(), 3.0, 0.7)
for i in range(1, 9): add(whoosh(0.45), S[i] - 0.25, 0.8)
add(pop(), S[1] + 0.2, 0.9); add(pop(), S[1] + 1.7, 0.9); add(impact(), S[1] + 1.8, 0.3)
for k in range(5): add(pop(), S[1] + 4.3 + k * 0.22, 0.8)
add(pop(), S[1] + 5.4, 1.0)
for k in range(6): add(pluck(330 * 2 ** (k / 12), 0.2), S[2] + 0.15 + k * 0.29, 1.2)
add(impact(), S[2] + 2.3, 0.8)
add(riser(1.5), S[3] - 1.5, 1.0); add(impact(), S[3], 0.8)
for x in (1.8, 2.6, 3.4): add(click(), S[3] + x, 1.0); add(whoosh(0.6), S[3] + x, 0.4)
add(ding(), S[3] + 4.1, 1.2)
add(pop(), S[4] + 0.3, 1.0); add(whoosh(1.2), S[4] + 0.6, 0.4)
for k in range(28): add(pluck(660 * 2 ** (k / 40), 0.1), S[5] + 0.3 + 1.7 * (1 - (1 - (k + 1) / 28) ** (1 / 2)), 0.6)
for x in (2.65, 3.35, 4.4): add(pop(), S[5] + x, 1.0)
for x in (0.2, 1.45, 3.35): add(pop(), S[6] + x, 1.0)
add(riser(4.0), S[6] + 0.5, 0.4)
for k in range(16): add(pluck(880 * 2 ** (k / 24), 0.12), S[7] + 0.15 + 1.35 * (1 - (1 - (k + 1) / 16) ** (1 / 3)), 0.8)
for x in (1.95, 3.0, 4.2, 4.6, 5.0, 5.4): add(pop(), S[7] + x, 0.8)
add(ding(), S[7] + 6.1, 1.0)
add(impact(), S[8], 0.5); add(click(), S[8] + 1.45, 1.0); add(ding(), S[8] + 1.5, 0.8)
st = np.stack([L, R], 1)
t = np.arange(N) / SR
st *= np.clip((DUR - t) / 1.2, 0, 1)[:, None]
st = np.tanh(st * 1.3) * 0.85
st /= np.abs(st).max() / 0.9
pcm = (st * 32767).astype(np.int16)
w = wave.open(os.path.join(os.getcwd(), "out", "music.wav"), "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print("ok")
