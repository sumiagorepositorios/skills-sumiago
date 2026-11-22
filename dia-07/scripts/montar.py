"""Une las 8 partes, les pone el audio (compresor + loudnorm) y arma la versión PC, como se publicó.
Uso:  python scripts/montar.py        -> dia-07.mp4 (1080x1920) y dia-07-pc.mp4 (1920x1080)
"""
import glob, os, subprocess
partes = sorted(glob.glob(os.path.join('out', 'p0*.mp4')))
open(os.path.join('out', 'list.txt'), 'w').write(''.join(f"file '{os.path.basename(p)}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join('out', 'list.txt'), '-c', 'copy', os.path.join('out', 'v.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join('out', 'v.mp4'), '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-pix_fmt', 'yuv420p', '-af', 'acompressor=threshold=-22dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9', '-ar', '44100',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', 'dia-07.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', 'pcbg.png', '-i', 'dia-07.mp4', '-i', 'pcmask.png', '-filter_complex',
                '[1:v]scale=562:1000:flags=lanczos,format=rgba[v];[2:v]format=gray[m];[v][m]alphamerge[vm];[0:v][vm]overlay=1262:40:shortest=1,format=yuv420p[o]',
                '-map', '[o]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-r', '30', '-c:a', 'copy', '-movflags', '+faststart', 'dia-07-pc.mp4'], check=True)
print('Listo: dia-07.mp4 y dia-07-pc.mp4')
