"""Voz con Fish Audio y tiempos (tl.json) para el motor de Sumiago.
  set FISH_API_KEY=tu_clave            (Windows)   |  export FISH_API_KEY=tu_clave
  python voz.py                        -> vt/NN.wav, voice.wav y tl.json
  python voz.py --sin-voz              -> solo tl.json con tiempos estimados (para revisar escenas sin gastar voz)
La clave nunca se escribe en archivos ni se sube a GitHub.
"""
import json, os, subprocess, sys, time, urllib.request, wave
import numpy as np
VOCES = {'narrador': 'bd35c17b29c54d3e9d2663863a28d212',      # "narrador educativo sumiago"
         'presentador': '6d13d023d0f44401a6070bdfde9ef620',   # "Presentador"
         'esqueleto': 'a335d470fff248e8890dce6550a2874b',     # mascota Sumiago ("Esqueleto")
         'leeknow': '95f7b8fe6a264953bad59931c6f8c571',       # segundo personaje ("Lee know")
         'femenina': 'bfed5c0810a347dbb62e8ccce7f59c48'}      # "Voz Femenina Español"
SR = 44100; PUN = ',:.…?»!'
G = json.load(open('guion.json', encoding='utf-8')); SIN = '--sin-voz' in sys.argv
os.makedirs('voz', exist_ok=True); os.makedirs('vt', exist_ok=True)

def tts(texto, voz, out):
    key = os.environ.get('FISH_API_KEY') or sys.exit('Falta FISH_API_KEY')
    ref = VOCES.get(voz, voz)
    for a in range(4):
        try:
            r = urllib.request.Request('https://api.fish.audio/v1/tts', json.dumps({'text': texto, 'reference_id': ref, 'format': 'wav'}).encode(),
                                       {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'model': 's1'})
            open(out, 'wb').write(urllib.request.urlopen(r, timeout=120).read()); return
        except Exception as e: print('reintento', e); time.sleep(3)
    sys.exit('Fish Audio no respondió')

def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def leer(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

def palabras(texto, a, d, t0):
    """Reparte las palabras del subtítulo usando las pausas reales de la voz en los signos de puntuación."""
    ws = texto.split(); brk = [i for i, x in enumerate(ws[:-1]) if x[-1] in PUN]; runs = []
    if a is not None:
        hop = int(.01 * SR); rms = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2)) for k in range(0, len(a) - hop, hop)])
        sil = rms < rms.max() * .08; k = 0
        while k < len(sil):
            if sil[k]:
                j = k
                while j < len(sil) and sil[j]: j += 1
                if j - k >= 8 and k > 5 and j < len(sil) - 3: runs.append((k * .01, j * .01))
                k = j
            else: k += 1
        runs = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:len(brk)])
    if len(runs) < len(brk): brk = sorted(sorted(brk, key=lambda i: (ws[i][-1] not in '.:?…»!', i))[:len(runs)])
    segs = []; s0 = 0.0; b0 = 0
    for bi, r in zip(brk, runs): segs.append((b0, bi + 1, s0, r[0])); b0 = bi + 1; s0 = r[1]
    segs.append((b0, len(ws), s0, d)); out = []
    for a0, a1, ta, tb in segs:
        part = ws[a0:a1]; tot = sum(len(x) + 2 for x in part) or 1; t = ta
        for x in part: out.append([x, round(t0 + t, 3)]); t += (len(x) + 2) / tot * (tb - ta)
    return out

clips = []; t = .25
for i, fr in enumerate(G['frases']):
    sub = fr['texto']; habla = fr.get('voz_texto', sub); voz = fr.get('voz', G.get('voz', 'narrador'))
    if SIN:
        d = len(habla) / 15.5 / G.get('velocidad', 1.0); a = None
    else:
        tts(habla, voz, f'voz/{i:02d}.wav')
        semi = fr.get('tono', G.get('tono', 0)); vel = fr.get('velocidad', G.get('velocidad', 1.04))
        af = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse'
        if semi: af += f',asetrate={SR}*{2 ** (semi / 12):.5f},aresample={SR},atempo={1 / 2 ** (semi / 12):.5f}'
        af += f',atempo={vel},aresample={SR}'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'voz/{i:02d}.wav', '-af', af, '-ac', '1', '-ar', str(SR), f'vt/{i:02d}.wav'], check=True)
        d = dur(f'vt/{i:02d}.wav'); a = leer(f'vt/{i:02d}.wav')
    clips.append({'i': i, 't0': round(t, 3), 'd': round(d, 3), 'text': sub, 'words': palabras(sub, a, d, t)})
    t += d + fr.get('pausa', G.get('pausa', .3))
total = round(t + 3.4, 2); v = np.zeros(int(total * SR), np.float32)
if not SIN:
    for c in clips:
        a = leer(f"vt/{c['i']:02d}.wav"); s = int(c['t0'] * SR); v[s:s + len(a)] += a[:len(v) - s]
    w = wave.open('voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(v, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
lv = [float(np.sqrt(np.mean(v[int(f / 30 * SR):int((f + 1) / 30 * SR)] ** 2) + 1e-9)) for f in range(int(total * 30))]
json.dump({'clips': clips, 'total': total, 'lv': lv}, open('tl.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('Duración:', total, 's')
