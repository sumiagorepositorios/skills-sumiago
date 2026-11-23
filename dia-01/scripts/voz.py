"""Genera la voz del guion con Fish Audio, línea por línea.
Uso:  python scripts/voz.py
Requiere la variable de entorno FISH_API_KEY (tu clave de Fish Audio). Nunca escribas la clave en este archivo.
Salida: voice.wav (voz completa) y durs.json (duración de cada línea), en la carpeta actual.
"""
import json, os, subprocess, sys, urllib.request

KEY = os.environ.get('FISH_API_KEY')
VOZ = os.environ.get('FISH_VOICE_ID', 'bd35c17b29c54d3e9d2663863a28d212')  # voz oficial de la mascota Sumiago
if not KEY:
    sys.exit('Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave')

# Sube 1,5 semitonos y queda un poco más rápida; quita silencios al inicio y al final y deja 0,25 s de pausa.
FILTRO = ('silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
          'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
          'aresample=44100,asetrate=44100*1.0905,aresample=44100,atempo=0.954,apad=pad_dur=0.25')

guion = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'guion.txt')
lineas = [l for l in open(guion, encoding='utf-8').read().strip().split('\n') if l.strip()]
os.makedirs('vo', exist_ok=True)
durs = []
for i, l in enumerate(lineas):
    req = urllib.request.Request('https://api.fish.audio/v1/tts',
        data=json.dumps({'text': l, 'reference_id': VOZ, 'format': 'mp3', 'normalize': True}).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's1'})
    mp3, wav = f'vo/{i:02d}.mp3', f'vo/{i:02d}.wav'
    open(mp3, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', FILTRO, '-ac', '1', '-ar', '44100', wav], check=True)
    durs.append(float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav])))
    print(f'{i + 1}/{len(lineas)}  {durs[-1]:.2f}s  {l[:50]}')
json.dump(durs, open('durs.json', 'w'))
open('lst.txt', 'w').write(''.join(f"file 'vo/{i:02d}.wav'\n" for i in range(len(durs))))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'lst.txt', '-c', 'copy', 'voice.wav'], check=True)
print(f'Listo: voice.wav ({sum(durs):.1f} s)')
