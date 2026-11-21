"""Mezcla la voz con música propia (hecha por código, sin derechos de autor) y efectos de sonido sincronizados con las escenas.
Uso (en la carpeta donde están voice.wav y durs.json):  python scripts/audio.py   -> mix.wav
"""
import numpy as np, json, wave, math
SR = 44100
durs = json.load(open('durs.json')); starts = np.cumsum([0] + durs[:-1]); TOTAL = sum(durs)
N = int((TOTAL + 0.5) * SR)
def env(n, a=0.005, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-np.arange(n) / (r * SR))
    return e
def sine(f, d, ph=0): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t + ph)
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i] * g
# ---------- música (original, generada por código) ----------
bpm = 112; beat = 60 / bpm; bar = beat * 4
music = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G
rng = np.random.default_rng(1)
nb = int(TOTAL / bar) + 2
for b in range(nb):
    t0 = b * bar; root, ch = prog[b % 4]
    pad = sum(sine(note(m + 12), bar) + 0.5 * sine(note(m + 12) * 1.003, bar) for m in ch)
    add(music, pad * env(len(pad), 0.3) * 0.035, t0)
    for k in range(8):  # bajo
        if k in (0, 3, 4, 6):
            x = sine(note(root - 12), beat * 0.45); x = np.tanh(2 * x) * env(len(x), 0.005, 0.18)
            add(music, x * 0.16, t0 + k * beat / 2)
    arp = ch + [ch[1] + 12]
    for k in range(16):  # arpegio
        if k % 2 == 0 or k in (7, 13):
            m = arp[k % 4] + 24; x = sine(note(m), 0.25) * env(int(0.25 * SR), 0.002, 0.07)
            add(music, x * 0.05, t0 + k * beat / 4)
    for k in range(4):
        n = int(0.25 * SR); tt = np.arange(n) / SR; f = 50 + 90 * np.exp(-tt * 35)
        kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9); add(music, kick * 0.35, t0 + k * beat)
        if k in (1, 3):
            n = int(0.18 * SR); cl = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.04 * SR)); add(music, cl * 0.06, t0 + k * beat)
    for k in range(8):
        n = int(0.05 * SR); hh = rng.normal(0, 1, n); hh = np.diff(hh, prepend=0) * np.exp(-np.arange(n) / (0.012 * SR)); add(music, hh * 0.05, t0 + k * beat / 2)
music = np.tanh(music * 1.5) / 1.5
fi = int(0.8 * SR); music[:fi] *= np.linspace(0, 1, fi); fo = int(1.5 * SR); music[N - fo:] *= np.linspace(1, 0, fo)
# ---------- voz + música que baja cuando se habla ----------
wf = wave.open('voice.wav'); v = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
win = int(0.05 * SR); en = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, 'same'))
duck = 1 - 0.55 * np.clip(en / 0.05, 0, 1)
duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
music *= duck * 0.55
# ---------- efectos ----------
sfx = np.zeros(N)
def whoosh():
    n = int(0.4 * SR); x = rng.normal(0, 1, n); out = np.zeros(n); a = 0.0
    for i in range(n):
        c = 0.02 + 0.5 * math.sin(math.pi * i / n) ** 2; a += c * (x[i] - a); out[i] = a
    return out * np.sin(np.pi * np.arange(n) / n) * 0.9
WH = whoosh()
def pop(f=900):
    n = int(0.09 * SR); tt = np.arange(n) / SR; fr = f * np.exp(-tt * 18); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 40)
def ding(f=1320, d=0.7): x = sine(f, d) + 0.4 * sine(f * 2.01, d); return x * env(len(x), 0.002, 0.2)
def coin(): return np.concatenate([sine(1975, 0.07) * env(int(0.07 * SR), 0.002, 0.03), sine(2637, 0.22) * env(int(0.22 * SR), 0.002, 0.08)])
def buzz(): x = np.sign(sine(110, 0.45)) * 0.5 + np.sign(sine(116, 0.45)) * 0.5; return x * env(len(x), 0.005, 0.25) * 0.5
def tick(): n = int(0.03 * SR); return rng.normal(0, 1, n) * np.exp(-np.arange(n) / (0.004 * SR))
L = lambda i, o=0: starts[i] + o
for i in range(1, len(durs)): add(sfx, WH, L(i) - 0.15, 0.35)
add(sfx, pop(700), L(0, 0.3), 0.5); add(sfx, ding(1046), L(0, 0.5), 0.25)
for k in range(int(durs[1] * 0.55 / 0.45)): add(sfx, coin(), L(1, 0.2 + k * 0.45), 0.22)   # monedas
for k in range(int(durs[1] / 0.5)): add(sfx, tick(), L(1, k * 0.5), 0.12)                  # tic-tac
add(sfx, buzz(), L(1, durs[1] * 0.55), 0.35)                                               # "si no vas, no cobras"
for k in range(8): add(sfx, pop(500 + k * 60), L(2, k * durs[2] * 0.7 / 8), 0.35)          # barras
for o in (0.1, 1.8, 3.2): add(sfx, pop(950), L(3, o), 0.45)
add(sfx, ding(1568), L(3, 3.2), 0.25)
for o in (0.1, 0.625, 1.25, 1.875): add(sfx, pop(1100), L(4, o), 0.4)
for j in range(3): add(sfx, pop(800 + j * 150), L(4, 2.2 + j * 0.5), 0.45)
for k in range(int(durs[5] / 0.3)): add(sfx, pop(1500 + (k % 3) * 200), L(5, k * 0.3), 0.18)  # likes
for k in range(4): add(sfx, ding(1046 + k * 130, 0.4), L(6, 0.8 + k * 0.8), 0.3)           # tareas
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
prev = -1
for k in range(int(durs[7] * 60)):                                                          # rangos
    lt = k / 60; lv = min(5, int(ease(lt / durs[7] * 1.1) * 6))
    if lv != prev:
        add(sfx, ding(784 * 2 ** (lv / 6), 0.5), L(7, lt), 0.3)
        if lv >= 2: add(sfx, coin(), L(7, lt + 0.05), 0.3)
        prev = lv
for o in (0.4, 0.8, 1.2): add(sfx, pop(600), L(8, o), 0.35)
for k in range(5): add(sfx, pop(1000 + k * 80), L(8, 2.0 + k * 0.4), 0.35)
add(sfx, ding(1318, 1.0), L(9, 0.05), 0.35); add(sfx, pop(900), L(9, 0.8), 0.4)
add(sfx, ding(1568, 1.2), L(10, 0.1), 0.3); add(sfx, ding(2093, 1.2), L(10, 0.25), 0.2)
mix = voice * 1.0 + music + sfx * 0.9
mix /= max(1.0, np.abs(mix).max() / 0.95)
out = (mix * 32767).astype(np.int16)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print('Listo: mix.wav', round(len(out) / SR, 1), 's')
