import json, wave, numpy as np
TL = json.load(open('tl.json')); SR = 44100
PUN = ',:.…?»'
for c in TL['clips']:
    w = wave.open(f"vt/{c['i']:02d}.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = int(.01 * SR); rms = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2)) for k in range(0, len(a) - hop, hop)])
    sil = rms < max(rms) * .08
    runs = []; k = 0
    while k < len(sil):
        if sil[k]:
            j = k
            while j < len(sil) and sil[j]: j += 1
            if j - k >= 8 and k > 5 and j < len(sil) - 3: runs.append((k * .01, j * .01))
            k = j
        else: k += 1
    ws = c['text'].split()
    brk = [i for i, x in enumerate(ws[:-1]) if x[-1] in PUN]
    runs = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:len(brk)])
    if len(runs) < len(brk):  # quedarse con las pausas de puntuación más fuertes
        pri = sorted(brk, key=lambda i: (ws[i][-1] not in '.:?…»', i))[:len(runs)]; brk = sorted(pri)
    # segmentos de habla
    segs = []; s0 = 0.0; b0 = 0
    for bi, r in zip(brk, runs):
        segs.append((b0, bi + 1, s0, r[0])); b0 = bi + 1; s0 = r[1]
    segs.append((b0, len(ws), s0, c['d']))
    out = []
    for a0, a1, t0, t1 in segs:
        part = ws[a0:a1]; tot = sum(len(x) + 2 for x in part); t = t0
        for x in part: out.append([x, round(c['t0'] + t, 3)]); t += (len(x) + 2) / tot * (t1 - t0)
    c['words'] = out; print(c['i'], len(brk), [(r[0], r[1]) for r in runs])
json.dump(TL, open('tl.json', 'w'), ensure_ascii=False)
