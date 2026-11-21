---
name: dinero-tiempo
description: Crea el reel reflexivo "El dinero va y viene, MIRA!" (siluetas al atardecer, palabras grandes en amarillo, subtítulos con palabras clave resaltadas, música suave y cierre con el logo de Sumiago) con voz de Fish Audio, en 9:16 y 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del dinero y el tiempo.
---

# Reel "El dinero va y viene, MIRA!"

Video vertical 9:16 (se dibuja a 720x1280 y se entrega a 1080x1920, 30 fps, unos 39 s). Estilo de siluetas negras sobre cielos de atardecer, noche y día, con una palabra grande en amarillo por idea. Lo narra la voz de la mascota, con música bajita. Cierra con la pantalla en blanco y el logo de Sumiago con rebote, ondas, chispas y un brillo, más "Aprende a crear videos así" y el botón "LINK EN MI PERFIL". También sale en 16:9 (1920x1080) para PC.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold e Inter-Medium en .otf): instálala desde rsms.me/inter o copia los .otf a una carpeta `fonts/` dentro de la skill.
- `assets/logo-sumiago.png` ya viene en la skill.
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 9 frases (cada frase es una escena).
- `scripts/voz.py`: voz con Fish Audio (voz `bd35c17b29c54d3e9d2663863a28d212`, sin silencios, 4 % más rápida) y línea de tiempo `tl.json` (0,3 s al inicio, 0,45 s entre frases, 3 s para el logo).
- `scripts/render.py`: dibuja todas las escenas, los subtítulos y el cierre.
- `scripts/audio.py`: mezcla voz + música (Dm–Bb–C–Am, generada por código, al 50 % y bajando cuando habla la voz) + brillo sonoro del logo.

## Pasos

Trabaja en una carpeta vacía y ejecuta los scripts desde ahí.

1. **Voz y línea de tiempo:**
   ```
   set FISH_API_KEY=tu_clave
   python ruta/dinero-tiempo/scripts/voz.py
   ```
2. **Datos para el audio:**
   ```
   python ruta/dinero-tiempo/scripts/render.py meta
   ```
3. **Música y mezcla:**
   ```
   python ruta/dinero-tiempo/scripts/audio.py
   ```
4. **Cuadros** (puedes partirlo en dos ventanas para ir más rápido, por ejemplo `0 580` y `580 2000`):
   ```
   python ruta/dinero-tiempo/scripts/render.py 0 2000
   ```
5. **Video 9:16:**
   ```
   ffmpeg -y -framerate 30 -i frames/%05d.jpg -i mix.wav -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 160k -shortest -movflags +faststart dinero-tiempo.mp4
   ```
6. **Versión 16:9 para PC:**
   ```
   ffmpeg -y -i dinero-tiempo.mp4 -filter_complex "[0:v]scale=1920:-2,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[b];[0:v]scale=-2:1080[f];[b][f]overlay=(W-w)/2:0,format=yuv420p[o]" -map "[o]" -map 0:a -c:v libx264 -preset veryfast -crf 21 -c:a copy -movflags +faststart dinero-tiempo-16x9.mp4
   ```
7. **Escúchalo completo** antes de publicarlo.

## Escenas (frase → lo que se ve)

Al cambiar de escena hay un zoom corto. La palabra grande amarilla aparece en el momento en que la voz la dice.

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | Miedo a gastar en lo que te hace feliz | Atardecer con montañas, pájaros y farol; silueta con billetera; "MIEDO A GASTAR" |
| 1 | 50 dólares en una cena → recuerdos | Cuatro amigos en la mesa; contador "50 · DÓLARES EN UNA CENA"; luego levantan los brazos con destellos y "RECUERDOS" |
| 2 | Un viaje te acompaña toda la vida | Camino con líneas que se mueven hacia el horizonte y una figura que se aleja; "1 VIAJE · UNA EXPERIENCIA" y "TODA TU VIDA" |
| 3 | Vivimos al revés, cuidando cada moneda | Figura ante un letrero de dirección, "AL REVÉS"; luego figura con bastón que sigue una moneda flotante, "LA ÚLTIMA MONEDA" |
| 4 | El dinero va y viene, el tiempo solo se va | Monedas girando alrededor, "VA Y VIENE · EL DINERO"; el sol baja y "SOLO SE VA · EL TIEMPO" |
| 5 | El dinero se recupera, el tiempo nunca | Noche estrellada, mesa con una vela que se consume; "DINERO · LO VUELVES A GANAR" y "TIEMPO · NUNCA LO RECUPERAS" |
| 6 | Haz planes, viaja y comparte | Día con figura y niño volando una cometa: "HAZ PLANES", "VIAJA"; luego un grupo de seis, "COMPARTE · CON QUIEN QUIERES" |
| 7 | El verdadero lujo | Ciudad con ventanas encendidas, "NO ES · ACUMULAR DINERO"; luego una casa que se ilumina con una pareja, "EL VERDADERO LUJO" |
| 8 | Regístrate en Sumiago, link en mi perfil | Figura señalando una tarjeta "@sumiago · Videos como este · Link: Regístrate" que late en rojo; "REGÍSTRATE" |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas rojas, chispas y brillo; "Aprende a crear videos así" y "LINK EN MI PERFIL" |

## Estilo y reglas

- Siluetas `#160C0E`; cielos en degradado (atardecer morado → naranja → durazno; noche azul con estrellas; día celeste). Horizonte en y = 760.
- Palabras grandes en amarillo `#FFC828` (Inter Black, máximo 640 px de ancho) y texto pequeño blanco debajo.
- Subtítulos arriba (y = 250) palabra por palabra, en blanco con borde oscuro; las palabras clave (miedo, recuerdos, dinero, tiempo, vida, regístrate…) van en un recuadro amarillo.
- Sin números de día y sin marcas de otros creadores; el cierre siempre invita a registrarse en Sumiago con el link del perfil.
- Si cambias el guion, conserva 9 frases en el mismo orden: cada escena busca sus palabras clave dentro de su frase.
