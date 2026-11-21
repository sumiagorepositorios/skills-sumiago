"""Quita los logos de la imagen de la mascota dormida (usada en las escenas de la cama).
Uso:  python scripts/limpiar_durmiendo.py "ruta/Mascota Sumiago durmiendo con ZZZ.png"
Salida: sleep_clean.png en la carpeta actual. Coordenadas ajustadas a esa imagen (unos 1194x1316).
"""
import sys
import cv2, numpy as np
from PIL import Image

if len(sys.argv) < 2:
    sys.exit('Uso: python scripts/limpiar_durmiendo.py "Mascota Sumiago durmiendo con ZZZ.png"')
im = np.array(Image.open(sys.argv[1]).convert('RGBA'))
rgb = im[:, :, :3].copy(); a = im[:, :, 3]

def limpiar(rgb, zonas):
    mask = np.zeros(a.shape, np.uint8)
    for x0, y0, x1, y1, modo in zonas:
        x0, y0, x1, y1 = [v * 2 for v in (x0, y0, x1, y1)]
        s = rgb[y0:y1, x0:x1].astype(int); r, g, b = s[..., 0], s[..., 1], s[..., 2]
        m = (np.minimum(np.minimum(r, g), b) < 170) if modo == 'nw' else ((r > 120) & (r - g > 60))
        m = m & (a[y0:y1, x0:x1] > 200); mask[y0:y1, x0:x1] |= (m * 255).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    return cv2.cvtColor(cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, 9, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)

rgb = limpiar(rgb, [(68, 182, 158, 262, 'nw'), (284, 362, 362, 422, 'nw'), (498, 388, 542, 418, 'red'), (498, 438, 538, 472, 'red')])
rgb = limpiar(rgb, [(295, 415, 330, 435, 'red'), (510, 425, 540, 448, 'red')])
Image.fromarray(np.dstack([rgb, a])).save('sleep_clean.png')
print('Listo: sleep_clean.png')
