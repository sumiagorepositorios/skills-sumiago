---
name: dia-50
description: Crea el video del Día 50 de Tareas Diarias de Sumiago, "La portada que se parecía a todas" (historia ilustrativa: la portada gratis de una floristería se veía igual a la de una ferretería; con la portada PRO de Sumiago le pone sus colores, una letra elegante, botones en píldora, video de flores de fondo y quita «Diseñado en Sumiago»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 50.
---

# Día 50 — "La portada que se parecía a todas"

Reel vertical de unos 60 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Valeria tiene una floristería e hizo su portada gratis en Sumiago; quedó bien, pero se parecía a la de todos (mismo fondo, botones y letra), y una floristería no debería verse igual que una ferretería. Con su membresía pasa su portada a **PRO**: elige sus colores (rosado, verde hoja y blanco), una letra más elegante, botones en forma de píldora y un **video de fondo** con sus flores; además quita "Diseñado en Sumiago". Ahora, antes de leer una palabra, cualquiera sabe que es una floristería. "Tu portada es tu vitrina en internet." Cierra: "Que tu negocio se vea… como tu negocio."

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
python ruta/dia-50/scripts/voz.py
python ruta/dia-50/scripts/tl.py
python ruta/dia-50/scripts/align.py
python ruta/dia-50/scripts/audio.py
python ruta/dia-50/scripts/render.py 0 600 a.mp4
python ruta/dia-50/scripts/render.py 600 1200 b.mp4
python ruta/dia-50/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-50.mp4
python ruta/dia-50/scripts/pc.py dia-50.mp4 dia-50-pc.mp4
```

Para revisar un momento: `python ruta/dia-50/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Valeria tiene una floristería… portada gratis… quedó bien | Floristería con flores que se mecen, Valeria y su portada en plantilla Oscuro; chip "QUEDÓ BIEN" | se aleja |
| 1 | Se parecía a la de todos | Tres portadas iguales (floristería, ferretería, barbería); chips "MISMO FONDO / MISMOS BOTONES / MISMA LETRA" | música bajita |
| 2 | Una floristería no debería verse igual que una ferretería | Flores ≠ martillo; sello "NO SE DEBEN VER IGUAL" | |
| 3 | Con su membresía pasó a PRO | La portada con sello dorado "PRO" y chispas | golpe + brillo |
| 4 | Sus colores: rosado, verde hoja y blanco | Panel "Diseño" (Colores) y la portada que cambia de color | pops |
| 5 | Letra elegante y botones en píldora | Panel con "Aa Elegante" y "Píldora"; la portada cambia | |
| 6 | Video de fondo: sus flores | Panel "Fondo · Video" y la portada con flores que se mueven; chip "VIDEO DE FONDO" | brillo |
| 7 | Ya no dice «Diseñado en Sumiago» | Interruptor "Quitar «Diseñado en»" y sello "100 % SUYA" | |
| 8 | Antes de leer una palabra… es una floristería | Portada final grande; chip "¡ES UNA FLORISTERÍA!" | ding |
| 9 | Tu portada es tu vitrina | La portada dentro de una vitrina; sello "QUE SE VEA COMO TU NEGOCIO" | |
| 10 | Colores, letra y estilo… con tu membresía | Tarjetas Colores / Letra / Estilo y chip "PORTADA PRO · CON TU MEMBRESÍA" | pops |
| 11 | Entra al link de mi perfil… como tu negocio | Tarjeta "Portada PRO · Tus colores, tu letra, tu fondo · SIN «DISEÑADO EN SUMIAGO»", mascota y frase final | |
| — | Cierre | Logo con rebote, ondas y brillo; "Que se vea como tu negocio" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Floristería en rosado y verde; paneles oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
