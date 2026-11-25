---
name: dia-27
description: Crea el video del Día 27 de Tareas Diarias de Sumiago, "Negocio simple: grabado láser personalizado (3 pasos)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 27.
---

# Día 27 — "Negocio simple: grabado láser personalizado (3 pasos)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con fondo de puntos: bolsa de dinero, 'PASO 1 GRABADORA LÁSER' con etiqueta '$300–$800', laptop conectada y casita, 'PASO 2 PRODUCTOS EN BLANCO' (termo, billetera, bolígrafo, llavero con precios), robot 'DISEÑOS CON IA', 'ASÍ FUNCIONA' en 4 pasos, 'PASO 3 VENDE AL TRIPLE' con flechas, teléfono con 'Termo personalizado $6 USD' en TikTok y Marketplace y cierre '¿QUIERES HACER VIDEOS ASÍ? REGÍSTRATE EN SUMIAGO'. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 11 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-27/scripts/voz.py
python ruta/dia-27/scripts/audio.py
python ruta/dia-27/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-27.mp4
python ruta/dia-27/scripts/pc.py dia-27.mp4 dia-27-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-27/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | Hay negocios que parecen sencillos, pero dejan muy buena plata. Guarda este video y pon atención. | Título «NEGOCIOS SIMPLES / QUE DEJAN PLATA» con «Guarda este video», icono dinero |
| 1 | Paso 1: consigue una grabadora láser. No la más cara: una china de 300 a 800 dólares funciona perfecto. | Número 1 grande y tarjeta «Grabadora láser»: No la más cara: una de 300 a 800 dólares funciona perfecto. |
| 2 | La conectas a tu computador y tu cuarto se convierte en una pequeña fábrica. | Título «Tu cuarto, / una pequeña fábrica», icono tienda |
| 3 | Paso 2: compra productos en blanco. Termos, billeteras, bolígrafos y llaveros de 2 a 5 dólares, y te llegan a la casa. | «Productos en blanco»: tarjetas Termo $2, Billetera $5, Bolígrafo $1, Llavero $2 (cada una entra cuando se nombra) |
| 4 | Con inteligencia artificial creas frases y nombres antes de que te los pidan: uno para el Día del Padre, otro para San Valentín. | «Diseños con IA»: tarjetas Papá, mi héroe, Te amo (cada una entra cuando se nombra) |
| 5 | Con esos diseños tomas tus fotos de muestra y grabas solo por encargo: un nombre, una inicial, una fecha. | Título «Fotos de muestra / solo por encargo», icono foto |
| 6 | El cliente te escribe el nombre, tú lo grabas, lo empacas y la transportadora se lo lleva hasta su casa. | Teléfono «Así funciona» con Te escribe el nombre, Tú lo grabas, Lo empacas, Llega a su casa; la cámara sigue la fila nueva |
| 7 | Paso 3: lo vendes al triple. El termo de 2 en 6, la billetera de 5 en 15, el bolígrafo de 1 en 3. | «Vende al triple»: barras Termo $2 → $6, Billetera $5 → $15, Bolígrafo $1 → $3 |
| 8 | Lo publicas en TikTok y en el marketplace de Sumiago, para bodas, grados y fechas especiales. | Teléfono «Marketplace Sumiago» con Termo personalizado · $6, Bodas, Grados, Fechas especiales; la cámara sigue la fila nueva |
| 9 | Empieza con un solo producto. | Cifra grande «1» y «solo producto para empezar» |
| 10 | Y si quieres hacer videos como este, regístrate en Sumiago y gana comisiones por recomendar la oportunidad. | Logo, «¿Quieres hacer videos así?», mascota con el pulgar y botón «REGÍSTRATE EN SUMIAGO» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Aprende a crear videos así» y botón «SUMIAGO.COM» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
