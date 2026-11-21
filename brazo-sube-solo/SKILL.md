---
name: brazo-sube-solo
description: Crea el reel "Tu brazo se mueve solo" (efecto Kohnstamm) con la mascota voxel animada, voz de Fish Audio y subtítulos palabra por palabra, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del brazo que sube solo.
---

# Reel "Tu brazo se mueve solo"

Video vertical 9:16 (1080x1920, 30 fps, unos 64 s) donde la mascota explica y hace el truco del brazo que sube solo después de empujar 30 segundos contra el marco de una puerta. También sale en 16:9 (1920x1080) para PC.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente Poppins Bold (si no está, usa Arial Bold).
- La imagen de la mascota de frente: `Personaje voxel Sumiago de frente.png` (1199x1312, fondo transparente).
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Pasos

Trabaja en una carpeta vacía (por ejemplo `trabajo/`) y ejecuta los scripts desde ahí.

1. **Voz.** Lee `guion.txt` (15 líneas, una por frase) y genera la voz con Fish Audio:
   ```
   set FISH_API_KEY=tu_clave
   python ruta/brazo-sube-solo/scripts/voz.py
   ```
   Usa la voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`), sube 1,5 semitonos, va un poco más rápida y quita silencios. Deja `voice.wav` y `durs.json`.

2. **Mascota sin marcas.** Borra logos y textos de la gorra, el pecho y los zapatos:
   ```
   python ruta/brazo-sube-solo/scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"
   ```
   Deja `mascot_clean.png`.

3. **Revisión rápida.** Saca cuadros de muestra antes del render completo:
   ```
   python ruta/brazo-sube-solo/scripts/render.py test 2 6 14 30 50 62
   ```
   Abre `test.jpg` y revisa que la mascota, la puerta y los textos no se tapen.

4. **Render 9:16.**
   ```
   python ruta/brazo-sube-solo/scripts/render.py full
   ```
   Sale `brazo-sube-solo.mp4`.

5. **Versión 16:9 para PC** (video centrado sobre su propio fondo desenfocado):
   ```
   ffmpeg -y -i brazo-sube-solo.mp4 -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart brazo-sube-solo-16x9.mp4
   ```

6. **Escúchalo completo** antes de publicarlo: revisa que la voz no se corte y que los subtítulos vayan a tiempo.

## Escenas (línea del guion → lo que se ve)

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | Gancho "Tu brazo se va a levantar solo" | Título "TU BRAZO SE / MUEVE SOLO"; la mascota sube y baja el brazo |
| 1 | Ponte en una puerta | Tarjeta "PASO 1 · Brazo pegado · dorso al marco" y flecha roja con borde blanco hacia la mano |
| 2 | Empuja treinta segundos | "¡EMPUJA!", flechas rojas de empuje y temporizador circular de 30 s |
| 3 | Algo que tú no pediste | "???" |
| 4 | Neurólogo alemán, 1915 | Tarjeta "1915 · Neurólogo alemán" y "¿POR QUÉ?" |
| 5 | A 1 de cada 3 no le pasa | Tres siluetas, la tercera tachada |
| 6 | Truco | "✕ No lo ayudes · ✕ No lo frenes · ✓ Solo míralo" |
| 7 | Últimos segundos | "¡AGUANTA!" parpadeando y gota de sudor; el temporizador se pone rojo en los últimos 5 s |
| 8 | Tres, dos, uno, ¡Ya! | Cuenta 3‑2‑1‑¡YA! grande; la mascota se aparta del marco; "BRAZO FLOJO" |
| 9 | ¿Lo notas? | El brazo sube solo con chispas en la mano; "¿LO NOTAS?" |
| 10 | El cerebro gritaba ¡arriba! | Cerebro brillante con señal al hombro y globo "¡ARRIBA!" |
| 11 | Eco del grito | Ondas del cerebro; "ECO DEL GRITO" |
| 12 | Es tuyo, puedes frenarlo | "ES TUYO" y cartel "STOP"; el brazo baja |
| 13 | ¿Te subió? Comenta VIRAL | Botones "SÍ / NO" y luego "COMENTA VIRAL" |
| 14 | Envíaselo a ese amigo | Avión de papel y "ENVÍASELO A ESE AMIGO" |

## Estilo y reglas

- Colores: amarillo `#FFD23F`, rojo `#E61E2D`, blanco; tarjetas oscuras con borde rojo.
- Fondo rojo oscuro con degradado radial y puntos suaves; puerta de madera dibujada desde cero.
- Subtítulos arriba, de 4 en 4 palabras, la palabra que suena en amarillo.
- La mascota habla (boca según el volumen de la voz), parpadea y respira.
- Sin logos ni el texto "Sumiago" en la mascota, sin números de día y sin marcas de otros creadores. La llamada a la acción es siempre "comenta VIRAL".
- Si cambias el guion, conserva 15 líneas en el mismo orden: las escenas dependen del número de línea.
