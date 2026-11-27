"""Cada escena dura lo que dura su frase + 0,2 s (sin silencios) y su animación se acelera o frena para caber.
Escribe dur.json, k.json y dur.js (los lee anim.html)."""
import json, subprocess
BASE = [3.6, 2.6, 2.4, 2.2, 3.0, 3.0, 3.6, 3.4, 3.0, 3.4, 3.0, 3.8, 3.4, 3.0, 5.4, 3.4]  # tiempo de diseño de cada animación; la 16 (logo) va sin voz
vd = [float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vt/{i:02d}.wav'])) for i in range(15)]
d = [round(v + 0.2, 2) for v in vd] + [2.8]
k = [round(min(1.5, max(.75, BASE[i] / d[i])), 3) for i in range(15)] + [1]
json.dump(d, open('dur.json', 'w')); json.dump(k, open('k.json', 'w'))
open('dur.js', 'w').write('window.DUR=' + json.dumps(d) + ';window.K=' + json.dumps(k) + ';')
print(d, k, round(sum(d), 2))
