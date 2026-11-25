---
name: dia-31
description: Crea el video del Día 31 de Tareas Diarias de Sumiago, "Los 12 mensajes" (historia de misterio que resulta hecha con IA e invita a unirse a Sumiago para crear videos así), en móvil 9:16 y PC 16:9, con la voz del narrador, música de misterio que cambia a ritmo, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 31.
---

# Día 31 — "Los 12 mensajes"

Reel vertical de unos 49 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Cuenta una historia de misterio original: Tomás tiene 12 mensajes en el contestador, todos llamados desde su propio teléfono fijo, que llevaba 2 años desconectado. Luego se revela: **"esta historia nunca pasó, la creamos con inteligencia artificial"**, e invita a crear videos así sin grabarse, aprendiendo con las herramientas de Sumiago. Termina con la mascota, el botón "LINK EN MI PERFIL" y el logo de Sumiago.

Estos son los scripts con los que se hizo el video publicado.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-BlackItalic, Inter-Bold, Inter-SemiBold, Inter-SemiBoldItalic, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `mascota-pulgar.png` y `logo-sumiago.png` (también `sumiago-a.png` y `sumiago-c.png`).
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 12 frases; cada una es `[texto para la voz, texto del subtítulo]` (la voz dice "dos y catorce" y el subtítulo muestra "2:14").
- `scripts/voz.py`: voz "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`), sin silencios y 4 % más rápida → `vt/NN.wav`.
- `scripts/tl.py`: pausas entre frases (más largas antes de la revelación: 1 s con estática) y 3,4 s para el logo → `tl.json`, `voice.npy` y `lv.json`.
- `scripts/align.py`: pone cada palabra del subtítulo en su momento real usando las pausas de la voz.
- `scripts/render.py`: las 12 escenas y el cierre (ver tabla).
- `scripts/audio.py`: voz + música de misterio (dron grave y latidos) que cambia a música con ritmo en la revelación + pitidos del contestador, tic-tac, sellos, estática, cinta, pops, whoosh en cada transformación y brillo del logo → `mix.wav`.
- `scripts/pc.py`: versión 1920x1080 (reel a la derecha; a la izquierda "LOS 12 MENSAJES: ESTA HISTORIA NUNCA PASÓ" y cuatro puntos).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-31/scripts/voz.py
python ruta/dia-31/scripts/tl.py
python ruta/dia-31/scripts/align.py
python ruta/dia-31/scripts/audio.py
python ruta/dia-31/scripts/render.py 0 740 a.mp4
python ruta/dia-31/scripts/render.py 740 99999 b.mp4
(echo file a.mp4 & echo file b.mp4) > l.txt        (en Linux/Mac: printf "file a.mp4\nfile b.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-31.mp4
python ruta/dia-31/scripts/pc.py dia-31.mp4 dia-31-pc.mp4
```

Las dos ventanas de `render.py` pueden correr a la vez. Para revisar un momento: `python ruta/dia-31/scripts/render.py still 17.5 20.3`. Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Cuando los bomberos entraron… 12 mensajes nuevos | Contestador sobre la mesa con LED "12" que parpadea, marcadores amarillos 1 y 2, etiqueta "EVIDENCIA · CASO 12", cinta "NO PASAR" y sello "12 NUEVOS" | acercamiento lento; pitido + golpe del sello |
| 1 | Tomás vivía solo desde hacía 9 años | Polaroid de Tomás (dibujo original) en un corcho y calendario "VIVE SOLO 9 AÑOS" | el contestador **se transforma** en la foto; la cámara va al calendario |
| 2 | El primero llegó a las 2:14… «No abras la puerta.» | Cuarto de noche, reloj rojo 2:14, contestador, contador "MENSAJE 01/12" y burbuja del mensaje | la foto se vuelve el reloj; la cámara va del reloj al mensaje; pitido |
| 3 | El segundo… «Ya subió las escaleras.» | Pasillo con escalera, silueta arriba, contador 02/12, reloj 2:15 | el contador pasa de escena; la cámara sigue a la silueta con temblor |
| 4 | Y así, uno cada minuto… durante 12 minutos | Celular con la lista de mensajes que crece, barra de 12 y reloj que avanza | la cámara baja con cada mensaje nuevo; pitidos y tic-tac |
| 5 | Lo raro: todos venían del mismo número | Registro de llamadas: 12 veces "601 555 0142" marcadas en rojo y sello "MISMO NÚMERO" | el celular se vuelve el registro; la cámara recorre la lista |
| 6 | El del teléfono fijo de Tomás | Teléfono de pared con pantalla "TOMÁS" y etiqueta "FIJO · TOMÁS" | el sello se vuelve la pantalla del teléfono |
| 7 | Un teléfono que llevaba 2 años desconectado | El cable se desconecta, polvo y sello "DESCONECTADO · HACE 2 AÑOS" | la cámara se aleja; ruido de cinta + golpe |
| 8 | ¿Quieres saber qué decía el último mensaje? Yo también. | Tarjeta "MENSAJE 12 · 2:25" con play, onda y "?" | la cámara sigue la onda; estática en "Yo también" |
| 9 | Porque esta historia nunca pasó… con inteligencia artificial | Expediente con la foto, el contestador y la voz; sello "ESTA HISTORIA NUNCA PASÓ" y cintas "HECHO CON IA · FICCIÓN" | estática de entrada; la música cambia a ritmo |
| 10 | Si tienes una historia, un canal o un negocio… sin grabarte | Tarjetas "Tu historia", "Tu canal", "Tu negocio", celular "HECHO CON IA" y cámara tachada | la foto del expediente se vuelve la primera tarjeta; la cámara baja al celular; pops |
| 11 | Únete a Sumiago… link de mi perfil | Tarjeta de Sumiago "Gana con Marketing e Inteligencia Artificial", chips VIDEOS VIRALES / VOCES IA / IDEAS, mascota con el pulgar y botón "LINK EN MI PERFIL" | pops encadenados |
| — | Cierre | Pantalla blanca, logo con rebote, ondas, chispas y brillo; "Crea videos con IA" y "LINK EN MI PERFIL" | la tarjeta se transforma en el logo; brillo |

## Estilo y reglas

- Misterio: azul noche, lámpara cálida y rojo Sumiago `#E6262F`; después de la revelación, colores de Sumiago (rojo, negro, blanco y gris).
- Subtítulos arriba a la izquierda, palabra por palabra: cada palabra **sube desde detrás de una máscara** y las palabras clave van en rojo con un subrayado que se dibuja. Hay una sombra arriba para que se lean sobre fondos claros.
- Las 5 técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, un objeto que se transforma en la siguiente escena (`morph` en `render.py`) y animaciones sincronizadas con la voz (`wt()` + `align.py`).
- La historia es ficción y se dice en el video. No prometer ganancias; no escribir «BinanTrader».
