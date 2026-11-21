---
name: por-que-sonamos
description: Crea el reel "¿Por qué soñamos?" (fase REM, terapia de noche y pesadillas como simulacro) con la mascota animada, voz de Fish Audio y subtítulos palabra por palabra, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video de por qué soñamos.
---

# Reel "¿Por qué soñamos?"

Video vertical 9:16 (1080x1920, 30 fps, unos 52 s) de noche, en tonos azul y morado. La mascota duerme en su cama, explica la fase REM y termina contando que las pesadillas son un simulacro. También sale en 16:9 (1920x1080) para PC.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente Poppins Bold (si no está, usa Arial Bold).
- Dos imágenes de la mascota (fondo transparente):
  - `Personaje voxel Sumiago de frente.png` (1199x1312): la mascota de pie, hablando.
  - `Mascota Sumiago durmiendo con ZZZ.png`: la mascota dormida para las escenas de la cama.
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Pasos

Trabaja en una carpeta vacía y ejecuta los scripts desde ahí.

1. **Voz.** Genera la voz de las 14 líneas de `guion.txt`:
   ```
   set FISH_API_KEY=tu_clave
   python ruta/por-que-sonamos/scripts/voz.py
   ```
   Usa la voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, un poco más rápida y sin silencios. Deja `voice.wav` y `durs.json`.

2. **Mascota sin marcas.**
   ```
   python ruta/por-que-sonamos/scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"
   python ruta/por-que-sonamos/scripts/limpiar_durmiendo.py "Mascota Sumiago durmiendo con ZZZ.png"
   ```
   Dejan `mascot_clean.png` y `sleep_clean.png`.

3. **Revisión rápida.**
   ```
   python ruta/por-que-sonamos/scripts/render.py test 1 3.5 9 13 17 36 46
   ```
   Abre `test.jpg` y revisa la cama, el cerebro y los textos.

4. **Render 9:16.**
   ```
   python ruta/por-que-sonamos/scripts/render.py full
   ```
   Sale `por-que-sonamos.mp4`.

5. **Versión 16:9 para PC** (el video centrado sobre su propio fondo desenfocado):
   ```
   ffmpeg -y -i por-que-sonamos.mp4 -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart por-que-sonamos-16x9.mp4
   ```

6. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

Cada línea es una escena. Al empezar cada escena hay un fundido rápido desde negro.

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | ¿Por qué soñamos... y las pesadillas? | Cuarto de noche: ventana con luna arriba a la izquierda, lámpara a la derecha y la mascota dormida en la cama azul. Una burbuja de sueño con estrellas y "SUEÑOS" se vuelve oscura con un rayo y "¿?" rojo |
| 1 | Tu cerebro está ensayando | Mascota de pie hablando, con un cerebro encima; el cartel "¿DESCANSA?" cambia a "ENSAYANDO" en rojo |
| 2 | Cada 90 minutos, fase REM | Gráfica de ciclos de sueño que se dibuja con 4 picos "REM" que brillan, marca "90 min" y estrellas; mascota pequeña abajo |
| 3 | Apaga casi todos tus músculos | Cuarto con la mascota dormida; tarjeta "MÚSCULOS" con interruptor que pasa de "ENCENDIDOS" (verde) a "APAGADOS" (rojo) |
| 4 | Emociones se encienden, la lógica se calma | Cerebro grande: brillo rojo de emociones y azul de lógica, con barras "EMOCIONES" que sube y "LÓGICA" que baja; mascota pequeña abajo a la derecha |
| 5 | Volar o hablar con alguien que ya no está | Cielo estrellado con luna y edificios; la mascota cruza volando acostada; aparece un fantasma amigable que dice "¡Hola!" y luego "¡NORMAL!" |
| 6 | Terapia de noche | Tarjeta "SOÑAR = TERAPIA DE NOCHE" con corazón rojo que late; mascota abajo |
| 7 | Baja la sustancia del estrés | Medidor semicircular verde‑amarillo‑rojo con aguja que baja a "ESTRÉS" bajo; tarjeta con un recuerdo que pasa de lluvia a colores claros y "lo que te dolió" |
| 8 | Comenta VIRAL | Teléfono con el cuarto dentro y botón amarillo "COMENTA VIRAL" que late |
| 9 | ¿Y las pesadillas? | Cuarto oscuro rojizo, nube negra y destellos; "PESADILLAS" en rojo |
| 10 | Simulacro: ensayas escapar | Pasillo oscuro con puerta de salida iluminada; la mascota corre mientras la persigue una sombra de ojos rojos; cartel "SIMULACRO" |
| 11 | Aparecen con estrés | Mascota corriendo en su sitio, contador "ensayo 1…5" y medidor de "ESTRÉS" que se llena |
| 12 | Tu cerebro practicando | Mascota dormida con un cerebro grande brillando y "PRACTICANDO" abajo |
| 13 | Envíaselo a ese amigo | Mascota de pie, avión de papel y "ENVÍASELO A ESE AMIGO" |

## Estilo y reglas

- Fondos con degradado radial: noche azul (`#28225A` → `#080814`), oscuro rojizo para pesadillas y cielo con estrellas.
- Colores: amarillo `#FFD23F`, rojo `#E61E2D`, rosa `#FF78AA`, celeste `#6EC8FF`; tarjetas oscuras con borde de color.
- Subtítulos arriba (y = 230), de 4 en 4 palabras, la palabra que suena en amarillo.
- La mascota habla (boca según el volumen de la voz) y parpadea; en la cama aparece la imagen de la mascota dormida.
- Sin logos ni el texto "Sumiago" en la mascota, sin números de día y sin marcas de otros creadores. La llamada a la acción es "comenta VIRAL".
- Si cambias el guion, conserva 14 líneas en el mismo orden: cada escena depende de su número de línea.
