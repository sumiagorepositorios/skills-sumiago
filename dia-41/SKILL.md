---
name: dia-41
description: Crea el video del Día 41 de Tareas Diarias de Sumiago, "Las citas de Karen" (historia ilustrativa: una manicurista que agendaba en un cuaderno y respondía mensajes hasta las 11 p. m. activa la agenda de citas de Mi Negocio en su portada de Sumiago y sus clientas reservan solas), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 41.
---

# Día 41 — "Las citas de Karen"

Reel vertical de unos 61 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Karen hace uñas en su casa y su celular no para: "¿Tienes cupo mañana?", "¿Y a las cuatro?", "¿Y el sábado?"; a las 11 p. m. sigue respondiendo. Anota en un cuaderno hasta que llegan 2 clientas a la misma hora. Con su membresía activa **Mi Negocio** en su portada de Sumiago y prende la **agenda de citas**: pone sus días, su horario y la duración de cada cita. La clienta entra a su enlace, ve las horas libres y escoge la suya; una hora ocupada nadie más la puede tomar. Karen ve todas sus citas en un solo lugar. "Ahora las noches son para descansar." Cierra: "Tu tiempo también vale."

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
python ruta/dia-41/scripts/voz.py
python ruta/dia-41/scripts/tl.py
python ruta/dia-41/scripts/align.py
python ruta/dia-41/scripts/audio.py
python ruta/dia-41/scripts/render.py 0 610 a.mp4
python ruta/dia-41/scripts/render.py 610 1220 b.mp4
python ruta/dia-41/scripts/render.py 1220 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-41.mp4
python ruta/dia-41/scripts/pc.py dia-41.mp4 dia-41-pc.mp4
```

Para revisar un momento: `python ruta/dia-41/scripts/render.py still 31 33.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Karen hace uñas… su celular no la deja en paz | Salón rosado con esmaltes; celular que vibra con contador de mensajes; chip "NO LA DEJA EN PAZ" | vibraciones |
| 1 | ¿Tienes cupo? ¿Y a las cuatro? ¿Y el sábado? 11 p. m. | Noche, burbujas de clientas y chip "11:00 p. m."; Karen con el celular iluminado | música bajita |
| 2 | Cuaderno… 2 clientas a la misma hora | Cuaderno con "3:00 - Lina", "4:00 - Sandra", "3:00 - Marcela"; dos clientas que llegan con "3:00"; sello "MISMA HORA" | golpe |
| 3 | Su agenda no podía depender de su memoria | Karen con nube de pensamiento y el cuaderno tachado; sello "NO MÁS DE MEMORIA" | |
| 4 | Con su membresía activó Mi Negocio… agenda de citas | Panel "Mi Negocio PRO" con pestañas Catálogo / Cobros USDT / Agenda / Clientes; interruptor "Recibir reservas desde mi portada" que se activa | ding |
| 5 | Días, horario, cuánto dura cada cita | Días L–S marcados, horario 9:00 a. m. → 6:00 p. m., "1 hora" | pops |
| 6 | La clienta entra… ve las horas libres y escoge | Celular "Uñas Karen · sumiago.com/unas-karen · Agenda tu cita" con horas libres y ocupadas; toque en 4:00 y "Reservado: 4:00 p. m." | |
| 7 | Una hora ocupada nadie más la toma | Intento sobre 3:00 ocupada que tiembla, candado y sello "NADIE MÁS LA TOMA" | golpe |
| 8 | Todas sus citas en un solo lugar… sin cuaderno | Lista "Mis citas · Viernes 28"; el cuaderno sale volando; chip "SIN REPETIR 20 VECES" | |
| 9 | Las noches son para descansar… se agendan solas | Karen durmiendo y avisos "Nueva cita…" que llegan solos | dings suaves |
| 10 | Uñas, barbería, belleza o consultas | Cuatro tarjetas y chip "AGENDA EN MI NEGOCIO" | pops |
| 11 | Entra al link de mi perfil… tu tiempo también vale | Tarjeta "Mi Negocio · Agenda de citas en tu portada", mascota, "LINK EN MI PERFIL" y "Tu tiempo también vale." | |
| — | Cierre | Logo con rebote, ondas y brillo; "Tu tiempo también vale" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Salón rosado y noche azul para la historia; paneles en rojo Sumiago `#E6262F`, blanco y gris. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: la agenda de citas es parte de **Mi Negocio (PRO)**, que se desbloquea con la membresía (decirlo); el dueño configura días, horario, duración y anticipación; la clienta reserva desde la portada y una hora ocupada no se puede volver a tomar; las citas se ven en el panel. No prometer clientes ni ganancias. No escribir «BinanTrader».
