---
name: dia-02
description: Crea el video del Día 2 de Tareas Diarias de Sumiago, "¿Cuántas horas pierdes en redes?" (más de dos horas al día, un mes al año mirando la vida de otros, sueldo exponencial de ejemplo y 3 cambios: pasar de consumir a crear, usar el celular como herramienta y darle una hora al día; contenido listo y piloto semiautomático; cierre "Comenta SUMIAGO"), con la mascota que habla, subtítulos en recuadro oscuro, música y efectos, en móvil 9:16 y PC 16:9 con diseño propio. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 2.
---

# Día 2 — "¿Cuántas horas pierdes en redes?"

Reel de unos 60 s a 30 fps en dos formatos hechos con el mismo código:

- **Móvil 9:16 (1080x1920):** los gráficos arriba, la mascota grande abajo dentro de un círculo y el subtítulo en un recuadro oscuro sobre ella.
- **PC 16:9 (1920x1080):** diseño propio, no es el móvil estirado: gráficos a la izquierda, la mascota a la derecha en su círculo y el subtítulo abajo al centro.

Cada escena tiene su fondo de color (crema, rosado, gris, negro o rojo). A partir del primer cambio aparece arriba a la izquierda el indicador de los 3 cambios (1 Crear · 2 Herramienta · 3 Una hora) con check verde en los que ya pasaron. Lleva música hecha por código (sin derechos de autor), efectos de sonido, un acercamiento corto al cambiar de escena y una barra roja de progreso abajo.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy opencv-python-headless`
- La fuente **Poppins Bold** ya viene en `fonts/` (licencia OFL); si la tienes instalada, usa esa.
- Las imágenes ya vienen en `assets/`: `mascota-frente.png` (la que habla), `mascota-lado.png` (de tres cuartos, con la mochila), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 23 frases, una por línea (cada línea es una escena). Las palabras entre `*asteriscos*` salen en **rojo** en el subtítulo; la voz no las lee.
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, sin silencios y 0,25 s entre frases. Deja `voice.wav` y `durs.json`.
- `scripts/preparar_mascota.py`: deja `mascot_clean.png` (la mascota de frente sin la marca de agua).
- `scripts/base.py`: parte común (tiempos por palabra, boca según el volumen de la voz y parpadeo).
- `scripts/render.py`: fondos, poses de la mascota, gráficos de cada escena, indicador de los 3 cambios, subtítulos, los dos formatos y la lista de efectos.
- `scripts/audio.py`: voz + música (124 bpm, C–Am–F–G) que baja cuando habla la voz + efectos → `mix.wav`.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-02/scripts/voz.py
python ruta/dia-02/scripts/preparar_mascota.py
python ruta/dia-02/scripts/audio.py
python ruta/dia-02/scripts/render.py test movil 1 5 12 20 35 55
python ruta/dia-02/scripts/render.py test pc 1 5 12 20 35 55
python ruta/dia-02/scripts/render.py full movil
python ruta/dia-02/scripts/render.py full pc
```

Salen `dia-02.mp4` (móvil) y `dia-02-pc.mp4` (PC). `render.py test` deja `test.jpg` con cuadros de muestra para revisar antes del render completo. Escucha el video completo antes de publicarlo.

## Escenas (línea del guion → fondo y pose → lo que se ve)

| # | Frase | Fondo · mascota | En pantalla |
|---|-------|-----------------|-------------|
| 0 | ¿Sabes cuántas horas pierdes al día en redes sociales? | crema · frente | "¿Cuántas horas / pierdes" en recuadros rojos + "en redes?"; teléfono con publicaciones que se deslizan |
| 1 | En promedio, más de dos horas | rosado · frente | Reloj que gira rápido y "+2 HORAS AL DÍA" |
| 2 | Eso es más de un mes completo al año… | gris · lado | Calendario "AL AÑO · +1 MES · en redes sociales" |
| 3 | mirando la vida de otros | negro · lado | Teléfono que se desliza rápido y corazones que suben |
| 4 | mientras tú miras, otros están ganando dinero… | gris · lado | Reloj de arena y luego avisos "Nuevo ingreso + $ / + $$ / + $$$" |
| 5 | Y lo mejor: están creando su propio sueldo exponencial… | crema · pulgar | Tarjeta "Ejemplo: sueldo mes a mes" con barras $20 → $320 y la nota "Ejemplo ilustrativo" |
| 6 | Te muestro tres cambios, en orden | rosado · frente | Cuadros 1, 2 y 3 |
| 7 | El primero: pasa de consumir a crear | crema · frente | "Consumir" ✗ y "Crear" ✓ (indicador en 1 Crear) |
| 8 | El que solo desliza, paga con su tiempo | rosado · lado | Teléfono que se desliza, reloj y "- tiempo" |
| 9 | El que publica, cobra por su atención | gris · frente | Teléfono con botón "Publicar" y monedas |
| 10 | El segundo: usa tu celular como herramienta | crema · frente | Teléfono y una llave; "HERRAMIENTA" (indicador en 2) |
| 11 | Con el mismo teléfono puedes atender prospectos y cerrar ventas | rosado · frente | Mensaje "Hola, ¿cómo funciona?" y luego "Venta cerrada" ✓ |
| 12 | Y el tercero, el más importante: dale una hora al día | rojo · frente | Gran "3" con puntos dorados y luego reloj "1 hora al día" (indicador en 3) |
| 13 | Solo una hora enfocada en construir tu ingreso por internet | gris · frente | Tarjeta "Tu ingreso" con barras que suben |
| 14 | Fíjate: ahora mismo estás en redes | negro · lado | Teléfono con un pin rojo y "AQUÍ" (los 3 con check) |
| 15 | La diferencia es si solo miras… o si empiezas a ganar | gris · lado | Ojo "solo miras" y luego flecha blanca hacia arriba "empiezas a ganar" |
| 16 | En Sumiago te damos el contenido listo cada día | crema · frente | Logo y "DÍA 1 / DÍA 2 / DÍA 3" |
| 17 | y el piloto semiautomático te trae prospectos interesados | rosado · frente | Teléfono con avisos "Nuevo prospecto" |
| 18 | Así que la próxima vez que abras una red social | gris · lado | Teléfono con publicaciones |
| 19 | pregúntate: ¿estoy perdiendo tiempo… | negro · lado | Reloj de arena y "perdiendo tiempo" |
| 20 | o estoy ganando dinero? | rojo · frente | Monedas que suben |
| 21 | Comenta SUMIAGO | crema · pulgar | Logo y caja de comentario donde se escribe "SUMIAGO" |
| 22 | y te envío el enlace para empezar hoy | rosado · pulgar | Logo y tarjeta "Te envío el enlace · EMPEZAR HOY" |

## Estilo y reglas

- Colores: crema `#FBF5EE`, rosado `#F9DEDE`, gris `#ECECF1`, negro `#1E1E24`, rojo `#E20812`; rojo Sumiago para los acentos y verde para los checks.
- Subtítulo en recuadro oscuro con esquinas redondeadas, en trozos de hasta unas 44 letras (máximo 2 líneas), cortando en la puntuación; las palabras clave en rojo.
- La mascota de lado no se voltea en espejo (el logo de la gorra se leería al revés).
- El sueldo de ejemplo ($20 → $320) siempre lleva la nota "Ejemplo ilustrativo: los resultados dependen de cada persona". No dice el precio de la membresía.
- Si cambias el guion, conserva 23 líneas en el mismo orden: cada escena, su fondo y cada efecto dependen de su número de línea.
