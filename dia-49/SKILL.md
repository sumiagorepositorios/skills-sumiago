---
name: dia-49
description: Crea el video del Día 49 de Tareas Diarias de Sumiago, "Hago muebles. Llamar." (historia ilustrativa: un carpintero que no sabía qué escribir usa los textos con IA de su portada de Sumiago para crear su bio, sus botones y las descripciones del catálogo, y los ajusta con su propia voz), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 49.
---

# Día 49 — "Hago muebles. Llamar."

Reel vertical de unos 66 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Ramiro es carpintero y hace muebles preciosos, pero su portada decía solo "Hago muebles. Llamar."; frente a la pantalla no se le ocurría nada: sabía hacer una mesa perfecta, no contarlo. En su portada de Sumiago toca **Textos con IA**, escribe en una línea lo que hace, elige el tono "Cercano" y en segundos tiene 3 opciones de presentación; escoge la que más se parece a él. Pide ideas para sus botones y descripciones para cada mueble del catálogo. No las copia tal cual: cambia una palabra aquí y otra allá, y quedan con su voz. "La inteligencia artificial no hizo los muebles. Pero le ayudó a mostrarlos." Cierra: "Tú haces el trabajo… deja que las palabras te ayuden."

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-BlackItalic, Inter-Bold, Inter-SemiBold, Inter-SemiBoldItalic, Inter-Medium .otf), instalada o en una carpeta `fonts/` dentro de la skill.
- Imágenes en `assets/`: `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free` (cámbialo con `FISH_MODEL`). Voz: "narrador educativo sumiago".

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-49/scripts/voz.py
python ruta/dia-49/scripts/tl.py
python ruta/dia-49/scripts/align.py
python ruta/dia-49/scripts/audio.py
python ruta/dia-49/scripts/render.py 0 660 a.mp4
python ruta/dia-49/scripts/render.py 660 1320 b.mp4
python ruta/dia-49/scripts/render.py 1320 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-49.mp4
python ruta/dia-49/scripts/pc.py dia-49.mp4 dia-49-pc.mp4
```

Para revisar un momento: `python ruta/dia-49/scripts/render.py still 28.5 39.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Ramiro es carpintero… «Hago muebles. Llamar.» | Taller de madera con aserrín, Ramiro con delantal, una mesa y su portada pobre; sello "¿ESO ES TODO?" | sierra |
| 1 | Frente a la pantalla, no se le ocurría nada | Celular "Escribe tu bio…" con cursor que parpadea; chip | música bajita |
| 2 | Una mesa perfecta… cómo contarlo | Mesa con nivel y chispas; chip "MESA PERFECTA"; burbuja "¿Y cómo lo cuento?" | brillo |
| 3 | Tocó el botón de textos con IA | Panel "Textos con IA" con toque; chip "INTELIGENCIA ARTIFICIAL" | brillo |
| 4 | Escribió lo que hace… tono cercano | Campo "¿Qué haces?" que se escribe y tonos Cercano / Profesional / Divertido / Elegante | tecleo |
| 5 | 3 opciones de presentación… escogió una | Tres bios que aparecen y una seleccionada con ✓; chip | ding |
| 6 | Ideas para botones y descripciones del catálogo | "Ideas para tus botones" (6 opciones) y "Descripciones del catálogo" | pops |
| 7 | No las copió tal cual… quedaron con su voz | Texto donde una frase se cambia en rojo; sello "CON SU VOZ" | tecleo |
| 8 | Su portada cuenta lo que él no sabía decir | Portada final "Ramiro Carpintería" con la bio nueva y los botones | brillo |
| 9 | La IA no hizo los muebles… le ayudó a mostrarlos | Mesa con brillo y las dos frases | brillo |
| 10 | Si te quedas en blanco… con tu membresía | Hoja "En blanco" frente a "Con IA"; chip "TEXTOS CON IA · CON TU MEMBRESÍA" | |
| 11 | Entra al link de mi perfil… que las palabras te ayuden | Tarjeta "Textos con IA · Bio, botones y descripciones · PORTADA PRO", mascota, "LINK EN MI PERFIL" y la frase final | |
| — | Cierre | Logo con rebote, ondas y brillo; "Que las palabras te ayuden" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Taller de madera cálido y paneles oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: los textos con IA son de la portada **PRO (con la membresía)**; generan 3 bios (máximo 150 caracteres), 6 textos para botones y 3 descripciones de producto, con tono cercano, profesional, divertido o elegante. Recomendar revisar y ajustar el texto. No prometer ventas ni ganancias. No escribir «BinanTrader».
