import json, os, re, subprocess, glob
import numpy as np
from PIL import Image

REPO = '/home/claude/binantrader/sumiago/assets/tareas/presentacion-video'
L = json.load(open('/home/claude/pres/lineas.json'))
HTML = {'03': 'p-planes', '03b': 'p-regla', '03c': 'p-cambiate'}
PRE, POST = 0.5, 1.0

def dur(f):
    return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

def pauses(f):
    o = subprocess.run(['ffmpeg', '-i', f, '-af', 'silencedetect=noise=-32dB:d=0.16', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]

def gray(p, size=(480, 270)):
    return np.array(Image.open(p).convert('L').resize(size, Image.BILINEAR)).astype(int)

def bbox_diff(a, b):
    m = np.abs(gray(a) - gray(b)) > 28
    if m.sum() < 30: return None
    ys, xs = np.where(m)
    x0, x1 = np.percentile(xs, 1), np.percentile(xs, 99)
    y0, y1 = np.percentile(ys, 1), np.percentile(ys, 99)
    return [x0 / 480, y0 / 270, (x1 - x0) / 480, (y1 - y0) / 270]

def title_box(p):
    a = np.array(Image.open(p).convert('RGB').resize((960, 540))).astype(int)
    bg = np.median(a[20:60, 60:400].reshape(-1, 3), axis=0)
    ink = (np.abs(a - bg).sum(2) > 90)
    ink[:, :40] = False; ink[:, 760:] = False  # sin la franja roja ni el logo
    rows = np.where(ink[25:200].any(1))[0] + 25
    if not len(rows): return None
    grp = []; s = rows[0]; pr = rows[0]
    for r in rows[1:]:
        if r - pr > 18: break
        pr = r
    y0, y1 = s, pr
    cols = np.where(ink[y0:y1 + 1].any(0))[0]
    if y1 - y0 > 170 or not len(cols): return None
    bgcol = '#%02x%02x%02x' % tuple(int(v) for v in bg)
    return [(cols.min() - 6) / 960, (y0 - 6) / 540, (cols.max() - cols.min() + 12) / 960, (y1 - y0 + 12) / 540, bgcol]

def snap(targets, cands, mn):
    out = []; prev = -9
    for t in targets:
        ok = [c for c in cands if c > prev + mn and abs(c - t) < 2.2]
        v = min(ok, key=lambda c: abs(c - t)) if ok else max(t, prev + mn)
        out.append(round(v, 2)); prev = v
    return out

def sentences(text, D, cands):
    parts = [p.strip() for p in re.split(r'(?<=[.?!:])\s+', text) if p.strip()]
    res = []
    for p in parts:  # partir frases largas por comas
        if len(p) > 120:
            sub = re.split(r'(?<=,)\s+', p); cur = ''
            for s in sub:
                if len(cur) + len(s) > 95 and cur: res.append(cur); cur = s
                else: cur = (cur + ' ' + s).strip()
            if cur: res.append(cur)
        else: res.append(p)
    tot = sum(len(r) for r in res); acc = 0; out = []
    starts = []
    for r in res:
        starts.append(D * acc / tot); acc += len(r)
    st = [0.05] + snap(starts[1:], cands, .6) if len(starts) > 1 else [0.05]
    for i, r in enumerate(res):
        t0 = st[i]; t1 = st[i + 1] if i + 1 < len(res) else D
        words = r.split(); n = sum(len(w) + 1 for w in words); a2 = 0; ws = []
        for w in words:
            ws.append([w, round(t0 + (t1 - t0 - .25) * a2 / n, 2)]); a2 += len(w) + 1
        out.append({'t0': round(t0, 2), 't1': round(t1, 2), 'w': ws})
    return out

for lang in ['es', 'en']:
    segs = []
    for x in [l for l in L if l['lang'] == lang]:
        sid = x['id']; mp3 = f'/home/claude/pres/voz/{lang}-{sid}.mp3'
        D = dur(mp3); cands = pauses(mp3); Ls = round(PRE + D + POST, 2)
        seg = {'id': sid, 'D': round(D, 2), 'L': Ls, 'text': x['text'], 'sub': sentences(x['text'], D, cands), 'ev': []}
        if sid in HTML:
            seg['type'] = 'html'; seg['k'] = HTML[sid]
        else:
            seg['type'] = 'img'
            steps = glob.glob(f'{REPO}/{lang}/h/s-{sid}-b*.jpg')
            steps.sort(key=lambda p: int(re.search(r'-b(\d+)\.jpg', p).group(1)))
            imgs = steps + [f'{REPO}/{lang}/h/s-{sid}.jpg']
            seg['imgs'] = ['/sumiago/assets/tareas/presentacion-video/' + os.path.relpath(p, REPO) + '?v=%d' % int(os.path.getmtime(p)) for p in imgs]
            k = len(imgs) - 1
            tg = [D * (0.08 + 0.67 * (j + .5) / k) for j in range(k)] if k else []
            st = [round(v + PRE, 2) for v in snap(tg, [c - .05 for c in cands], .7)] if k else []
            seg['steps'] = st
            # cámara: sigue cada elemento nuevo y al final se aleja
            kf = [[0, 1, .5, .5]]
            last = [1, .5, .5]
            for j in range(k):
                bb = bbox_diff(imgs[j], imgs[j + 1])
                if not bb: continue
                bw, bh = bb[2], bb[3]
                z = max(1.0, min(1.32, 0.78 / max(bw, bh * 0.9, 0.05)))
                cx, cy = bb[0] + bw / 2, bb[1] + bh / 2
                hw, hh = .5 / z, .5 / z
                cx = min(max(cx, hw), 1 - hw); cy = min(max(cy, hh), 1 - hh)
                t = st[j]
                if t - kf[-1][0] < .3: t = kf[-1][0] + .3
                kf.append([round(t, 2)] + last)
                last = [round(z, 3), round(cx, 3), round(cy, 3)]
                kf.append([round(t + .9, 2)] + last)
            if len(kf) > 1:
                t_out = max(kf[-1][0] + 1.2, Ls - 2.4)
                kf.append([round(t_out, 2)] + last); kf.append([round(t_out + 1.1, 2), 1, .5, .5])
            else:
                kf = [[0, 1, .5, .5], [1.2, 1, .5, .5], [Ls, 1.07, .5, .48]]
            seg['cam'] = kf
            seg['title'] = title_box(imgs[0])
            seg['ev'] += [[0.02, 'whoosh'], [0.45, 'swish']] + [[t, 'pop'] for t in st]
        segs.append(seg)
    # transiciones: sin cierre en planes (se transforma la corona) y sin apertura en regla
    for s in segs:
        s['intro'] = s['id'] != '03b'
        s['outro'] = s['id'] != '03'
        if s['outro']: s['ev'].append([round(s['L'] - .95, 2), 'morph'])
        if s['type'] == 'html' and s['intro']: s['ev'].append([0.02, 'whoosh'])
    json.dump(segs, open(f'/home/claude/pres/data-{lang}.json', 'w'), ensure_ascii=False)
    print(lang, len(segs), 'segmentos', round(sum(s['L'] for s in segs) / 60, 2), 'min')
