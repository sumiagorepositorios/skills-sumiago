---
name: dia-04
description: Crea el video del Día 4 de Tareas Diarias de Sumiago, "Marketplace Sumiago" (diálogo entre Sofi y Sumiago: publicación rechazada, problemas de vender en grupos, Marketplace gratis, 0 % de comisión y sello VENDIDO), con dos voces, labios sincronizados, cámara que se acerca y aleja, música y efectos, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 4.
---

# Día 4 — "Marketplace Sumiago" (Sofi y Sumiago)

Reel vertical 9:16 (1080x1920, 30 fps, unos 49 s) con fondo blanco. Es un diálogo: Sofi (personaje de bloques con ropa turquesa, pelo largo y sin marcas) cuenta que le rechazaron la publicación de su bicicleta y Sumiago le explica el Marketplace. Cada uno mueve la boca solo cuando habla y al ritmo de su voz, los dos parpadean, y la cámara se acerca a la cara del que habla o se aleja para las explicaciones, con "whoosh" y destello blanco en cada cambio. Música hecha por código (116 bpm) y efectos. La versión PC pone el reel en el centro sobre su propio fondo difuminado.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente **Poppins Bold** (si no está, usa Arial Bold) y una fuente de emojis a color (Noto Color Emoji o Segoe UI Emoji `seguiemj.ttf`; también puedes copiar `NotoColorEmoji.ttf` a la carpeta de la skill).
- La mascota de frente ya viene en `assets/mascota-frente.png` (1199x1312). En este video va **sin logos**.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `dialogo.txt`: las 13 frases con quién habla (`W|` = Sofi, `S|` = Sumiago).
- `guion.txt`: las mismas 13 frases sin el hablante (lo usan los subtítulos). Si cambias una frase, cámbiala en los dos.
- `scripts/voz.py`: voces de Fish Audio. Sumiago `bd35c17b29c54d3e9d2663863a28d212` (1,5 semitonos más aguda); Sofi `bfed5c0810a347dbb62e8ccce7f59c48` "Voz Femenina Español" (5 % más rápida); 0,22 s entre frases. Deja `voice.wav`, `durs.json` y `speakers.json`.
- `scripts/limpiar_mascota.py`: quita logos y textos de la gorra, el pecho y los zapatos → `mascot_clean.png`.
- `scripts/crear_sofi.py`: crea a Sofi desde `mascot_clean.png` → `sofi.png`.
- `scripts/base.py` y `scripts/portada_base.py`: partes comunes (tiempos por palabra, emojis, sellos, confeti, píldoras).
- `scripts/render.py`: personajes, cámara, escenas, subtítulos con el nombre del que habla y lista de efectos.
- `scripts/audio.py`: voces + música + efectos → `mix.wav`.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-04/scripts/voz.py
python ruta/dia-04/scripts/limpiar_mascota.py ruta/dia-04/assets/mascota-frente.png
python ruta/dia-04/scripts/crear_sofi.py
python ruta/dia-04/scripts/audio.py
python ruta/dia-04/scripts/render.py test 1 3.5 6 10.5 15 19
python ruta/dia-04/scripts/render.py full
python ruta/dia-04/scripts/pc.py dia-04.mp4 dia-04-pc.mp4
```

Revisa `test.jpg` antes del render completo y escucha el video entero antes de publicarlo (voces y sincronía de la boca).

## Escenas (frase → cámara → lo que se ve)

| # | Quién | Cámara | En pantalla |
|---|-------|--------|-------------|
| 0 | Sofi: ¡Otra vez me rechazaron! | cerca de Sofi | Teléfono con "Bicicleta en venta", destello rojo, Sofi tiembla y sello "RECHAZADA" |
| 1 | Sumiago: ¿Qué pasó, Sofi? | Sumiago | — |
| 2 | Sofi: se pierde entre miles | Sofi | Lista de publicaciones que baja y "+10.000 publicaciones" |
| 3 | Sofi: ¿precio?… y desaparece | cerca de Sofi | Chat: "¿precio?", "$80, ¿te interesa?", "Visto" y "Se desconectó…" |
| 4 | Sofi: perfiles falsos, fotos robadas, comisión | los dos | Tarjetas rojas "Perfiles falsos", "Fotos robadas", "Comisión por venta" |
| 5 | Sumiago: para eso está el Marketplace | cerca de Sumiago | Cartel "MARKETPLACE SUMIAGO" |
| 6 | Sumiago: primer artículo gratis | los dos | Teléfono "Bicicleta de ruta · $80 · Maracaibo", "GRATIS", "fotos reales" y sello "VISIBLE YA" |
| 7 | Sumiago: te escriben a WhatsApp | Sumiago | Chat de WhatsApp con el artículo y "directo a tu chat" |
| 8 | Sofi: ¿cuánto me cobran? | cerca de Sofi | 🤔 |
| 9 | Sumiago: cero por ciento | cerca de Sumiago (salta) | "0%" gigante, "de comisión", "todo es para ti" |
| 10 | Sumiago: reputación, fotos copiadas, cerca de ti | los dos | Tarjetas turquesa con check: Reputación, Fotos verificadas, Cerca de ti |
| 11 | Sofi: ¡Ya vendí mi bicicleta! | Sofi (salta) | "Nuevo mensaje · ¡Te la compro!", sello "VENDIDO" y confeti |
| 12 | Sumiago: publica gratis, link en mi perfil | los dos | "PUBLICA GRATIS HOY", "sumiago.com/marketplace", "link en mi perfil" |

## Estilo y reglas

- Fondo blanco con dos brillos suaves detrás de los personajes (turquesa para Sofi, rojo para Sumiago).
- Subtítulos arriba (y = 190) con una etiqueta del que habla; la palabra que suena va en turquesa (Sofi) o rojo (Sumiago).
- Barra roja de progreso al pie. La venta de la bicicleta ($80, Maracaibo) es un ejemplo inventado.
- Si cambias el diálogo, conserva 13 frases en el mismo orden y con el mismo hablante: la cámara, las escenas y los efectos dependen del número de frase.
