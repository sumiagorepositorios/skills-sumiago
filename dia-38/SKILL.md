---
name: dia-38
description: Crea el video del Día 38 de Tareas Diarias de Sumiago, "Las 500 tarjetas de don Jairo" (historia ilustrativa: un plomero cuyas tarjetas de papel se pierden pasa a una portada gratis de Sumiago con WhatsApp y código QR pegado en su caja de herramientas), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 38.
---

# Día 38 — "Las 500 tarjetas de don Jairo"

Reel vertical de unos 66 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Don Jairo, plomero de los buenos, mandó a hacer 500 tarjetas; se le acabaron en 2 meses y casi nadie lo llamó (terminaban en la billetera o en la lavadora). Su sobrina le pregunta qué encuentra la gente si lo busca en internet: nada. Esa noche le hace una **portada gratis en Sumiago** (foto, servicios, fotos de trabajos y botón de WhatsApp), todo en un solo enlace `sumiago.com/jairo-plomero`, e imprime su **código QR** para la caja de herramientas y la moto. Ahora el cliente escanea y lo guarda para la próxima. "Las tarjetas se pierden. Un enlace no." Cierra: "Que la próxima vez que te busquen… te encuentren."

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
python ruta/dia-38/scripts/voz.py
python ruta/dia-38/scripts/tl.py
python ruta/dia-38/scripts/align.py
python ruta/dia-38/scripts/audio.py
python ruta/dia-38/scripts/render.py 0 660 a.mp4
python ruta/dia-38/scripts/render.py 660 1320 b.mp4
python ruta/dia-38/scripts/render.py 1320 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-38.mp4
python ruta/dia-38/scripts/pc.py dia-38.mp4 dia-38-pc.mp4
```

Para revisar un momento: `python ruta/dia-38/scripts/render.py still 30.5 40`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | 500 tarjetas… 2 meses… casi nadie lo llamó | Pila de tarjetas "JAIRO · Plomería" que baja con contador 500→0, chip "2 MESES", tarjeta "Llamadas 2" | hojas que pasan |
| 1 | En la billetera… o en la lavadora | Billetera con la tarjeta y lavadora donde la tarjeta gira entre burbujas | la cámara va de la billetera a la lavadora; ruido de lavadora |
| 2 | Jairo es plomero. De los buenos… a tiempo | Jairo con gorra roja y llave inglesa, chips "PLOMERO" / "DE LOS BUENOS", sello "LLEGA A TIEMPO" | |
| 3 | Su sobrina: ¿qué encuentra? | Jairo y su sobrina con burbujas | |
| 4 | Nada. No encontraba nada. | Celular buscando "Jairo plomero": "0 resultados", sello "NADA" | golpe |
| 5 | Portada gratis: foto, servicios, trabajos y WhatsApp | La portada se arma: foto, "Jairo · Plomero", chips Fugas/Baños/Calentadores, 3 fotos de trabajos y botón "Escríbeme"; sello "GRATIS" | la cámara baja por la portada |
| 6 | Un solo enlace: sumiago.com/jairo-plomero | Barra que escribe `sumiago.com/jairo-plomero` y chip "UN SOLO ENLACE" | tecleo + ding |
| 7 | Imprimió su QR… caja de herramientas y moto | Código QR grande que se pega en la caja roja y en la moto | la cámara baja |
| 8 | El cliente escanea… guardado para la próxima | Clienta escaneando el QR de la caja; celular "Guardado · Jairo · Plomero"; chip "PARA LA PRÓXIMA" | obturador + ding |
| 9 | Las tarjetas se pierden. Un enlace no. | Pantalla dividida: tarjetas cayendo a la basura ("SE PIERDEN") y enlace brillando ("NO SE PIERDE") | brillo |
| 10 | Si tienes un oficio o un negocio… gratis | Tarjetas "Tu oficio" y "Tu negocio", sello "TU PORTADA GRATIS" | pops |
| 11 | Entra al link de mi perfil… te encuentren | Tarjeta "Mi Portada · Tu negocio en un solo enlace · GRATIS · CON QR", mascota, "LINK EN MI PERFIL", "…te encuentren." | |
| — | Cierre | Logo con rebote, ondas y brillo; "Que te encuentren" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F` para la portada y el cierre. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real de Mi Portada: crearla es gratis, con foto, enlaces, botón de WhatsApp, redes y código QR imprimible; la dirección es `sumiago.com/tu-nombre`. No prometer clientes ni ganancias. No escribir «BinanTrader».
