# vedabase-zim

Archivo ZIM (Kiwix) del Vedabase Original. El generador vigente es
`build_zim_d1.py`, que parte del export de D1 de vedabase.cc; `build_zim.py` es
el v1 viejo, que ya no se usa.

Se construye con el `python3.14` de Homebrew: es el unico interprete del mini
que tiene `markdown`, `libzim` y `pillow`.

```
/opt/homebrew/bin/python3.14 build_zim_d1.py build/vedabase_en_all_2026-10.zim build/icon48.png
```

## Current Work
- Rama `master`: ZIM rehecho desde la fuente y **ya subido y verificado** en
  `r2://vedabase-files/vedabase_en_all_2026-10.zim` (sha256 `472fc065…eed8eee6`,
  61.575.844 bytes). Resueltos los dos puntos de la revision de Kiwix (titulos
  cortados a 80, indice de Light of the Bhagavata sin enlaces) y dos defectos
  propios que salieron despues (el lugar pegado en los titulos de carta, el
  sufijo `(2)` en el indice de `krp`).
- **Siguiente accion:** pegar en openzim/zim-requests#1703 la respuesta ya
  redactada a @Popolechien (borrador en el historial de la sesion del 16-oct;
  si se ha perdido, rehacerlo con los datos de `PROGRESS.md`). Lo unico sin
  verificar es `zimcheck`: no hay zim-tools en el mini.
- Detalle y verificaciones: `PROGRESS.md`.
