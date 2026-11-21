---
name: montana-fria
description: Crea el reel "¿Por qué arriba de una montaña hace frío si estás más cerca del sol?" (el sol calienta el suelo, el aire que sube se estira y se enfría, -6 °C por km) con la mascota animada, voz de Fish Audio y subtítulos palabra por palabra, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video de la montaña fría.
---

# Reel "¿Por qué arriba hace frío?"

Video vertical 9:16 (1080x1920, 30 fps, unos 59 s) con montañas nevadas dibujadas, de noche y de día. La mascota tiembla en la cima y explica por qué estar más cerca del sol no te calienta. También sale en 16:9 (1920x1080) para PC.

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
   python ruta/montana-fria/scripts/voz.py
   ```
   Usa la voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, un poco más rápida y sin silencios.
2. **Mascota sin marcas:**
   ```
   python ruta/montana-fria/scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"
   ```
3. **Revisión rápida:**
   ```
   python ruta/montana-fria/scripts/render.py test 2 6 11 15 19 23 28 32 36 40 45 51 57
   ```
4. **Render 9:16:**
   ```
   python ruta/montana-fria/scripts/render.py full
   ```
   Sale `montana-fria.mp4`.
5. **Versión 16:9 para PC:**
   ```
   ffmpeg -y -i montana-fria.mp4 -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart montana-fria-16x9.mp4
   ```
6. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

Cada escena empieza con un fundido rápido desde negro.

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | ¿Por qué arriba hace más frío? | Noche estrellada, sol, tres montañas nevadas; la mascota tiembla en la cima; termómetro "-33°C" y "¿POR QUÉ?" grande abajo |
| 1 | El Everest te acerca 9 km de 150 millones | Espacio: Tierra con el punto rojo "Everest", línea al sol y tarjeta "9 km de 150.000.000 km" |
| 2 | Una bombilla a 10 m… menos que un pelo | Pasillo con una bombilla al fondo y "10 m"; tarjeta con un pelo "0,07 mm" y "te acercas: 0,0006 mm" |
| 3 | La distancia no importa, el sol no calienta el aire | Montañas de día; "distancia" tachada en rojo; luego rayos del sol y "el sol casi no calienta el aire" |
| 4 | La luz atraviesa como una ventana y calienta el suelo | Cuarto con ventana; un haz de luz baja hasta el piso y aparece "suelo" caliente; mascota en la esquina |
| 5 | El suelo calienta el aire, como una olla | Suelo naranja con ondas de calor que suben; tarjeta "como una olla" con olla al fuego |
| 6 | El aire caliente sube y se estira | Bola de aire naranja que sube por la montaña y crece; "menos aire = se estira" |
| 7 | El aire que se estira se enfría (válvula) | Rueda con válvula soltando aire celeste; cartel "frío"; mascota en la esquina |
| 8 | -6 grados por kilómetro | Montaña con regla de 0 a 5 km y temperaturas que bajan; flecha roja que sube; "-6°C por km" |
| 9 | A la altura de un avión, -50 °C | Noche; avión que cruza a 9–12 km y termómetro "-50°C" |
| 10 | Lejos de lo que te calienta: el suelo | Montañas de día con la mascota en la cima; flecha "te calienta" hacia el suelo; "-20°C" |
| 11 | Comenta SUMIAGO | Teléfono con la montaña dentro y botón amarillo "COMENTA SUMIAGO" que late |
| 12 | Envíaselo a ese amigo | Mascota en la cima con carámbanos, avión de papel y "ENVÍASELO A ESE AMIGO" |

## Estilo y reglas

- Cielo de noche `#0E1E50` → `#285AAA` con estrellas; cielo de día `#468CDC` → `#B4DCFA`; montañas grises en facetas con nieve.
- Amarillo `#FFD23F` para títulos y cifras, celeste `#6EC8FF` para el frío, rojo `#E61E2D` para tachar y para "SUMIAGO".
- Subtítulos arriba (y = 230), de 4 en 4 palabras, la palabra que suena en amarillo.
- La mascota habla (boca según el volumen de la voz) y parpadea.
- Sin logos ni el texto "Sumiago" en la mascota y sin números de día. En este video la llamada a la acción es "comenta SUMIAGO".
- Si cambias el guion, conserva 13 líneas en el mismo orden: cada escena depende de su número de línea.
