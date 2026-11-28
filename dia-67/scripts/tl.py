"""Cada escena dura su frase + 0,2 s (mínimo 55 % del tiempo de diseño) y su animación se acelera o frena para caber.
Escribe dur.json, k.json y dur.js (los lee anim.html)."""
import json, subprocess
BASE = [3.6, 2.6, 3.6, 3.6, 3.0, 3.0, 2.6, 3.4, 2.6, 3.6, 3.6, 2.6, 3.0, 3.0, 5.4, 3.4]  # la 16 (logo) va sin voz
vd = [float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vt/{i:02d}.wav'])) for i in range(15)]
d = [round(max(v + 0.2, BASE[i] * 0.55), 2) for i, v in enumerate(vd)] + [2.8]
k = [round(min(1.85, max(.75, BASE[i] / d[i])), 3) for i in range(15)] + [1]
json.dump(d, open('dur.json', 'w')); json.dump(k, open('k.json', 'w'))
open('dur.js', 'w').write('window.DUR=' + json.dumps(d) + ';window.K=' + json.dumps(k) + ';')
print(d, k, round(sum(d), 2))
