# PROGRESS — Rehacer vedabase_en_all desde la fuente (16-oct-2026)

Motivo: revisión de Kiwix (openzim/zim-requests#1703, Popolechien): títulos
cortados («1. Observing the Armies on the») e índice sin enlaces en
Light of the Bhagavata. El ZIM 2026-10 anterior era una copia del vedabase.zim
de marzo (generador perdido): 62 títulos cortados a 80 caracteres, 3 libros en
una sola página con índice en texto, conversaciones tituladas con su primera
frase. El usuario decidió rehacerlo ahora.

## Hecho (con la verificación)
- Export D1 de vedabase.cc (solo lectura) → `build/d1md/` (24 ficheros).
- `build_zim_d1.py` nuevo → `build/vedabase_en_all_2026-10.zim`
  (61,8 MB, sha256 54b03640cc06a69bd2eb75c8b2c52aa87093f58c57193f0af44d8db5ff5687b9).
  - 30.959 páginas de contenido = 30.959 filas D1 (dos recuentos).
  - 31.332 páginas HTML en total (con índices); 0 enlaces internos rotos;
    0 títulos de entrada repetidos.
  - Índice de títulos y de texto completo presentes; búsqueda «Kurukṣetra
    armies» → bg/1 primero; sugerencia «Observing the» → bg/1.
  - Comprobado a ojo (capturas headless Chrome): Bg. 1.1, índice de BG 1,
    SB 1.8.36 (conferencia 28-4-1973).
  - Títulos: «Chapter 1: Observing the Armies on the Battlefield of Kurukṣetra»,
    «SB 2.7: Scheduled Incarnations with Specific Functions»,
    conferencias «<título> — <lugar>, <fecha>», cartas «Letter to X — lugar, fecha».
  - LoB, Reservoir y el resto: índice enlazado, una página por capítulo.

## NO probado
- La lectura en la propia app Kiwix. En el mini no hay `kiwix-serve` ni
  `zimcheck`; todo lo verificado arriba es con `libzim`, que lee el fichero
  pero no es el visor. El fichero sí se abrió en Kiwix.app, y mirarlo a ojo
  (títulos del Gītā, índice de LoB, búsqueda) queda del usuario.

## Siguiente paso exacto
Responder en openzim/zim-requests#1703 diciendo que el ZIM está rehecho desde
la fuente y ya subido a la misma URL.

## Decidido (16-oct-2026)
- **El ZIM lleva lo que está en D1 y nada más** (decisión del usuario,
  16-oct-2026). Los tres libros que el ZIM viejo traía y D1 no tiene
  —Teachings of Lord Kapila, Teachings of Prahlāda Mahārāja, Second Chance—
  quedan fuera, y seguirán fuera mientras no entren en D1. `ORDER` de
  `build_zim_d1.py` son los 24 libros de D1; el generador no los contempla.
  Comprobado en el ZIM nuevo: ninguna entrada de esos tres libros (las 23
  coincidencias de «Kapila/Prahlāda» son cartas y capítulos del SB legítimos;
  el viejo tenía además `b10 Teachings of Prahlada Maharaja`).
- Subido a R2 (`vedabase-files/vedabase_en_all_2026-10.zim`, misma clave y misma
  URL, así que no hubo que desplegar el sitio). Verificado sobre lo que sirve
  R2, no sobre el log: sha256 del fichero descargado =
  54b03640cc06a69bd2eb75c8b2c52aa87093f58c57193f0af44d8db5ff5687b9, igual al
  construido; 61.775.037 bytes; `Content-Type: application/x-openzim`. Esa copia
  descargada se abrió con libzim: 31.332 artículos, título más largo de 283
  caracteres (el recorte a 80 del viejo ya no está), `bg/1` =
  «Chapter 1: Observing the Armies on the Battlefield of Kurukṣetra», búsqueda
  «Kurukṣetra armies» → `bg/1` primero.
- Abierto en Kiwix.app del Mac mini. Revisión a ojo en la app: del usuario.

## Pendiente del usuario
- Responder en openzim/zim-requests#1703.
