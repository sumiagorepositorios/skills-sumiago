---
name: dia-45
description: Crea el video del Día 45 de Tareas Diarias de Sumiago, "El cliente de otro país" (historia ilustrativa: una diseñadora de logos con un cliente extranjero deja las transferencias internacionales y activa los cobros en USDT de Mi Negocio en su portada de Sumiago; el pago llega directo a su billetera BEP20), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 45.
---

# Día 45 — "El cliente de otro país"

Reel vertical de unos 66 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Daniela diseña logos desde su casa y le escribe un cliente de otro país; le encanta su trabajo, pero pagar es un problema (transferencias internacionales, comisiones, días de espera y papeles). El cliente pregunta "¿no recibes en USDT?". Con su membresía, en **Mi Negocio** de su portada de Sumiago, activa los **cobros en USDT**: pone la dirección de su billetera en la red BEP20 y montos sugeridos. Su enlace muestra "Págame en USDT" con código QR y botón para copiar la dirección. El cliente escanea, paga y llega **directo a su billetera**: **Sumiago no guarda ni toca ese dinero**. Funciona igual en la esquina o al otro lado del mundo. Cierra: "Tu trabajo no tiene fronteras… tus cobros tampoco."

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
python ruta/dia-45/scripts/voz.py
python ruta/dia-45/scripts/tl.py
python ruta/dia-45/scripts/align.py
python ruta/dia-45/scripts/audio.py
python ruta/dia-45/scripts/render.py 0 660 a.mp4
python ruta/dia-45/scripts/render.py 660 1320 b.mp4
python ruta/dia-45/scripts/render.py 1320 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-45.mp4
python ruta/dia-45/scripts/pc.py dia-45.mp4 dia-45-pc.mp4
```

Para revisar un momento: `python ruta/dia-45/scripts/render.py still 35 40.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Daniela diseña logos… cliente de otro país | Daniela con portátil donde se dibuja un logo; aviso "Nuevo cliente · Desde otro país" con globo | se aleja; ding |
| 1 | Le encantó… el problema, pagar | Burbujas "¡Me encantó el logo!" y "¿Cómo te pago?"; "$ ?" | |
| 2 | Transferencias, comisiones, espera, papeles | Banco con chips "TRANSFERENCIA INTERNACIONAL", "COMISIONES", "DÍAS DE ESPERA", "PAPELES" y papeles que caen | música bajita |
| 3 | ¿No recibes en USDT? | Burbuja y monedas "USDT" flotando | monedas |
| 4 | Con su membresía… activó los cobros en USDT | Panel "Mi Negocio PRO", pestaña Cobros USDT, interruptor "Mostrar cobros en USDT en mi portada" | ding |
| 5 | Dirección de su billetera BEP20 y montos sugeridos | Dirección que se escribe, chip "RED BNB SMART CHAIN · BEP20", montos 50/100/200 USDT y aviso "El dinero llega directo… Sumiago no guarda ni toca tus fondos… Revisa bien la dirección" | tecleo |
| 6 | «Págame en USDT», QR y botón para copiar | Portada "Daniela Diseño" con la sección, QR, dirección, "Copiar dirección" → "¡Copiada!" y montos | la cámara se acerca |
| 7 | Escaneó, envió… directo a la billetera | Celular del cliente escaneando; monedas que vuelan a la billetera; "+100 USDT"; sello "DIRECTO A SU BILLETERA" | monedas + ding |
| 8 | Sumiago no guarda ni toca ese dinero | Flecha "Tu cliente → Tu billetera" y tarjeta de Sumiago "No guarda ni toca tu dinero" | |
| 9 | En la esquina… o al otro lado del mundo | Globo con pines "Tu barrio" y "Otro país" unidos por un arco | |
| 10 | Servicios o productos a cualquier país | Tarjetas "Servicios" y "Productos" con moneda, globo y chip "COBROS EN USDT · MI NEGOCIO" | pops |
| 11 | Entra al link de mi perfil… tus cobros tampoco | Tarjeta "Mi Negocio · Cobros USDT · Directo a tu billetera (BEP20)", mascota, "LINK EN MI PERFIL" y la frase final | brillo |
| — | Cierre | Logo con rebote, ondas y brillo; "Cobra en cualquier país" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Historia en tonos claros; paneles oscuros con rojo Sumiago `#E6262F`; monedas en verde azulado (genéricas, sin logos de terceros). Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: los cobros en USDT son parte de **Mi Negocio (PRO, con la membresía)**; se configura la dirección de wallet en BNB Smart Chain (BEP20, empieza por 0x y tiene 42 caracteres), un título ("Págame en USDT"), una nota y hasta 8 montos sugeridos; la portada muestra QR, dirección y botón "Copiar dirección"; el dinero llega directo a la wallet y Sumiago no guarda ni toca los fondos. No decir "sin comisiones" (la red cobra una pequeña tarifa) ni dar consejos de inversión. No prometer ganancias. No escribir «BinanTrader».
