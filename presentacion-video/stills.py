import json, subprocess, sys
REPO='/home/claude/binantrader/sumiago/assets/tareas/presentacion-video'
lang=sys.argv[1]
D=json.load(open(f'data-{lang}.json')); off={}; acc=0
for s in D: off[s['id']]=(acc,s['L']); acc+=s['L']
for o,fmt in [('h','16x9'),('v','9x16')]:
    src=f'out/final/presentacion-{lang}-{fmt}.mp4'
    for sid in ['03','03b','03c']:
        a,L=off[sid]; t=a+L-(1.6 if sid!='03' else 2.5)
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{t:.2f}','-i',src,'-frames:v','1','-q:v','3',f'{REPO}/{lang}/{o}/s-{sid}.jpg'],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-ss','3','-i',src,'-frames:v','1','-q:v','3',f'out/final/presentacion-{lang}-{fmt}.jpg'],check=True)
print('ok',lang)
