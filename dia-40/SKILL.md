---
name: dia-40
description: Crea el video del Día 40 de Tareas Diarias de Sumiago, "Las clases de las 10 de la noche" (historia ilustrativa: Andrea vende ropa desde casa, estudia de noche en la comunidad Gana con Marketing de Sumiago, prueba una cosa cada día y deja de adivinar), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 40.
---

# Día 40 — "Las clases de las 10 de la noche"

Reel vertical de unos 65 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Andrea vende ropa desde su casa: de día trabaja y de noche estudia, en su celular, a las 10 p. m., cuando los niños duermen. No sabía qué era un público objetivo ni por qué nadie veía sus publicaciones. Entra a la comunidad **Gana con Marketing** de Sumiago (cursos de marketing e inteligencia artificial): cada noche una clase y al otro día prueba una sola cosa. Cambia sus fotos, mejora sus descripciones, cuenta quién es y crea publicaciones con IA en minutos. La primera semana casi nada; la tercera le preguntan más que en todo el mes anterior. "No se volvió experta de un día para otro. Solo dejó de adivinar." Cierra: "Tu próxima clase… puede ser esta noche."

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
python ruta/dia-40/scripts/voz.py
python ruta/dia-40/scripts/tl.py
python ruta/dia-40/scripts/align.py
python ruta/dia-40/scripts/audio.py
python ruta/dia-40/scripts/render.py 0 650 a.mp4
python ruta/dia-40/scripts/render.py 650 1300 b.mp4
python ruta/dia-40/scripts/render.py 1300 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-40.mp4
python ruta/dia-40/scripts/pc.py dia-40.mp4 dia-40-pc.mp4
```

Para revisar un momento: `python ruta/dia-40/scripts/render.py still 20 41`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Andrea vende ropa… de día trabaja… de noche estudia | Ropa colgada, Andrea; el día se vuelve noche (sol que baja, luna que aparece); chips "DE DÍA TRABAJA" / "DE NOCHE ESTUDIA" | brillo |
| 1 | No en una universidad… celular, 10 de la noche, niños dormidos | Noche: niños dormidos (zzz), Andrea con el celular iluminado, "10:00 p. m.", sello "UNIVERSIDAD" que cambia a "EN SU CELULAR" | música bajita |
| 2 | No sabía qué era un público objetivo… nadie | Burbuja "¿Público objetivo?" y celular con publicaciones "0 vistas" | |
| 3 | Gana con Marketing… cursos de marketing e IA | Pantalla "GANA CON MARKETING e Inteligencia Artificial" con 3 cursos y barras de progreso; chip "MARKETING + IA" | pops |
| 4 | Cada noche una clase, al otro día una cosa | Tarjeta que alterna noche ("Una clase") y día ("Probar 1 cosa") y 7 círculos que se marcan | hojas |
| 5 | Fotos, descripciones, quién es ella | Foto ANTES/DESPUÉS de una blusa, descripción que se escribe y tarjeta «Soy Andrea…» | la cámara baja |
| 6 | Con IA, publicaciones en minutos | Celular con "IA" que escribe la publicación y la imagen; chip "EN MINUTOS" | tecleo + brillo |
| 7 | Primera semana casi nada… la tercera… | Barras de "Preguntas por semana" (semana 3 roja y alta), chip "MÁS QUE TODO EL MES" | ding |
| 8 | No se volvió experta… dejó de adivinar | Andrea y un dado que se tacha; sello "DEJÓ DE ADIVINAR" | golpe |
| 9 | Aprender no te quita tiempo… a ciegas | Camino en zigzag "A ciegas" frente a flecha recta "Aprendiendo"; chip "MESES PERDIDOS" | |
| 10 | Si vendes algo o quieres empezar… | La pantalla de Gana con Marketing con chips "SI VENDES ALGO" / "O QUIERES EMPEZAR" | |
| 11 | Entra al link de mi perfil… esta noche | Tarjeta "Gana con Marketing e Inteligencia Artificial", mascota, "LINK EN MI PERFIL" y "…puede ser esta noche." | brillo |
| — | Cierre | Logo con rebote, ondas y brillo; "Deja de adivinar" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Día claro y noche azul para la historia; Gana con Marketing en rojo Sumiago `#E6262F`, blanco y gris. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Gana con Marketing es la comunidad de cursos de marketing e inteligencia artificial de Sumiago, para quien tiene la membresía activa: no decir que es gratis. Las barras de preguntas son ilustrativas (sin cifras). No prometer ventas ni ganancias. No escribir «BinanTrader».
