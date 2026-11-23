"""Prepara los dos personajes del Día 1.
- mascot_clean.png: la mascota Sumiago de frente (con sus logos), sin la marca de agua de la esquina.
- pesimista.png: el personaje "pesimista" (camiseta azul) con cejas caídas, boca triste y colores apagados.
Uso:  python scripts/preparar_personajes.py      -> deja los dos PNG en la carpeta actual
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

im = np.array(Image.open(os.path.join(A, 'mascota-frente.png')).convert('RGBA')); im[:200, :300, 3] = 0
Image.fromarray(im).save('mascot_clean.png')

p = Image.open(os.path.join(A, 'pesimista-base.png')).convert('RGBA')
d = ImageDraw.Draw(p)
piel = p.getpixel((600, 380))[:3]
# borra cejas, mejillas y sonrisa con el color de la piel
for caja in ((450, 262, 550, 288), (650, 262, 750, 288), (435, 372, 500, 402), (700, 372, 754, 402), (530, 400, 670, 442)):
    d.rectangle(caja, fill=piel + (255,))
# cejas caídas hacia el centro (cara de enojo/tristeza) y boca triste
d.polygon([(455, 266), (548, 282), (548, 292), (455, 278)], fill=(30, 20, 16, 255))
d.polygon([(745, 266), (652, 282), (652, 292), (745, 278)], fill=(30, 20, 16, 255))
d.arc((548, 412, 652, 470), 200, 340, fill=(95, 35, 30, 255), width=9)
# colores apagados (gris), como en el video original
rgb = ImageEnhance.Color(p.convert('RGB')).enhance(0.45)
rgb = ImageEnhance.Brightness(rgb).enhance(0.92)
out = rgb.convert('RGBA'); out.putalpha(p.getchannel('A'))
out.save('pesimista.png')
print('Listo: mascot_clean.png y pesimista.png')
