---
name: dia-62
description: Crea el video del Día 62 de Tareas Diarias de Sumiago, "A la vuelta de la esquina" (historia ilustrativa: doña Marleny cocina almuerzos caseros que solo conoce su cuadra; los publica en «Comida casera» › «Almuerzos» y Andrés, recién mudado, comparte su ubicación, ordena por «Más cercanos a mí» y la encuentra), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 62.
---

# Día 62 — "A la vuelta de la esquina"

Reel vertical de unos 65 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Doña Marleny cocina los mejores almuerzos de su barrio (sancocho, frijoles, sudado de pollo), pero solo le compran los vecinos de la cuadra. Su hija la ayuda a publicar en el Marketplace de Sumiago en **«Comida casera» › «Almuerzos»**: foto del plato, precio y ciudad. Andrés acaba de mudarse y no sabe dónde almorzar; entra al Marketplace, el navegador le pregunta si quiere **compartir su ubicación**, dice que sí y aparece **«Más cercanos a mí»**: los anuncios de su ciudad salen primero y ahí está el almuerzo de doña Marleny. Toca «¡Lo quiero!», le escribe por WhatsApp y ese mediodía almuerza como en casa; hoy le encarga casi todos los días y le llevó a tres compañeros. La ubicación se puede quitar cuando quieras. Cierra: "Lo que buscas… a veces está a la vuelta de la esquina."

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
python ruta/dia-62/scripts/voz.py
python ruta/dia-62/scripts/tl.py
python ruta/dia-62/scripts/align.py
python ruta/dia-62/scripts/audio.py
python ruta/dia-62/scripts/render.py 0 600 a.mp4
python ruta/dia-62/scripts/render.py 600 1200 b.mp4
python ruta/dia-62/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-62.mp4
python ruta/dia-62/scripts/pc.py dia-62.mp4 dia-62-pc.mp4
```

Para revisar un momento: `python ruta/dia-62/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Los mejores almuerzos del barrio | Doña Marleny en su cocina; aparecen los platos con su nombre | se aleja |
| 1 | Solo la cuadra… nadie sabía | Mapa de casas con la cuadra resaltada y signos de pregunta; sello "NADIE SABÍA" | música bajita |
| 2 | «Comida casera» › «Almuerzos» | Formulario: categoría y subcategorías; chip "CON AYUDA DE SU HIJA" | ding |
| 3 | Foto, precio y ciudad | Anuncio "Almuerzo casero del día · $ 15.000 · Bucaramanga" | obturador |
| 4 | Andrés recién mudado | Andrés con cajas y burbuja "¿Dónde almuerzo?" | |
| 5 | ¿Compartir ubicación? | Ventana del navegador "sumiago.com quiere conocer tu ubicación" | ding |
| 6 | Sí → «Más cercanos a mí» | "Usando tu ubicación · quitar" y menú de orden con "Más cercanos a mí" | brillo |
| 7 | Su ciudad primero | Lista ordenada; el almuerzo arriba con borde dorado | ding |
| 8 | «¡Lo quiero!», WhatsApp… como en casa | Botón, mensaje y Andrés almorzando; chip "COMO EN CASA" | brillo |
| 9 | Casi todos los días, +3 compañeros | Mesa con cuatro platos | pops |
| 10 | Ubicación: más cercano, la quitas cuando quieras | Tarjeta con pin "Más cercanos a mí" | pops |
| 11 | Entra al link… a la vuelta de la esquina | Tarjeta "Marketplace Sumiago · Lo más cercano a ti", mascota y frase final | |
| — | Cierre | Logo; "Encuentra lo cercano" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): categoría «Comida casera» (Almuerzos, Desayunos, Postres y tortas, Comida rápida, Panadería, Bebidas, Comida típica, Por encargo); en marketplace/index.php el navegador pide (una vez) compartir la ubicación; con ella aparece «Usando tu ubicación · quitar» y el orden «Más cercanos a mí» (por las coordenadas de la ciudad del anuncio). No decir que muestra la dirección exacta ni distancias en metros.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
