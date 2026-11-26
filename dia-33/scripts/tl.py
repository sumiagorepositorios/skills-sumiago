import json, subprocess, numpy as np, wave
g = json.load(open('guion.json', encoding='utf-8'))
# pausas: más largas antes del susurro, después del "No." y antes de la revelación de la esposa
gap = {0: .45, 1: .4, 2: .3, 3: .3, 4: .3, 5: .3, 6: .3, 7: .4, 8: .45, 9: .3, 10: .3, 11: .45, 12: .35, 13: .35, 14: .45, 15: .4}
t = 0.25; cl = []
for i, x in enumerate(g):
    d = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'vt/{i:02d}.wav']))
    cl.append({'i': i, 'sp': x[0], 't0': round(t, 3), 'd': round(d, 3), 'text': x[2]}); t += d + gap.get(i, .3)
total = round(t + 3.4, 2)
json.dump({'clips': cl, 'total': total}, open('tl.json', 'w'), ensure_ascii=False)
SR = 44100; v = np.zeros(int(total * SR) + SR, np.float32)
for c in cl:
    w = wave.open(f"vt/{c['i']:02d}.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    s = int(c['t0'] * SR); v[s:s + len(a)] += a
v = v[:int(total * SR)]
np.save('voice.npy', v)
n = int(total * 30); lv = [float(np.sqrt(np.mean(v[int(f/30*SR):int((f+1)/30*SR)]**2) + 1e-9)) for f in range(n)]
json.dump(lv, open('lv.json', 'w'))
print(total, [(c['i'], c['t0']) for c in cl])
