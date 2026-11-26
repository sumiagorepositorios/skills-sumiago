---
name: dia-36
description: Crea el video del Día 36 de Tareas Diarias de Sumiago, "La moto que no era mía" (historia ilustrativa: Camilo ayuda a vender la moto de su vecino don Hernán compartiendo su enlace de Dropshipping del Marketplace de Sumiago; la comisión es un acuerdo voluntario), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 36.
---

# Día 36 — "La moto que no era mía"

Reel vertical de unos 62 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Gancho: "Camilo vendió una moto… y nunca tuvo una moto". Su vecino don Hernán llevaba 2 meses sin vender la suya. Camilo ve en el **Marketplace de Sumiago** que el anuncio tiene **Dropshipping** activado, toca **«Gana comisión»**, se copia su enlace personal y lo comparte en su estado de WhatsApp y en 2 grupos del barrio. Al cuarto día un comprador entra por su enlace y le escribe a don Hernán; Sumiago les avisa a los dos que llegó gracias a Camilo. La moto se vende y don Hernán cumple la comisión ofrecida. Aclara que la comisión es **un acuerdo voluntario: Sumiago no la cobra ni la garantiza**. Cierra: "A lo mejor tu primera venta… no es tuya."

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
python ruta/dia-36/scripts/voz.py
python ruta/dia-36/scripts/tl.py
python ruta/dia-36/scripts/align.py
python ruta/dia-36/scripts/audio.py
python ruta/dia-36/scripts/render.py 0 640 a.mp4
python ruta/dia-36/scripts/render.py 640 1280 b.mp4
python ruta/dia-36/scripts/render.py 1280 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-36.mp4
python ruta/dia-36/scripts/pc.py dia-36.mp4 dia-36-pc.mp4
```

Para revisar un momento: `python ruta/dia-36/scripts/render.py still 14.9 31.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Camilo vendió una moto… y nunca tuvo una moto | Calle de barrio, Camilo junto a la moto, sello "VENDIDA", "?" y chip "NUNCA TUVO UNA MOTO" | se aleja; motor + golpe |
| 1 | Don Hernán… 2 meses… nadie preguntaba | Don Hernán con la moto y letrero "SE VENDE", chip "2 MESES", tarjeta "Preguntas 0", hojas que caen | |
| 2 | …Marketplace… había activado Dropshipping | Celular con el anuncio "Moto 150 cc · 2021"; el interruptor Dropshipping se activa | el letrero se transforma en el anuncio; la cámara se acerca al interruptor; ding |
| 3 | El vendedor ofrece una comisión a quien le ayude | Tarjetas "Don Hernán · VENDEDOR" → flecha "COMISIÓN %" → "Camilo · TE AYUDA" | el interruptor se transforma en la flecha |
| 4 | Tocó «Gana comisión» y se copió su enlace | Botón verde "Gana comisión 5 %" con toque y aviso "Tu enlace se copió · sumiago.com/…#14" | la cámara baja al aviso |
| 5 | Lo compartió en WhatsApp y 2 grupos | El enlace baja a "Mi estado", "Vecinos del barrio" y "Compra y venta barrio" con "COMPARTIDO" | pops |
| 6 | Al cuarto día… le escribió a don Hernán | Calendario DÍA 1→4, comprador con "#14" y burbuja "¿Todavía está la moto?", foto de don Hernán | hojas de calendario |
| 7 | Sumiago les avisó a los dos… gracias a Camilo | Avisos "Para don Hernán" y "Para Camilo"; sello "GRACIAS A CAMILO" | dings |
| 8 | La moto se vendió… cumplió con la comisión | Sello "VENDIDA", sobre que pasa a Camilo, chip "COMISIÓN CUMPLIDA" | la cámara baja a Camilo; brillo |
| 9 | Ojo: acuerdo voluntario… no la cobra ni la garantiza | Tarjeta "ACUERDO VOLUNTARIO" con "Sumiago no la cobra" y "Sumiago no la garantiza" | música más bajita |
| 10 | Hay cosas que no son tuyas… las puedes ayudar a vender | Camilo rodeado de anuncios con "Comisión" (moto, celular, nevera, bicicleta, sofá); "AYÚDALAS A VENDER" | pops |
| 11 | Entra al link de mi perfil… tu primera venta… no es tuya | Tarjeta "Marketplace Sumiago · Anuncios con Dropshipping · GANA COMISIÓN", mascota, "LINK EN MI PERFIL", "…no es tuya." | |
| — | Cierre | Logo con rebote, ondas y brillo; "Ayuda a vender" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Barrio de día (cielo, casas de colores) y escenas oscuras con rojo Sumiago `#E6262F`; botón de comisión en verde como en el Marketplace. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: el vendedor activa Dropshipping y ofrece un %; el usuario toca «Gana comisión» y copia su enlace (#ID); si un comprador llega por ese enlace y contacta al vendedor, Sumiago avisa al vendedor y al referido. **La comisión es voluntaria: Sumiago no la cobra ni la garantiza** — decirlo siempre. No prometer ganancias. No escribir «BinanTrader».
