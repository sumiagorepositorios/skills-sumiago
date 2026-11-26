---
name: dia-46
description: Crea el video del Día 46 de Tareas Diarias de Sumiago, "¿Cuánto vale?" (historia ilustrativa: Tatiana vende bisutería por estados de WhatsApp y responde precios uno por uno; arma su catálogo en Mi Negocio de su portada de Sumiago y las clientas le envían el pedido completo con total por WhatsApp), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 46.
---

# Día 46 — "¿Cuánto vale?"

Reel vertical de unos 60 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Tatiana vende aretes y collares hechos a mano y los publica en su estado de WhatsApp; cada día le preguntan 40 veces "¿cuánto vale?", responde precio por precio y la clienta ya se fue. Con su membresía arma su **catálogo** en **Mi Negocio** de su portada de Sumiago (foto, precio y descripción). La clienta entra a su enlace, ve todo con precio, agrega al pedido los aretes dorados y el collar rojo y ve el total; toca **«Enviar pedido por WhatsApp»** y a Tatiana le llega el pedido completo con productos y total. Sin preguntar el precio ni esperar respuesta: Tatiana confirma, empaca y envía. Cierra: "Que tus clientes compren… sin tener que preguntar."

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
python ruta/dia-46/scripts/voz.py
python ruta/dia-46/scripts/tl.py
python ruta/dia-46/scripts/align.py
python ruta/dia-46/scripts/audio.py
python ruta/dia-46/scripts/render.py 0 600 a.mp4
python ruta/dia-46/scripts/render.py 600 1200 b.mp4
python ruta/dia-46/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-46.mp4
python ruta/dia-46/scripts/pc.py dia-46.mp4 dia-46-pc.mp4
```

Para revisar un momento: `python ruta/dia-46/scripts/render.py still 31 36`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Tatiana vende aretes y collares… estado de WhatsApp | Tatiana con su bisutería; celular con el estado y chip "ESTADO DE WHATSAPP" | se aleja |
| 1 | 40 veces: ¿cuánto vale? | Burbujas "¿Cuánto vale?" que se amontonan y contador de mensajes | dings; música bajita |
| 2 | Precio por precio… ya se había ido | Respuestas de precio una a una; "Clienta: desconectada"; sello "YA SE HABÍA IDO" | |
| 3 | Con su membresía… armó su catálogo | Panel "Mi Negocio PRO", pestaña Catálogo, interruptor "Catálogo con pedidos · Llegan a tu WhatsApp" | ding |
| 4 | Foto, precio y descripción | Formulario "Nuevo producto" que se llena | pops |
| 5 | Entra a su enlace, ve todo con precio | Celular "Tati Bisutería · Catálogo" con 4 productos y precios | la cámara se acerca |
| 6 | Agrega los aretes dorados, el collar rojo… y ve el total | Botones "Agregar" → "Agregado", "Ver pedido 2" y tarjeta "Tu pedido · Total $ 63.000" | toques |
| 7 | «Enviar pedido por WhatsApp»… pedido completo | Botón verde con toque y mensaje "Hola, quiero hacer este pedido: … *Total: $ 63.000*"; chip "PEDIDO COMPLETO" | ding |
| 8 | Sin preguntar el precio. Sin esperar respuesta. | Burbujas "¿Cuánto vale?" y "Esperando respuesta…" tachadas | |
| 9 | Confirma, empaca y envía | Tres tarjetas con íconos | pops |
| 10 | Si vendes por WhatsApp… el catálogo con pedidos | Burbujas "¿Cuánto vale?" que desaparecen y tarjeta del catálogo; chip "CATÁLOGO CON PEDIDOS · MI NEGOCIO" | |
| 11 | Entra al link de mi perfil… sin tener que preguntar | Tarjeta "Mi Negocio · Catálogo · Pedidos completos a tu WhatsApp", mascota, "LINK EN MI PERFIL" y la frase final | brillo |
| — | Cierre | Logo con rebote, ondas y brillo; "Que compren sin preguntar" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Tonos cálidos (naranja, crema) para la historia; paneles oscuros con rojo Sumiago `#E6262F`; verde para WhatsApp. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: el catálogo con pedidos es parte de **Mi Negocio (PRO, con la membresía)**; productos con nombre, categoría, descripción, precio y foto; la clienta agrega al pedido, ve el total, puede dejar una nota y toca "Enviar pedido por WhatsApp", que abre WhatsApp con "Hola, quiero hacer este pedido:", los productos y el total (sin número de WhatsApp no se muestra el carrito). No prometer ventas ni ganancias. No escribir «BinanTrader».
