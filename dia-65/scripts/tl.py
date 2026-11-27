"""Duración de cada escena según la voz -> dur.json y dur.js (los lee anim.html)."""
import json, subprocess
BASE = [3.6, 2.4, 3.6, 3.2, 2.8, 3.4, 2.8, 2.6, 2.6, 5.4, 2.8, 4.2, 3.2, 2.6, 6.2, 3.4]  # 16 escenas; la última (logo) sin voz
vd = [float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vt/{i:02d}.wav'])) for i in range(15)]
d = [round(max(b, vd[i] + 0.45), 2) if i < 15 else b for i, b in enumerate(BASE)]
json.dump(d, open('dur.json', 'w')); open('dur.js', 'w').write('window.DUR=' + json.dumps(d) + ';')
print(d, round(sum(d), 2))
