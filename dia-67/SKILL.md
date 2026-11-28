---
name: dia-67
description: Crea el video del Día 67 de Tareas Diarias de Sumiago, "Sin mostrar tu cara" (tipografía en movimiento estilo motion graphics: ¿te da pena salir en cámara?, muchos videos que más se ven no muestran a nadie, 3 formatos para hoy —texto animado, tus manos desde arriba, tu pantalla—, la voz puede ser la tuya o hecha con IA, lo que importa es que le sirva a alguien; cierre "Comenta SUMIAGO y te envío toda la información"), en móvil 9:16 y PC 16:9, con narrador, música, efectos y logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 67 o un video educativo de texto animado con este estilo.
---

# Día 67 — "Sin mostrar tu cara"

Reel vertical de unos 48 s (1080x1920, 30 fps) hecho solo con texto animado, figuras e interfaces, igual que los Días 64 y 65. Le habla a quien no quiere salir en cámara. Le muestra tres formatos que puede grabar hoy mismo sin mostrar su cara y cierra con la dinámica de comentar la palabra **SUMIAGO**.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+, FFmpeg en el PATH y Google Chrome. Paquetes: `pip install playwright numpy pillow`
- Fuentes **Inter Display** (Black, ExtraBold), **Inter** (Medium, Black, Bold, SemiBold) y **Crimson Text** SemiBold Italic, instaladas o en una carpeta `fonts/` junto a `anim.html`. Una fuente de emojis a color para los íconos de la escena 7 y 10.
- `assets/logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free`. Voz: "narrador educativo sumiago".

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
export CHROME=/ruta/a/chrome          (en Windows: set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe)
python ruta/dia-67/scripts/voz.py
python ruta/dia-67/scripts/tl.py
python ruta/dia-67/scripts/sound.py
python ruta/dia-67/scripts/shoot.py full
ffmpeg -y -i video_tmp.mp4 -i fx.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-67.mp4
python ruta/dia-67/scripts/pc.py dia-67.mp4 dia-67-pc.mp4
```

Para revisar momentos sueltos sin renderizar todo: `python ruta/dia-67/scripts/shoot.py test 1.5,9.5,27.5`.

## Escenas

| # | Voz | En pantalla | Técnica / sonido |
|---|-----|-------------|------------------|
| 0 | ¿Te da pena salir en cámara? | "CÁMARA?" en recuadro rojo que gira; tarjeta de cámara con REC parpadeando y la silueta tachada | pops, barrido |
| 1 | Tranquilo, no tienes que hacerlo. | "NO", "tienes que" en cursiva serif, "HACERLO." | golpe |
| 2 | Muchos de los videos que más se ven no muestran a nadie. | "NADIE" en recuadro; tres tarjetas de videos sin cara con vistas que suben | pops |
| 3 | Aquí tienes tres formatos… sin mostrar tu cara. | "3" gigante rojo, "FORMATOS" y tres tarjetas TEXTO / MANOS / PANTALLA | pops |
| 4 | Formato uno: texto animado, como este video. | Etiqueta FORMATO 1; palabras en tarjetas que caen girando | pops |
| 5 | Frases cortas, que aparecen al ritmo de la voz. | Frase que se ilumina palabra por palabra y onda de voz | tic por palabra |
| 6 | Formato dos: tus manos. | FORMATO 2; vista desde arriba con manos que se mueven sobre un plato | pop |
| 7 | Graba desde arriba mientras cocinas, empacas o arreglas algo. | "ARRIBA" y tres tarjetas que entran con ✓ | pops |
| 8 | Formato tres: tu pantalla. | FORMATO 3; celular "Grabando pantalla" | pop |
| 9 | Grabas tu celular mientras enseñas a usar una app o una página. | Celular con PASO 1-3 de 3, toques con onda roja | clics |
| 10 | Y en los tres, la voz puede ser la tuya o una voz hecha con IA. | "VOZ" gigante; dos tarjetas con su onda ("la tuya" gris, "IA" roja) | pops |
| 11 | Lo que importa no es tu cara. | Fondo claro (segundo acto); "TU CARA" tachado | golpe, barrido |
| 12 | Es que lo que dices le sirva a alguien. | "le sirva" en recuadro, "a alguien." en cursiva roja | pop |
| 13 | Elige un formato y publica tu primer video hoy. | Selector que salta entre los 3 formatos y queda en TEXTO; casilla ✓ "HOY" | pop, ding |
| 14 | ¿Quieres aprender a crear videos así? Comenta SUMIAGO… | "SUMIAGO" gigante, comentario que se escribe solo y corazón | tecleo, clic, ding |
| — | Cierre | Logo, "Crea tus videos con IA", "LINK EN MI PERFIL" | golpe |

## Estilo y reglas

- Fondo negro con brillo rojo Sumiago que se mueve; el segundo acto (escenas 11-13 y logo) cambia a fondo claro. Solo rojo `#E10600`, negro, blanco y gris.
- Palabras que suben desde una máscara, palabras tachadas con una línea roja animada, palabras clave en recuadro rojo, acentos en cursiva serif roja, acercamiento lento de cámara en cada escena y transición con desenfoque.
- Sin silencios: cada escena dura su frase + 0,2 s (mínimo 55 % de su tiempo de diseño) y su animación se acelera o frena para caber (`tl.py`). No usar «…» en el texto de la voz, porque Fish hace pausas largas. La música baja cuando habla el narrador.
- Para cambiar la palabra del cierre, cambia la frase 14 en `guion.json` y la palabra `SUMIAGO` (dos veces) en la escena 15 de `anim.html`.
- Las cifras de vistas de las tarjetas son ilustrativas. Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
