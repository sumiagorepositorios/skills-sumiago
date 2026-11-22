"""Crea a Sofi (la mujer del video) a partir de la mascota sin logos: ropa turquesa, pelo largo de bloques, flequillo, pestañas, rubor y aretes.
Uso (en la carpeta donde está mascot_clean.png):  python scripts/crear_sofi.py
Salida: sofi.png
"""
import numpy as np
from PIL import Image, ImageDraw

im = Image.open('mascot_clean.png').convert('RGBA'); A = np.array(im).astype(int)
r, g, b, a = A[..., 0], A[..., 1], A[..., 2], A[..., 3]
red = (r > 110) & (r - g > 100) & (g < 100) & (b < 110) & (a > 0)
mouth = np.zeros_like(red); mouth[325:400, 535:665] = True
m = red & ~mouth; L = r[m]
A[..., 0][m] = (L * 0.14).astype(int); A[..., 1][m] = (L * 0.72).astype(int); A[..., 2][m] = (L * 0.76).astype(int)
out = Image.fromarray(A.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(out)
HAIR = (96, 55, 30); HAIR2 = (84, 47, 25); HAIR3 = (125, 74, 40)
for side, (x0, x1) in enumerate(((400, 463), (738, 802))):
    for y in range(215, 600, 32):
        w = (x1 - x0) - (0 if y < 510 else (y - 510) // 2)
        xa, xb = (x1 - w, x1) if side == 0 else (x0, x0 + w)
        d.rectangle([xa, y, xb, y + 31], fill=HAIR if (y // 32) % 3 else HAIR2)
        d.rectangle([xa if side == 0 else xb - 8, y, (xa + 8) if side == 0 else xb, y + 31], fill=HAIR3)
for box in ((492, 248, 512, 262), (693, 248, 713, 262), (498, 240, 515, 250), (690, 240, 707, 250)): d.rectangle(box, fill=(30, 20, 20))
for box in ((496, 326, 540, 342), (664, 326, 708, 342)): d.rectangle(box, fill=(240, 145, 145))
for x in (455, 745): d.rectangle([x - 9, 385, x + 9, 403], fill=(240, 200, 60))
# flequillo: las manchas rojas de la frente pasan a color pelo
src = A0 = np.array(im).astype(int)
out = np.array(out).astype(int)
r, g, b, a = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
red = (r > 110) & (r - g > 100) & (g < 100) & (b < 110) & (a > 0)
box = np.zeros_like(red); box[190:330, 455:750] = True
m = red & box; L = r[m] / 255
out[..., 0][m] = (96 * L * 1.3).astype(int); out[..., 1][m] = (55 * L * 1.3).astype(int); out[..., 2][m] = (30 * L * 1.3).astype(int)
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save('sofi.png')
print('Listo: sofi.png')
