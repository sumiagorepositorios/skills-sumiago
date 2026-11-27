---
name: dia-51
description: Crea el video del Día 51 de Tareas Diarias de Sumiago, "El mejor precio" (historia ilustrativa: Lucía quiere una bicicleta de $600.000 en el Marketplace de Sumiago, tiene 500 y le da pena regatear; la guarda en favoritos, usa «Hacer oferta», el vendedor contraoferta $550.000, ella acepta, toca «¡Lo quiero!» y cuadran por WhatsApp), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 51.
---

# Día 51 — "El mejor precio"

Reel vertical de unos 59 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Lucía encuentra en el Marketplace de Sumiago una bicicleta perfecta a $600.000. Ella tenía 500 y le daba pena escribirle al vendedor para regatear. Primero la guardó en **favoritos** y le llegó un recordatorio por correo. Luego vio el botón **«Hacer oferta»** y propuso $500.000, sin llamadas incómodas. El vendedor podía aceptarla, rechazarla o proponer otro precio: le respondió con una **contraoferta** de $550.000. Lucía la aceptó, tocó **«¡Lo quiero!»**, le escribió por WhatsApp y cuadraron la entrega. La bicicleta quedó **VENDIDA** y los dos contentos. Cierra: "A veces, el mejor precio… solo hay que proponerlo."

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-BlackItalic, Inter-Bold, Inter-SemiBold, Inter-SemiBoldItalic, Inter-Medium .otf), instalada o en una carpeta `fonts/` dentro de la skill.
- Imágenes en `assets/`: `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free` (cámbialo con `FISH_MODEL`). Voz: "narrador educativo sumiago".

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-51/scripts/voz.py
python ruta/dia-51/scripts/tl.py
python ruta/dia-51/scripts/align.py
python ruta/dia-51/scripts/audio.py
python ruta/dia-51/scripts/render.py 0 600 a.mp4
python ruta/dia-51/scripts/render.py 600 1200 b.mp4
python ruta/dia-51/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-51.mp4
python ruta/dia-51/scripts/pc.py dia-51.mp4 dia-51-pc.mp4
```

Para revisar un momento: `python ruta/dia-51/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Lucía encontró una bicicleta… $600.000 | Lucía junto al teléfono con el anuncio; chip "$ 600.000" | se aleja |
| 1 | Tenía 500 y le daba pena regatear | Chip "TIENE $ 500.000", burbuja tachada "¿Me lo deja en…?", sello "LE DA PENA REGATEAR" | música bajita |
| 2 | La guardó en favoritos… recordatorio por correo | Corazón que se pinta y correo "Lo guardaste en favoritos" | brillo + ding |
| 3 | Un botón que no había notado: «Hacer oferta» | El anuncio grande, el botón brilla y la cámara baja hacia él | pop |
| 4 | Propuso $500.000 sin llamadas incómodas | Formulario "Hacer oferta" que escribe $ 500.000; chips "SIN LLAMADAS INCÓMODAS / SIN EXPLICAR NADA" | teclas |
| 5 | El vendedor podía aceptar, rechazar o proponer otro precio | Tarjeta "Nueva oferta de Lucía" con Aceptar / Rechazar / Contraoferta | pops |
| 6 | Contraoferta: $550.000 | Tarjeta del vendedor "$ 550.000" | ding |
| 7 | Lucía lo pensó y la aceptó | Puntos suspensivos y sello "¡ACEPTADA!" | golpe + brillo |
| 8 | «¡Lo quiero!», WhatsApp y la entrega | Toque en «¡Lo quiero!», mensaje de WhatsApp; chip "CUADRARON LA ENTREGA" | burbuja |
| 9 | La marcó como vendida, los dos contentos | Etiqueta "VENDIDO", Lucía y el vendedor con un corazón | |
| 10 | Publicar, guardar y negociar con ofertas | Tarjetas "Publica tus anuncios / Guarda tus favoritos / Negocia con ofertas"; chip "MARKETPLACE SUMIAGO" | pops |
| 11 | Entra al link de mi perfil… solo hay que proponerlo | Tarjeta "Marketplace Sumiago · Favoritos y ofertas sin pena · HACER OFERTA", mascota y frase final | |
| — | Cierre | Logo con rebote; "Propón tu precio" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): favoritos envía un recordatorio por correo; en «Hacer oferta» el vendedor puede aceptar, rechazar o contraofertar, y el comprador responde igual; «¡Lo quiero!» muestra el WhatsApp del vendedor y le avisa; el vendedor marca el anuncio como VENDIDO.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
