"""Genera el diálogo con dos voces de Fish Audio: Sofi (W) y Sumiago (S).
Uso:  python scripts/voz.py        (necesita la variable FISH_API_KEY; nunca escribas la clave aquí)
Lee dialogo.txt ("W|frase" o "S|frase", una por línea).
Salida en la carpeta actual: voice.wav, durs.json (duración de cada frase) y speakers.json (quién dice cada frase).
"""
import json, os, subprocess, sys, time, urllib.request

KEY = os.environ.get('FISH_API_KEY')
if not KEY:
    sys.exit('Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave')
# S = voz oficial de la mascota Sumiago (1,5 semitonos más aguda); W = "Voz Femenina Español" de Fish (5 % más rápida)
V = {'S': (os.environ.get('FISH_VOICE_ID', 'bd35c17b29c54d3e9d2663863a28d212'), True),
     'W': (os.environ.get('FISH_VOICE_SOFI', 'bfed5c0810a347dbb62e8ccce7f59c48'), False)}
AQUI = os.path.dirname(os.path.abspath(__file__))
rows = [l.split('|', 1) for l in open(os.path.join(AQUI, '..', 'dialogo.txt'), encoding='utf-8').read().strip().split('\n') if l.strip()]
os.makedirs('vo', exist_ok=True)
durs = []
for i, (sp, l) in enumerate(rows):
    ref, mod = V[sp]
    for a in range(4):
        try:
            req = urllib.request.Request('https://api.fish.audio/v1/tts',
                data=json.dumps({'text': l, 'reference_id': ref, 'format': 'mp3', 'normalize': True}).encode(),
                headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's1'})
            open(f'vo/{i:02d}.mp3', 'wb').write(urllib.request.urlopen(req, timeout=120).read()); break
        except Exception as e:
            print(i, 'error', e); time.sleep(3)
    af = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,aresample=44100'
    af += ',asetrate=44100*1.0905,aresample=44100,atempo=0.954' if mod else ',atempo=1.05'
    af += ',apad=pad_dur=0.22'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'vo/{i:02d}.mp3', '-af', af, '-ac', '1', '-ar', '44100', f'vo/{i:02d}.wav'], check=True)
    durs.append(float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vo/{i:02d}.wav'])))
    print(f'{i + 1}/{len(rows)}  {sp}  {durs[-1]:.2f}s  {l[:50]}')
json.dump(durs, open('durs.json', 'w')); json.dump([r[0] for r in rows], open('speakers.json', 'w'))
open('lst.txt', 'w').write(''.join(f"file 'vo/{i:02d}.wav'\n" for i in range(len(durs))))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'lst.txt', '-c', 'copy', 'voice.wav'], check=True)
print(f'Listo: voice.wav ({sum(durs):.1f} s)')
