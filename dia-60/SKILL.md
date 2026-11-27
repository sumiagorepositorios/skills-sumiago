---
name: dia-60
description: Crea el video del Día 60 de Tareas Diarias de Sumiago, "Deja de buscar" (historia ilustrativa: Paola ama las plantas pero en las páginas de ventas solo ve carros, celulares y sofás; en el Marketplace de Sumiago guarda plantas en favoritos, abre anuncios de materas y la pestaña «Para ti» se llena de lo que le gusta), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 60.
---

# Día 60 — "Deja de buscar"

Reel vertical de unos 62 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Paola ama las plantas, pero en las páginas de ventas ve de todo (carros, celulares, sofás) y pasa 10 minutos bajando sin encontrar una matera. En el Marketplace de Sumiago guarda en favoritos una monstera y una suculenta, y abre un par de anuncios de materas. Al otro día entra a la pestaña **«Para ti»** y está llena de lo que le gusta: plantas, materas, tierra abonada y hasta un estante. «Para ti» aprende de lo que miras, de tus favoritos, de lo que te interesa y de tus ofertas; muestra anuncios de tu mismo país y nunca los tuyos; lo que ya viste muchas veces baja un poco para darle espacio a lo nuevo. Esa semana compra dos materas de barro sin buscarlas. La pestaña es para usuarios registrados: entre más la usas, mejor te conoce. Cierra: "Deja de buscar… y empieza a encontrar."

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
python ruta/dia-60/scripts/voz.py
python ruta/dia-60/scripts/tl.py
python ruta/dia-60/scripts/align.py
python ruta/dia-60/scripts/audio.py
python ruta/dia-60/scripts/render.py 0 600 a.mp4
python ruta/dia-60/scripts/render.py 600 1200 b.mp4
python ruta/dia-60/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-60.mp4
python ruta/dia-60/scripts/pc.py dia-60.mp4 dia-60-pc.mp4
```

Para revisar un momento: `python ruta/dia-60/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Paola ama las plantas… ve de todo | Paola con su monstera ("AMA LAS PLANTAS"); luego un feed de carros, celulares y sofás | se aleja |
| 1 | 10 minutos bajando… ni una matera | Feed que baja rápido, reloj "10 MIN" y sello "NI UNA MATERA" | música bajita |
| 2 | Favoritos: monstera y suculenta | Dos tarjetas y los corazones; chip "GUARDADAS EN FAVORITOS" | pops |
| 3 | Abrió anuncios de materas | Tarjetas de materas con la etiqueta "Visto" | pops |
| 4 | La pestaña «Para ti», llena de lo que le gusta | Pestañas Anuncios / Para ti / Destacados y el feed de plantas | brillo |
| 5 | Plantas, materas, tierra, estante | Las tarjetas aparecen con cada palabra | pops |
| 6 | Aprende de lo que miras, favoritos, interés y ofertas | Cuatro íconos que alimentan el círculo "Para ti" | pops |
| 7 | Su mismo país, nunca los suyos | Globo con pin "DE SU MISMO PAÍS" y "Tu anuncio" tachado | golpe |
| 8 | Lo visto muchas veces baja | La tarjeta "Visto 3 veces" baja y sube una nueva; chip "ESPACIO PARA LO NUEVO" | whoosh + ding |
| 9 | Dos materas de barro sin buscarlas | Paola con dos materas; chip "SIN BUSCARLAS" | brillo |
| 10 | Para usuarios registrados; mejor te conoce | Tarjeta "Solo usuarios registrados"; chips | pops |
| 11 | Entra al link… empieza a encontrar | Tarjeta "Marketplace Sumiago · Tu pestaña «Para ti»", mascota y frase final | |
| — | Cierre | Logo; "Descubre lo tuyo" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código, includes/mp_feed.php): «Para ti» (marketplace.php?parati=1) solo con sesión; pondera categorías/subcategorías de lo que el usuario vio (últimos 60 días), sus favoritos, sus «¡Lo quiero!» y sus ofertas; filtra por el país del usuario y excluye sus propios anuncios; lo visto 3 veces o más baja en el orden; sin datos muestra «Lo más buscado».
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
