---
name: dia-30
description: Crea el video del Día 30 de Tareas Diarias de Sumiago, "El cliente que siempre pide rebaja", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 30.
---

# Día 30 — "El cliente que siempre pide rebaja"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Diálogo claro de 36 s: una clienta (gorra turquesa) regatea una bicicleta con la mascota Sumiago; tarjetas '$20', '1 abrazo', 'tu tía', 'MARKETPLACE SUMIAGO', teléfono 'Bicicleta de ruta $80 · Mi última oferta', sello '¡ACEPTADA!' y 'PUBLICA GRATIS y que te ofrezcan'; cierre blanco con logo. Voces (probables): narrador para la mascota y 'Voz Femenina Español' para la clienta.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 15 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`), "Voz Femenina Español" (`bfed5c0810a347dbb62e8ccce7f59c48`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-30/scripts/voz.py
python ruta/dia-30/scripts/audio.py
python ruta/dia-30/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-30.mp4
python ruta/dia-30/scripts/pc.py dia-30.mp4 dia-30-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-30/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿En cuánto me dejas la bici? | Habla el segundo personaje (burbuja) |
| 1 | Ochenta dólares. | Habla la mascota (burbuja) |
| 2 | ¿Ochenta? Te doy veinte. | Habla el segundo personaje (burbuja) |
| 3 | ¿Veinte? Eso no alcanza ni para las llantas. | Habla la mascota (burbuja) |
| 4 | Bueno… veinte y un abrazo. | Habla el segundo personaje (burbuja) |
| 5 | Con ese abrazo ya me estás debiendo. | Habla la mascota (burbuja) |
| 6 | Veinte, un abrazo y te recomiendo con mi tía. | Habla el segundo personaje (burbuja) |
| 7 | ¿Tu tía? ¿Y ella cuánto ofrece? | Habla la mascota (burbuja) |
| 8 | Diez. | Habla el segundo personaje (burbuja) |
| 9 | ¡Basta de discutir! Mejor publico en el marketplace de Sumiago. | Título «MARKETPLACE / SUMIAGO» con «sin discutir por rebajas» y el logo |
| 10 | ¿Y entonces cómo te ofrezco? | Habla el segundo personaje (burbuja) |
| 11 | Fácil: tú pones tu última oferta y yo solo la acepto o no. | Teléfono «Bicicleta de ruta · $80» con Mi última oferta, Aceptar, Rechazar; la cámara sigue la fila nueva |
| 12 | Mi última oferta: setenta. | Habla el segundo personaje (burbuja) |
| 13 | ¡Aceptada! | Cifra grande «¡ACEPTADA!» y «$70 · Bicicleta de ruta» |
| 14 | Publica gratis en el marketplace de Sumiago y deja de discutir por rebajas. | Logo, «Publica gratis y que te ofrezcan», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Publica gratis en el Marketplace» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
