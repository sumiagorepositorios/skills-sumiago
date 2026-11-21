---
name: dia-18
description: Crea el video del Día 18 de Tareas Diarias de Sumiago, "Crear un canal en 2026: siguiente, siguiente y finalizar" (asistente de instalación animado, mascota que habla, clics, cierre con el logo), en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 18.
---

# Día 18 — "Siguiente, siguiente y finalizar"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps, unos 32 s). La mascota está en su cuarto de noche y explica que crear un canal de videos es como instalar un programa: aparece una ventana de asistente con los pasos Bienvenida → Nicho → Estructura → Producción → Publicar, un cursor que hace clic en "Siguiente" y, al final, "¿Y mañana?" con un botón gigante de "Siguiente". Cierra con la pantalla en blanco y el logo de Sumiago con rebote, ondas, chispas y brillo. La versión PC pone el reel a la derecha y un panel con el mensaje a la izquierda.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` (boca abierta), `sumiago-c.png` (boca cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 7 frases (cada frase es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), sin silencios y 7 % más rápida; crea `tl.json` (0,3 s al inicio, 0,3 s entre frases, 3,2 s para el logo).
- `scripts/promo_base.py`: motor común (fuentes, tiempos por palabra, mascota que habla, cuarto de noche, ventana del asistente, cursor, subtítulos y cierre con logo).
- `scripts/render.py`: las escenas de este video, las palabras clave y los clics.
- `scripts/audio.py`: voz + música nocturna (Dm–Bb–C–Am, hecha por código) + clics + brillo del logo.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-18/scripts/voz.py
python ruta/dia-18/scripts/render.py meta
python ruta/dia-18/scripts/audio.py
python ruta/dia-18/scripts/render.py 0 2000
ffmpeg -y -framerate 30 -i frames/%05d.jpg -i mix.wav -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 160k -shortest -movflags +faststart dia-18.mp4
python ruta/dia-18/scripts/pc.py dia-18.mp4 dia-18-pc.mp4
```

El paso de cuadros se puede partir en dos ventanas (`0 490` y `490 2000`) para ir más rápido. Escucha el video completo antes de publicarlo.

## Escenas

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | Crear un canal es siguiente, siguiente y finalizar | Mascota en su cuarto de noche (ventana con luna, estante, lámpara); luego la ventana "Asistente · Canal de videos": Bienvenida → Componentes con checks → "Instalando canal..." con barra al 100 % y "Canal listo". El cursor hace clic en cada botón |
| 1 | Eliges un nicho que funcione | Lista de nichos; se marca "Historias de misterio", etiqueta verde con visitas que suben a 184.000 y "Competencia baja" |
| 2 | Copias la estructura, no el contenido | Miniatura de un viral "2,4 M" que gira y se vuelve "Tu historia"; pasos Gancho / Giro / Final; "su contenido" tachado y "su estructura" en verde; mascota pequeña abajo |
| 3 | Guion, voz, imágenes y video | "Producción": líneas de texto, onda de voz roja, tres miniaturas y barra del video, cada una con check verde |
| 4 | Finalizar: lo publicas | "Mi primer video" con barra de subida, "¡Publicado!", visitas a 3.402 y confeti |
| 5 | ¿Y mañana? Otra vez siguiente | El cuarto amanece; luego un botón gigante "Siguiente ›" que se presiona y "Siguiente video en marcha" |
| 6 | Visita la bio y regístrate | Mascota hablando y tarjeta "@sumiago · Aprende a crear videos que funcionan · sumiago.com · Regístrate aquí" que late; el cursor la toca |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; "Visita la bio de mi perfil" y "REGÍSTRATE EN EL LINK" |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, verde `#2EBE6E`, dorado `#FFC43C`; ventana clara tipo sistema operativo sobre un cuarto azul oscuro.
- Subtítulos arriba (y = 250) palabra por palabra, en blanco con borde oscuro; las palabras clave (siguiente, finalizar, nicho, visitas, viral, estructura, guion, voz, publicas, mañana, bio, link, regístrate…) van en un recuadro rojo.
- La mascota alterna boca abierta/cerrada según el volumen de la voz.
- Sin números de día dentro del video (tampoco en el panel de PC).
- Si cambias el guion, conserva 7 frases en el mismo orden: cada escena busca sus palabras clave dentro de su frase.
