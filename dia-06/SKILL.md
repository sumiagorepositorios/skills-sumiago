---
name: dia-06
description: Crea el video del Día 6 de Tareas Diarias de Sumiago, el tutorial "Cómo registrarte y publicar en el Marketplace" (registro en 3 pasos, código de verificación, panel, publicar un artículo y compartirlo por WhatsApp), con fondo blanco, interfaz animada, subtítulos palabra por palabra y la voz Presentador de Fish Audio, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 6.
---

# Día 6 — "Cómo registrarte y publicar en el Marketplace"

Tutorial vertical 9:16 de 64 s. Empieza con "Oye, te voy a enseñar a vender en Sumiago… es muy sencillo" y muestra la interfaz de Sumiago dibujada y animada sobre fondo blanco con cuadrícula gris: crear la cuenta en 3 pasos, verificar el correo con el código de 6 dígitos, abrir el Marketplace desde el panel, subir las fotos, llenar el formulario, publicar y compartir por WhatsApp con vista previa. Cierra con "1 artículo gratis" y el logo con la mascota. Los subtítulos salen palabra por palabra al ritmo de la voz, con las palabras clave en rojo cursiva. Lleva música lo-fi propia, toques y tecleo. La versión PC pone el video a la derecha y, a la izquierda, el logo, "TUTORIAL PASO A PASO", el título, sumiago.com y la mascota con el pulgar arriba.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Las fuentes ya vienen en `fonts/` (DM Sans y Crimson Text, licencia OFL), y el logo y la mascota en `assets/`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 22 frases con su tiempo (inicio–fin en segundos). Las frases salen de la lista `CAPS` de `scripts/render.py`; si cambias una, cámbiala allí.
- `scripts/voz.py`: una voz por frase con "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`), 4,5 % más aguda, 7 % más rápida y un poco más brillante. "sumiago.com" se lee "sumiago punto com". Deja `vo/t/*.wav` y `vo/dur.json`.
- `scripts/render.py`: dibuja las 6 escenas (`a_intro`, `b_reg`, `c_ver`, `d_panel`, `e_mk`, `f_outro`). Una escena por comando, en paralelo si quieres.
- `scripts/audio.py`: música + efectos + voz → `out/audio.wav`.
- `scripts/montar.py`: une las escenas y pone el audio con compresor y `loudnorm` → video final.
- `scripts/pc.py`: versión 1920x1080.

## Pasos (Windows, en una carpeta de trabajo vacía)

```
set FISH_API_KEY=tu_clave
python ruta\dia-06\scripts\voz.py
python ruta\dia-06\scripts\render.py still 40 prueba.png
set OUTW=1080
set ODIR=out1080
mkdir out1080
python ruta\dia-06\scripts\render.py 0
python ruta\dia-06\scripts\render.py 1
python ruta\dia-06\scripts\render.py 2
python ruta\dia-06\scripts\render.py 3
python ruta\dia-06\scripts\render.py 4
python ruta\dia-06\scripts\render.py 5
python ruta\dia-06\scripts\audio.py
python ruta\dia-06\scripts\montar.py out1080 dia-06.mp4
python ruta\dia-06\scripts\pc.py dia-06.mp4 dia-06-pc.mp4
```

`voz.py` muestra cuánto dura cada voz y cuánto espacio tiene su frase: si una voz no cabe, acorta la frase. Escucha el video entero antes de publicarlo.

## Escenas

| Tiempo | Escena | Lo que se ve |
|--------|--------|--------------|
| 0–5,5 s | Intro | Logo Sumiago, etiqueta "MARKETPLACE" y la mascota de frente |
| 5,5–25,5 s | Registro | Navegador en sumiago.com → "Crear cuenta" → paso 1 (usuario, nombre, apellido, términos) → paso 2 (correo, país Colombia, WhatsApp) → paso 3 (contraseña y confirmación) → botón cargando |
| 25,5–32 s | Verificación | Notificación con el código 482915, las 6 casillas que se llenan y "Verificar correo" |
| 32–37 s | Panel | "Hola, Carlos", menú del panel; toque en "Marketplace" con etiqueta NUEVO |
| 37–55,5 s | Publicar | Formulario "Publicar un artículo": fotos, título "Celular 128 GB como nuevo", Electrónica › Celulares, 180 USD, Usado, descripción, ciudad y país bloqueado; tarjeta "Publicado" y vista previa del enlace en WhatsApp |
| 55,5–64 s | Cierre | Tarjetas de planes ("1 artículo · $0"), logo, sumiago.com y mascota con el pulgar arriba |

## Estilo y reglas

- Fondo `#F7F7F9` con cuadrícula gris suave y brillo rojizo; tarjetas blancas con sombra; rojo Sumiago `#E10600`; texto `#141418`.
- Subtítulos abajo, palabra por palabra; las palabras entre `*asteriscos*` en `CAPS` salen en rojo cursiva subrayadas.
- La línea de tiempo es fija: cada frase tiene su hueco y la voz se coloca al inicio de cada hueco.
- Los datos del ejemplo (Carlos Pérez, celular de $180, Medellín) son inventados.
