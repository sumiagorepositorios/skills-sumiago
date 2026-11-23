"""Mezcla la voz con música propia (hecha por código, 124 bpm, C-Am-F-G, sin derechos de autor) y los efectos de sonido de cada escena del Día 2.
Uso (en la carpeta donde están voice.wav, durs.json y mascot_clean.png):  python scripts/audio.py
Salida: mix.wav
"""
import os, sys, json, wave, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import render as render6
SR = 44100; TOTAL = render6.TOTAL; N = int((TOTAL + 0.3) * SR)
rng = np.random.default_rng(7)
def env(n, a=0.005, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-np.arange(n) / (r * SR))
    return e
def sine(f, d): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t)
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i] * g
def note(m): return 440 * 2 ** ((m - 69) / 12)
# ---- original upbeat music 124 bpm ----
bpm = 124; beat = 60 / bpm; bar = beat * 4
music = np.zeros(N)
prog = [(60, [60, 64, 67]), (57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62])]  # C Am F G
for b in range(int(TOTAL / bar) + 2):
    t0 = b * bar; root, ch = prog[b % 4]
    pad = sum(sine(note(m + 12), bar) for m in ch); add(music, pad * env(len(pad), 0.2) * 0.025, t0)
    for k in range(8):
        x = sine(note(root - 12), beat * 0.4); x = np.tanh(2.5 * x) * env(len(x), 0.004, 0.12); add(music, x * 0.14, t0 + k * beat / 2)
    mel = [ch[0] + 24, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[0] + 24, ch[1] + 24, ch[2] + 24, ch[1] + 24]
    for k in range(8):
        if (b + k) % 3 != 2:
            x = (sine(note(mel[k]), 0.22) + 0.3 * sine(note(mel[k]) * 2, 0.22)) * env(int(0.22 * SR), 0.002, 0.06); add(music, x * 0.045, t0 + k * beat / 2)
    for k in range(4):
        n = int(0.25 * SR); tt = np.arange(n) / SR; fr = 48 + 100 * np.exp(-tt * 38)
        add(music, np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 10) * 0.38, t0 + k * beat)
        if k in (1, 3):
            n = int(0.16 * SR); add(music, rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.035 * SR)) * 0.07, t0 + k * beat)
    for k in range(8):
        n = int(0.04 * SR); hh = np.diff(rng.normal(0, 1, n), prepend=0) * np.exp(-np.arange(n) / (0.01 * SR)); add(music, hh * 0.05, t0 + k * beat / 2 + beat / 4)
music = np.tanh(music * 1.4) / 1.4
fi = int(0.3 * SR); music[:fi] *= np.linspace(0, 1, fi); fo = int(1.5 * SR); music[-fo:] *= np.linspace(1, 0, fo)
# ---- voice + ducking ----
wf = wave.open('voice.wav'); v = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
win = int(0.05 * SR); en = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, 'same'))
duck = 1 - 0.5 * np.clip(en / 0.05, 0, 1); duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
music *= duck * 0.55
# ---- sfx ----
def lp_noise(d, c0=0.02, c1=0.5):
    n = int(d * SR); x = rng.normal(0, 1, n); out = np.zeros(n); a = 0.0
    for i in range(n):
        c = c0 + c1 * math.sin(math.pi * i / n) ** 2; a += c * (x[i] - a); out[i] = a
    return out
WH = lp_noise(0.35) * np.sin(np.pi * np.arange(int(0.35 * SR)) / int(0.35 * SR))
SW = lp_noise(0.22, 0.05, 0.6) * np.sin(np.pi * np.arange(int(0.22 * SR)) / int(0.22 * SR))
def pop(f):
    n = int(0.09 * SR); tt = np.arange(n) / SR; fr = f * np.exp(-tt * 18); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 40)
def ding(f, d=0.7): x = sine(f, d) + 0.4 * sine(f * 2.01, d); return x * env(len(x), 0.002, 0.2)
def coin(): return np.concatenate([sine(1975, 0.07) * env(int(0.07 * SR), 0.002, 0.03), sine(2637, 0.25) * env(int(0.25 * SR), 0.002, 0.08)])
def boom():
    n = int(0.8 * SR); tt = np.arange(n) / SR; fr = 35 + 120 * np.exp(-tt * 12)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 4) + rng.normal(0, 1, n) * np.exp(-tt * 25) * 0.4
def stamp():
    n = int(0.25 * SR); tt = np.arange(n) / SR; return (rng.normal(0, 1, n) * np.exp(-tt * 30) * 0.6 + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 18))
def key(): n = int(0.03 * SR); return np.diff(rng.normal(0, 1, n), prepend=0) * np.exp(-np.arange(n) / (0.005 * SR))
def tap(): return pop(400) * 0.8
def msg(): return np.concatenate([ding(1760, 0.15), ding(2349, 0.4)])
def buzz(): x = np.sign(sine(110, 0.4)) * 0.5 + np.sign(sine(117, 0.4)) * 0.5; return x * env(len(x), 0.005, 0.2) * 0.5
def riser():
    d = 1.2; n = int(d * SR); tt = np.arange(n) / SR; fr = 300 + 1500 * (tt / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * 0.3 + lp_noise(d, 0.05, 0.3) * 0.6) * (tt / d)
def cheer():
    out = np.zeros(int(1.2 * SR))
    for k in range(6): add(out, ding(note(72 + [0, 4, 7, 12, 16, 19][k]), 0.6), k * 0.06, 0.5)
    return out
sfx = np.zeros(N)
G = dict(whoosh=0.35, boom=0.6, stamp=0.55, pop=0.42, key=0.25, ding=0.3, cheer=0.35, swipe=0.4, tap=0.4, msg=0.4, coin=0.3, buzz=0.35, riser=0.35)
for (t, kind, prm) in render6.events():
    x = {'whoosh': lambda: WH, 'boom': boom, 'stamp': stamp, 'pop': lambda: pop(prm), 'key': key, 'ding': lambda: ding(prm),
         'cheer': cheer, 'swipe': lambda: SW, 'tap': tap, 'msg': msg, 'coin': coin, 'buzz': buzz, 'riser': riser}[kind]()
    add(sfx, x, t, G[kind])
mix = voice + music + sfx * 0.85
mix /= max(1.0, np.abs(mix).max() / 0.95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', round(len(mix) / SR, 2))
