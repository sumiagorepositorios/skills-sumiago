"""Mezcla: voz + música de fondo bajita (hecha por código, sin derechos de autor) + efectos.
  python audio.py   -> mix.wav   (necesita guion.json, tl.json y voice.wav)
Música: G['musica'] = 'alegre' (por defecto), 'misterio' o 'tension' (tensa al inicio y alegre desde la frase G['giro']).
"""
import json, os, sys, wave, importlib.util
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('m', os.path.join(AQUI, 'motor.py')); M = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(M)
SR = 44100; T = M.TL['total']; N = int(T * SR); rng = np.random.RandomState(1); G = M.G
w = wave.open('voice.wav'); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)[:N] / 32768
v = np.pad(v, (0, N - len(v))); out = np.zeros(N, np.float32)
def add(sig, t, g=1.0):
    if t is None: return
    s = int(t * SR); e = min(N, s + len(sig))
    if 0 <= s < N: out[s:e] += sig[:e - s] * g
def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=.005, r=.1):
    e = np.ones(n); na = max(1, int(a * SR)); nr = min(n, int(r * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def whoosh(d=.6): x = tt(d); n = np.convolve(rng.randn(len(x)), np.ones(20) / 20, 'same'); return n * np.sin(np.pi * x / d) ** 2 * .35
def pop(): x = tt(.12); return np.sin(2 * np.pi * (500 + 900 * np.exp(-x * 40)) * x) * np.exp(-x * 30) * .5
def ding(): x = tt(.7); return (np.sin(2 * np.pi * 1318 * x) + .5 * np.sin(2 * np.pi * 1976 * x)) * np.exp(-x * 6) * .22
def thud(): x = tt(.5); return np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 9) * .8
def shimmer(): x = tt(1.6); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 3) for f in (1320, 1760, 2093, 2637)) * .08
def tick(): x = tt(.04); return rng.randn(len(x)) * np.exp(-x * 150) * .35

def pista(t0, t1, alegre=True):
    """Música por compases: acordes + bajo + bombo + platillo (alegre) o dron con latido (misterio)."""
    m = np.zeros(N); x0 = int(t0 * SR); x1 = int(t1 * SR)
    if not alegre:
        x = np.arange(x1 - x0) / SR
        m[x0:x1] = (np.sin(2 * np.pi * 55 * x) * .5 + np.sin(2 * np.pi * 82.4 * x) * .25) * (0.6 + .4 * np.sin(2 * np.pi * .1 * x)) * .3
        for tb in np.arange(t0 + 1, t1 - .5, 1.05):
            s = tt(.12); h = np.sin(2 * np.pi * 50 * s) * np.exp(-s * 30)
            for off, g in ((0, 1), (.22, .7)):
                i = int((tb + off) * SR); m[i:i + len(h)] += h * g * .6
        return m
    beat = 60 / 112; ch = [(261.6, 329.6, 392), (220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7)]
    for b in range(int((t1 - t0) / beat)):
        tb = t0 + b * beat; c = ch[(b // 4) % 4]; s = tt(beat)
        seg = sum(np.sin(2 * np.pi * f * s) for f in c) * .05 * env(len(s), .02, .2)
        seg += np.sin(2 * np.pi * (50 + 90 * np.exp(-s * 25)) * s) * np.exp(-s * 12) * (.5 if b % 2 == 0 else 0)
        seg += rng.randn(len(s)) * np.exp(-((s - beat / 2) % beat) * 80) * (s > beat / 2) * .05
        seg += np.sin(2 * np.pi * c[0] / 2 * s) * .14 * env(len(s), .01, .1)
        i = int(tb * SR); n = min(len(seg), N - i)
        if n > 0: m[i:i + n] += seg[:n]
    return m

mus = G.get('musica', 'alegre')
if mus == 'misterio': music = pista(0, T, False)
elif mus == 'tension':
    g = M.ct(G.get('giro', len(M.CL) // 2)) - .2; music = pista(0, g, False) * np.clip((g - np.arange(N) / SR) / .5, 0, 1) + pista(g, T, True)
else: music = pista(0, T, True)
x = np.arange(N) / SR; music *= np.clip(x / 1.0, 0, 1) * np.clip((T - x) / 1.0, 0, 1)
out += music * .5

# efectos sincronizados con lo que aparece en pantalla
for i in range(1, len(M.CL)): add(whoosh(), M.ST[i] - .3, .8)
for i, fr in enumerate(G['frases']):
    e = fr['escena']; tp = e.get('tipo')
    if tp in ('tarjetas', 'telefono', 'linea'):
        for tq in M.appear_times(i, e.get('items') or e.get('filas') or []): add(pop(), tq)
    elif tp == 'lista': add(pop(), M.ct(i)); add(ding(), M.ct(i) + .3)
    elif tp == 'dato': add(thud(), M.ct(i)); add(ding(), M.ct(i) + .8)
    elif tp == 'titulo': add(pop(), M.ct(i))
    elif tp == 'comparacion': add(pop(), M.ct(i)); add(ding(), M.wt(i, e['b'].get('palabra')) or M.ct(i) + M.CL[i]['d'] * .5)
    elif tp == 'dialogo': add(pop(), M.ct(i), .6)
    elif tp == 'cierre': add(ding(), M.wt(i, e.get('boton_palabra', 'link')) or M.wt(i, 'enlace'))
    for k in e.get('ticks', []): add(tick(), M.wt(i, k))
add(whoosh(.7), M.LOGO_T - .25); add(thud(), M.LOGO_T + .2, .6); add(shimmer(), M.LOGO_T + .9)
mix = v + out * .36; mix /= max(1, np.abs(mix).max() / .95)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('mix.wav listo')
