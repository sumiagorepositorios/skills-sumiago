---
name: dia-11
description: Crea el video del Día 11 de Tareas Diarias de Sumiago, "5 herramientas, 1 membresía", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 11.
---

# Día 11 — "5 herramientas, 1 membresía"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro estilo terminal: ventana con '/portada', '/marketplace', '/tienda', '/tareas', '/cursos', contador de pasos 01–05 abajo y títulos grandes blancos y rojos arriba; cierre 'REGÍSTRATE EN SUMIAGO' con flecha. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 9 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-11/scripts/voz.py
python ruta/dia-11/scripts/audio.py
python ruta/dia-11/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-11.mp4
python ruta/dia-11/scripts/pc.py dia-11.mp4 dia-11-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-11/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | Cinco herramientas de Sumiago para ganar desde tu celular, y una sola membresía. | Cifra grande «5» y «herramientas» (1 membresía) |
| 1 | No necesitas experiencia, solo ganas de aprender. | Título «SIN / EXPERIENCIA», icono libro |
| 2 | Herramienta uno: tu portada de negocios, un enlace propio con tu nombre, listo para compartir. | Número 1 grande y tarjeta «Tu portada»: sumiago.com/tu-nombre: un enlace propio listo para compartir. |
| 3 | Herramienta dos: el marketplace. Publica y vende en tu país, mejor que en Facebook. | Número 2 grande y tarjeta «Marketplace»: Publica y vende en tu país. |
| 4 | Herramienta tres: tu propia tienda, con tu logo y tu enlace para WhatsApp. | Número 3 grande y tarjeta «Tu propia tienda»: Con tu logo y tu enlace para compartir por WhatsApp. |
| 5 | Herramienta cuatro: tareas diarias. Cada día, un paso nuevo explicado en video. | Número 4 grande y tarjeta «Tareas diarias»: Cada día, un paso nuevo explicado en video. |
| 6 | Y la cinco, la mejor: los cursos Gana con Marketing, con rangos y premio de sueldo mensual. | Número 5 grande y tarjeta «Gana con Marketing»: Cursos, rangos y premio de Sueldo Mensual. |
| 7 | Cinco herramientas, una sola membresía. | «Una sola membresía»: tarjetas Portada, Marketplace, Tienda, Tareas, Cursos (cada una entra cuando se nombra) |
| 8 | Si quieres aprender y ganar un sueldo mensual, visita el enlace de mi perfil para registrarte en Sumiago. | Logo, «Regístrate en Sumiago», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «5 herramientas, 1 membresía» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
