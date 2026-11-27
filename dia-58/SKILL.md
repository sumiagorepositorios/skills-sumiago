---
name: dia-58
description: Crea el video del Día 58 de Tareas Diarias de Sumiago, "Pedir ayuda bien" (historia ilustrativa: don Ramiro no logra agregar su método de pago y lo iba a dejar para después; su nieta le dice que use Soporte; abre un Nuevo Ticket con categoría «Métodos de pago», subcategoría, prioridad media y una captura, y le llega «Soporte respondió tu ticket»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 58.
---

# Día 58 — "Pedir ayuda bien"

Reel vertical de unos 63 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Don Ramiro quiere agregar su método de pago en Sumiago y algo no le sale; lo intenta tres veces y piensa «Mejor lo dejo para después». Su nieta le dice que pregunte en Soporte. Entra y toca **«Nuevo Ticket»**: elige la categoría **«Métodos de pago»** y debajo aparece su problema exacto, «No puedo agregar mi método de pago»; escribe qué pasó y marca **prioridad media**; adjunta **imágenes (hasta 5)**: una captura del mensaje que le salía. ¡Ticket creado! Más tarde le llega la notificación **«Soporte respondió tu ticket»**; con la captura lo entienden a la primera y queda listo. Cierra: "Pedir ayuda bien… es la mitad de la solución."

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
python ruta/dia-58/scripts/voz.py
python ruta/dia-58/scripts/tl.py
python ruta/dia-58/scripts/align.py
python ruta/dia-58/scripts/audio.py
python ruta/dia-58/scripts/render.py 0 600 a.mp4
python ruta/dia-58/scripts/render.py 600 1200 b.mp4
python ruta/dia-58/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-58.mp4
python ruta/dia-58/scripts/pc.py dia-58.mp4 dia-58-pc.mp4
```

Para revisar un momento: `python ruta/dia-58/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Algo no le salía | Don Ramiro y el celular en "Métodos de pago" con un aviso; chip "ALGO NO LE SALÍA" | se aleja |
| 1 | Tres veces… lo dejo para después | Tres X rojas y burbuja "Mejor lo dejo para después…"; deja el celular | música bajita |
| 2 | «Abuelo, pregunta en Soporte» | La nieta con su burbuja y unos audífonos de soporte | pop |
| 3 | «Nuevo Ticket» | Pantalla de Soporte con el botón "+ Nuevo Ticket" | toque |
| 4 | Categoría y subcategoría | Tarjetas de categoría; "Métodos de pago" y "No puedo agregar mi método de pago" | ding |
| 5 | Escribió qué pasó y prioridad media | Descripción que se escribe y prioridad Baja / Media / Alta / Urgente | teclas |
| 6 | Adjuntar imágenes, hasta 5 | "Adjuntar imágenes" y cinco casillas; chip "HASTA 5 IMÁGENES" | pops |
| 7 | La captura y ¡Ticket creado! | Flash de captura que va al ticket; tarjeta "¡Ticket creado!" con estado "Abierto" | obturador + ding |
| 8 | «Soporte respondió tu ticket» | Notificación sobre don Ramiro | ding |
| 9 | Lo entendieron a la primera… listo | Hilo del ticket con su captura y la respuesta en pasos; "Solucionado" y sello "¡QUEDÓ LISTO!" | brillo |
| 10 | Categorías, prioridad, imágenes y respuestas guardadas | Cuatro tarjetas; chip "SOPORTE SUMIAGO" | pops |
| 11 | Entra al link… la mitad de la solución | Tarjeta "Soporte Sumiago · Abre tu ticket con capturas", mascota y frase final | |
| — | Cierre | Logo; "Abre tu ticket" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): Soporte en el panel (app/soporte.php) con «Nuevo Ticket»; categorías con subcategorías (p. ej. «Métodos de pago» → «No puedo agregar mi método de pago», «Quiero cambiar mi wallet»); prioridad Baja/Media/Alta/Urgente; hasta 5 imágenes por mensaje; al responder, el usuario recibe la notificación «Soporte respondió tu ticket»; estados Abierto, Pendiente, Respondido, Solucionado, Cerrado. No prometer un tiempo de respuesta concreto.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
