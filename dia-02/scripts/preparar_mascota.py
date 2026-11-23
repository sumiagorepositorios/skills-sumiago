"""Prepara la mascota del Día 2: la imagen de frente con sus logos, sin la marca de agua de la esquina de arriba a la izquierda.
Uso:  python scripts/preparar_mascota.py      -> mascot_clean.png en la carpeta actual
"""
import os
import numpy as np
from PIL import Image

im = np.array(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'mascota-frente.png')).convert('RGBA'))
im[:200, :300, 3] = 0
Image.fromarray(im).save('mascot_clean.png')
print('Listo: mascot_clean.png')
