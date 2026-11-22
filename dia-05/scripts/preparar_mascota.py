"""Prepara la mascota del Día 5: es la imagen de frente con sus logos (este video sí lleva la marca Sumiago).
Solo borra la esquina de arriba a la izquierda (marca de agua de la imagen original).
Uso:  python scripts/preparar_mascota.py            (usa assets/mascota-frente.png)
      python scripts/preparar_mascota.py otra.png
Salida: mascot_clean.png en la carpeta actual.
"""
import os, sys
import numpy as np
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'mascota-frente.png')
im = np.array(Image.open(src).convert('RGBA')); im[:200, :300, 3] = 0
Image.fromarray(im).save('mascot_clean.png')
print('Listo: mascot_clean.png')
