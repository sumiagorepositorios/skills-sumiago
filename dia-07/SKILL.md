---
name: dia-07
description: Crea el video del Día 7 de Tareas Diarias de Sumiago, la historia "De desempleado a vender en Sumiago" (lo despiden, semanas sin respuesta, la idea de comprar en China con poca inversión, publicar en el Marketplace, primeras ventas y "crea tu tienda al suscribirte"), con la mascota que habla con labios sincronizados, caras tristes y felices, tomas cerca y lejos, un fondo por escena, música y efectos, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 7.
---

# Día 7 — "De desempleado a vender en Sumiago"

Historia vertical 9:16 (1080x1920, 30 fps, unos 55 s) contada por la mascota en primera persona. Empieza con "No te vayas, que de seguro te identificas conmigo…", pasa de la tristeza (despedido, lluvia, semanas sin respuesta, noche sin dormir) a la alegría (la idea de comprar en China, el paquete, la tienda en el Marketplace, los primeros mensajes y ventas) y cierra con "Compra barato, vende en Sumiago · CREA TU TIENDA AL SUSCRIBIRTE · sumiago.com". La mascota mueve la boca al ritmo de la voz, cambia de cara (triste, con lágrimas, feliz), y la cámara alterna tomas cerca y lejos. Cada escena tiene su fondo (oficina, calle con lluvia, cuarto, noche, rayos de luz, puerta con cajas, parque) y un título arriba. Lleva música propia, efectos y subtítulos en una píldora blanca abajo, con la palabra que suena en rojo. La versión PC pone el video a la derecha y, a la izquierda, el logo, el título y la mascota con el pulgar arriba.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy scipy`
- Ya vienen en la skill: las dos poses de la mascota (`assets/sumiago-a.png` boca abierta y `sumiago-c.png` boca cerrada), el logo, la mascota con el pulgar y la fuente Poppins (`fonts/`, licencia OFL).
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 11 frases. Son la lista `LINES` de `scripts/timeline.py`; si cambias una frase, cámbiala allí.
- `scripts/voz.py`: voz oficial de la mascota (`bd35c17b29c54d3e9d2663863a28d212`). Cada frase lleva su velocidad: lenta y triste al inicio (0,92–0,97) y más rápida desde la idea (1,05). Deja `vo/l01.wav` … `vo/l11.wav`.
- `scripts/timeline.py`: pausas entre frases, tiempo de cada palabra (por los silencios de la voz) y boca abierta/cerrada por cuadro → `timeline.json` y `voice.wav`.
- `scripts/faces.py`, `scripts/scenes.py`: caras de la mascota y tiempos de escena (los usan los demás).
- `scripts/render.py`: dibuja el video en 8 partes.
- `scripts/audio.py`: música, efectos y voz → `audio.wav` (música al 20 %, efectos al 32 %, baja más cuando habla).
- `scripts/pc.py`: fondo de la versión PC → `pcbg.png` y `pcmask.png`.
- `scripts/montar.py`: une las partes, pone el audio y arma la versión PC.

## Pasos (Windows, en una carpeta de trabajo vacía)

```
set FISH_API_KEY=tu_clave
python ruta\dia-07\scripts\voz.py
python ruta\dia-07\scripts\timeline.py
python ruta\dia-07\scripts\audio.py
mkdir st out
python ruta\dia-07\scripts\render.py still 1.5 8 20 30 45 52
python ruta\dia-07\scripts\render.py video 0 8
   (repite con 1 8, 2 8 … 7 8; puedes abrir varias ventanas y correrlas a la vez)
python ruta\dia-07\scripts\pc.py
python ruta\dia-07\scripts\montar.py
```

Revisa los cuadros de `st/` antes del render completo y escucha el video entero antes de publicarlo. Si una frase suena cortada, vuelve a generarla.

## Escenas (frase → título → fondo y toma)

| # | Frase | Título | Fondo / lo que pasa |
|---|-------|--------|---------------------|
| 0 | No te vayas… estás despedido | EL DÍA QUE LO / PERDÍ TODO | Primer plano mirando a la cámara; la cámara se abre en la oficina y vuelve a acercarse en "despedido"; papel que cae |
| 1 | Sin trabajo, sin ahorros | SIN TRABAJO / Y SIN AHORROS | Calle con lluvia y trueno, lágrima |
| 2 | Pasaron semanas | SEMANAS / SIN RESPUESTA | Cuarto, hojas de vida volando y calendario "SEMANAS" |
| 3 | Una noche… vi algo en mi celular | HASTA QUE / UNA NOCHE... | Cuarto de noche, luz del celular |
| 4 | ¡Productos de China a precios bajísimos! | ¡LA IDEA QUE / LO CAMBIÓ TODO! | Rayos de luz, cara feliz, productos con precio (audífonos, lámpara, reloj) |
| 5 | Inversión mínima | COMPRÉ EN CHINA / CON POCO DINERO | Tienda mayorista con carrito y "INVERSIÓN MÍNIMA" |
| 6 | Llegó el paquete, lo publiqué | ¡LLEGÓ MI / PAQUETE! | Puerta con cajas "DESDE CHINA" y teléfono con el Marketplace y "PUBLICADO" |
| 7 | Creé mi tienda | MI PROPIA / TIENDA | Teléfono con "Mi Tienda" y sus productos |
| 8 | Un mensaje… ¡vendí! | ¡MIS PRIMERAS / VENTAS! | Notificaciones "¿Todavía está disponible?", "¡Lo quiero!" y confeti |
| 9 | Hoy tengo mi propio negocio | MI PROPIO / NEGOCIO | Parque con sol |
| 10 | Entra a sumiago punto com… | — | Logo, "Compra barato, vende en Sumiago", "CREA TU TIENDA AL SUSCRIBIRTE", sumiago.com y la nota "Historia ilustrativa. Los resultados dependen de tu esfuerzo." |

## Estilo y reglas

- Fondo blanco o claro en todas las escenas; rojo `#DC1826`, texto `#1A1A1E`.
- Títulos en una tarjeta blanca arriba (primera línea oscura, segunda en rojo).
- Es una historia ilustrativa: no promete ingresos.
- Si cambias el guion, conserva 11 frases en el mismo orden: las escenas, las tomas y los efectos dependen del número de frase y de palabras clave ("despedido", "ese", "suscribirte"…).
