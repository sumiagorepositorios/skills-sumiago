"""Voz + música con ritmo bajita (hecha por código, sin derechos de autor) + efectos: caja registradora, pops, dings,
"bajón", subida antes de la membresía, transiciones y brillo del logo.
Uso (después de 'python scripts/render.py meta'):  python scripts/audio.py   -> mix.wav y lv.json
"""
import numpy as np, json, wave
SR = 44100; tl = json.load(open('tl.json')); N = int(tl['total'] * SR)
def rd(f):
    w = wave.open(f); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
voice = np.zeros(N, np.float32)
for c in tl['clips']:
    a = rd(f"vt/{c['i']:02d}.wav"); s = int(c['t0'] * SR); voice[s:s + len(a)] += a[:N - s]
voice /= np.abs(voice).max() / 0.92
t = np.arange(N) / SR; mus = np.zeros(N, np.float32); bpm = 118; bt = 60 / bpm
ch = [[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7]]  # C Am F G
nb = int(tl['total'] / bt) + 1
for j in range(nb):
    s = int(j * bt * SR); c = ch[(j // 8) % 4]
    L = min(N - s, int(.3 * SR))
    if L <= 0: break
    pt = np.arange(L) / SR
    mus[s:s + L] += 0.16 * np.exp(-pt * 16) * np.sin(2 * np.pi * (50 + 110 * np.exp(-pt * 35)) * pt) if j % 2 == 0 else 0   # bombo
    if j % 2 == 1:
        nz = np.random.default_rng(j).standard_normal(L).astype(np.float32); mus[s:s + L] += 0.035 * nz * np.exp(-pt * 25)    # caja
    for h in range(2):
        hs = s + int(h * bt / 2 * SR); hl = min(N - hs, int(.05 * SR))
        if hl > 0: mus[hs:hs + hl] += 0.012 * np.random.default_rng(j * 7 + h).standard_normal(hl) * np.exp(-np.arange(hl) / SR * 80)
    f = c[(j * 2) % 3] * 2; L2 = min(N - s, int(.25 * SR)); pt2 = np.arange(L2) / SR
    mus[s:s + L2] += 0.03 * np.exp(-pt2 * 9) * (np.sign(np.sin(2 * np.pi * f * pt2)) * 0.4 + np.sin(2 * np.pi * f * pt2))
    if j % 8 == 0:
        L3 = min(N - s, int(8 * bt * SR)); pt3 = np.arange(L3) / SR
        for fr in c: mus[s:s + L3] += 0.018 * np.sin(2 * np.pi * fr / 2 * pt3) * np.minimum(1, pt3 / .3) * np.minimum(1, (8 * bt - pt3) / .3)
env = np.convolve(np.abs(voice), np.ones(4410) / 4410, 'same'); duck = 1 - 0.6 * np.clip(env * 12, 0, 1)
mix = voice + mus * duck * 0.5
rng = np.random.default_rng(5)
def add(s, x):
    s = int(s * SR)
    if s < 0 or s >= N: return
    L = min(len(x), N - s); mix[s:s + L] += x[:L]
for tc, k in json.load(open('clicks.json')):
    if k == 'cash':
        L = int(.7 * SR); pt = np.arange(L) / SR
        x = 0.12 * np.exp(-pt * 40) * rng.standard_normal(L)
        x += sum(0.09 * np.exp(-pt * 6) * np.sin(2 * np.pi * f * pt) for f in (2637, 3520)) * (pt > .06)
        add(tc - .05, x.astype(np.float32))
    elif k == 'pop':
        L = int(.12 * SR); pt = np.arange(L) / SR; add(tc, (0.22 * np.exp(-pt * 40) * np.sin(2 * np.pi * (500 + 900 * pt * 8) * pt)).astype(np.float32))
    elif k == 'ding':
        L = int(1.0 * SR); pt = np.arange(L) / SR; add(tc, (sum(0.07 * np.exp(-pt * (4 + i)) * np.sin(2 * np.pi * f * pt) for i, f in enumerate([1568, 2093, 2637]))).astype(np.float32))
    elif k == 'down':
        L = int(.8 * SR); pt = np.arange(L) / SR; add(tc, (0.12 * np.exp(-pt * 3) * np.sin(2 * np.pi * (400 * np.exp(-pt * 2.5)) * pt * 3)).astype(np.float32))
    elif k == 'riser':
        L = int(.7 * SR); pt = np.arange(L) / SR; nz = rng.standard_normal(L).astype(np.float32); nz = np.convolve(nz, np.ones(8) / 8, 'same')
        add(tc, (0.13 * nz * (pt / .7) ** 2 + 0.05 * np.sin(2 * np.pi * (200 + 900 * pt / .7) * pt) * (pt / .7)).astype(np.float32))
    elif k == 'whoosh':
        L = int(.35 * SR); nz = rng.standard_normal(L).astype(np.float32); nz = np.convolve(nz, np.ones(30) / 30, 'same')
        add(tc, 0.3 * nz * np.sin(np.pi * np.arange(L) / L) ** 2)
s = json.load(open('logo_t.json')) + 0.4; L = int(1.6 * SR); pt = np.arange(L) / SR
add(s, (sum(np.sin(2 * np.pi * f * pt) * np.exp(-pt * (3 + k)) for k, f in enumerate([1318.5, 1760, 2093, 2637])) * 0.07 + 0.22 * np.exp(-pt * 14) * np.sin(2 * np.pi * (70 + 60 * np.exp(-pt * 20)) * pt)).astype(np.float32))
mix[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))
mix = np.clip(mix / np.abs(mix).max() * 0.95, -1, 1)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
fps = 30; nf = int(tl['total'] * fps)
json.dump([float(np.abs(voice[int(i * SR / fps):int((i + 1) * SR / fps)]).mean()) for i in range(nf)], open('lv.json', 'w'))
print('Listo: mix.wav')
