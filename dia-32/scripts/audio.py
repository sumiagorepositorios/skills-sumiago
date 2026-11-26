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
def thud(): x = tt(.5); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 9) + rng.randn(len(x)) * np.exp(-x * 40) * .5) * .9
def whoosh(d=.45):
    x = tt(d); n = rng.randn(len(x)); n = np.convolve(n, np.ones(20) / 20, 'same'); return n * np.sin(np.pi * x / d) ** 2 * .35
def pop(): x = tt(.12); return np.sin(2 * np.pi * (500 + 900 * np.exp(-x * 40)) * x) * np.exp(-x * 30) * .5
def tick(): x = tt(.04); return rng.randn(len(x)) * np.exp(-x * 150) * .4
def shimmer(): x = tt(1.6); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 3) for f in (1320, 1760, 2093, 2637)) * .08
def buzz(d=.7):  # vibración del celular
    x = tt(d); return np.sign(np.sin(2 * np.pi * 150 * x)) * (0.6 + .4 * np.sin(2 * np.pi * 22 * x)) * env(len(x), .01, .05) * .22
def click(): x = tt(.06); return (np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 120) + rng.randn(len(x)) * np.exp(-x * 200) * .3) * .5
def chime(): x = tt(.9); return (np.sin(2 * np.pi * 880 * x) + .5 * np.sin(2 * np.pi * 1320 * x)) * np.exp(-x * 4) * .25
def sting():  # golpe dramático + cuerdas que chillan
    x = tt(1.4); s = sum(np.sin(2 * np.pi * f * x + np.sin(2 * np.pi * 6 * x) * 2) for f in (740, 784, 1046)) * .12 * np.exp(-x * 1.6)
    return s + np.concatenate([thud(), np.zeros(len(x) - len(thud()))]) * 1.1
x = np.arange(N) / SR
# --- música 1: noche tranquila (cajita de música suave) ---
t_pat = r.ct(4) - .3; t_turn = r.wt(9, 'volteó') - .3; t_cta = r.ct(10) - .2
m1 = np.zeros(N); notes = [523.3, 659.3, 784, 659.3, 587.3, 698.5, 880, 698.5]
for k, tb in enumerate(np.arange(.2, t_pat, .45)):
    s = tt(1.2); f = notes[k % len(notes)]; add_ = np.sin(2 * np.pi * f * s) * np.exp(-s * 3.5) * .16 + np.sin(2 * np.pi * f / 2 * s) * .05 * np.exp(-s * 2)
    i = int(tb * SR); e = min(N, i + len(s)); m1[i:e] += add_[:e - i]
pad = (np.sin(2 * np.pi * 130.8 * x) + np.sin(2 * np.pi * 196 * x) * .6) * .05
m1 += pad * np.clip((t_pat - x) / .4, 0, 1)
out += m1 * np.clip(x / 1.0, 0, 1) * np.clip((t_pat + .2 - x) / .3, 0, 1)
# --- música 2: tema sensual y misterioso (bajo lento + platillos suaves) ---
m2 = np.zeros(N); bpm = 84; beat = 60 / bpm; bass = [110, 110, 130.8, 98]
for b in range(int((t_turn - t_pat) / beat) + 1):
    tb = t_pat + b * beat; s = tt(beat)
    bs = np.sin(2 * np.pi * bass[(b // 2) % 4] * s) * .22 * env(len(s), .02, .2)
    hat = rng.randn(len(s)) * np.exp(-s * 40) * .03
    snap = (rng.randn(len(s)) * np.exp(-s * 60) * .12) if b % 2 else 0
    pd = sum(np.sin(2 * np.pi * f * s) for f in (220, 261.6, 329.6)) * .025
    seg = bs + hat + snap + pd; i = int(tb * SR); e = min(N, i + len(seg)); m2[i:e] += seg[:e - i]
out += m2 * np.clip((x - t_pat) / .5, 0, 1) * np.clip((t_turn - x) / .25, 0, 1)
# --- tensión: latidos ---
for k, tb in enumerate(np.arange(t_turn, t_cta - .2, .55)):
    s = tt(.12); h = np.sin(2 * np.pi * 50 * s) * np.exp(-s * 30)
    for off, g in ((0, 1), (.2, .7)): add(h * .9, tb + off, g)
# --- música 3: positiva (llamado a la acción) ---
bpm = 112; beat = 60 / bpm; chords = [(220, 277.2, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
pos = np.zeros(N); t0 = t_cta + .2
for b in range(int((T - t0) / beat)):
    tb = t0 + b * beat; ch = chords[(b // 4) % 4]; s = tt(beat)
    pd = sum(np.sin(2 * np.pi * f * s) for f in ch) * .05 * env(len(s), .02, .2)
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 25)) * s) * np.exp(-s * 12) * (.5 if b % 2 == 0 else 0)
    hat = rng.randn(len(s)) * np.exp(-((s - beat / 2) % beat) * 80) * (s > beat / 2) * .05
    bs = np.sin(2 * np.pi * ch[0] / 2 * s) * .14 * env(len(s), .01, .1)
    i = int(tb * SR); seg = pd + kick + hat + bs; e = min(N, i + len(seg)); pos[i:e] += seg[:e - i]
out += pos * np.clip((x - t0) / 1.2, 0, 1) * .55
# --- efectos ---
for i in range(1, len(r.CL)):
    if i not in r.NOMORPH: add(whoosh(.64), r.ct(i) - .47, .8)
vb = r.wt(0, 'vibrar') - .5; tc = r.wt(2, 'contesté')
k = vb
while k < tc - .2:
    add(buzz(.55), k, .9); k += .95
for kk in range(6): add(tick(), .3 + kk * 1.0, .5)
add(thud(), r.wt(0, '3:00'), .8); add(thud(), r.wt(1, 'nada'), .8); add(thud(), r.wt(2, 'nunca'), .8)
add(click(), tc); add(chime(), tc + .05, .6)
add(shimmer(), r.wt(4, 'patricia'), .7)
add(thud(), r.ct(7), 1.0); add(thud(), r.wt(8, 'escuela'), .8); add(pop(), r.wt(8, 'redes') - .5)
add(whoosh(.5), r.wt(9, 'volteó') - .2, 1.0); add(sting(), r.wt(9, 'ojos') - .05, 1.0)
for w in ('producto', 'servicio', 'negocio', 'empresa'): add(pop(), r.wt(10, w) - .05)
add(pop(), r.wt(10, 'regístrate')); add(chime(), r.wt(10, 'regístrate') + .1, .6); add(pop(), r.wt(10, 'comienza'))
add(whoosh(.6), r.LOGO_T - .2); add(shimmer(), r.LOGO_T + .9); add(thud(), r.LOGO_T + .35, .6)
mix = v * 1.0 + out * .36
mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
