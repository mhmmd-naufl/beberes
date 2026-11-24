"""Validator wilayah (kota/provinsi) terhadap data referensi.

- Normalisasi: rapikan spasi, 'Kota X'/'Kab. X' -> 'X', kapitalisasi.
- Cocokkan exact dulu; kalau gagal, fuzzy-match (difflib) untuk saran.

Kode masalah:
  WIL001 - nama wilayah tidak dikenal (mungkin typo)
"""

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data" / "wilayah.json"


@lru_cache(maxsize=1)
def _daftar() -> list[str]:
    data = json.loads(_DATA.read_text(encoding="utf-8"))
    return sorted(set(data.get("provinsi", []) + data.get("kota", [])))


_PREFIX = re.compile(r"^(kota|kabupaten|kab|kecamatan|kec)\.?\s+", re.IGNORECASE)
_SPASI = re.compile(r"\s+")


def normalisasi_wilayah(nilai) -> str:
    """Rapikan nama wilayah: buang prefix administrasi, spasi, kapital."""
    teks = _SPASI.sub(" ", str(nilai)).strip()
    teks = _PREFIX.sub("", teks)
    return teks.title()


def saran_wilayah(nilai) -> str | None:
    """Kembalikan nama wilayah terdekat (fuzzy) atau None."""
    norm = normalisasi_wilayah(nilai)
    daftar = _daftar()
    if norm in daftar:
        return norm
    cocok = difflib.get_close_matches(norm, daftar, n=1, cutoff=0.75)
    return cocok[0] if cocok else None


def periksa_wilayah(nilai) -> list[str]:
    """Kembalikan ['WIL001'] kalau nama tidak ada di daftar referensi."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    if normalisasi_wilayah(teks) in _daftar():
        return []
    return ["WIL001"]
