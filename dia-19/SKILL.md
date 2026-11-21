---
name: dia-19
description: Crea el video del Día 19 de Tareas Diarias de Sumiago, "Si no te ven en internet, no te encuentran" (negocios que cierran, clientes que buscan en el celular, alcance en barrio-ciudad-país, mascota que habla y cierre con el logo), en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 19.
---

# Día 19 — "Si no te ven en internet, no te encuentran"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps, unos 35 s) con gancho en los primeros 3 segundos. La mascota está frente a su negocio en una calle de noche y muestra con datos reales que muchos negocios nuevos cierran pronto, que hoy los clientes buscan en el celular y que los negocios que crecen se dejan ver en internet y redes. Música bajita y cierre con el logo de Sumiago. La versión PC pone el reel a la derecha y un panel con el mensaje a la izquierda.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` (boca abierta), `sumiago-c.png` (boca cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 8 frases (cada frase es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), sin silencios y 7 % más rápida; crea `tl.json` (0,15 s al inicio, 0,3 s entre frases, 3 s para el logo).
- `scripts/promo_base.py`: motor común (fuentes, tiempos por palabra, mascota que habla, cuarto de noche, ventana del asistente, cursor, subtítulos y cierre con logo).
- `scripts/render.py`: las escenas de este video, las palabras clave y los clics.
- `scripts/audio.py`: voz + música nocturna bajita (Dm–Bb–C–Am, hecha por código, al 55 %) + golpes en los datos + brillo del logo.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-19/scripts/voz.py
python ruta/dia-19/scripts/render.py meta
python ruta/dia-19/scripts/audio.py
python ruta/dia-19/scripts/render.py 0 2000
ffmpeg -y -framerate 30 -i frames/%05d.jpg -i mix.wav -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 160k -shortest -movflags +faststart dia-19.mp4
python ruta/dia-19/scripts/pc.py dia-19.mp4 dia-19-pc.mp4
```

El paso de cuadros se puede partir en dos ventanas (`0 520` y `520 2000`) para ir más rápido. Escucha el video completo antes de publicarlo.

## Escenas

| # | Frase | En pantalla |
|---|-------|-------------|
| 0 | Si tienes un negocio y nadie lo ve en internet, escucha esto | Calle de noche con edificios iluminados y el local "MI NEGOCIO"; la mascota habla; alerta roja "!" y tarjeta "Búsquedas de tu negocio: 0" |
| 1 | En países latinoamericanos, 3 de cada 10 cierran el primer año | "AÑO 1": 10 locales; tres bajan la persiana con "CERRADO"; "3 de cada 10 · cierran en el primer año" |
| 2 | Casi la mitad no llega a los dos años | "2 AÑOS": cuatro locales, dos cierran; "Casi la mitad · no llega a los 2 años" |
| 3 | Abres el local, pones el letrero y esperas | El letrero se enciende, la gente pasa de largo y aparece un reloj que corre |
| 4 | Tus clientes te buscan en el celular | Gente con celular; sube un teléfono que escribe "panadería cerca de mí", salen tres resultados con estrellas y "Tu negocio no aparece" |
| 5 | Barrio, ciudad y país con redes sociales | Mapa oscuro con un pin; círculos rojos BARRIO → CIUDAD → PAÍS con puntos dorados; iconos de corazón, comentario y compartir con contadores |
| 6 | En Sumiago aprendes a posicionar tu negocio y ganas | Teléfono con el perfil "Mi Negocio", visitas que suben a 12.480 y gráfica; monedas que suben; mascota con el pulgar arriba; "APRENDE + GANA" |
| 7 | Visita la bio de mi perfil y regístrate | Mascota en la calle y tarjeta "@sumiago · Posiciona tu negocio en internet · sumiago.com · Regístrate aquí"; el cursor la toca |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; "Posiciona tu negocio" y "LINK EN MI BIO" |

Las cifras en pantalla llevan la fuente: INEGI (México) y Confecámaras (Colombia). Si cambias los datos, verifícalos antes y cambia también la fuente.

## Estilo y reglas

- Rojo Sumiago `#E6262F`, verde `#2EBE6E`, dorado `#FFC43C`; calle nocturna azul con ventanas encendidas y locales con toldo rojo y blanco.
- Subtítulos arriba (y = 250) palabra por palabra, en blanco con borde oscuro; las palabras clave (internet, latinoamericanos, cierran, primer, mitad, dos, celular, crecen, redes, barrio, ciudad, país, sumiago, ganas, bio, link, regístrate…) van en un recuadro rojo.
- La mascota alterna boca abierta/cerrada según el volumen de la voz.
- Sin números de día dentro del video (tampoco en el panel de PC).
- Si cambias el guion, conserva 8 frases en el mismo orden: cada escena busca sus palabras clave dentro de su frase.
