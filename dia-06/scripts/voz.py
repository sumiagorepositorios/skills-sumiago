"""Genera la voz del Día 6 con Fish Audio, una frase por subtítulo (las 22 frases de CAPS en render.py).
Voz "Presentador" (6d13d023d0f44401a6070bdfde9ef620), luego 4,5 % más aguda, 7 % más rápida y un poco más brillante.
Uso:  set FISH_API_KEY=tu_clave
      python scripts/voz.py
Salida en la carpeta actual: vo/NN.wav (original), vo/t/NN.wav (procesada) y vo/dur.json (duración de cada frase).
Nunca escribas la clave en este archivo.
"""
import json, os, subprocess, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import CAPS

KEY = os.environ.get('FISH_API_KEY')
if not KEY:
    sys.exit('Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave')
VOZ = os.environ.get('FISH_VOICE_ID', '6d13d023d0f44401a6070bdfde9ef620')
rep = {'sumiago.com': 'sumiago punto com', '1 minuto': 'un minuto', 'hasta 5': 'hasta cinco'}
os.makedirs(os.path.join('vo', 't'), exist_ok=True)
durs = []
for i, (a, b, t) in enumerate(CAPS):
    t = t.replace('*', '')
    for k, v in rep.items(): t = t.replace(k, v)
    t = t[0].upper() + t[1:]
    if not t.endswith(('.', '?', '!')): t += '.'
    raw = os.path.join('vo', f'{i:02d}.wav'); out = os.path.join('vo', 't', f'{i:02d}.wav')
    for intento in range(4):
        try:
            req = urllib.request.Request('https://api.fish.audio/v1/tts',
                data=json.dumps({'text': t, 'reference_id': VOZ, 'format': 'wav'}, ensure_ascii=False).encode(),
                headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's1'})
            open(raw, 'wb').write(urllib.request.urlopen(req, timeout=120).read()); break
        except Exception as e:
            print(i, 'reintento', e); time.sleep(3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                    'aresample=44100,asetrate=44100*1.045,aresample=44100,atempo=1.07,equalizer=f=3000:t=q:w=1:g=2', '-ac', '1', out], check=True)
    durs.append(float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out])))
    print(f'{i + 1}/{len(CAPS)}  hueco {b - a:.2f}s  voz {durs[-1]:.2f}s  {t}')
json.dump(durs, open(os.path.join('vo', 'dur.json'), 'w'))
print('Listo: vo/t y vo/dur.json. Si una voz dura más que su hueco, acorta la frase.')
