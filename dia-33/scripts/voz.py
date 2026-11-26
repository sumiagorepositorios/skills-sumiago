import json, os, subprocess, sys, time, urllib.request
KEY = os.environ['FISH_API_KEY']
VOCES = {'N': 'bd35c17b29c54d3e9d2663863a28d212',   # narrador educativo sumiago
         'P': '22550e2d849b44e18c7df57f61e666f9',   # Patricia (susurro)
         'E': '9ea79fe31584435abe88b02e7aed4e6e'}   # esposa
TEMPO = {'N': 1.04, 'P': 1.0, 'E': 1.05}
MODEL = os.environ.get('FISH_MODEL', 's2.1-pro-free')
g = json.load(open('guion.json', encoding='utf-8'))
os.makedirs('voz', exist_ok=True); os.makedirs('vt', exist_ok=True)
only = [int(x) for x in sys.argv[1:]] or range(len(g))
for i in only:
    sp, t = g[i][0], g[i][1]
    for a in range(4):
        try:
            r = urllib.request.Request('https://api.fish.audio/v1/tts', json.dumps({'text': t, 'reference_id': VOCES[sp], 'format': 'wav'}).encode(),
                {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': MODEL})
            open(f'voz/{i:02d}.wav', 'wb').write(urllib.request.urlopen(r, timeout=120).read()); print(i, sp, 'ok', flush=True); break
        except Exception as e: print(i, 'error', e); time.sleep(3)
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'voz/{i:02d}.wav','-af',
        f'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={TEMPO[sp]},aresample=44100','-ac','1',f'vt/{i:02d}.wav'], check=True)
