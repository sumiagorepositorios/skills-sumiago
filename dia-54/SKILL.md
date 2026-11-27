---
name: dia-54
description: Crea el video del Día 54 de Tareas Diarias de Sumiago, "Lo que a ti te sobra" (historia ilustrativa: doña Inés quiere regalar la cuna de su nieto; en un grupo la piden para revenderla; en el Marketplace de Sumiago la publica en la categoría «Regalo», sin precio, sale primero al ordenar por precio y una pareja de su ciudad toca «¡Lo quiero!»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 54.
---

# Día 54 — "Lo que a ti te sobra"

Reel vertical de unos 60 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Doña Inés tiene la cuna de su nieto guardada hace tres años y una bolsa de ropita. No quiere venderla: quiere regalarla a quien de verdad la necesite. En un grupo le llueven comentarios («Yo», «Info», «¿La mandas?») y varios la quieren para revenderla. La publica en el Marketplace de Sumiago, en la categoría **«Regalo»**: no pone precio y el anuncio dice «Regalo» donde va el precio; al **ordenar por precio**, los regalos salen primero. Una pareja de su ciudad toca «¡Lo quiero!», a ella le llega el aviso y le escriben por WhatsApp: van a tener una bebé y no tenían dónde acostarla. El sábado pasan por la cuna y doña Inés les regala también la ropita. Cierra: "Lo que a ti te sobra… a otro le hace falta."

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
python ruta/dia-54/scripts/voz.py
python ruta/dia-54/scripts/tl.py
python ruta/dia-54/scripts/align.py
python ruta/dia-54/scripts/audio.py
python ruta/dia-54/scripts/render.py 0 600 a.mp4
python ruta/dia-54/scripts/render.py 600 1200 b.mp4
python ruta/dia-54/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-54.mp4
python ruta/dia-54/scripts/pc.py dia-54.mp4 dia-54-pc.mp4
```

Para revisar un momento: `python ruta/dia-54/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | La cuna guardada hace tres años | Cuarto de atrás con polvo, la cuna y la bolsa de ropita; chip "3 AÑOS GUARDADA" | se aleja |
| 1 | No la quería vender: regalarla | "$ Vender" tachado, corazón y chips "REGALARLA / A QUIEN DE VERDAD LA NECESITE" | |
| 2 | Le llovieron comentarios | Publicación del grupo y comentarios «Yo», «Info», «¿La mandas?»; chip "+87 COMENTARIOS" | burbujas, música bajita |
| 3 | Para revenderla | Gente gris con signos de pesos; sello "PARA REVENDERLA" | golpe |
| 4 | Marketplace, categoría Regalo | Tarjeta "Categoría" con un regalo y "Regalo (gratis)" | brillo |
| 5 | Sin precio; el anuncio dice «Regalo» | Formulario con precio desactivado y sello "SIN PRECIO"; luego el anuncio con "Regalo" resaltado | ding |
| 6 | Al ordenar por precio, los regalos primero | Lista que se reordena con "Menor precio" y la cuna sube al primer lugar | |
| 7 | Una pareja de su ciudad tocó «¡Lo quiero!» | Botón, aviso "Alguien quiere tu cuna"; chip "MISMA CIUDAD" | pop + ding |
| 8 | El mensaje por WhatsApp | Chat de WhatsApp con el mensaje y "¡Es suya!" | burbujas |
| 9 | El sábado… también la ropita | La pareja lleva la cuna y doña Inés les da la bolsa; corazones | brillo |
| 10 | Vender, comprar… y regalar | Tarjetas Vender / Comprar / Regalar | pops |
| 11 | Entra al link… a otro le hace falta | Tarjeta "Marketplace Sumiago · Regala lo que ya no usas · CATEGORÍA REGALO", mascota y frase final | |
| — | Cierre | Logo; "Regala lo que no usas" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): la categoría «Regalo (gratis)» desactiva el campo de precio y el anuncio muestra «Regalo»; al ordenar por menor precio, los regalos aparecen primero; «¡Lo quiero!» avisa al dueño y muestra su WhatsApp; el anuncio muestra la ciudad.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
