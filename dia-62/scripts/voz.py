import json, os, subprocess, sys, time, urllib.request
KEY = os.environ['FISH_API_KEY']; VOZ = 'bd35c17b29c54d3e9d2663863a28d212'   # narrador educativo sumiago
MODEL = os.environ.get('FISH_MODEL', 's2.1-pro-free')
g = json.load(open('guion.json', encoding='utf-8'))
os.makedirs('voz', exist_ok=True); os.makedirs('vt', exist_ok=True)
only = [int(x) for x in sys.argv[1:]] or range(len(g))
for i in only:
    t = g[i][0]
    for a in range(4):
        try:
            r = urllib.request.Request('https://api.fish.audio/v1/tts', json.dumps({'text': t, 'reference_id': VOZ, 'format': 'wav'}).encode(),
                {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': MODEL})
            open(f'voz/{i:02d}.wav', 'wb').write(urllib.request.urlopen(r, timeout=120).read()); print(i, 'ok', flush=True); break
        except Exception as e: print(i, 'error', e); time.sleep(3)
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'voz/{i:02d}.wav','-af',
        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.04,aresample=44100','-ac','1',f'vt/{i:02d}.wav'], check=True)
