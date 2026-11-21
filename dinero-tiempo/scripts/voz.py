"""Genera la narración con Fish Audio y la línea de tiempo del video.
Uso:  python scripts/voz.py      (necesita la variable FISH_API_KEY; nunca escribas la clave aquí)
Salida en la carpeta actual: voz/NN.wav (original), vt/NN.wav (recortado y 4 % más rápido) y tl.json (inicio y duración de cada frase).
"""
import json, os, subprocess, sys, time, urllib.request

KEY = os.environ.get('FISH_API_KEY')
VOZ = os.environ.get('FISH_VOICE_ID', 'bd35c17b29c54d3e9d2663863a28d212')  # voz oficial de la mascota Sumiago
if not KEY:
    sys.exit('Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave')
g = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'guion.json'), encoding='utf-8'))
os.makedirs('voz', exist_ok=True); os.makedirs('vt', exist_ok=True)
for i, t in enumerate(g):
    for a in range(4):  # Fish a veces falla una frase: reintenta
        try:
            r = urllib.request.Request('https://api.fish.audio/v1/tts', json.dumps({'text': t, 'reference_id': VOZ, 'format': 'wav'}).encode(),
                                       {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's1'})
            open(f'voz/{i:02d}.wav', 'wb').write(urllib.request.urlopen(r, timeout=90).read()); print(i, 'ok'); break
        except Exception as e:
            print(i, 'error', e); time.sleep(3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'voz/{i:02d}.wav', '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.04,aresample=44100',
                    '-ac', '1', f'vt/{i:02d}.wav'], check=True)
t = 0.3; tl = []
for i, x in enumerate(g):
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vt/{i:02d}.wav']))
    tl.append({'i': i, 't0': round(t, 3), 'd': round(d, 3), 'text': x}); t += d + 0.45
json.dump({'clips': tl, 'total': round(t + 3.0, 2)}, open('tl.json', 'w'), ensure_ascii=False)
open('lv.json', 'w').write('[]')
print('Listo: tl.json', round(t + 3.0, 1), 's')
