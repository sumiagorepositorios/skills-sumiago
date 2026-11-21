"""Quita los logos y textos de la mascota (gorra, pecho y zapatos) para que el video no lleve marcas.
Uso:  python scripts/limpiar_mascota.py "ruta/Personaje voxel Sumiago de frente.png"
Salida: mascot_clean.png en la carpeta actual.
Las coordenadas están ajustadas a esa imagen (1199x1312). Con otra imagen hay que ajustarlas.
"""
import sys
import cv2, numpy as np
from PIL import Image

if len(sys.argv) < 2:
    sys.exit('Uso: python scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"')
im = np.array(Image.open(sys.argv[1]).convert('RGBA'))
im[:200, :300, 3] = 0
rgb = im[:, :, :3].copy(); a = im[:, :, 3]
mask = np.zeros(a.shape, np.uint8)

def reg(x0, y0, x1, y1, mode):
    s = rgb[y0:y1, x0:x1].astype(int); r, g, b = s[..., 0], s[..., 1], s[..., 2]
    if mode == 'nonwhite': m = np.minimum(np.minimum(r, g), b) < 170
    elif mode == 'black': m = np.maximum(np.maximum(r, g), b) < 45
    else: m = (r > 120) & (r - g > 60)
    m = m & (a[y0:y1, x0:x1] > 200)
    mask[y0:y1, x0:x1] |= (m * 255).astype(np.uint8)

reg(480, 0, 720, 128, 'nonwhite'); reg(600, 110, 690, 132, 'red')                                  # gorra
reg(478, 524, 692, 688, 'nonwhite'); reg(500, 680, 690, 712, 'red'); reg(686, 610, 712, 680, 'black')  # pecho
reg(400, 1096, 520, 1170, 'red'); reg(660, 1096, 780, 1170, 'red')                                  # zapatos
mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
out = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, 9, cv2.INPAINT_TELEA)
out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
Image.fromarray(np.dstack([out, a])).save('mascot_clean.png')
print('Listo: mascot_clean.png')
