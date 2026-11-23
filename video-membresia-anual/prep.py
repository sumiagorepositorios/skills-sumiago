import json, re, subprocess, sys
sys.path.insert(0, '/home/claude/pres')
src = open('/home/claude/pres/prep.py').read().split("for lang in ['es', 'en']:")[0]
exec(src)
L = json.load(open('/home/claude/anual/lineas.json'))
for lang in ['es', 'en']:
    segs = []
    for x in [l for l in L if l['lang'] == lang]:
        mp3 = f"/home/claude/anual/voz/{lang}-{x['id']}.mp3"; D = dur(mp3)
        s = {'id': x['id'], 'type': 'html', 'k': 'a-' + x['id'], 'D': round(D, 2), 'L': round(PRE + D + POST, 2), 'text': x['text'], 'sub': sentences(x['text'], D, pauses(mp3)), 'intro': True, 'outro': True}
        s['outro'] = x['id'] != 'cierre'
        s['ev'] = [[0.02, 'whoosh']] + ([[round(s['L'] - .95, 2), 'morph']] if s['outro'] else [])
        segs.append(s)
    json.dump(segs, open(f'/home/claude/anual/data-{lang}.json', 'w'), ensure_ascii=False)
    print(lang, round(sum(s['L'] for s in segs), 1), 's')
