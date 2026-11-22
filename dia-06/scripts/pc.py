"""Versión PC 16:9 (1920x1080) del Día 6: a la izquierda logo, "TUTORIAL PASO A PASO", el título, sumiago.com y la mascota;
a la derecha el video vertical con esquinas redondeadas y sombra.
Uso:  python scripts/pc.py dia-06.mp4 dia-06-pc.mp4
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import render as r
if len(sys.argv) < 3: sys.exit('Uso: python scripts/pc.py dia-06.mp4 dia-06-pc.mp4')
W, H = 1920, 1080
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
img = np.zeros((H, W, 3), np.float32) + np.array(r.BG, np.float32)
grid = ((xx % 48 < 1) | (yy % 48 < 1)).astype(np.float32)
img -= grid[..., None] * np.array([12, 12, 12], np.float32)
d = np.sqrt(((xx - W * 0.3) / (W * 0.45)) ** 2 + ((yy - H * 0.4) / (H * 0.6)) ** 2)
img -= (np.clip(1 - d, 0, 1) ** 2)[..., None] * np.array([0, 26, 26], np.float32)
bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
VX, VY, VW, VH = 1230, 40, 562, 1000
sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([VX, VY + 14, VX + VW, VY + VH + 14], radius=36, fill=70)
sh = sh.filter(ImageFilter.GaussianBlur(22))
bg = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), bg, sh.point(lambda v: v // 2))
def F(sz, w): f = ImageFont.truetype(r.FD, sz); f.set_variation_by_axes([min(sz, 40), w]); return f
dr = ImageDraw.Draw(bg, 'RGBA')
logo = Image.open(r.AS + 'img/logo-sumiago.png').convert('RGBA'); logo = logo.crop(logo.getbbox()); logo = logo.resize((460, int(logo.height * 460 / logo.width)), Image.LANCZOS)
bg.paste(logo, (130, 110), logo)
pill = 'TUTORIAL PASO A PASO'; fp = F(24, 800); pw = dr.textlength(pill, font=fp) + 56
dr.rounded_rectangle([130, 300, 130 + pw, 352], radius=26, fill=r.RED); dr.text((130 + pw / 2, 326), pill, font=fp, fill='white', anchor='mm')
ft = F(72, 800)
for i, (t, c) in enumerate([('Cómo registrarte', r.INK), ('y publicar en el', r.INK), ('Marketplace', r.RED)]): dr.text((130, 400 + i * 88), t, font=ft, fill=c)
fs = F(30, 400)
for i, t in enumerate(['Crea tu cuenta gratis y publica tu', 'primer artículo en minutos.']): dr.text((130, 690 + i * 44), t, font=fs, fill=r.GRAY)
dr.rounded_rectangle([130, 820, 130 + 330, 884], radius=32, fill='white', outline=r.RED, width=2)
dr.text((295, 852), 'sumiago.com', font=F(30, 700), fill=r.INK, anchor='mm')
m = Image.open(r.AS + 'videos-virales/mascota-pulgar.png').convert('RGBA'); m = m.crop(m.getbbox()); m = m.resize((int(m.width * 600 / m.height), 600), Image.LANCZOS)
bg.paste(m, (1180 - m.width - 20, H - 600 - 20), m)
bg.convert('RGB').save('pc_bg.png')
mk = Image.new('L', (VW, VH), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, VW - 1, VH - 1], radius=36, fill=255); mk.save('pc_mask.png')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-loop', '1', '-t', '64', '-i', 'pc_bg.png', '-i', sys.argv[1], '-framerate', '30', '-loop', '1', '-t', '64', '-i', 'pc_mask.png',
                '-filter_complex', '[1:v]scale=562:1000:flags=lanczos,format=rgba[v];[2:v]format=gray[m];[v][m]alphamerge[vm];[0:v][vm]overlay=1230:40:shortest=1:format=auto,format=yuv420p[o]',
                '-map', '[o]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'copy', '-t', '64', '-movflags', '+faststart', sys.argv[2]], check=True)
print('Listo:', sys.argv[2])
