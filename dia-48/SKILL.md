---
name: dia-48
description: Crea el video del Día 48 de Tareas Diarias de Sumiago, "La promo que nadie quitó" (historia ilustrativa: el botón «2x1 los martes» de una pizzería seguía en su portada toda la semana; con los enlaces programados y destacados de su portada de Sumiago aparece el martes y se esconde solo a la medianoche), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 48.
---

# Día 48 — "La promo que nadie quitó"

Reel vertical de unos 65 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). En la pizzería de Mauricio el martes es 2x1 y su portada tenía un botón que lo anunciaba, pero el miércoles seguía ahí, y el jueves, y el sábado; los clientes llegaban pidiendo su 2x1 y él explicaba una y otra vez "eso era solo el martes". Con su membresía descubre los **enlaces programados** de su portada en Sumiago: cada semana programa el botón para mostrarse desde el martes a las 12 y esconderse solo a la medianoche, y lo marca como **destacado**. El miércoles el botón ya no está, y la promo de Navidad la deja lista desde octubre para que aparezca sola el 1 de diciembre. Cierra: "Que tus promociones lleguen… y se vayan a tiempo."

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
python ruta/dia-48/scripts/voz.py
python ruta/dia-48/scripts/tl.py
python ruta/dia-48/scripts/align.py
python ruta/dia-48/scripts/audio.py
python ruta/dia-48/scripts/render.py 0 650 a.mp4
python ruta/dia-48/scripts/render.py 650 1300 b.mp4
python ruta/dia-48/scripts/render.py 1300 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-48.mp4
python ruta/dia-48/scripts/pc.py dia-48.mp4 dia-48-pc.mp4
```

Para revisar un momento: `python ruta/dia-48/scripts/render.py still 29 37.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Pizzería de Mauricio… martes 2x1… un botón | Pizzería con horno y mantel a cuadros, Mauricio (chef), tarjeta "MARTES", chip "2x1" y portada con el botón | se aleja |
| 1 | El miércoles, el botón seguía ahí | Tarjeta "MIÉRCOLES" y la portada con "2x1 los martes"; chip "EL BOTÓN SEGUÍA AHÍ" | música bajita |
| 2 | Jueves, sábado… pidiendo su 2x1 | La tarjeta cambia a JUEVES y SÁBADO; fila de clientes y burbuja "¡Quiero mi 2x1!" | |
| 3 | Explicar una y otra vez | Mauricio con burbujas "Eso era solo el martes…" y gota de sudor | |
| 4 | Con su membresía… enlaces programados | "Editar enlace · 2x1 los martes" con interruptores Destacado y Programar | ding |
| 5 | Cada semana: desde el martes a las 12… se esconde a la medianoche | Campos "Mostrar desde: Martes · 12:00 p. m." y "Mostrar hasta: Miércoles · 12:00 a. m."; chip "CADA SEMANA" | tecleo |
| 6 | Destacado, lo primero que se ve | Portada con el botón 2x1 en rojo y brillo dorado; chip "LO PRIMERO QUE SE VE" | brillo |
| 7 | El miércoles el botón ya no está | El botón desaparece de la portada; sello "SE ESCONDIÓ SOLO" | ding |
| 8 | La promo de Navidad… desde octubre… 1 de diciembre | Árbol, tarjeta "OCTUBRE" → "1 DIC" y enlace "Promo de Navidad" programado; chip "APARECERÁ SOLA" | |
| 9 | Ya no hay clientes confundidos | Clientes con pizzas; chips "SIN CONFUSIONES" / "SIN DISCUSIONES" | |
| 10 | Promociones, eventos o descuentos por días | Tres tarjetas y chip "ENLACES PROGRAMADOS Y DESTACADOS" | pops |
| 11 | Entra al link de mi perfil… se vayan a tiempo | Tarjeta "Enlaces programados · Aparecen y se esconden solos · PORTADA PRO", mascota, "LINK EN MI PERFIL" y la frase final | |
| — | Cierre | Logo con rebote, ondas y brillo; "Tus promos, a tiempo" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Pizzería cálida (horno, mantel rojo y blanco) y paneles oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: los enlaces destacados y programados son de la portada **PRO (con la membresía)**; cada enlace puede tener "Mostrar desde" y "Mostrar hasta" y se oculta solo fuera de ese rango. No se repite solo cada semana: por eso en la historia se programa cada semana. No prometer ventas ni ganancias. No escribir «BinanTrader».
