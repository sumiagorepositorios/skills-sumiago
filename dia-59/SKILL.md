---
name: dia-59
description: Crea el video del Día 59 de Tareas Diarias de Sumiago, "Lo vi tarde" (historia ilustrativa: Hernán vende su nevera, alguien toca «¡Lo quiero!» de noche y él se entera al otro día, cuando el comprador ya compró otra; instala Sumiago en su pantalla de inicio, activa las notificaciones y la próxima vez responde en 2 minutos), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 59.
---

# Día 59 — "Lo vi tarde"

Reel vertical de unos 67 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Hernán vende su nevera en el Marketplace de Sumiago. Un martes en la noche alguien toca «¡Lo quiero!», pero él no lo ve: se entera al otro día y el comprador le responde «Ya compré otra, gracias». Esa tarde, al entrar a Sumiago, le aparece abajo el aviso **«Instala Sumiago»**: toca «Instalar» y el ícono queda en su pantalla de inicio como cualquier aplicación. Luego le sale **«Activa las notificaciones»** (ofertas, mensajes y ventas): toca «Activar» y acepta el permiso. Si deja presionado el ícono tiene **atajos**: «Publicar anuncio», «Para ti» y «Mis ofertas». Una semana después el celular suena: «Alguien quiere tu artículo»; responde en 2 minutos y esa noche la nevera tiene nuevo dueño. En iPhone se instala desde Safari: «Compartir» → «Agregar a pantalla de inicio». Cierra: "A veces, vender… es cuestión de enterarse a tiempo."

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
python ruta/dia-59/scripts/voz.py
python ruta/dia-59/scripts/tl.py
python ruta/dia-59/scripts/align.py
python ruta/dia-59/scripts/audio.py
python ruta/dia-59/scripts/render.py 0 600 a.mp4
python ruta/dia-59/scripts/render.py 600 1200 b.mp4
python ruta/dia-59/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-59.mp4
python ruta/dia-59/scripts/pc.py dia-59.mp4 dia-59-pc.mp4
```

Para revisar un momento: `python ruta/dia-59/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | De noche alguien tocó «¡Lo quiero!» | Cocina de noche con la nevera; el celular se ilumina; chips "MARTES, 9:40 P. M." y "¡LO QUIERO!" | ding suave |
| 1 | No lo vio; se enteró al otro día | Hernán dormido ("NO LO VIO"); en la mañana la notificación de ayer | música bajita |
| 2 | «Ya compré otra, gracias» | Chat de WhatsApp y sello "TARDE" | golpe |
| 3 | El aviso «Instala Sumiago» | Barra negra abajo del Marketplace con el botón «Instalar» | pop |
| 4 | Instalar → ícono en la pantalla de inicio | Toque y pantalla de inicio con el ícono de Sumiago; chip "EN TU PANTALLA DE INICIO" | brillo |
| 5 | «Activa las notificaciones» | Barra con «Activar», campana y chips OFERTAS / MENSAJES / VENTAS | ding |
| 6 | Activar y aceptar el permiso | Ventana "¿Permitir notificaciones de Sumiago?" y Permitir | ding |
| 7 | Atajos al presionar el ícono | Menú con «Publicar anuncio», «Para ti», «Mis ofertas» | brillo |
| 8 | El celular sonó | Pantalla de bloqueo con "Alguien quiere tu artículo" vibrando; chip "UNA SEMANA DESPUÉS" | vibración + ding |
| 9 | Respondió en 2 minutos… nuevo dueño | Reloj, la nevera pasa al comprador; sello "¡NUEVO DUEÑO!" | brillo |
| 10 | Android y iPhone | Tarjetas: botón «Instalar» / Safari «Compartir» → «Agregar a pantalla de inicio» | pops |
| 11 | Entra al link… enterarse a tiempo | Tarjeta "Sumiago en tu celular · Instálala y activa los avisos", mascota y frase final | |
| — | Cierre | Logo; "Instala Sumiago" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): Sumiago es una app instalable (PWA, manifest.php) con atajos «Publicar anuncio», «Para ti» y «Mis ofertas»; assets/pwa.js muestra la barra «Instala Sumiago — Más rápido y con avisos de tus ventas» y luego «Activa las notificaciones — Entérate al instante de ofertas, mensajes y ventas»; en iPhone se instala con Compartir → «Agregar a pantalla de inicio» (y desde ahí se activan los avisos); «¡Lo quiero!» envía la notificación «Alguien quiere tu artículo» (campana + push).
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
