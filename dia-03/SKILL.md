---
name: dia-03
description: Crea el video del Día 3 de Tareas Diarias de Sumiago, "Portadas Sumiago" (todo tu negocio en un solo link, gratis, 3 pasos, pedidos a WhatsApp, PRO y cierre "Reclama tu nombre"), con fondo blanco, mascota que habla, música y efectos, en móvil 9:16 y PC 16:9. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 3.
---

# Día 3 — "Portadas Sumiago"

Reel vertical 9:16 (1080x1920, 30 fps, unos 60 s) con **fondo blanco**. Engancha con el sello "¡PARA!" sobre una bio con un solo link y luego muestra la portada animada de Sumiago: botones de redes, WhatsApp, catálogo y pago en USDT, "GRATIS", los 3 pasos, el pedido que llega a WhatsApp, lo que trae PRO, "Otros: 10 links / Tú: 1 que vende por ti" y el cierre "RECLAMA TU NOMBRE · sumiago.com/portadas". Lleva música hecha por código (sin derechos de autor), efectos de sonido en cada escena, un acercamiento rápido al empezar cada escena y una barra roja de progreso abajo. La versión PC pone el reel en el centro sobre su propio fondo difuminado.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy opencv-python-headless`
- Fuente **Poppins Bold** (si no está, usa Arial Bold).
- Fuente de emojis a color: Noto Color Emoji (Linux) o Segoe UI Emoji (Windows, `seguiemj.ttf`). También puedes copiar `NotoColorEmoji.ttf` a la carpeta de la skill.
- La mascota ya viene en `assets/mascota-frente.png` (1199x1312). En este video **sí** va con los logos de Sumiago.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.txt`: las 12 frases, una por línea (cada línea es una escena).
- `scripts/voz.py`: voz de la mascota con Fish Audio (`bd35c17b29c54d3e9d2663863a28d212`), 1,5 semitonos más aguda, sin silencios y 0,25 s entre frases. Deja `voice.wav` y `durs.json`.
- `scripts/preparar_mascota.py`: deja `mascot_clean.png` (la mascota con sus logos; solo borra la esquina de arriba a la izquierda).
- `scripts/base.py`: parte común (tiempos por palabra, boca según el volumen de la voz, parpadeo, brillos).
- `scripts/render.py`: todas las escenas, la portada animada, sellos, confeti, QR y la lista de efectos.
- `scripts/audio.py`: voz + música (124 bpm, C–Am–F–G) que baja cuando habla la voz + efectos → `mix.wav`.
- `scripts/pc.py`: versión 1920x1080.

## Pasos

Trabaja en una carpeta vacía y ejecuta desde ahí:

```
set FISH_API_KEY=tu_clave
python ruta/dia-03/scripts/voz.py
python ruta/dia-03/scripts/preparar_mascota.py
python ruta/dia-03/scripts/audio.py
python ruta/dia-03/scripts/render.py test 0.6 3.5 6 10.5 14 18.5
python ruta/dia-03/scripts/render.py full
python ruta/dia-03/scripts/pc.py dia-03.mp4 dia-03-pc.mp4
```

`render.py test` deja `test.jpg` con cuadros de muestra para revisar antes del render completo. Escucha el video completo antes de publicarlo.

## Escenas (línea del guion → lo que se ve → sonido)

| # | Frase | En pantalla | Sonido |
|---|-------|-------------|--------|
| 0 | ¡Para! ¿Un solo link en tu bio? | Perfil "tu_negocio · Bio aburrida..." con "un-solo-link.com/xyz"; destello rojo, la pantalla tiembla y sello "¡PARA!"; luego 📉 y "pierdes clientes" | golpe grave + sello + pop |
| 1 | Todo tu negocio en un solo link | La portada sube desde abajo con brillo rojo y sus botones aparecen uno a uno; sello "1 SOLO LINK" | pops + sello |
| 2 | Redes, WhatsApp, catálogo, cobros | Emojis 📸 🎵 💬 🛒 💰 vuelan hacia la portada; se escribe "sumiago.com/@tunombre" | pops + teclas |
| 3 | Es gratis | Sello verde "GRATIS" con confeti; tarjetas "Sin tarjeta", "Lista en 2 minutos", "Desde tu celular" con check | sello + aplausos + dings |
| 4 | Paso uno | "PASO 1", se escribe "sumiago.com/@tunombre" y sale "¡Disponible!"; mascota abajo | teclas + ding |
| 5 | Paso dos | "PASO 2", carrusel de plantillas Restaurante, Barbería, Tienda, Coach | swipes |
| 6 | Paso tres | "PASO 3", portada + Instagram / TikTok / Estados y código QR con impresora | pops |
| 7 | El pedido llega a WhatsApp | Dedo que toca el catálogo, carrito que vuela y chat de WhatsApp "NUEVO PEDIDO · 2x Hamburguesa · 1x Papas grandes · Total: $14"; "directo a tu chat" | toque + pop + mensaje |
| 8 | ¿Quieres más? PRO | Sello dorado "PRO" y tarjetas Pagos USDT, Agenda, Menú QR, Reseñas, Estadísticas; barras de estadísticas | sello + pops + subida |
| 9 | Si recomiendas Sumiago | Avatar en el centro, 🙋 alrededor y monedas que llegan; "+ comisión" | pops + monedas |
| 10 | Otros diez links, tú uno | "OTROS" con 10 links tachados / "TÚ" con la portada; sello "VENDE POR TI" | zumbido + sello + ding |
| 11 | Reclama tu nombre | Botón rojo que late "RECLAMA TU NOMBRE", "sumiago.com/portadas", "link en mi perfil" 👇, mascota y confeti | subida + pop + aplausos |

## Estilo y reglas

- Fondo blanco con degradado suave (`#FFFFFF` → `#F0F0F5`), rojo Sumiago `#E11E28`, verde WhatsApp `#25D366`, amarillo `#FFD23F`.
- Subtítulos arriba (y = 200), de 4 en 4 palabras, en negro con borde blanco; la palabra que suena en **rojo** y un poco más arriba.
- Cada escena entra con un acercamiento rápido (6 %) y un "whoosh"; barra roja de progreso al pie.
- No dice el precio de la membresía. El pedido de WhatsApp ($14) es un ejemplo inventado.
- Si cambias el guion, conserva 12 líneas en el mismo orden: cada escena y cada efecto dependen de su número de línea.
