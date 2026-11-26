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
dark = (x > r.ct(1)) & (x < r.ct(3) - .3)       # la noche y las dudas: más bajita
mus *= np.where(dark, .65, 1.0)
out += mus * .9
# --- efectos ---
for i in range(1, 12): add(whoosh(), r.ct(i) - .5, .7)
add(pop(), r.wt(0, 'trabaja')); add(shimmer(), r.wt(0, 'noche') - .2); add(pop(), r.wt(0, 'estudia'))
add(thud(), r.wt(1, 'universidad'), .4); add(thud(), r.wt(1, 'celular'), .6); add(pop(), r.wt(1, '10')); add(pop(), r.wt(1, 'dormidos'))
add(bubble(), r.wt(2, 'público'))
for k in range(3): add(pop(), r.wt(2, 'nadie') + k * .15, .4)
for k in range(3): add(pop(), r.wt(3, 'cursos') + k * .2, .6)
add(ding(), r.wt(3, 'inteligencia'))
for k in range(5): add(page(), r.ct(4) + k * .71, .4)
add(ding(1760), r.wt(5, 'fotos')); add(shutter(), r.wt(5, 'descripciones'), .3); add(pop(), r.wt(5, 'ella'))
for k in range(20): add(shutter(), r.wt(6, 'inteligencia') + k * .08, .15)
add(shimmer(), r.wt(6, 'publicaciones')); add(pop(), r.wt(6, 'minutos'))
add(pop(), r.wt(7, 'primera')); add(pop(), r.wt(7, 'primera') + .4); add(thud(), r.wt(7, 'tercera'), .5); add(ding(2093), r.wt(7, 'preguntaron'))
add(pop(), r.wt(8, 'experta')); add(thud(), r.wt(8, 'adivinar'), .7)
add(whoosh(.5), r.wt(9, 'ahorra'), .6)
add(pop(), r.wt(10, 'vendes')); add(pop(), r.wt(10, 'empezar'))
add(pop(), r.ct(11)); add(pop(), r.wt(11, 'link')); add(shimmer(), r.wt(11, 'noche'))
add(whoosh(.6), r.LOGO_T - .2); add(shimmer(), r.LOGO_T + .9); add(thud(), r.LOGO_T + .35, .6)
mix = v * 1.0 + out * .32
mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
