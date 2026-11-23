---
name: dia-01
description: Crea el video del Día 1 de Tareas Diarias de Sumiago, "Hoy es el lanzamiento: ¿pesimista o positivo?" (el pesimista con su nube de lluvia que pone excusas y se autosabotea frente al emprendedor positivo que no pierde la fe, la rueda ya está hecha, constancia y disciplina, "¿Cuál eres tú?" y cierre "Comenta SUMIAGO"), con fondo claro, mascota que habla, música y efectos, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 1.
---

# Día 1 — "Hoy es el lanzamiento: ¿pesimista o positivo?"

Reel vertical 9:16 (1080x1920, 30 fps, unos 60 s) con fondo claro. La mascota Sumiago anuncia el lanzamiento y presenta los dos tipos de personas: el **pesimista** (personaje de camiseta azul, colores apagados, cara triste y una nube de lluvia encima) y el **positivo** (la mascota, con un sol de rayos que giran). Termina con "¿Cuál eres tú?" y "Comenta SUMIAGO". Lleva música hecha por código (sin derechos de autor), efectos de sonido, un acercamiento rápido al empezar cada escena y una barra roja de progreso abajo. La versión PC pone el reel en el centro sobre su propio fondo difuminado.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy opencv-python-headless`
- La fuente **Poppins Bold** ya viene en `fonts/` (licencia OFL); si la tienes instalada, usa esa.
- Las imágenes ya vienen en `assets/`: `mascota-frente.png` (la mascota que habla, con sus logos), `mascota-pulgar.png`, `logo-sumiago.png` y `pesimista-base.png` (el personaje de camiseta azul).
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 18 frases, una por línea (cada línea es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, sin silencios y 0,25 s entre frases. Deja `voice.wav` y `durs.json`.
- `scripts/preparar_personajes.py`: deja `mascot_clean.png` (la mascota sin la marca de agua) y `pesimista.png` (cejas caídas, boca triste y colores apagados).
- `scripts/base.py`: parte común (tiempos por palabra, boca según el volumen de la voz y parpadeo).
- `scripts/render.py`: todas las escenas, carteles, sellos, la puerta que se cierra, engranajes, la rueda, la gráfica y la lista de efectos.
- `scripts/audio.py`: voz + música (124 bpm, C–Am–F–G) que baja cuando habla la voz + efectos → `mix.wav`.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-01/scripts/voz.py
python ruta/dia-01/scripts/preparar_personajes.py
python ruta/dia-01/scripts/audio.py
python ruta/dia-01/scripts/render.py test 0.5 3 6 12 30 50
python ruta/dia-01/scripts/render.py full
python ruta/dia-01/scripts/pc.py dia-01.mp4 dia-01-pc.mp4
```

`render.py test` deja `test.jpg` con cuadros de muestra para revisar antes del render completo. Escucha el video completo antes de publicarlo.

## Escenas (línea del guion → lo que se ve → sonido)

| # | Frase | En pantalla | Sonido |
|---|-------|-------------|--------|
| 0 | ¡Oye! ¿Sabes qué? | Mascota grande de frente y globo amarillo "¡OYE!" | pop |
| 1 | Hoy es el lanzamiento de SUMIAGO | "HOY ES EL" + cartel rojo "LANZAMIENTO" + logo; un cohete despega | sello + pop + subida |
| 2 | Dos tipos de personas: el pesimista y el positivo | Pantalla partida: arriba gris con el pesimista y su nube, abajo vino tinto con la mascota y un brillo naranja; círculo "VS"; etiquetas PESIMISTA y POSITIVO | golpe + pops |
| 3 | Comencemos con el pesimista | El pesimista se acerca, nube con lluvia | — |
| 4 | Él dice: eso no es para mí… | Cartel "EL PESIMISTA"; globos "Eso no es para mí" y "No soy bueno para eso" | pops |
| 5 | Esa es otra estafa más | Sello rojo "¿OTRA ESTAFA?" y un rayo en la nube | sello + zumbido |
| 6 | Allí no se gana nada si no trabajas | Globo "Sin trabajar no se gana nada" | pop |
| 7 | Vive quejándose, postergando… | "VIVE ASÍ" y etiquetas SE QUEJA / LO DEJA PARA MAÑANA / PONE EXCUSAS | pops |
| 8 | Se autosabotea… | "AUTOSABOTAJE", barra "AVANCE: 0%" y la puerta "NUEVA OPORTUNIDAD" que se abre, se cierra y queda con candado | zumbido |
| 9 | Y está el emprendedor positivo, optimista | Sol con rayos que giran, mascota, "EL POSITIVO" y "OPTIMISTA" | ding + subida |
| 10 | Ha pasado por estafas, engaños y fraudes | Etiquetas negras ESTAFAS, ENGAÑOS, FRAUDES le caen encima | sellos |
| 11 | Pero es incansable… | "INCANSABLE": las etiquetas se caen, aparece el corazón "FE" y "UNA NUEVA OPORTUNIDAD" | pop + ding |
| 12 | Voy a conocer ese sistema, voy a probar… | Teléfono con el menú de Sumiago (Tareas diarias, Gana con Marketing, Marketplace, Comunidad), lupa y botón "PROBAR"; "VOY A CONOCER" → "VOY A PROBAR" | pop + toque |
| 13 | Voy a hacer que este sistema funcione para mí | Engranajes grises que se vuelven rojo y negro y giran más rápido; "¡QUE FUNCIONE!" | sello |
| 14 | La rueda ya está hecha… | Carretera, la mascota con la rueda que gira; "LA RUEDA YA ESTÁ HECHA" y "TAREAS DIARIAS" | pop |
| 15 | Y a los meses, con constancia y disciplina… | CONSTANCIA y DISCIPLINA, barras M1–M6 que suben, "SUS PRIMEROS $522 USD" y la nota "Los resultados dependen de tu constancia y disciplina." | pops + monedas |
| 16 | ¿Y tú cuál de los dos eres? | "¿CUÁL ERES TÚ?" con dos tarjetas: PESIMISTA (gris) y POSITIVO (vino tinto con borde dorado) | sello + pops |
| 17 | Hoy es el lanzamiento de SUMIAGO. ¡Comenta SUMIAGO! | Logo, "HOY ES EL LANZAMIENTO", confeti, recuadro amarillo "COMENTA SUMIAGO" y la mascota con el pulgar arriba | subida + aplausos + ding |

## Estilo y reglas

- Fondo blanco con degradado suave; las escenas del pesimista van en gris; rojo Sumiago `#E61E2D`, amarillo `#FFD23F`, vino tinto `#6E0A12`.
- Subtítulos arriba (y = 230), de 4 en 4 palabras, en negro con borde blanco; la palabra que suena en **rojo** y un poco más arriba.
- El pesimista nunca lleva los logos de Sumiago; la mascota sí.
- La cifra de $522 USD es un ejemplo y va siempre con la nota de que los resultados dependen de la constancia y la disciplina. No dice el precio de la membresía.
- Si cambias el guion, conserva 18 líneas en el mismo orden: cada escena y cada efecto dependen de su número de línea.
