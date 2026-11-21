---
name: mar-salado
description: Crea el reel "¿Por qué el mar es salado?" (ríos, lluvia ácida, evaporación, chimeneas del fondo, 35 g por litro) con la mascota animada, voz de Fish Audio y subtítulos palabra por palabra, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del mar salado.
---

# Reel "¿Por qué el mar es salado?"

Video vertical 9:16 (1080x1920, 30 fps, unos 53 s) con paisajes dibujados (cielo celeste, montaña, río y mar) que explican de dónde sale la sal del mar. La mascota aparece en las esquinas y al final en la playa con flotador. También sale en 16:9 (1920x1080) para PC.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente Poppins Bold (si no está, usa Arial Bold).
- La imagen `Personaje voxel Sumiago de frente.png` (1199x1312, fondo transparente).
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 13 frases, una por línea (cada línea es una escena).
- `scripts/voz.py`: genera la voz con Fish Audio.
- `scripts/limpiar_mascota.py`: quita los logos de la mascota.
- `scripts/base.py`: parte común (subtítulos, boca sincronizada, parpadeo, tarjetas, brillos).
- `scripts/render.py`: dibuja todas las escenas de este video.

## Pasos

Trabaja en una carpeta vacía y ejecuta los scripts desde ahí.

1. **Voz:**
   ```
   set FISH_API_KEY=tu_clave
   python ruta/mar-salado/scripts/voz.py
   ```
   Usa la voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, un poco más rápida y sin silencios. Deja `voice.wav` y `durs.json`.
2. **Mascota sin marcas:**
   ```
   python ruta/mar-salado/scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"
   ```
3. **Revisión rápida:**
   ```
   python ruta/mar-salado/scripts/render.py test 2 5 9 13 16 19 23 30 36 42 46 51
   ```
   Revisa `test.jpg`.
4. **Render 9:16:**
   ```
   python ruta/mar-salado/scripts/render.py full
   ```
   Sale `mar-salado.mp4`.
5. **Versión 16:9 para PC:**
   ```
   ffmpeg -y -i mar-salado.mp4 -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart mar-salado-16x9.mp4
   ```
6. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

Cada escena empieza con un fundido rápido desde negro.

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | ¿Por qué el mar es salado y los ríos no? | Paisaje: montaña nevada, río que baja al mar, sol y nubes; etiquetas "agua dulce" y "agua salada"; mascota abajo a la izquierda; "¿POR QUÉ?" amarillo |
| 1 | La sal se la llevan los ríos | Mismo paisaje con granitos blancos de sal bajando por el río y acumulándose en el mar; cartel "sal al mar" |
| 2 | La lluvia es un poco ácida | Cielo gris con lluvia; una roca que se desmorona; tarjeta verde con una gota "un poco ácida" y luego tarjeta "agua con gas MUY FLOJA" con burbujas |
| 3 | Les arranca sales, poquitas | Sales saliendo de la roca hacia un río; tarjeta "SAL EN EL RÍO" con barra casi vacía y "casi nada"; mascota en la esquina |
| 4 | El sol evapora el agua | Sol grande sobre el mar; gotas azules que suben ("agua sube") y sal que se queda ("sal: se queda") |
| 5 | Como en una olla | Olla al fuego: el agua baja, aparece la "costra blanca" y sale vapor; mascota en la esquina |
| 6 | Cientos de millones de años | Mar profundo que se va llenando de sal, ríos que entran, contador que sube hasta "500 millones de años" |
| 7 | Chimeneas de agua ardiendo | Fondo marino oscuro con dos chimeneas que echan humo naranja y sal; cartel "agua ardiendo" |
| 8 | 35 gramos por litro | Jarra de "1 L", salero y báscula que sube a "35 g" (también en grande arriba) |
| 9 | Capa de 150 m, edificio de 40 plantas | Edificio de 40 pisos; una capa de "SAL" sube hasta su techo; medida "150 m" y cartel "edificio de 40 plantas" |
| 10 | El agua se va y la sal no | Mar con sol; salero tachado con una X roja y luego "el agua se va / la sal no" |
| 11 | Comenta VIRAL | Teléfono con el paisaje dentro y botón amarillo "COMENTA VIRAL" que late |
| 12 | Envíaselo a ese amigo | Mascota en el mar con flotador rojo, avión de papel y "ENVÍASELO A ESE AMIGO" |

## Estilo y reglas

- Paleta de día: cielo `#78B9F0` → `#D2EBFF`, mar `#1E6EBE`, arena `#E6CD96`, pasto `#5AAA5A`; tarjetas oscuras con borde de color.
- Amarillo `#FFD23F` para títulos y cifras, rojo `#E61E2D` para tachar y para "VIRAL".
- Subtítulos arriba (y = 230), de 4 en 4 palabras, la palabra que suena en amarillo.
- La mascota habla (boca según el volumen de la voz) y parpadea.
- Sin logos ni el texto "Sumiago" en la mascota, sin números de día y sin marcas de otros creadores. La llamada a la acción es "comenta VIRAL".
- Si cambias el guion, conserva 13 líneas en el mismo orden: cada escena depende de su número de línea.
