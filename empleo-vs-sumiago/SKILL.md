---
name: empleo-vs-sumiago
description: Crea el reel promocional "Empleo vs Sumiago, MIRA!" (empleo con techo frente a un segundo ingreso semiautomático con Sumiago) con fondo blanco, la mascota animada, voz de Fish Audio, música propia y efectos de sonido, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video Empleo vs Sumiago.
---

# Reel "Empleo vs Sumiago, MIRA!"

Video vertical 9:16 (1080x1920, 30 fps, unos 51 s) con **fondo blanco**, que compara los ingresos de un empleo con armar Sumiago en los ratos libres sin dejar el empleo. Tiene música hecha por código (sin derechos de autor) que baja cuando habla la voz, y efectos de sonido en cada escena. También sale en 16:9 (1920x1080) para PC.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente Poppins Bold (si no está, usa Arial Bold).
- La imagen `Personaje voxel Sumiago de frente.png` (1199x1312, fondo transparente).
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 11 frases, una por línea (cada línea es una escena).
- `scripts/voz.py`: genera la voz con Fish Audio.
- `scripts/limpiar_mascota.py`: quita los logos de la mascota.
- `scripts/audio.py`: mezcla voz + música + efectos en `mix.wav`.
- `scripts/base.py`: parte común (tiempos, boca sincronizada, parpadeo, tarjetas, brillos).
- `scripts/render.py`: dibuja todas las escenas de este video.

## Pasos

Trabaja en una carpeta vacía y ejecuta los scripts desde ahí.

1. **Voz:**
   ```
   set FISH_API_KEY=tu_clave
   python ruta/empleo-vs-sumiago/scripts/voz.py
   ```
   Usa la voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, un poco más rápida y sin silencios.
2. **Mascota sin marcas:**
   ```
   python ruta/empleo-vs-sumiago/scripts/limpiar_mascota.py "Personaje voxel Sumiago de frente.png"
   ```
3. **Música y efectos:**
   ```
   python ruta/empleo-vs-sumiago/scripts/audio.py
   ```
   Deja `mix.wav`.
4. **Revisión rápida:**
   ```
   python ruta/empleo-vs-sumiago/scripts/render.py test 2 5 9 20 24 30 35 41 45.5 48
   ```
5. **Render 9:16:**
   ```
   python ruta/empleo-vs-sumiago/scripts/render.py full
   ```
   Sale `empleo-vs-sumiago.mp4`.
6. **Versión 16:9 para PC:**
   ```
   ffmpeg -y -i empleo-vs-sumiago.mp4 -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:5,eq=brightness=-0.05[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0" -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -c:a copy -movflags +faststart empleo-vs-sumiago-16x9.mp4
   ```
7. **Escúchalo completo** antes de publicarlo: voz, música y efectos juntos.

## Escenas (línea del guion → lo que se ve → sonido)

Cada escena empieza con un fundido rápido desde **blanco** y un "whoosh".

| # | Frase | En pantalla | Sonido |
|---|-------|-------------|--------|
| 0 | ¿Tu sueldo depende de las horas? | Pantalla partida: "EMPLEO" gris con reloj / "SUMIAGO" rojo con teléfono, círculo "VS"; mascota abajo | pop + ding |
| 1 | Tiempo por dinero, si no vas no cobras | Reloj grande con monedas cayendo y "TIEMPO = DINERO"; luego "SI NO VAS, NO COBRAS" y el reloj tachado | tic-tac, monedas, zumbido de error |
| 2 | Tu ingreso tiene un techo | Gráfica de barras grises iguales mes a mes (E, F, M…) bajo una línea roja "TECHO"; "MISMO SUELDO" | pop en cada barra |
| 3 | No dejas tu empleo, ratos libres | Mascota; tarjetas "EMPLEO lo mantienes" y "+ SUMIAGO ratos libres"; "SEGUNDO INGRESO" | pops + ding |
| 4 | La IA crea tus videos, tú publicas | Teléfono con videos que se activan, cuadro "IA" que brilla, etiquetas TikTok / Reels / Shorts; "TÚ SOLO PUBLICAS" | pops |
| 5 | Tus videos trabajan mientras duermes | Pantalla partida día (edificio, "en tu empleo") / noche (luna, "mientras duermes"); "+1" subiendo y contador "+9.920 vistas" | pops de likes |
| 6 | Gana con Marketing, tareas diarias | Tarjeta "GANA CON MARKETING" con 4 tareas que se marcan en verde; "pocos minutos al día" | ding por tarea |
| 7 | Subes de rango, Sueldo Mensual desde Oro | Escalera de rangos Bronce → Plata → Oro → Platino → Diamante → Corona que se encienden; etiqueta verde "Sueldo" desde Oro; la mascota sube a la derecha | ding más agudo por rango, monedas desde Oro |
| 8 | Empleo vs Sumiago (resumen) | Dos columnas: EMPLEO (1 ingreso, horario fijo, tiene techo) / SUMIAGO (tu sueldo + negocio semiautomático, crece con tu constancia) | pops |
| 9 | Todo empieza con tu membresía | Tarjeta que crece "MEMBRESÍA SUMIAGO" y "TODO EMPIEZA AQUÍ" (sin precio) | ding + pop |
| 10 | Comenta SUMIAGO | Botón amarillo "COMENTA SUMIAGO", "sin dejar tu empleo" y "Los resultados dependen de tu constancia." | ding doble de cierre |

## Estilo y reglas

- Fondo blanco con degradado suave (`#FFFFFF` → `#EEEEF2`); bloques gris oscuro `#2D2D37` (empleo) y rojo `#780A0F` / `#E61E2D` (Sumiago); verde `#3CC86E` para lo positivo; amarillo `#FFD23F` para resaltar.
- Subtítulos arriba (y = 230) en negro con borde blanco, de 4 en 4 palabras, la palabra que suena en **rojo**.
- La mascota habla (boca según el volumen de la voz) y parpadea.
- No decir el precio de la membresía. No poner montos del Sueldo Mensual (se cambian desde el admin). El contador de vistas es ilustrativo.
- Hablar de "comisiones directas"; nunca de segundo o tercer nivel ni de donaciones.
- Sin logos en la mascota y sin números de día. Llamada a la acción: "comenta SUMIAGO".
- Si cambias el guion, conserva 11 líneas en el mismo orden: cada escena y cada efecto dependen de su número de línea.
