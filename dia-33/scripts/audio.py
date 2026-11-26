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
def chime(): x = tt(.9); return (np.sin(2 * np.pi * 880 * x) + .5 * np.sin(2 * np.pi * 1320 * x)) * np.exp(-x * 4) * .25
def sparkle(): x = tt(.8); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * (5 + k)) for k, f in enumerate((1568, 2093, 2637, 3136))) * .07
x = np.arange(N) / SR
# --- música alegre y bajita (pluck + bajo + palmas) ---
bpm = 108; beat = 60 / bpm; chords = [(261.6, 329.6, 392), (220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7)]
mus = np.zeros(N); t0 = .2
for b in range(int((T - t0) / beat)):
    tb = t0 + b * beat; ch = chords[(b // 4) % 4]; s = tt(beat)
    pl = sum(np.sin(2 * np.pi * f * 2 * s) * np.exp(-s * 9) for f in ch[(b % 3):(b % 3) + 1]) * .12
    pd = sum(np.sin(2 * np.pi * f * s) for f in ch) * .03 * env(len(s), .02, .2)
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 25)) * s) * np.exp(-s * 12) * (.45 if b % 2 == 0 else 0)
    clap = rng.randn(len(s)) * np.exp(-s * 35) * (.12 if b % 2 else 0)
    hat = rng.randn(len(s)) * np.exp(-((s - beat / 2) % beat) * 80) * (s > beat / 2) * .04
    bs = np.sin(2 * np.pi * ch[0] / 2 * s) * .13 * env(len(s), .01, .1)
    i = int(tb * SR); seg = pl + pd + kick + clap + hat + bs; e = min(N, i + len(seg)); mus[i:e] += seg[:e - i]
mus *= np.clip(x / .8, 0, 1) * np.clip((T - x) / 1.5, 0, 1)
out += mus * .5
# --- efectos ---
for i in range(1, len(r.CL)):
    if i not in r.NOMORPH: add(whoosh(.64), r.ct(i) - .47, .8)
for k in range(1, 6): add(whoosh(.8), r.ct(k + 2), .5)      # la cámara pasa al siguiente puesto
add(sparkle(), r.wt(0, 'vender'), 1.0); add(thud(), r.wt(0, 'año'), .8)
add(chime(), r.ct(1) + .7, .6)
for k, w in enumerate(r.EMO_WORD): add(pop(), r.wt(k + 2, w) - .1); add(pop(), r.wt(k + 2, w) + .1, .6)
for k in range(30):                                          # ruleta
    tk = r.ct(8) - .15 + 2.0 * (1 - (1 - k / 30) ** .5)
    add(tick(), tk, .7)
add(thud(), r.wt(8, 'todo'), .7)
for i in (9, 10, 11):
    add(thud(), r.wt(i, 'no'), .7); add(chime(), r.wt(i, r.EX[i][5]) - .2, .7)
add(sparkle(), r.wt(12, 'mejor'), 1.0); add(thud(), r.wt(12, 'ahora'), .8)
tm = r.wt(13, 'miles')
for k in range(24): add(tick(), tm - .3 + k * 1.4 / 24, .45)
for w in ('voz', 'escenas', 'música'): add(pop(), r.wt(14, w) - .1)
for w in ('cámara', 'actores'): add(pop(), r.wt(14, w) - .1, .8)
add(thud(), r.wt(14, 'inteligencia'), .8)
add(pop(), r.wt(15, 'qué'))
add(pop(), r.wt(16, 'perfil') - .3); add(chime(), r.wt(16, 'ganar'), .6)
add(whoosh(.6), r.LOGO_T - .2); add(shimmer(), r.LOGO_T + .9); add(thud(), r.LOGO_T + .35, .6)
mix = v * 1.0 + out * .34
mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
