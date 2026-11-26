---
name: dia-33
description: Crea el video del Día 33 de Tareas Diarias de Sumiago, "No vendas productos: vende emociones" (la fórmula de 6 emociones en una calle de puestos, la ruleta "EL JUEGO", café/gimnasio/juguetería, video hecho con IA y cierre "visita el enlace de mi perfil y comienza a ganar en Sumiago"), en móvil 9:16 y PC 16:9, con la voz del narrador, música alegre bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 33.
---

# Día 33 — "No vendas productos: vende emociones"

Reel vertical de unos 66 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps), con el motor del Día 31 y estilo claro de infografía (calle de puestos, ciudad al fondo, subtítulos grandes al centro palabra por palabra). Cuenta "la forma más fácil de vender cualquier cosa": a cada persona se le vende una emoción (orgullo, confianza, tranquilidad, aventura, sentirse parte del grupo, oportunidad), con ejemplos (cafetería → tu pausa, gimnasio → tu reflejo, juguetería → silencio para los papás), muestra que el video se hizo con IA, pregunta "¿qué emoción venderías tú?" y cierra con "Visita el enlace de mi perfil y comienza a ganar en Sumiago".

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg. `pip install pillow numpy`
- Fuente **Inter** instalada o en `fonts/`.
- Imágenes en `assets/` (mascota y logo).
- Tu clave de Fish Audio en `FISH_API_KEY` (**nunca la escribas en los archivos**). Modelo por defecto `s2.1-pro-free`; con crédito: `export FISH_MODEL=s1`.
- Voz: "narrador educativo sumiago" `bd35c17b29c54d3e9d2663863a28d212`.

## Pasos

```
export FISH_API_KEY=tu_clave
python ruta/dia-33/scripts/voz.py
python ruta/dia-33/scripts/tl.py
python ruta/dia-33/scripts/align.py
python ruta/dia-33/scripts/audio.py
python ruta/dia-33/scripts/render.py 0 1000 a.mp4
python ruta/dia-33/scripts/render.py 1000 99999 b.mp4
printf "file a.mp4\nfile b.mp4\n" > l.txt
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-33.mp4
python ruta/dia-33/scripts/pc.py dia-33.mp4 dia-33-pc.mp4
```

Para revisar un momento: `python ruta/dia-33/scripts/render.py still 9.0 27.6`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | La forma más fácil de vender… este año | Cinta con cajas "PRODUCTO"; una se vuelve roja, se abre con corazones y la gente corre; sello "ESTE AÑO" | la cámara sigue a la caja; brillo + golpe |
| 1 | Esta es la fórmula completa | Caja fuerte que se abre: tarjeta "LA FÓRMULA" | la caja se transforma en la caja fuerte |
| 2-7 | A los hombres… orgullo / mujeres… confianza / padres… tranquilidad / niños… aventura / jóvenes… grupo / los que empiezan… oportunidad | Calle de 6 puestos con toldo; el letrero se abre y la emoción sube desde la máscara; frasco con ícono y el cliente que llega caminando | la cámara recorre la calle siguiendo a cada cliente; pops |
| 8 | Eso es todo. Así funciona el juego | Ruleta "EL JUEGO" con las 6 emociones, sello "ESO ES TODO" | tic-tac de la ruleta |
| 9-11 | Cafetería / gimnasio / juguetería | Tarjeta del producto tachada con sello "NO" y tarjeta de la emoción (5:00, espejo, sofá "shh…") | la cámara pasa del producto a la emoción; campanita |
| 12 | Pero aquí viene lo mejor… ahora | Mascota con el pulgar sobre rayos, sello "AHORA" | |
| 13 | Con un celular… miles de personas desde tu casa | Casa con el celular emitiendo y multitud que crece con contador | la cámara se aleja del celular a la multitud |
| 14 | Sin cámara ni actores… inteligencia artificial | Cámara y actor tachados, celular con VOZ · IA, ESCENAS · IA, MÚSICA · IA, sello "HECHO CON IA" | pops |
| 15 | ¿Qué emoción venderías tú? | Puesto "TU NEGOCIO" que va probando emociones y un "?" | |
| 16 | Visita el enlace de mi perfil y comienza a ganar en Sumiago | Tarjeta Sumiago, chips, mascota, botón "LINK EN MI PERFIL" y "COMIENZA A GANAR EN SUMIAGO" | |
| — | Cierre | Logo con rebote y brillo, "LINK EN MI PERFIL" | el botón se transforma en el logo |

## Reglas

- Las 5 técnicas: texto desde máscara, movimientos encadenados (barra del letrero → texto), cámara que sigue lo importante, transformación entre escenas (`morph`) y animaciones sincronizadas con la voz (`wt()` + `align.py`).
- Historia propia (no copiar frases del video de referencia). No prometer montos; no escribir «BinanTrader».
