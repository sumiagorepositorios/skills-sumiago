"""Música propia (lo-fi 90 bpm), toques, tecleo y la voz del Presentador, con la música que baja cuando habla.
Uso (en tu carpeta de trabajo, después de voz.py):  python scripts/audio.py   -> out/audio.wav
"""
import numpy as np, wave, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import R, V, P, M, SCENES

SR = 44100; DUR = 64.0
N = int(SR * DUR)
out = np.zeros(N, np.float64)
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR


def add(sig, t0, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(sig)); out[i:j] += sig[:j - i] * g


# ---- music: lofi pad + soft beat, 90 bpm
bpm = 90; beat = 60 / bpm; bar = beat * 4
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]  # Am7 Fmaj7 Cmaj7 G7
mf = lambda m: 440 * 2 ** ((m - 69) / 12)
music = np.zeros(N)
nb = int(DUR / bar) + 1
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    n = int(bar * SR * 1.1); tt = np.arange(n) / SR
    env = np.minimum(tt / 0.4, 1) * np.exp(-tt * 0.5)
    s = np.zeros(n)
    for m in ch:
        f = mf(m)
        s += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt) + 0.5 * np.sin(2 * np.pi * f * 0.997 * tt)) * 0.06
    bf = mf(ch[0] - 12)
    s += np.sin(2 * np.pi * bf * tt) * 0.16 * np.exp(-tt * 1.2)
    i = int(t0 * SR); j = min(N, i + n); music[i:j] += (s * env)[:j - i]
    # plucks (arp) on 8ths
    for k in range(8):
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        nn = int(0.35 * SR); tt2 = np.arange(nn) / SR
        pl = np.sin(2 * np.pi * mf(m) * tt2) * np.exp(-tt2 * 9) * 0.05
        ii = int((t0 + k * beat / 2) * SR); jj = min(N, ii + nn)
        if ii < N: music[ii:jj] += pl[:jj - ii]
# drums
for k in range(int(DUR / beat)):
    t0 = k * beat
    nn = int(0.3 * SR); tt = np.arange(nn) / SR
    if k % 4 in (0, 2) and t0 > 0.4:
        f = 110 * np.exp(-tt * 18) + 45
        kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 0.35
        ii = int(t0 * SR); jj = min(N, ii + nn); music[ii:jj] += kick[:jj - ii]
    if k % 4 in (1, 3) and t0 > 0.4:
        sn = rng.standard_normal(nn) * np.exp(-tt * 22) * 0.07
        ii = int(t0 * SR); jj = min(N, ii + nn); music[ii:jj] += sn[:jj - ii]
    hh = np.diff(rng.standard_normal(int(0.05 * SR) + 1)) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80) * 0.02
    for off in (0, beat / 2):
        ii = int((t0 + off) * SR); jj = min(N, ii + len(hh))
        if ii < N: music[ii:jj] += hh[:jj - ii]
# simple lowpass smoothing
music = np.convolve(music, np.ones(6) / 6, mode='same')
fade = np.minimum(1, t_all / 1.0) * np.minimum(1, (DUR - t_all) / 1.5)
# voice
import json
from render import CAPS, VO
voice = np.zeros(N)
for i, (a, b, t) in enumerate(CAPS):
    with wave.open(os.path.join('vo', 't', f'{i:02d}.wav')) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    ii = int((a + VO) * SR); jj = min(N, ii + len(x)); voice[ii:jj] += x[:jj - ii]
voice = voice / np.max(np.abs(voice)) * 0.9
env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.6 * np.clip(env * 3, 0, 1)
out += music * fade * 0.45 * duck


# ---- sfx
def click(g=1.0):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 140) * 0.5 + rng.standard_normal(n) * np.exp(-tt * 300) * 0.15) * g


def tick():
    n = int(0.025 * SR); tt = np.arange(n) / SR
    return np.diff(np.r_[0, rng.standard_normal(n)]) * np.exp(-tt * 400) * 0.06


def whoosh():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    no = rng.standard_normal(n)
    k = 30; sm = np.convolve(no, np.ones(k) / k, 'same')
    env = np.sin(np.pi * tt / tt[-1]) ** 2
    return sm * env * 0.5


def chime():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * mf(76) * tt) * np.exp(-tt * 5)
    s2 = np.zeros(n); d = int(0.11 * SR)
    s2[d:] = np.sin(2 * np.pi * mf(83) * tt[:n - d]) * np.exp(-tt[:n - d] * 4)
    return (s + s2) * 0.16


def pop():
    n = int(0.12 * SR); tt = np.arange(n) / SR
    f = 500 + 900 * tt / tt[-1]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30) * 0.2


def typing(t0, t1, s):
    n = len(s)
    for i in range(n):
        add(tick(), t0 + (t1 - t0) * (i + 0.5) / n)


st = {n: a for n, a, b, f in SCENES}
for n, a, b, f in SCENES:
    if a > 0: add(whoosh(), a - 0.15, 0.6)
# intro
for t0 in (0.35, 0.8, 1.5, 1.9, 2.3): add(pop(), t0, 0.7)
# registro
b = st['b_reg']
typing(b + R['url'][0], b + R['url'][1], 'sumiago.com')
add(click(), b + R['tap_crear'])
for k, txt in [('user', 'carlosventas'), ('nom', 'Carlos'), ('ape', 'Pérez'), ('mail', 'carlos@gmail.com'), ('wa', '+57 300 123 4567'), ('pw1', 'carlos2026'), ('pw2', 'carlos2026')]:
    add(click(0.6), b + R[k][0] - 0.12)
    typing(b + R[k][0], b + R[k][1], txt)
for k in ('tap_terms', 'tap_sig1', 'tap_sig2', 'tap_crear2'): add(click(), b + R[k])
add(click(0.6), b + R['pais'] - 0.7); typing(b + R['pais'] - 0.5, b + R['pais'] - 0.15, 'Col'); add(click(0.7), b + R['pais'])
add(chime(), b + R['ok'])
# verificar
v = st['c_ver']
add(pop(), v + V['notif'], 0.9)
add(click(0.6), v + V['tap_box'])
for i in range(6): add(tick(), v + V['digits'] + i * 0.2, 2.0)
add(click(), v + V['tap_ver']); add(chime(), v + V['ok'])
# panel
p = st['d_panel']
add(click(), p + P['tap_mk']); add(click(), p + P['tap_pub'])
# marketplace
m = st['e_mk']
for k in ('tap1', 'tap2'): add(click(), m + M[k])
for k in ('ph1', 'ph2'): add(pop(), m + M[k], 0.8)
for k, txt in [('tit', 'Celular 128 GB como nuevo'), ('pre', '180'), ('desc', 'Batería al 90%, con caja y cargador original. Entrega en Medellín.'), ('ciu', 'Medellín')]:
    add(click(0.6), m + M[k][0] - 0.12); typing(m + M[k][0], m + M[k][1], txt)
for k in ('cat', 'sub', 'mon'): add(click(0.6), m + M[k] - 0.1); add(click(0.5), m + M[k])
add(click(), m + M['est'])
add(whoosh(), m + M['sc1'][0], 0.25); add(whoosh(), m + M['sc2'][0], 0.25)
add(click(), m + M['tap_pub']); add(chime(), m + M['art'])
add(click(), m + M['tap_share']); add(pop(), m + M['wa'])
# outro
o = st['f_outro']
add(pop(), o + 0.15); add(pop(), o + 3.2); add(chime(), o + 5.4, 0.8)

out = out / max(1e-9, np.max(np.abs(out))) * 0.35 + voice
out = out / max(1e-9, np.max(np.abs(out))) * 0.89
st2 = np.stack([out, out], 1)
os.makedirs('out', exist_ok=True)
with wave.open(os.path.join('out', 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st2 * 32767).astype(np.int16).tobytes())
