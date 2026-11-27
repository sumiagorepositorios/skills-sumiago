---
name: dia-57
description: Crea el video del Día 57 de Tareas Diarias de Sumiago, "Pensé en ti" (historia ilustrativa: Valentina ve en el Marketplace de Sumiago la guitarra que su primo Simón busca hace meses; en vez de una captura que se pierde en WhatsApp usa «Recomiéndalo a un amigo», el recuadro le avisa que escribió mal el correo, lo corrige y a Simón le llega el correo con el artículo), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 57.
---

# Día 57 — "Pensé en ti"

Reel vertical de unos 62 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Valentina ve en el Marketplace de Sumiago una guitarra usada en perfecto estado: justo la que su primo Simón lleva meses buscando. Antes le habría mandado una captura por WhatsApp que se perdería entre stickers y audios. Esta vez baja en el anuncio hasta **«Recomiéndalo a un amigo»**, escribe el nombre y el correo de Simón, pero lo escribe mal y el recuadro le avisa al instante; lo corrige y lo envía. A Simón le llega un correo «Valentina te recomienda» con el artículo, el precio y quién se lo recomienda. Lo abre en el bus, toca «¡Lo quiero!» y esa misma semana tiene la guitarra; esa noche le manda un video tocándola: «Gracias». Valentina no vendió nada: solo pensó en alguien. Cierra: "A veces, lo que alguien busca… lo encuentras tú primero."

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
python ruta/dia-57/scripts/voz.py
python ruta/dia-57/scripts/tl.py
python ruta/dia-57/scripts/align.py
python ruta/dia-57/scripts/audio.py
python ruta/dia-57/scripts/render.py 0 600 a.mp4
python ruta/dia-57/scripts/render.py 600 1200 b.mp4
python ruta/dia-57/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-57.mp4
python ruta/dia-57/scripts/pc.py dia-57.mp4 dia-57-pc.mp4
```

Para revisar un momento: `python ruta/dia-57/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Valentina ve una guitarra en el Marketplace | Valentina y el anuncio de la guitarra; chip "EN PERFECTO ESTADO" | acerca |
| 1 | La que Simón buscaba hace meses | Simón con una nube de pensamiento con la guitarra y "?", calendario; chip "MESES BUSCANDO" | |
| 2 | Una captura… perdida entre stickers y audios | Chat de WhatsApp: la captura sube y la tapan stickers y audios; sello "SE PERDIÓ" | burbujas, música bajita |
| 3 | El recuadro «Recomiéndalo a un amigo» | El anuncio baja hasta el recuadro, que se resalta | brillo |
| 4 | Escribió el nombre y el correo… mal | Se escriben "Simón Rojas" y "simon@gmailcom"; chip "LO ESCRIBIÓ MAL" | teclas |
| 5 | Le avisó, lo corrigió y lo envió | Mensaje rojo "Escribe un correo válido", luego "Correo válido." y el avión de papel | ding + whoosh |
| 6 | El correo «Valentina te recomienda» | Bandeja de correo y el correo abierto con la guitarra, el precio y "Te lo recomienda Valentina" | ding |
| 7 | En el bus tocó «¡Lo quiero!»… esa misma semana | Simón en el bus con el celular; luego con la guitarra; chip "ESA MISMA SEMANA" | brillo |
| 8 | Un video tocándola: «Gracias» | Chat con el video y el mensaje "Gracias" | ding |
| 9 | No vendió nada. Solo pensó en alguien | Valentina, chip "NO VENDIÓ NADA" y corazón "SOLO PENSÓ EN ALGUIEN" | brillo |
| 10 | Recomiéndalo por correo, hasta 5 al día | Tarjeta con sobre; chips "HASTA 5 AL DÍA" y "EN CADA ANUNCIO" | pops |
| 11 | Entra al link… lo encuentras tú primero | Tarjeta "Marketplace Sumiago · Recomiéndalo a un amigo · POR CORREO", mascota y frase final | |
| — | Cierre | Logo; "Piensa en alguien" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): cada anuncio tiene «Recomiéndalo a un amigo» (con sesión iniciada): nombre y correo del amigo; el correo se valida antes de enviar (sintaxis, desechables, dominio que recibe correo) y avisa si está mal; el amigo recibe un correo «[Nombre] te recomienda: …» con el artículo, el precio y quién lo recomienda; máximo 5 recomendaciones por día y no se repite el mismo artículo al mismo correo en la semana.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
