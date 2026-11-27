---
name: dia-52
description: Crea el video del Día 52 de Tareas Diarias de Sumiago, "Info al privado" (historia ilustrativa: doña Rosa publica su apartamento en un grupo con «Info al privado», le llegan 40 mensajes con las mismas preguntas y nadie va a verlo; lo publica en Inmuebles › Alquiler del Marketplace de Sumiago con su ficha completa, comodidades, condiciones y mapa, y ahora le preguntan «¿Puedo ir a verlo el sábado?»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 52.
---

# Día 52 — "Info al privado"

Reel vertical de unos 67 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Doña Rosa arrienda un apartamento: sube una foto a un grupo con «Arriendo apto. Info al privado». Esa noche le llegan 40 mensajes y casi todos preguntan lo mismo (habitaciones, parqueadero, estrato, mascotas). Responde hasta la medianoche y al otro día nadie va a verlo. Su sobrina le dice que lo publique en el Marketplace de Sumiago, en **Inmuebles › Alquiler**. El formulario le pregunta área, habitaciones, baños, parqueadero, estrato y piso; marca balcón y conjunto cerrado, y pone sus condiciones (depósito, contrato mínimo, acepta mascotas). El anuncio queda con su **ficha completa** y la **ubicación en el mapa**. Ahora los mensajes son «¿Puedo ir a verlo el sábado?»; van tres familias y una se queda con el apartamento. Cierra: "Un buen anuncio… responde antes de que pregunten."

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
python ruta/dia-52/scripts/voz.py
python ruta/dia-52/scripts/tl.py
python ruta/dia-52/scripts/align.py
python ruta/dia-52/scripts/audio.py
python ruta/dia-52/scripts/render.py 0 600 a.mp4
python ruta/dia-52/scripts/render.py 600 1200 b.mp4
python ruta/dia-52/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-52.mp4
python ruta/dia-52/scripts/pc.py dia-52.mp4 dia-52-pc.mp4
```

Para revisar un momento: `python ruta/dia-52/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Doña Rosa… «Arriendo apto. Info al privado» | Rosa y el teléfono con la publicación del grupo; sello "INFO AL PRIVADO" | acerca |
| 1 | 40 mensajes, todos preguntaban lo mismo | Noche, chats que llegan y contador hasta 40 | dings, música bajita |
| 2 | ¿Habitaciones? ¿Parqueadero? ¿Estrato? ¿Mascotas? | Burbujas de preguntas que se repiten | burbujas |
| 3 | Hasta la medianoche… nadie fue a verlo | Reloj a las 12; luego el edificio y sello "NADIE FUE A VERLO" | golpe |
| 4 | Publícalo en el Marketplace, Inmuebles, Alquiler | Rosa y su sobrina; chips Marketplace › Inmuebles › Alquiler | pops |
| 5 | Área, habitaciones, baños, parqueadero, estrato y piso | Formulario que se llena campo por campo | clics |
| 6 | Balcón, conjunto cerrado y condiciones | Casillas de comodidades y condiciones (depósito, contrato mínimo, acepta mascotas) | pops |
| 7 | Ficha completa y ubicación en el mapa | Anuncio con la ficha en cuadros y el pin en el mapa; chip "FICHA COMPLETA" | brillo |
| 8 | «¿Puedo ir a verlo el sábado?» | Tres mensajes nuevos; chip "MENSAJES DISTINTOS" | dings |
| 9 | Tres familias, una se quedó | Familias frente al edificio, llave y sello "¡ARRENDADO!" | golpe + brillo |
| 10 | Cada inmueble trae su ficha | Tarjetas Casas / Apartamentos / Locales / Terrenos | pops |
| 11 | Entra al link de mi perfil… antes de que pregunten | Tarjeta "Inmuebles en Sumiago", mascota y frase final | |
| — | Cierre | Logo; "Publica tu inmueble" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): categoría Inmuebles con Casas en venta, Apartamentos en venta, Alquiler, Habitaciones, Locales y oficinas y Terrenos; ficha con área, habitaciones, baños, parqueaderos, estrato, piso, amoblado; en arriendo: depósito, contrato mínimo, acepta mascotas; casillas de comodidades (balcón, conjunto cerrado, cerca a transporte público…); el anuncio muestra la ubicación (ciudad) en un mapa.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
