---
name: dia-16
description: Crea el video del Día 16 de Tareas Diarias de Sumiago, "Gana comisiones compartiendo anuncios (Dropshipping)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 16.
---

# Día 16 — "Gana comisiones compartiendo anuncios (Dropshipping)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con la mascota abajo y títulos arriba ('Nadie ve tu anuncio', 'Activa Dropshipping', 'Toca Gana comisión', 'Compártelo en tus redes', 'Tu enlace funcionó', 'Seamos honestos', '¿Eres vendedor?'); pantallas del anuncio 'Celular Samsung A54' y contador de visitas. Voz: narrador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 8 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-16/scripts/voz.py
python ruta/dia-16/scripts/audio.py
python ruta/dia-16/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-16.mp4
python ruta/dia-16/scripts/pc.py dia-16.mp4 dia-16-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-16/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Sabías que puedes ganar comisiones vendiendo artículos de otras personas, sin invertir un peso? | Título «¿Ganar vendiendo / cosas que NO son tuyas?», icono dinero |
| 1 | Muchos venden su carro, su celular o sus productos, pero nadie ve su anuncio. | Cifra grande «0» y «visitas al anuncio» (Vendo celular, buen estado) |
| 2 | En el marketplace de Sumiago, el vendedor activa Dropshipping y ofrece un porcentaje de comisión a quien le ayude a vender. | Teléfono «Publicar artículo» con Celular Samsung A54, $ 950.000, ☑ Dropshipping, Comisión: 9 %; la cámara sigue la fila nueva |
| 3 | Tú entras al anuncio, tocas el botón verde «Gana comisión» y se copia tu enlace personal. | Teléfono «Celular Samsung A54» con $ 950.000, Tu enlace #14 copiado; botón «Gana comisión 10 %»; la cámara sigue la fila nueva |
| 4 | Compártelo en tus estados de WhatsApp, grupos de Facebook y Telegram. Entre más lo compartas, a más personas llegas. | «Compártelo»: tarjetas WhatsApp, Facebook, Telegram (cada una entra cuando se nombra) |
| 5 | Cuando alguien llega por tu enlace y contacta al vendedor, Sumiago le avisa que fuiste tú quien le ayudó, y a ti te llegan los datos del vendedor. | «Tu enlace funcionó»: tarjetas Alguien llegó por ti, Aviso al vendedor, Datos del vendedor (cada una entra cuando se nombra) |
| 6 | Ojo: la comisión es un acuerdo voluntario entre tú y el vendedor. Sumiago no la cobra ni la garantiza, pero le pedimos al vendedor ser honesto y recompensarte. | Título «Seamos / honestos» con «Comisión voluntaria entre usuarios», icono escudo |
| 7 | Y si tú eres el vendedor, activa la comisión y deja que cientos de personas compartan tu anuncio por ti. Regístrate gratis en Sumiago. | Logo, «¿Eres vendedor? Activa la comisión», mascota con el pulgar y botón «REGÍSTRATE GRATIS» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «sumiago.com/marketplace» y botón «REGÍSTRATE GRATIS» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
