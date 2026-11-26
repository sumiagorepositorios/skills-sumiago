---
name: dia-37
description: Crea el video del Día 37 de Tareas Diarias de Sumiago, "La panadera que no sabía editar" (historia ilustrativa: doña Marta, que nunca ha editado un video, muestra su panadería con Videos Virales de Sumiago sin grabarse y la gente llega diciendo "la vi en un video"), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 37.
---

# Día 37 — "La panadera que no sabía editar"

Reel vertical de unos 59 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Doña Marta hace el mejor pan de bono del barrio y nunca ha editado un video. Su hijo le dice que hay que subir videos a redes, pero no tiene tiempo, así que ella lo intenta sola: entra a **Videos Virales** en Sumiago, encuentra **ideas que ya funcionan**, sigue el tutorial, elige una idea, escribe la historia de su panadería, escoge una voz y le da **crear**. Sin cámara, sin grabarse, sin editar. Sus vecinos ven el primer video y el quinto lo comparte alguien de otra ciudad; hoy entra gente diciendo "¡La vi en un video!". Cierra: "Tu negocio merece que lo vean… aunque tú no salgas en cámara."

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
python ruta/dia-37/scripts/voz.py
python ruta/dia-37/scripts/tl.py
python ruta/dia-37/scripts/align.py
python ruta/dia-37/scripts/audio.py
python ruta/dia-37/scripts/render.py 0 600 a.mp4
python ruta/dia-37/scripts/render.py 600 1200 b.mp4
python ruta/dia-37/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-37.mp4
python ruta/dia-37/scripts/pc.py dia-37.mp4 dia-37-pc.mp4
```

Para revisar un momento: `python ruta/dia-37/scripts/render.py still 19 25`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Doña Marta… pan de bono… nunca ha editado un video | Panadería con estantes de pan de bono, doña Marta con delantal, chip "EL MEJOR PAN DE BONO", sello "0 VIDEOS EDITADOS" | se aleja; golpe |
| 1 | Su hijo: hay que subir videos… ¿y quién los hace? | Marta y su hijo con burbujas | la cámara pasa del hijo a la respuesta |
| 2 | Él tampoco tenía tiempo… lo intentó sola | Reloj que corre, "SIN TIEMPO", Marta con portátil y "LO INTENTÓ SOLA" | tic-tac; música bajita |
| 3 | Videos Virales… ideas que ya están funcionando | Pantalla "VIDEOS VIRALES" pestaña Ideas con 3 ideas y sus vistas; sello "YA FUNCIONAN" | la cámara baja por las ideas |
| 4 | Tutorial, idea, historia, voz… crear | Pestaña Estudio: pasos 1–4 con ✓ (el guion se escribe solo), botón "¡CREAR VIDEO!" con toque y barra de progreso | la cámara va al botón; ding |
| 5 | Sin cámara. Sin grabarse. Sin editar. | Tres íconos que se tachan uno a uno | golpe por cada uno |
| 6 | El primero lo vieron sus vecinos… el quinto, otra ciudad | Mapa: puntos de vecinos, línea a "OTRA CIUDAD", contador de vistas que sube | la cámara sigue la línea |
| 7 | ¡La vi en un video! | Clientes que llegan a la panadería y burbuja roja | |
| 8 | Sigue sin saber editar. Y no le hace falta. | Marta en primer plano con chispas, chip y sello "Y NO LE HACE FALTA" | brillo |
| 9 | Si tienes un negocio y te da pena grabarte… | Persona tapándose la cara, chip "NEGOCIO", sello "ESTO ES PARA TI" | |
| 10 | Entra al link de mi perfil… Videos Virales y Gana con Marketing | Tarjeta Sumiago con chips VIDEOS VIRALES / GANA CON MARKETING, "Crea videos sin grabarte", mascota y "LINK EN MI PERFIL" | pops |
| 11 | Tu negocio merece que lo vean… aunque no salgas en cámara | Celular con el video de "Panadería Marta", corazones y "aunque no salgas en cámara" | |
| — | Cierre | Logo con rebote, ondas y brillo; "Que vean tu negocio" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Panadería cálida (crema, madera, toldo rojo y blanco) y pantallas oscuras con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real de Videos Virales: pestañas Estudio, Ideas Virales, Voces, Mi YouTube y Mis Videos; guion → voz → Short 9:16; cada usuario conecta sus propias claves (por eso se menciona el tutorial) y se necesita la membresía activa. No decir que es gratis ni prometer ganancias o vistas. No escribir «BinanTrader».
