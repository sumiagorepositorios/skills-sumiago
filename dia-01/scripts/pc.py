"""Versión PC 16:9 (1920x1080): el video vertical centrado sobre su propio fondo difuminado, como se publicó.
Uso:  python scripts/pc.py dia-01.mp4 dia-01-pc.mp4
"""
import subprocess, sys
if len(sys.argv) < 3: sys.exit('Uso: python scripts/pc.py entrada.mp4 salida.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', sys.argv[1], '-filter_complex',
                '[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:5,eq=brightness=-0.05[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', sys.argv[2]], check=True)
print('Listo:', sys.argv[2])
