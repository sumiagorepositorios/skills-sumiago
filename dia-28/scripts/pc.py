"""Versión PC (1920x1080): panel oscuro con el mensaje a la izquierda y el reel vertical con esquinas redondeadas a la derecha.
Uso:  python scripts/pc.py video.mp4 video-pc.mp4   (textos en guion.json -> "pc")
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__)); ARGS = sys.argv[1:]
FONT_DIRS = ['/usr/share/fonts/opentype/inter/', os.path.join(AQUI, '..', 'fonts') + os.sep,
             os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts') + os.sep, 'C:\\Windows\\Fonts\\']
def F(n, s):
    for dd in FONT_DIRS:
        if os.path.isfile(dd + n): return ImageFont.truetype(dd + n, s)
    sys.exit(f'No encontré la fuente {n}. Instala Inter.')

import json
_G = json.load(open('guion.json', encoding='utf-8')).get('pc', {})
TITULO = _G.get('titulo', ['SUMIAGO'])
PUNTOS = _G.get('puntos', [])[:4]
PIE = _G.get('pie', 'Regístrate en el link de mi perfil')
ANCHO_CAJA = 920; TAM = 30

W, H = 1920, 1080; RED = (230, 38, 47)
bg = Image.new('RGB', (W, H), (10, 10, 12))
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((-400, -600, 1300, 500), fill=120); g = g.filter(ImageFilter.GaussianBlur(220))
bg = Image.composite(Image.new('RGB', (W, H), (90, 14, 20)), bg, g); d = ImageDraw.Draw(bg)
d.text((120, 130), 'SUMIAGO', font=F('Inter-Black.otf', 40), fill=(220, 220, 225), anchor='lm'); d.rectangle((120, 160, 300, 165), fill=RED)
for k, s in enumerate(TITULO):
    d.text((120, 320 + k * 90), s, font=F('Inter-Black.otf', 76), fill=RED if k == len(TITULO) - 1 else (245, 245, 247), anchor='lm')
for i, c in enumerate(PUNTOS):
    y = 600 + i * 82
    d.rounded_rectangle((120, y, ANCHO_CAJA, y + 66), 14, fill=(30, 30, 36), outline=(44, 44, 52), width=2)
    d.text((150, y + 33), f'0{i + 1}', font=F('Inter-Bold.otf', 26), fill=(120, 120, 130), anchor='lm')
    d.text((220, y + 33), c, font=F('Inter-Bold.otf', TAM), fill='white', anchor='lm')
d.text((120, 1010), PIE, font=F('Inter-SemiBold.otf', 30), fill=(150, 150, 160), anchor='lm')
d.rounded_rectangle((1196, 26, 1196 + 580 + 8, 26 + 1028), 28, fill=(20, 20, 24), outline=(44, 44, 52), width=3)
bg.save('pc_bg.png')

esquinas = "a='if(lt(min(min(X,W-1-X),min(Y,H-1-Y)),24)*lt(hypot(24-min(X,W-1-X),24-min(Y,H-1-Y)),24)+gte(min(min(X,W-1-X),min(Y,H-1-Y)),24)+if(lt(min(X,W-1-X),24),if(lt(min(Y,H-1-Y),24),0,1),if(lt(min(Y,H-1-Y),24),1,0)),255,0)'"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', ARGS[0], '-loop', '1', '-framerate', '30', '-i', 'pc_bg.png', '-filter_complex',
                f"[0:v]scale=576:1024,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':{esquinas}[v];[1:v][v]overlay=1200:30:shortest=1,format=yuv420p[o]",
                '-map', '[o]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30', '-c:a', 'copy', '-movflags', '+faststart', ARGS[1]], check=True)
print('Listo:', ARGS[1])
