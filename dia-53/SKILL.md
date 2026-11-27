---
name: dia-53
description: Crea el video del Día 53 de Tareas Diarias de Sumiago, "¿Y si me estafas?" (historia ilustrativa: Andrés vende celulares usados y nadie le cree; en el Marketplace de Sumiago su perfil de vendedor muestra correo verificado, WhatsApp, miembro, vendidos y fecha, pide a cada comprador que lo califique y su termómetro de reputación pasa del gris al verde), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 53.
---

# Día 53 — "¿Y si me estafas?"

Reel vertical de unos 65 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Andrés vende celulares usados, buenos y revisados, pero todos le preguntan «¿Y si me estafas?»: nadie lo conocía. Publica en el Marketplace de Sumiago, donde cada anuncio muestra quién es el vendedor: correo verificado, WhatsApp, miembro Sumiago, cuántos ha vendido y desde cuándo está. Al principio dice «Vendedor nuevo, aún sin calificaciones». Después de cada entrega pide «Califícame en Sumiago»: cinco estrellas y «Llegó igualito a las fotos». Venta tras venta, su **termómetro de reputación** pasa del gris al verde y ahora le preguntan «¿Todavía lo tienes?». Cierra: "La confianza no se pide… se gana, una venta a la vez."

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
python ruta/dia-53/scripts/voz.py
python ruta/dia-53/scripts/tl.py
python ruta/dia-53/scripts/align.py
python ruta/dia-53/scripts/audio.py
python ruta/dia-53/scripts/render.py 0 600 a.mp4
python ruta/dia-53/scripts/render.py 600 1200 b.mp4
python ruta/dia-53/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-53.mp4
python ruta/dia-53/scripts/pc.py dia-53.mp4 dia-53-pc.mp4
```

Para revisar un momento: `python ruta/dia-53/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Andrés vende celulares usados | Andrés y su mesa con celulares y cargador; chip "✓ REVISADOS" | se aleja |
| 1 | «¿Y si me estafas?» | Chat con cinco mensajes iguales; chip "SIEMPRE LA MISMA PREGUNTA" | dings, música bajita |
| 2 | Nadie lo conocía… no le creen | Gente gris con signos de pregunta; sello "NO LE CREEN" | golpe |
| 3 | Cada anuncio muestra quién es el vendedor | Anuncio del celular; la cámara baja al recuadro del vendedor | brillo |
| 4 | Correo verificado, WhatsApp, miembro, vendidos, desde | Tarjeta del vendedor con insignias que aparecen una a una | pops |
| 5 | «Vendedor nuevo, aún sin calificaciones» | Termómetro gris resaltado | |
| 6 | «Califícame en Sumiago» | Andrés entrega el celular a la compradora | burbuja |
| 7 | Cinco estrellas y un comentario | Recuadro "¿Ya trataste con este vendedor?" con estrellas y texto | pops + teclas |
| 8 | Del gris… al verde | El termómetro sube hasta "Excelente reputación" | ding + brillo |
| 9 | «¿Todavía lo tienes?» | "¿Es confiable?" tachado y tres mensajes nuevos | dings |
| 10 | Solo califica quien tocó «¡Lo quiero!» | Tarjetas con estrella y termómetro; chip "MARKETPLACE SUMIAGO" | pops |
| 11 | Entra al link… una venta a la vez | Tarjeta "Marketplace Sumiago · Tu reputación, a la vista", mascota y frase final | |
| — | Cierre | Logo; "Vende con confianza" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): el anuncio muestra al vendedor con su termómetro de reputación (5 franjas; "Vendedor nuevo · aún sin calificaciones" si no tiene), insignias Correo verificado, WhatsApp y Miembro Sumiago, cuántos ha vendido y desde cuándo está; solo puede calificar (1 a 5 estrellas + comentario) quien tocó «¡Lo quiero!» en ese anuncio.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
