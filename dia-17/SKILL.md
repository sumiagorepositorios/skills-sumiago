---
name: dia-17
description: Crea el video del Día 17 de Tareas Diarias de Sumiago, "¿Por qué unos videos tienen millones de visitas?", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 17.
---

# Día 17 — "¿Por qué unos videos tienen millones de visitas?"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música de misterio (dron grave y latido), bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro sin mascota: pared de videos con visitas ('2,4 M' vs '200'), dedo que desliza, contador '1.7 segundos', anzuelo bajo el agua con peces, onda de audio con 'CORO', reloj 'FINAL = INICIO', ciudad con aviones de papel 'Compartido 88.836'; cierre blanco con logo y 'ENLACE EN MI BIOGRAFÍA'. Voz: narrador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 11 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-17/scripts/voz.py
python ruta/dia-17/scripts/audio.py
python ruta/dia-17/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-17.mp4
python ruta/dia-17/scripts/pc.py dia-17.mp4 dia-17-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-17/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Por qué unos videos tienen millones de visitas y el tuyo se queda en 200? | «Tu video» (200) contra «Viral» (2,4 M) con VS |
| 1 | Porque no compites solo contra otros videos. Compites contra un pulgar. | Título «Compites contra / un pulgar», icono play |
| 2 | En promedio, la gente le da dos segundos a cada video antes de deslizar. | Cifra grande «2» y «segundos» (antes de deslizar) |
| 3 | Y el algoritmo primero lo muestra a unos pocos. Si se quedan, se lo enseña a miles. | barras Unos pocos 3, Si se quedan 100, Miles 1000+ |
| 4 | Por eso lo primero es el gancho. | Título «1. El / GANCHO», icono alerta |
| 5 | En una frase dices de qué va y prometes algo. | Número 1 grande y tarjeta «El gancho»: Una frase: de qué va el video y qué prometes. |
| 6 | Después, cada frase responde una pregunta y abre otra, para que nadie se vaya. | Número 2 grande y tarjeta «Pregunta y respuesta»: Cada frase responde una pregunta y abre otra. |
| 7 | Es como una canción que se corta justo antes del coro: el cerebro necesita terminarla. | Título «Antes del / CORO», icono play |
| 8 | Y el final se une con el principio, para que el video vuelva a empezar sin que lo notes. | Número 3 grande y tarjeta «Final = inicio»: El video vuelve a empezar sin que lo notes. |
| 9 | Pero lo que más lo empuja es que lo compartan. Si sorprende o enseña algo útil, la gente lo envía. | Cifra grande «88.836» y «veces compartido» (si sorprende o enseña algo útil) |
| 10 | Si quieres aprender a hacer este tipo de videos, entra al enlace de mi biografía y regístrate en Sumiago. Mientras aprendes, ganas dentro de la comunidad. | Logo, «Aprende a crear videos virales», mascota con el pulgar y botón «ENLACE EN MI BIOGRAFÍA» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Aprende · Crea · Gana» y botón «ENLACE EN MI BIOGRAFÍA» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
