# Vedabase ZIM

Offline archive of [Vedabase Original Edition](https://vedabase.cc) — the complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupada — in [ZIM format](https://wiki.openzim.org/wiki/ZIM_file_format) for use with [Kiwix](https://kiwix.org).

## Download

- [vedabase.zim on archive.org](https://archive.org/details/vedabase-zim)

## Building from source

Current builder (v2): `build_zim_d1.py`, from the vedabase.cc D1 export
(`vedabase-original/scripts/export_d1.sh`, copied to `build/d1md/`):

```bash
python build_zim_d1.py build/vedabase_en_all_YYYY-MM.zim build/icon48.png
```

Needs `libzim`, `markdown`, `pillow`. The steps below are the old v1 builder.

### Old v1 builder

### Requirements

- Python 3.10+
- [python-libzim](https://pypi.org/project/libzim/) (`pip install libzim`)

### Steps

1. Place `vedabase.md` in the same directory as `build_zim.py`
2. Run the build script:

```bash
python build_zim.py
```

This produces `vedabase.zim` in the current directory.

### Notes

- The build uses `zstd` compression for standard ZIM compatibility
- All 7 required metadata fields (Title, Description, Language, Creator, Publisher, Date, Name) are included — Kiwix will not open ZIM files with missing metadata
- The `Item` subclass must implement `get_hints()` — python-libzim 3.9+ requires this

## Opening

Open `vedabase.zim` with [Kiwix](https://kiwix.org/en/download/) on any platform (Windows, macOS, Linux, Android, iOS).
