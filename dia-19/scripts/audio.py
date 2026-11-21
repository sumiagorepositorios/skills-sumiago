"""Mezcla la voz con música suave hecha por código (sin derechos de autor) , golpes en los datos y el brillo sonoro del logo final.
Uso (después de 'python scripts/render.py meta'):  python scripts/audio.py   -> mix.wav y lv.json (volumen por cuadro para animaciones)
"""
import numpy as np, json, wave
SR = 44100; tl = json.load(open('tl.json')); N = int(tl['total'] * SR)
def rd(f):
    w = wave.open(f); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
voice = np.zeros(N, np.float32)
for c in tl['clips']:
    a = rd(f"vt/{c['i']:02d}.wav"); s = int(c['t0'] * SR); voice[s:s + len(a)] += a[:N - s]
voice /= np.abs(voice).max() / 0.92
t = np.arange(N) / SR; mus = np.zeros(N, np.float32)
ch = [[146.8, 220, 293.7], [116.5, 174.6, 233.1], [130.8, 196, 261.6], [110, 164.8, 220]]  # Dm Bb C Am
for k in range(int(tl['total'] / 4) + 1):
    s = int(k * 4 * SR); e = min(N, s + int(4.3 * SR)); tt = t[s:e] - k * 4
    env = np.minimum(1, tt / 0.8) * np.minimum(1, (4.3 - tt) / 0.8)
    for f in ch[k % 4]: mus[s:e] += env * 0.05 * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt))
    for j in range(16):
        ps = s + int(j * 0.25 * SR); pe = min(N, ps + int(0.3 * SR))
        if ps >= N: break
        f = ch[k % 4][(j * 2) % 3] * 4; pt = np.arange(pe - ps) / SR
        mus[ps:pe] += 0.022 * np.exp(-pt * 12) * np.sin(2 * np.pi * f * pt)
    for j in range(4):
        ps = s + int(j * SR); pe = min(N, ps + int(0.25 * SR))
        if ps >= N: break
        pt = np.arange(pe - ps) / SR; mus[ps:pe] += 0.11 * np.exp(-pt * 18) * np.sin(2 * np.pi * (55 + 90 * np.exp(-pt * 30)) * pt)
env = np.convolve(np.abs(voice), np.ones(4410) / 4410, 'same'); duck = 1 - 0.55 * np.clip(env * 12, 0, 1)
mix = voice + mus * duck * 0.55   # música bajita
for tc in json.load(open('clicks.json')):  # golpes en "cierran", "uno" y "regístrate"
    s = int(tc * SR); L = int(0.06 * SR); pt = np.arange(L) / SR
    if s + L < N: mix[s:s + L] += 0.35 * np.exp(-pt * 90) * np.sin(2 * np.pi * 2400 * pt) + 0.2 * np.exp(-pt * 60) * np.sin(2 * np.pi * 900 * pt)
s = int(json.load(open('logo_t.json')) * SR + 0.4 * SR); L = int(1.6 * SR); pt = np.arange(L) / SR   # brillo del logo
if s + L < N:
    mix[s:s + L] += sum(np.sin(2 * np.pi * f * pt) * np.exp(-pt * (3 + k)) for k, f in enumerate([1318.5, 1760, 2093, 2637])) * 0.06 + 0.2 * np.exp(-pt * 14) * np.sin(2 * np.pi * (70 + 60 * np.exp(-pt * 20)) * pt)
mix[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))
mix = np.clip(mix / np.abs(mix).max() * 0.95, -1, 1)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
fps = 30; nf = int(tl['total'] * fps)
json.dump([float(np.abs(voice[int(i * SR / fps):int((i + 1) * SR / fps)]).mean()) for i in range(nf)], open('lv.json', 'w'))
print('Listo: mix.wav')
