import json, subprocess, sys
lang, o, fixes = sys.argv[1], sys.argv[2], sys.argv[3:]
D = json.load(open(f'data-{lang}.json')); F = 25
starts = {}; acc = 0
for s in D: starts[s['id']] = (acc, round(s['L'] * F)); acc += round(s['L'] * F)
inp = []; fc = ''; parts = []; cur = 0; k = 0
for sid in sorted(fixes, key=lambda x: starts[x][0]):
    a, n = starts[sid]
    inp += ['-i', f'out/vid-{lang}-{o}.mp4']; j0 = len(inp) // 2 - 1
    fc += f'[{j0}:v]trim=start_frame={cur}:end_frame={a},setpts=PTS-STARTPTS[p{k}];'; parts.append(f'[p{k}]'); k += 1
    inp += ['-i', f'out/seg-{lang}-{o}-{sid}.mp4']; idx = len(inp) // 2 - 1
    fc += f'[{idx}:v]setpts=PTS-STARTPTS[p{k}];'; parts.append(f'[p{k}]'); k += 1
    cur = a + n
inp += ['-i', f'out/vid-{lang}-{o}.mp4']; j0 = len(inp) // 2 - 1
fc += f'[{j0}:v]trim=start_frame={cur},setpts=PTS-STARTPTS[p{k}];'; parts.append(f'[p{k}]')
fc += ''.join(parts) + f'concat=n={len(parts)}:v=1:a=0[v]'
nom = {'h': '16x9', 'v': '9x16'}[o]
cmd = ['ffmpeg', '-y', '-v', 'error'] + inp + ['-i', f'out/audio-{lang}.wav', '-filter_complex', fc, '-map', '[v]', '-map', f'{len(inp)//2}:a',
       '-c:v', 'libx264', '-preset', 'faster', '-crf', '25', '-pix_fmt', 'yuv420p', '-r', '25', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', f'out/final/presentacion-{lang}-{nom}.mp4']
subprocess.run(cmd, check=True); print('ok', acc, 'frames')
