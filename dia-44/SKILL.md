---
name: dia-44
description: Crea el video del Día 44 de Tareas Diarias de Sumiago, "Lo voy a pensar" (historia ilustrativa: en una mueblería los interesados se iban sin dejar su número; doña Nubia activa la captura de clientes de Mi Negocio en su portada de Sumiago, guarda la lista, la descarga para Excel y les escribe cuando llega la nueva colección), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 44.
---

# Día 44 — "Lo voy a pensar"

Reel vertical de unos 58 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). En la mueblería de doña Nubia la frase más escuchada era "lo voy a pensar": la gente se iba sin dejar nombre ni número y casi nunca volvía; no era que no les gustara, es que nadie les volvía a escribir. Con su membresía activa la **captura de clientes** en **Mi Negocio** de su portada de Sumiago: en su enlace aparece "Déjame tus datos y te contacto", el interesado pone nombre, WhatsApp y correo en segundos, y Nubia ve la lista en su panel y la descarga en un archivo para Excel. Cuando llega la nueva colección, les escribe a todos los que habían dicho "lo voy a pensar"… y algunos ya lo habían pensado. Cierra: "Que nadie se vaya sin dejar su número."

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
python ruta/dia-44/scripts/voz.py
python ruta/dia-44/scripts/tl.py
python ruta/dia-44/scripts/align.py
python ruta/dia-44/scripts/audio.py
python ruta/dia-44/scripts/render.py 0 590 a.mp4
python ruta/dia-44/scripts/render.py 590 1180 b.mp4
python ruta/dia-44/scripts/render.py 1180 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-44.mp4
python ruta/dia-44/scripts/pc.py dia-44.mp4 dia-44-pc.mp4
```

Para revisar un momento: `python ruta/dia-44/scripts/render.py still 26.5 31.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | En la mueblería… «lo voy a pensar» | Mueblería con sofá y lámpara; cliente con burbuja; chip "LA FRASE MÁS ESCUCHADA" | se aleja |
| 1 | Se iban sin nombre ni número… casi nunca volvían | Clientes que salen por la puerta; tarjeta "Nombre: — / Número: —"; sello "CASI NUNCA VOLVÍAN" | puerta; música bajita |
| 2 | Sí les gustaba… nadie les volvió a escribir | Corazón "SÍ LES GUSTABA" y celular con "0"; chip "NADIE LES ESCRIBIÓ" | |
| 3 | Con su membresía activó la captura de clientes | Panel "Mi Negocio PRO", pestaña Clientes, interruptor "Captura de clientes" | ding |
| 4 | «Déjame tus datos y te contacto» | Portada "Mueblería Nubia · sumiago.com/muebleria-nubia" con el formulario | la cámara se acerca |
| 5 | Nombre, WhatsApp y correo en 10 segundos | Los campos se llenan; chip "EN 10 SEGUNDOS" | tecleo + ding |
| 6 | Ve la lista y la descarga para Excel | Tabla "Clientes" (Nombre, WhatsApp, Fecha), botón verde "Descargar para Excel" y archivo CSV | |
| 7 | Llegó la nueva colección… sin esperar | Camión "NUEVO"; chip "NUEVA COLECCIÓN"; sello "SIN ESPERAR" | |
| 8 | Les escribió a todos | Celular "Mensaje para tu lista" con ✓ en cada interesado | dings |
| 9 | Y algunos… ya lo habían pensado | Respuestas "¡Sí! Lo quiero", "¿Todavía está el sofá azul?", "Paso el sábado"; sello "YA LO HABÍAN PENSADO" | brillo |
| 10 | Un interesado que se va… oportunidad que se pierde | Persona que se aleja ("OPORTUNIDAD PERDIDA") frente a la lista "Interesados" ("GUARDADOS") | |
| 11 | Entra al link de mi perfil… sin dejar su número | Tarjeta "Mi Negocio · Clientes · Tus interesados en una lista · DESCARGABLE PARA EXCEL", mascota, "LINK EN MI PERFIL" y "Que nadie se vaya sin dejar su número." | |
| — | Cierre | Logo con rebote, ondas y brillo; "Guarda a tus interesados" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Mueblería cálida y pantallas oscuras con rojo Sumiago `#E6262F`; verde Excel para la descarga. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: la captura de clientes es parte de **Mi Negocio (PRO, con la membresía)**; el formulario de la portada ("Déjame tus datos y te contacto") pide nombre, WhatsApp y correo, y el dueño ve la lista en la pestaña Clientes y la exporta en CSV (se abre en Excel). Los mensajes a la lista los envía el dueño. No prometer ventas ni ganancias. No escribir «BinanTrader».
