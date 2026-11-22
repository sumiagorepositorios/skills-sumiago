"""Genera las 11 frases del Día 7 con la voz oficial de la mascota (Fish Audio bd35c17b29c54d3e9d2663863a28d212),
cada una con su velocidad, como en el video publicado. Las frases se leen de timeline.py (lista LINES).
Uso:  set FISH_API_KEY=tu_clave
      python scripts/voz.py
Salida: vo/l01.mp3 ... vo/l11.mp3 y vo/l01.wav ... vo/l11.wav (mono, 44,1 kHz). Nunca escribas la clave en este archivo.
"""
import json, os, re, subprocess, sys, time, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get('FISH_API_KEY')
if not KEY:
    sys.exit('Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave')
VOZ = os.environ.get('FISH_VOICE_ID', 'bd35c17b29c54d3e9d2663863a28d212')
src = open(os.path.join(AQUI, 'timeline.py'), encoding='utf-8').read()
LINES = [l.strip() for l in src.split('"""')[1].split('\n')]
SPEED = [0.95, 0.92, 0.92, 0.97, 1.05, 1.05, 1.05, 1.05, 1.05, 1.0, 1.05]  # triste y lento al inicio, rápido desde la idea
os.makedirs('vo', exist_ok=True)
for i, t in enumerate(LINES):
    mp3 = os.path.join('vo', f'l{i + 1:02d}.mp3'); wav = mp3[:-4] + '.wav'
    for intento in range(4):
        try:
            req = urllib.request.Request('https://api.fish.audio/v1/tts',
                data=json.dumps({'text': t, 'reference_id': VOZ, 'format': 'mp3', 'prosody': {'speed': SPEED[i]}}, ensure_ascii=False).encode(),
                headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's1'})
            open(mp3, 'wb').write(urllib.request.urlopen(req, timeout=120).read()); break
        except Exception as e:
            print(i + 1, 'reintento', e); time.sleep(3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', '44100', wav], check=True)
    print(f'{i + 1}/{len(LINES)}  {t}')
print('Listo. Si una frase suena cortada, vuelve a generarla (borra su .mp3 y corre de nuevo).')
