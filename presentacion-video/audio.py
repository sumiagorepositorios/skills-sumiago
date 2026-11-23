import json, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR = 44100
rng = np.random.default_rng(7)

def load(f):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r)

def tone(f, d, typ='sine', g=.3, a=.005, r=None):
    n = int(d * SR); t = np.arange(n) / SR
    if np.ndim(f) == 0: ph = 2 * np.pi * f * t
    else: ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) if typ == 'sine' else (np.sign(np.sin(ph)) * .6 if typ == 'square' else 2 / np.pi * np.arcsin(np.sin(ph)))
    return w * env(n, a, r or d / 3) * g

def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)

def sweep(f0, f1, d):
    n = int(d * SR); return np.geomspace(f0, f1, n)

def noise_sweep(d, lo0, lo1, g):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); k = 8; seg = n // k
    for i in range(k):
        f = lo0 * (lo1 / lo0) ** (i / (k - 1))
        out[i * seg:(i + 1) * seg] = bp(x, f, min(f * 2.2, 18000))[i * seg:(i + 1) * seg]
    e = np.sin(np.pi * np.arange(n) / n) ** 1.5
    return out * e * g

SFX = {
    'whoosh': lambda: noise_sweep(.5, 300, 2600, .5),
    'swish': lambda: noise_sweep(.3, 2000, 6000, .25),
    'pop': lambda: tone(sweep(500, 980, .12), .12, g=.32, r=.04),
    'ding': lambda: tone(1318.5, .6, g=.2, r=.18) + np.pad(tone(1975.5, .45, g=.09, r=.12), (int(.02 * SR), int(.6 * SR)))[:int(.6 * SR)],
    'stamp': lambda: tone(sweep(170, 50, .3), .3, g=.7, r=.07),
    'buzz': lambda: (tone(110, .3, 'square', .12, r=.2) + tone(117, .3, 'square', .1, r=.2)),
    'alert': lambda: np.concatenate([tone(880, .15, 'square', .08, r=.08), tone(660, .25, 'square', .08, r=.1)]),
    'coin': lambda: np.concatenate([tone(987.8, .08, 'square', .06, r=.05), tone(1318.5, .35, 'square', .06, r=.12)]),
    'cash': lambda: np.concatenate([tone(1568, .1, 'tri', .16, r=.06), tone(2093, .45, 'tri', .14, r=.15)]),
    'morph': lambda: tone(sweep(220, 1500, .95), .95, g=.16, a=.25, r=.5) + np.pad(noise_sweep(.4, 1500, 5000, .2), (int(.5 * SR), int(.95 * SR)))[:int(.95 * SR)],
    'tick': lambda: tone(1800, .04, 'square', .03, r=.02),
}

def music(n):
    # pad suave La m – Fa – Do – Sol, 84 bpm, con arpegio
    CH = [[220, 261.63, 329.63], [174.61, 220, 261.63], [261.63, 329.63, 392], [196, 246.94, 293.66]]
    beat = 60 / 84 / 2; bar = beat * 8; out = np.zeros(n + SR * 6, np.float32)
    t = 0.0; i = 0
    while t * SR < n:
        ch = CH[i % 4]; s = int(t * SR)
        for f in ch:
            x = tone(f / 2, bar * 1.15, 'tri', .05, a=.6, r=bar) + tone(f, bar * 1.15, 'sine', .03, a=.8, r=bar)
            out[s:s + len(x)] += x
        b = tone(ch[0] / 4, bar, 'sine', .07, a=.05, r=bar / 2); out[s:s + len(b)] += b
        for k, a in enumerate([0, 1, 2, 1, 0, 2, 1, 2]):
            x = tone(ch[a] * 2, beat * 1.6, 'sine', .025, a=.01, r=.25); s2 = s + int(k * beat * SR); out[s2:s2 + len(x)] += x
        t += bar; i += 1
    return out[:n]

# Eventos de las escenas nuevas (tiempos de la voz, iguales a pres_scenes.php)
CUES = {
 'es': {'03': [(2.1,'pop'),(3.0,'coin'),(5.5,'pop'),(6.2,'coin'),(8.5,'swish'),(10.0,'stamp'),(13.0,'pop'),(14.8,'pop'),(16.7,'pop'),(18.2,'pop'),(20.7,'pop'),(21.6,'morph'),(0.6,'swish')],
        '03b': [(1.6,'ding'),(1.8,'swish'),(5.9,'pop'),(6.8,'pop'),(7.7,'pop'),(8.7,'pop'),(9.0,'pop'),(9.6,'tick'),(10.3,'buzz'),(11.4,'alert'),(12.9,'swish'),(14.4,'pop')],
        '03c': [(0.3,'swish'),(1.0,'ding'),(2.4,'whoosh'),(4.2,'whoosh'),(6.9,'cash'),(7.0,'pop'),(7.7,'whoosh'),(8.2,'pop'),(9.4,'pop'),(9.6,'swish'),(13.2,'pop')]},
 'en': {'03': [(1.6,'pop'),(2.4,'coin'),(4.6,'pop'),(5.4,'coin'),(7.9,'swish'),(9.3,'stamp'),(12.6,'pop'),(14.2,'pop'),(16.3,'pop'),(18.2,'pop'),(21.0,'pop'),(22.15,'morph'),(0.6,'swish')],
        '03b': [(1.6,'ding'),(1.8,'swish'),(5.5,'pop'),(6.1,'pop'),(7.6,'pop'),(8.6,'pop'),(8.9,'pop'),(9.5,'tick'),(10.5,'buzz'),(11.8,'alert'),(12.6,'swish'),(14.1,'pop')],
        '03c': [(0.3,'swish'),(1.4,'ding'),(3.0,'whoosh'),(4.7,'whoosh'),(7.4,'cash'),(7.5,'pop'),(8.3,'whoosh'),(8.8,'pop'),(10.0,'pop'),(10.2,'swish'),(14.0,'pop')]},
}

lang = sys.argv[1]
D = json.load(open(f'/home/claude/pres/data-{lang}.json'))
tot = sum(s['L'] for s in D); N = int(tot * SR) + SR
voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
def put(buf, x, t):
    s = int(t * SR); e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s]
off = 0.0
for s in D:
    v = load(f"/home/claude/pres/voz/{lang}-{s['id']}.mp3"); put(voice, v, off + .5)
    ev = list(s['ev']) + [(t + .5, n) for t, n in CUES[lang].get(s['id'], [])]
    for t, n in ev: put(fx, SFX[n]().astype(np.float32), off + t)
    off += s['L']
# música bajita que baja más cuando habla la voz
m = music(N)
lvl = np.abs(voice); k = int(.25 * SR)
act = np.convolve(lvl > .02, np.ones(k) / k, 'same')
duck = 1 - .55 * np.clip(act * 3, 0, 1)
duck = np.convolve(duck, np.ones(k) / k, 'same')
fade = np.ones(N); fade[:2 * SR] = np.linspace(0, 1, 2 * SR); fade[-3 * SR:] = np.linspace(1, 0, 3 * SR)
mix = voice * 1.0 + fx * .55 + m * .55 * duck * fade
pk = np.max(np.abs(mix)); mix = mix / max(1, pk / .97)
wavfile.write(f'/home/claude/pres/out/audio-{lang}.wav', SR, (mix * 32767).astype(np.int16))
print(lang, round(tot, 2), 's', 'pico', round(float(pk), 3), 'musica rms', round(float(np.sqrt(np.mean((m * .55 * duck) ** 2))), 4), 'voz rms', round(float(np.sqrt(np.mean(voice ** 2))), 4))
