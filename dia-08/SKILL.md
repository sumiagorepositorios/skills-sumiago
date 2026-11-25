---
name: dia-08
description: Crea el video del Día 8 de Tareas Diarias de Sumiago, "6 tips para comprar seguro en el Marketplace", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 8.
---

# Día 8 — "6 tips para comprar seguro en el Marketplace"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con la mascota de Sumiago abajo, tarjetas 'TIP 1…6' arriba y pantallas del Marketplace (perfil de 'Laura M.' con estrellas, correo verificado, mapa, chat de WhatsApp). Voz: narrador (probable).

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
python ruta/dia-08/scripts/voz.py
python ruta/dia-08/scripts/audio.py
python ruta/dia-08/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-08.mp4
python ruta/dia-08/scripts/pc.py dia-08.mp4 dia-08-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-08/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¡Alto! Antes de comprar por internet, mira esto o te pueden estafar. | Título «¡NO TE DEJES / ESTAFAR!», icono alerta |
| 1 | Te voy a dar seis tips para comprar seguro en el marketplace de Sumiago. | «6 tips»: tarjetas Reputación, Ubicación, Preguntas, En persona, Revisa, Muy barato (cada una entra cuando se nombra) |
| 2 | Uno: revisa la reputación del vendedor. | Número 1 grande y tarjeta «Reputación»: Revisa el perfil del vendedor antes de escribirle. |
| 3 | Mira sus estrellas, cuántos artículos ha vendido y si tiene el correo verificado. | tarjetas 4.8 estrellas, 15 vendidos, Correo verificado (cada una entra cuando se nombra) |
| 4 | Dos: mira la ubicación, que el vendedor esté en tu misma ciudad, cerca de tu zona. | Número 2 grande y tarjeta «Ubicación»: Que el vendedor esté en tu misma ciudad, cerca de tu zona. |
| 5 | Tres: escríbele por WhatsApp y hazle varias preguntas del artículo. Pídele más fotos y un video reciente. | Número 3 grande y tarjeta «Pregunta por WhatsApp»: Haz varias preguntas del artículo y pide más fotos y un video reciente. |
| 6 | Cuatro: dile que estás en su misma ciudad y acuerden verse en persona, en un lugar público y de día. | Número 4 grande y tarjeta «Verse en persona»: En un lugar público y de día. |
| 7 | Cinco: revisa el producto antes de pagar. Pruébalo bien y nunca envíes anticipos a desconocidos. | Número 5 grande y tarjeta «Revisa antes de pagar»: Enciende, prueba y compara con las fotos. Nunca envíes anticipos a desconocidos. |
| 8 | Seis: desconfía de los precios demasiado bajos y de las prisas. Si algo te parece raro, repórtalo en Sumiago. | Número 6 grande y tarjeta «Ojo con lo muy barato»: Precios demasiado bajos y prisas son señal de alerta. Repórtalo en Sumiago. |
| 9 | Con estos seis tips compras tranquilo y sin engaño. | Título «¡AHORA COMPRAS / SIN ENGAÑOS!», icono escudo |
| 10 | No te pierdas esta gran oportunidad: entra y regístrate en Sumiago si no lo has hecho. | Logo, «Compra seguro en Sumiago», mascota con el pulgar y botón «REGÍSTRATE EN SUMIAGO» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Compra seguro en Sumiago» y botón «REGÍSTRATE · LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
