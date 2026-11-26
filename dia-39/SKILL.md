---
name: dia-39
description: Crea el video del Día 39 de Tareas Diarias de Sumiago, "El ayudante que ya sabía" (historia ilustrativa: doña Gloria, dueña de una ferretería, deja de buscar con letreros y grupos y encuentra a su ayudante en Contrátame Sumiago buscando por profesión, ciudad y experiencia), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 39.
---

# Día 39 — "El ayudante que ya sabía"

Reel vertical de unos 67 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Doña Gloria lleva un mes buscando ayudante para su ferretería: el letrero trae 3 personas que no saben de herramientas y el grupo le deja 40 mensajes de gente que no leyó el anuncio. Su hija le dice "no busques entre todos, busca al que ya sabe". En **Contrátame Sumiago** buscan por profesión, ciudad y años de experiencia; aparecen perfiles revisados con foto y experiencia. Eligen a Mateo (3 años en una bodega de materiales, vive a 10 minutos), tocan **«Contactar candidato»** y le escriben por WhatsApp; el lunes ya atiende el mostrador. Invita a empresas y a quienes buscan trabajo. Cierra: "La persona que buscas… puede que ya esté ahí."

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
python ruta/dia-39/scripts/voz.py
python ruta/dia-39/scripts/tl.py
python ruta/dia-39/scripts/align.py
python ruta/dia-39/scripts/audio.py
python ruta/dia-39/scripts/render.py 0 670 a.mp4
python ruta/dia-39/scripts/render.py 670 1340 b.mp4
python ruta/dia-39/scripts/render.py 1340 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-39.mp4
python ruta/dia-39/scripts/pc.py dia-39.mp4 dia-39-pc.mp4
```

Para revisar un momento: `python ruta/dia-39/scripts/render.py still 32 37.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Doña Gloria… un mes buscando ayudante | Ferretería con herramientas, Gloria en el mostrador, calendario "30 DÍAS", chip "BUSCA AYUDANTE" | se aleja |
| 1 | Letrero… 3 personas… ninguna sabía | Letrero "SE NECESITA AYUDANTE", 3 personas que llegan con "?", chip "NO SABÍAN DE HERRAMIENTAS" | la cámara baja a las personas |
| 2 | Grupo… 40 personas… no leyeron | Celular con mensajes "Info?", "Cuánto pagan?"…, contador hasta 40 y sello "NO LEYERON" | dings |
| 3 | Su hija: busca al que ya sabe | Gloria y su hija con burbujas | |
| 4 | Contrátame Sumiago: profesión, ciudad, experiencia | Buscador que escribe "Ayudante de ferretería" y chips Ayudante / Mi ciudad / +2 años | tecleo |
| 5 | Perfiles revisados con foto y experiencia | Tarjetas de candidatos con foto, oficio, años y sello "Revisado" | pops |
| 6 | Mateo: 3 años en bodega, a 10 minutos | Se resalta la tarjeta de Mateo, las demás se apagan; chips "3 AÑOS EN BODEGA DE MATERIALES" y "VIVE A 10 MINUTOS" | la cámara se acerca |
| 7 | «Contactar candidato»… WhatsApp esa tarde | Botón con toque y mensaje "Hola Mateo, vi tu perfil. ¿Puedes venir mañana?" | |
| 8 | El lunes ya atendía el mostrador | Mateo en el mostrador con Gloria, chip "LUNES", sello "YA SABÍA" | brillo |
| 9 | No tiene que ser un dolor de cabeza | Montón de mensajes ("Todos") frente a lupa sobre perfiles ("Los que ya saben") | |
| 10 | Si tienes un negocio… o buscas trabajo | Tarjetas "Tu negocio busca" y "Tú buscas trabajo", sello "ES PARA TI" | |
| 11 | Entra al link de mi perfil… ya esté ahí | Tarjeta "Contrátame Sumiago · Talento y empresas, conectados", mascota, "LINK EN MI PERFIL" y "…puede que ya esté ahí." | |
| — | Cierre | Logo con rebote, ondas y brillo; "Encuentra a quien ya sabe" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Ferretería cálida y pantallas claras; cierre oscuro con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real de Contrátame Sumiago: las empresas se registran en Sumiago, buscan por profesión, ciudad o departamento, años de experiencia y nivel académico, ven perfiles revisados y usan «Contactar candidato»; el candidato recibe el contacto por WhatsApp o correo. No prometer contrataciones. No escribir «BinanTrader».
