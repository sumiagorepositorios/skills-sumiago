---
name: dia-05
description: Crea el video del Día 5 de Tareas Diarias de Sumiago, "Mira lo que no te han dicho: las 4 herramientas" (Portada de negocio, Marketplace, Videos Virales y Gana con Marketing, una sola membresía y cierre "Toca el link de mi perfil"), explosivo, con números que caen, música rápida y efectos, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 5.
---

# Día 5 — "Mira lo que no te han dicho" (las 4 herramientas)

Reel vertical 9:16 (1080x1920, 30 fps, unos 50 s) con fondo blanco y ritmo rápido. Abre con "MIRA LO QUE NO TE HAN DICHO" 👀 y las 4 herramientas que salen disparadas. Cada herramienta entra con un número gigante que cae (1, 2, 3, 4), su color y su fila de título centrada. Luego vienen los rangos, las 4 herramientas juntas con "1 SOLA MEMBRESÍA", la urgencia con "TU COMPETENCIA YA VIENE" y el cierre "TOCA EL LINK DE MI PERFIL · y escríbeme". Cada cambio de escena tiene acercamiento, destello blanco, "whoosh" y golpe. Música hecha por código a 128 bpm. La versión PC pone el reel en el centro sobre su propio fondo difuminado.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente **Poppins Bold** (si no está, usa Arial Bold) y una fuente de emojis a color (Noto Color Emoji o Segoe UI Emoji `seguiemj.ttf`; también puedes copiar `NotoColorEmoji.ttf` a la carpeta de la skill).
- La mascota ya viene en `assets/mascota-frente.png` (1199x1312). En este video **sí** va con los logos de Sumiago.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 9 frases, una por línea (cada línea es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, sin silencios y 0,2 s entre frases. Deja `voice.wav` y `durs.json`.
- `scripts/preparar_mascota.py`: deja `mascot_clean.png` (con logos; solo borra la esquina de arriba a la izquierda).
- `scripts/base.py` y `scripts/portada_base.py`: partes comunes (tiempos por palabra, boca, emojis, sellos, confeti, portada animada, subtítulos).
- `scripts/render.py`: todas las escenas y la lista de efectos.
- `scripts/audio.py`: voz + música (128 bpm, C–Am–F–G) + efectos → `mix.wav`.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-05/scripts/voz.py
python ruta/dia-05/scripts/preparar_mascota.py
python ruta/dia-05/scripts/audio.py
python ruta/dia-05/scripts/render.py test 0.8 3.6 7 12 20 28.5
python ruta/dia-05/scripts/render.py full
python ruta/dia-05/scripts/pc.py dia-05.mp4 dia-05-pc.mp4
```

Revisa `test.jpg` antes del render completo y escucha el video entero antes de publicarlo.

## Escenas (línea del guion → lo que se ve → sonido)

| # | Frase | En pantalla | Sonido |
|---|-------|-------------|--------|
| 0 | ¡Mira lo que no te han dicho! | "MIRA LO QUE / NO TE HAN DICHO" con 👀; 4 cuadros de colores (🔗 🛒 🎬 🎓) que se abren; "4 HERRAMIENTAS · 1 LUGAR"; mascota abajo; la pantalla tiembla | golpe + sello + pops + ding |
| 1 | Uno: Portada de negocio | Número 1 que cae, fila "1 · PORTADA DE NEGOCIO" roja, portada animada y sello "GRATIS" | pops + sello + aplausos |
| 2 | Dos: Marketplace | "2 · MARKETPLACE" naranja, artículo "Tenis deportivos · $35 · Bogotá · Publicado gratis", mensaje "¿Aún está disponible?" y sello "0% COMISIÓN" | pops + mensaje + sello + moneda |
| 3 | Tres: Videos Virales | "3 · VIDEOS VIRALES" morado, teléfono con la mascota y palabras "ESTO SE HACE VIRAL", corazones, cuadro "IA", etiquetas TikTok / Reels / Shorts | teclas + pops |
| 4 | Cuatro: Gana con Marketing | "4 · GANA CON MARKETING" turquesa, tarjetas "Cursos paso a paso", "Tareas diarias de minutos", "Comunidad que te acompaña" | dings |
| 5 | Subes de rango | Rayos dorados, escalera Bronce → Corona que se enciende, "Sueldo" en verde desde Oro, monedas; la mascota sube | ding por rango + monedas |
| 6 | Todo con una sola membresía | Las 4 herramientas en cuadrícula, sello "1 SOLA MEMBRESÍA" y confeti | sellos + aplausos |
| 7 | No esperes a tu competencia | Pantalla que parpadea, ⏰ y 🏃 corriendo de derecha a izquierda; "TU COMPETENCIA YA VIENE" | zumbidos |
| 8 | Toca el link de mi perfil | Flecha roja que rebota, "TOCA EL LINK DE MI PERFIL", "y escríbeme" 💬, mascota, confeti y "Los resultados dependen de tu constancia." | subida + mensaje + aplausos |

## Estilo y reglas

- Fondo blanco; cada herramienta con su color: Portada rojo `#E11E28`, Marketplace naranja `#FF8C00`, Videos Virales morado `#7C3AED`, Gana con Marketing turquesa `#14AAAF`.
- Subtítulos arriba (y = 200), de 4 en 4 palabras, en negro con borde blanco y la palabra que suena en rojo.
- Títulos y textos se achican solos para no salirse de sus cuadros. Barra roja de progreso al pie.
- No dice el precio de la membresía ni montos del Sueldo Mensual. El artículo (tenis de $35 en Bogotá) es un ejemplo inventado.
- Si cambias el guion, conserva 9 líneas en el mismo orden: cada escena y cada efecto dependen de su número de línea.
