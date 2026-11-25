---
name: dia-28
description: Crea el video del Día 28 de Tareas Diarias de Sumiago, "5 instrucciones para que tus videos con Claude no parezcan PowerPoint", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 28.
---

# Día 28 — "5 instrucciones para que tus videos con Claude no parezcan PowerPoint"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con franjas rosadas y píldora 'SUMIAGO': '¿TUS VIDEOS CON CLAUDE PARECEN POWERPOINT?', 'GUARDA estas 5 instrucciones', números grandes 1–5 con etiqueta roja y caja 'Prompt' que se escribe, ejemplos (antes/después 'Hola mundo', botón que empuja, cámara siguiendo un carro, tarjeta que se vuelve pantalla, onda de voz 'carro/crear'), 'PRACTÍCALAS EN TAREAS DIARIAS', 'COMENTA SUMIAGO' y cierre con logo. Voz: narrador (probable). Este motor ya aplica las 5 instrucciones.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 9 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-28/scripts/voz.py
python ruta/dia-28/scripts/audio.py
python ruta/dia-28/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-28.mp4
python ruta/dia-28/scripts/pc.py dia-28.mp4 dia-28-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-28/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Tus videos hechos con Claude parecen una presentación de PowerPoint? Guarda estas cinco instrucciones. | Título «¿Tus videos con Claude / parecen PowerPoint?» con «Guarda estas 5 instrucciones», icono play |
| 1 | Uno: revela el texto desde una máscara. Así las palabras salen detrás de un borde, en lugar de solo encenderse. | Número 1 grande y tarjeta «Revela desde una máscara»: Las palabras salen detrás de un borde en lugar de solo encenderse. |
| 2 | Dos: encadena tus movimientos. Cada elemento entra y empuja al siguiente, como fichas de dominó. | Número 2 grande y tarjeta «Movimientos encadenados»: Cada elemento entra y empuja al siguiente, como fichas de dominó. |
| 3 | Tres: haz que la cámara siga algo importante. Un zoom que acompaña la acción mantiene la atención. | Número 3 grande y tarjeta «Una cámara que sigue»: Un zoom que acompaña la acción mantiene la atención. |
| 4 | Cuatro: transforma un objeto para presentar la siguiente escena. Esta tarjeta se convierte en la pantalla que sigue. | Número 4 grande y tarjeta «Un objeto que se transforma»: Esta tarjeta se convierte en la pantalla que sigue. |
| 5 | Cinco: sincroniza las animaciones con tu voz. Si dices «carro», aparece un carro; si dices «crear», se presiona el botón. | «5 · Sincronía con tu voz»: tarjetas Carro, Crear (cada una entra cuando se nombra) |
| 6 | Practica estas instrucciones en tus tareas diarias y tus videos se verán profesionales. | «Practícalas en tareas diarias»: tarjetas Máscara, Encadena, Cámara, Transforma, Sincroniza (cada una entra cuando se nombra) |
| 7 | Comenta «Sumiago» y ve al link de mi perfil para regalarte el enlace, y comiences a aprender y ganar hoy. | Logo, «Comenta SUMIAGO», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| 8 | Sumiago: aprendemos, nos ayudamos y crecemos juntos. | Título «Aprendemos, nos ayudamos / y crecemos juntos» y el logo |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Aprendemos, nos ayudamos y crecemos juntos» y botón «SUMIAGO.COM» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
