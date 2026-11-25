import json, numpy as np, wave, sys
sys.argv = ['x', 'still']  # evitar main
import importlib.util
import os
spec = importlib.util.spec_from_file_location('r', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.py')); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
SR = 44100; TL = json.load(open('tl.json')); T = TL['total']; N = int(T * SR)
v = np.load('voice.npy')[:N]; out = np.zeros(N, np.float32); rng = np.random.RandomState(1)
def add(sig, t, g=1.0):
    s = int(t * SR); e = min(N, s + len(sig))
    if s < N: out[s:e] += sig[:e - s] * g
def env(n, a=.005, rel=.1):
    e = np.ones(n); na = int(a * SR); nr = min(n, int(rel * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
tt = lambda d: np.arange(int(d * SR)) / SR
def beep(f=1000, d=.18): x = tt(d); return np.sin(2 * np.pi * f * x) * env(len(x), .003, .03) * .35
def thud(): x = tt(.5); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 9) + rng.randn(len(x)) * np.exp(-x * 40) * .5) * .9
def whoosh(d=.45):
    x = tt(d); n = rng.randn(len(x)); n = np.convolve(n, np.ones(20) / 20, 'same'); return n * np.sin(np.pi * x / d) ** 2 * .35
def pop(): x = tt(.12); return np.sin(2 * np.pi * (500 + 900 * np.exp(-x * 40)) * x) * np.exp(-x * 30) * .5
def tick(): x = tt(.04); return rng.randn(len(x)) * np.exp(-x * 150) * .4
def rip(d=.5): x = tt(d); n = rng.randn(len(x)) * (np.abs(np.sin(x * 260)) > .3); return n * env(len(x), .01, .2) * .3
def shimmer(): x = tt(1.6); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 3) for f in (1320, 1760, 2093, 2637)) * .08
def static(d): x = tt(d); return rng.randn(len(x)) * .25 * env(len(x), .02, .1)

# --- música de misterio (0 → reveal) ---
rev = r.ct(9); x = np.arange(N) / SR
drone = (np.sin(2 * np.pi * 55 * x) * .5 + np.sin(2 * np.pi * 82.4 * x) * .25 + np.sin(2 * np.pi * 110.5 * x) * .12) * (0.6 + .4 * np.sin(2 * np.pi * .1 * x))
noise = np.convolve(rng.randn(N), np.ones(200) / 200, 'same') * 3
mys = (drone + noise * .3) * .16
hb = np.zeros(N)
for k, tb in enumerate(np.arange(1.0, rev - .8, 1.05)):
    s = tt(.12); h = np.sin(2 * np.pi * 50 * s) * np.exp(-s * 30)
    for off, g in ((0, 1), (.22, .7)):
        i = int((tb + off) * SR); hb[i:i + len(h)] += h * g
mys += hb * .5
fade = np.clip((rev - .8 - x) / .5, 0, 1); fade *= np.clip(x / 1.0, 0, 1); out += mys * fade
# --- música positiva (reveal → final) ---
bpm = 112; beat = 60 / bpm; chords = [(220, 277.2, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
pos = np.zeros(N); t0 = rev + .3
for b in range(int((T - t0) / beat)):
    tb = t0 + b * beat; ch = chords[(b // 4) % 4]; s = tt(beat)
    pad = sum(np.sin(2 * np.pi * f * s) for f in ch) * .05 * env(len(s), .02, .2)
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 25)) * s) * np.exp(-s * 12) * (.5 if b % 2 == 0 else 0)
    hat = rng.randn(len(s)) * np.exp(-((s - beat / 2) % beat) * 80) * (s > beat / 2) * .05
    bass = np.sin(2 * np.pi * ch[0] / 2 * s) * .14 * env(len(s), .01, .1)
    i = int(tb * SR); seg = pad + kick + hat + bass; pos[i:i + len(seg)] += seg[:N - i] if i + len(seg) > N else seg
pos *= np.clip((x - t0) / 1.5, 0, 1); out += pos * .55
# --- efectos ---
for i in range(1, 12): add(whoosh(.64), r.ct(i) - .47, .8)
add(thud(), r.wt(0, '12')); add(beep(), r.wt(0, '12') - .3)
add(beep(1000), r.wt(2, '«no') - .2); add(beep(1000), r.wt(3, '«ya') - .2)
for k in range(10): add(beep(1100 + k * 30, .09), r.ct(4) + .3 + k * (r.CL[4]['d'] - .4) / 10, .7)
for k in range(int(r.CL[4]['d'] / .5)): add(tick(), r.ct(4) + k * .5)
for k in range(12): add(tick(), r.ct(5) + .5 + k * .1, .7)
add(thud(), r.wt(5, 'mismo')); add(thud(), r.wt(7, 'desconectado')); add(rip(.35), r.ct(7) + .1, .7)
add(static(.9), r.wt(8, 'yo'), 1.0); add(static(.3), r.ct(9) - .1, .8)
add(thud(), r.wt(9, 'nunca')); add(rip(), r.wt(9, 'inteligencia'), .9)
for w in ('historia', 'canal', 'negocio', 'crear', 'sin'): add(pop(), r.wt(10, w) - .05)
for k in range(3): add(pop(), r.wt(11, 'herramientas') + k * .12)
add(pop(), r.ct(11)); add(pop(), r.wt(11, 'regístrate'))
add(whoosh(.6), r.LOGO_T - .2); add(shimmer(), r.LOGO_T + .9); add(thud(), r.LOGO_T + .35, .6)
mix = v * 1.0 + out * .36
mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
