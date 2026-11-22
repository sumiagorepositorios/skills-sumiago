"""Une las 6 escenas y les pone el audio (compresor + loudnorm), como se publicó.
Uso:  python scripts/montar.py out1080 dia-06.mp4
"""
import os, subprocess, sys
d = sys.argv[1] if len(sys.argv) > 1 else 'out1080'; salida = sys.argv[2] if len(sys.argv) > 2 else 'dia-06.mp4'
open(os.path.join(d, 'list.txt'), 'w').write(''.join(f"file '{n}.mp4'\n" for n in ('a_intro', 'b_reg', 'c_ver', 'd_panel', 'e_mk', 'f_outro')))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(d, 'list.txt'), '-c', 'copy', os.path.join(d, 'v.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, 'v.mp4'), '-i', os.path.join('out', 'audio.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'acompressor=threshold=-22dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9', '-ar', '44100',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', salida], check=True)
print('Listo:', salida)
