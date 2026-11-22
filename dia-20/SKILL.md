---
name: dia-20
description: Crea el video del Día 20 de Tareas Diarias de Sumiago, "Un fin de semana o tu membresía: tú decides" (gastos de cine, comida y centro comercial frente a las herramientas de Sumiago, sin montos, con música, efectos y cierre con el logo), en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 20.
---

# Día 20 — "Un fin de semana o tu membresía: tú decides"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps, unos 37 s) con mucho ritmo: compara lo que se va en un fin de semana (cine, comida rápida, centro comercial) con activar la membresía de Sumiago y usar sus herramientas. **No menciona montos ni valores** en la voz ni en la pantalla. Lleva música con ritmo bajita, caja registradora, pops, dings, transiciones y cierre con el logo. La versión PC pone el reel a la derecha y el mensaje a la izquierda.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` (boca abierta), `sumiago-c.png` (boca cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 9 frases (cada frase es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), sin silencios y 8 % más rápida; crea `tl.json` (0,15 s al inicio, 0,25 s entre frases, 0,5 s antes de "Ahora mira esto", 3 s para el logo).
- `scripts/promo_base.py`: motor común (fuentes, tiempos por palabra, mascota que habla, cuarto de noche, ventana del asistente, cursor, subtítulos y cierre con logo).
- `scripts/render.py`: las escenas de este video, las palabras clave y los momentos de cada efecto.
- `scripts/audio.py`: voz + música con ritmo bajita (C–Am–F–G, 118 bpm, hecha por código) + caja registradora, pops, dings, bajón, subida, transiciones y brillo del logo.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-20/scripts/voz.py
python ruta/dia-20/scripts/render.py meta
python ruta/dia-20/scripts/audio.py
python ruta/dia-20/scripts/render.py 0 2000
ffmpeg -y -framerate 30 -i frames/%05d.jpg -i mix.wav -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 160k -shortest -movflags +faststart dia-20.mp4
python ruta/dia-20/scripts/pc.py dia-20.mp4 dia-20-pc.mp4
```

El paso de cuadros se puede partir en dos ventanas (`0 550` y `550 2000`) para ir más rápido. Escucha el video completo antes de publicarlo.

## Escenas

| # | Frase | En pantalla | Sonido |
|---|-------|-------------|--------|
| 0 | ¿Cuánto te gastas en un fin de semana? | Billetes que salen volando de una billetera y un "?" grande | — |
| 1 | Vas al cine con crispetas | Pantalla de cine iluminada, butacas, crispetas y boleto "CINE"; etiqueta roja "GASTO"; barra "TU DINERO" arriba que empieza a bajar | caja registradora |
| 2 | Un combo en cualquier franquicia | Hamburguesa y papas; "GASTO"; la barra sigue bajando | caja registradora |
| 3 | Una vuelta por el centro comercial | Fachada "MALL" y tres bolsas de compra que caen; "GASTO" | caja registradora |
| 4 | Y ese dinero el lunes ya no está | Recibo con tres líneas "PAGADO" y "SE FUE"; luego billetera gris vacía y "LUNES: VACÍA" | caja + bajón |
| 5 | En vez de eso, activas tu membresía | "FIN DE SEMANA · se acaba" contra tarjeta roja con el logo de Sumiago, "ACTÍVATE · membresía" y "VS" | subida + ding |
| 6 | Cursos, portada, marketplace, tienda, tareas, comunidad y comisiones directas | Siete tarjetas con icono que aparecen una a una: Cursos, Mi Portada, Marketplace, Mi Tienda, Tareas diarias, Comunidad y Comisiones directas (flecha que sube) | pop por tarjeta |
| 7 | Uno se acaba el domingo, el otro trabaja para ti | Calendario "DOM" tachado, "Gasto que se acaba" contra tarjeta roja con curva que sube, "Herramientas que trabajan para ti" y etiquetas CONSTANCIA y DISCIPLINA | ding por etiqueta |
| 8 | Tú decides. Regístrate en el link de mi perfil | Mascota con el pulgar arriba y botón blanco "LINK EN MI PERFIL" que late | pop |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; "Tú decides" y "REGÍSTRATE · LINK EN MI PERFIL" | brillo del logo |

Cada cambio de escena lleva un "whoosh".

## Estilo y reglas

- Rojo Sumiago `#E6262F`, verde `#2EBE6E`, dorado `#FFC43C`; fondos oscuros con un resplandor de color distinto por escena (rojo, azul cine, naranja comida, magenta centro comercial).
- Subtítulos arriba (y = 250) palabra por palabra, en blanco con borde oscuro; las palabras clave (fin, semana, cine, combo, centro, dinero, lunes, activas, membresía, cursos, portada, marketplace, tienda, tareas, comunidad, comisiones, exponenciales, herramientas, constancia, disciplina, decides, link, regístrate…) van en un recuadro rojo.
- La mascota alterna boca abierta/cerrada según el volumen de la voz.
- Sin números de día dentro del video (tampoco en el panel de PC).
- Si cambias el guion, conserva 9 frases en el mismo orden: cada escena busca sus palabras clave dentro de su frase.
- No mencionar montos ni precios (ni de los gastos ni de la membresía) y no prometer ganancias: las herramientas "trabajan para ti si las usas con constancia y disciplina".
- Las comisiones se nombran como "comisiones directas exponenciales por recomendar las herramientas"; nunca segundo o tercer nivel.
