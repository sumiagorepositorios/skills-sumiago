---
name: dia-32
description: Crea el video del Día 32 de Tareas Diarias de Sumiago, "La llamada de las 3 a. m." (historia de humor: Patricia llama de madrugada, la esposa despierta y ella misma invita a registrarse en sumiago.com), en móvil 9:16 y PC 16:9, con narrador, voz de Patricia susurrando, voz de la esposa, música que cambia, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 32.
---

# Día 32 — "La llamada de las 3 a. m."

Reel vertical de unos 44 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps), con el mismo motor del Día 31. Historia de humor contada en primera persona: a las 3:00 a. m. vibra el celular, el protagonista contesta un número desconocido, Patricia le susurra "soy yo", dice que es "la de la escuela" y que consiguió su número por redes sociales… y la esposa se voltea, abre los ojos y es ella quien invita: "regístrate en sumiago.com y comienza". Cierra con la mascota y el logo.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg. `pip install pillow numpy`
- Fuente **Inter** instalada o en `fonts/`.
- Imágenes en `assets/` (mascota y logo, las mismas del Día 31).
- Tu clave de Fish Audio en `FISH_API_KEY` (**nunca la escribas en los archivos**). Modelo por defecto `s2.1-pro-free`; con crédito puedes usar `export FISH_MODEL=s1`.

## Voces (Fish Audio)

- Narrador (el protagonista): "narrador educativo sumiago" `bd35c17b29c54d3e9d2663863a28d212`
- Patricia (susurro, con la etiqueta `[whisper]`): "Mujer Voz Venezuela" `22550e2d849b44e18c7df57f61e666f9`
- Esposa: `9ea79fe31584435abe88b02e7aed4e6e`

## Pasos

```
export FISH_API_KEY=tu_clave
python ruta/dia-32/scripts/voz.py
python ruta/dia-32/scripts/tl.py
python ruta/dia-32/scripts/align.py
python ruta/dia-32/scripts/audio.py
python ruta/dia-32/scripts/render.py 0 660 a.mp4
python ruta/dia-32/scripts/render.py 660 99999 b.mp4
printf "file a.mp4\nfile b.mp4\n" > l.txt
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-32.mp4
python ruta/dia-32/scripts/pc.py dia-32.mp4 dia-32-pc.mp4
```

`guion.json`: cada frase es `[quién habla (N/P/E), texto para la voz, subtítulo]`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Eran las 3:00… mi celular empezó a vibrar | Cuarto de noche, pareja dormida, reloj 3:00, sello "3:00 A. M.", celular que vibra | la cámara va al celular; vibración |
| 1 | Como estaba en vibración, ella no escuchó nada | Esposa dormida (zzz), chip "VIBRACIÓN", sello "NO ESCUCHÓ NADA" | el celular se transforma en el chip |
| 2 | Yo nunca contesto números desconocidos… contesté | Llamada entrante "Número desconocido", sello "YO NUNCA CONTESTO", el pulgar contesta | la cámara sigue al pulgar; clic |
| 3 | ¿Aló? | Él sentado en la cama con el celular | burbuja |
| 4 | «Hola… soy yo. Patricia.» | Silueta de Patricia con luz roja, tarjeta "LLAMADA EN CURSO" y el nombre sube desde la máscara, onda del susurro | música cambia a tema sensual |
| 5 | Creo que estás equivocada | Él en primer plano, gota de sudor | |
| 6 | «No me tranques… ¿No me recuerdas?» | Silueta más cerca, dos burbujas encadenadas | |
| 7 | No. | Sello "NO." | golpe y temblor |
| 8 | «Patricia, la de la escuela… redes sociales» | Corcho con polaroid de Patricia niña, sello "LA DE LA ESCUELA" y perfil de redes con "TU NÚMERO" | la cámara va de la foto al perfil |
| 9 | Y justo ahí… mi esposa se volteó… y abrió los ojos | La esposa gira y abre los ojos, luz roja | latidos; la cámara entra a sus ojos con temblor y golpe dramático |
| 10 | Si te ha gustado este video… sumiago.com y comienza | La esposa habla a cámara, chips PRODUCTO/SERVICIO/NEGOCIO/EMPRESA, botón "REGÍSTRATE EN SUMIAGO.COM", mascota | sus ojos se transforman en su retrato; música positiva; pops |
| — | Cierre | Logo con rebote, brillo y "REGÍSTRATE EN SUMIAGO.COM" | el botón se transforma en el logo |

## Reglas

- Las 5 técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, transformación entre escenas (`morph`) y animaciones sincronizadas con la voz (`wt()`, `align.py`, labios que se mueven con la voz).
- Humor familiar: Patricia nunca se muestra de forma explícita (solo silueta). No prometer ganancias; no escribir «BinanTrader».
