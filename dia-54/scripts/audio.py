"""Voz + música cálida hecha por código (sin derechos de autor) + efectos → mix.wav"""
import json, numpy as np, wave, sys, os, importlib.util
sys.argv = ['x', 'still']
spec = importlib.util.spec_from_file_location('r', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.py')); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
SR = 44100; TL = json.load(open('tl.json')); T = TL['total']; N = int(T * SR)
v = np.load('voice.npy')[:N]; out = np.zeros(N, np.float32); rng = np.random.RandomState(1)
def add(sig, t, g=1.0):
    s = int(t * SR); e = min(N, s + len(sig))
    if 0 <= s < N: out[s:e] += sig[:e - s] * g
def env(n, a=.005, rel=.1):
    e = np.ones(n); na = max(1, int(a * SR)); nr = min(n, int(rel * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
tt = lambda d: np.arange(int(d * SR)) / SR
def thud(): x = tt(.5); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 9) + rng.randn(len(x)) * np.exp(-x * 40) * .5) * .8
def whoosh(d=.6): x = tt(d); n = np.convolve(rng.randn(len(x)), np.ones(20) / 20, 'same'); return n * np.sin(np.pi * x / d) ** 2 * .35
def pop(): x = tt(.12); return np.sin(2 * np.pi * (500 + 900 * np.exp(-x * 40)) * x) * np.exp(-x * 30) * .5
def ding(f=1568): x = tt(.7); return (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.5 * x)) * np.exp(-x * 6) * .22
def page(): x = tt(.35); n = np.convolve(rng.randn(len(x)), np.ones(6) / 6, 'same'); return n * np.sin(np.pi * x / .35) * .25
def shutter(): x = tt(.16); return rng.randn(len(x)) * (np.exp(-x * 60) + np.exp(-np.maximum(0, x - .07) * 60) * (x > .07)) * .4
def drawer(): x = tt(.7); return np.convolve(rng.randn(len(x)), np.ones(40) / 40, 'same') * env(len(x), .05, .2) * 1.4
def bubble(): x = tt(.25); return np.sin(2 * np.pi * (300 + 600 * x / .25) * x) * np.exp(-x * 12) * .3
def shimmer(): x = tt(1.6); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 3) for f in (1320, 1760, 2093, 2637)) * .08
# --- música: guitarra/piano suave (arpegios) 84 bpm, sube en la parte de Sumiago ---
x = np.arange(N) / SR; mus = np.zeros(N)
bpm = 84; e8 = 60 / bpm / 2
prog = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
up = r.ct(10) - .2
for k in range(int(T / e8)):
    tb = k * e8; ch = prog[(k // 8) % 4]; f = ch[[0, 1, 2, 1][k % 4]] * (2 if k % 8 >= 4 else 1)
    s = tt(e8 * 3); note = (np.sin(2 * np.pi * f * s) + .3 * np.sin(4 * np.pi * f * s)) * np.exp(-s * 3.2) * .10
    if k % 8 == 0: note = note + np.sin(2 * np.pi * ch[0] / 2 * s) * np.exp(-s * 1.5) * .12
    if tb > up:   # pulso suave cuando llega Sumiago
        if k % 4 == 0: note = note + np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 25)) * s) * np.exp(-s * 12) * .35
        if k % 2 == 1: note = note + rng.randn(len(s)) * np.exp(-s * 70) * .04
    i = int(tb * SR); e = min(N, i + len(note)); mus[i:e] += note[:e - i]
mus *= np.clip(x / 1.2, 0, 1) * np.clip((T - x) / 1.5, 0, 1)
dark = (x > r.ct(2)) & (x < r.ct(4) - .3)       # los revendedores: más bajita
mus *= np.where(dark, .7, 1.0)
out += mus * .9
# --- efectos ---
for i in range(1, 12): add(whoosh(), r.ct(i) - .5, .7)
add(pop(), r.wt(0, 'años')); add(pop(), r.wt(0, 'bolsa'), .6)
add(thud(), r.wt(1, 'vender') + .3, .4); add(pop(), r.wt(1, 'regalarla')); add(pop(), r.wt(1, 'necesitara'))
for k in range(7): add(bubble(), r.wt(2, 'comentarios') - .2 + k * .3, .5)
for k in range(3): add(pop(), r.wt(3, 'revenderla') - .3 + k * .12, .4)
add(thud(), r.wt(3, 'revenderla'), .6)
add(pop(), r.wt(4, 'marketplace')); add(pop(), r.wt(4, 'categoría')); add(shimmer(), r.wt(4, 'regalo'))
add(thud(), r.wt(5, 'precio'), .4); add(ding(), r.wt(5, 'regalo'))
add(shutter(), r.wt(6, 'ordena'), .5); add(pop(), r.wt(6, 'primero'))
add(pop(), r.wt(7, 'quiero')); add(ding(1760), r.wt(7, 'aviso')); add(pop(), r.wt(7, 'ciudad'), .6)
add(bubble(), r.wt(8, 'vamos') - .2); add(bubble(), r.wt(8, 'acostarla'))
add(pop(), r.wt(9, 'sábado')); add(shimmer(), r.wt(9, 'regaló'))
for w in ('vender', 'comprar', 'regalar'): add(pop(), r.wt(10, w))
add(pop(), r.ct(11)); add(pop(), r.wt(11, 'link'))
add(whoosh(.6), r.LOGO_T - .2); add(shimmer(), r.LOGO_T + .9); add(thud(), r.LOGO_T + .35, .6)
mix = v * 1.0 + out * .32
mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
