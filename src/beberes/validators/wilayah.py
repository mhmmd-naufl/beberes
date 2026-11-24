"""Validator wilayah (kabupaten/kota/provinsi/kecamatan) terhadap data resmi.

Data referensi: `src/beberes/data/wilayah.json` — hasil parse repo
cahyadsn/wilayah (lisensi MIT, Kepmendagri 300.2.2-2138 Tahun 2025).
Level desa/kelurahan belum dibundel (ukuran file).

- Normalisasi: rapikan spasi, 'Kota X'/'Kab. X'/'Kec. X' -> 'X'.
- Cocokkan exact nama (semua level digabung); fuzzy-match untuk saran.
- `kode_wilayah` dipakai validator NIK untuk cek kode provinsi/kab/kec.

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
def _mentah() -> dict:
    return json.loads(_DATA.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _semua() -> list[dict]:
    d = _mentah()
    return d.get("provinsi", []) + d.get("kabupaten", []) + d.get("kecamatan", [])


@lru_cache(maxsize=1)
def _daftar() -> list[str]:
    return sorted({w["nama"] for w in _semua()})


@lru_cache(maxsize=1)
def _kode_set() -> set[str]:
    return {w["kode"] for w in _semua()}


@lru_cache(maxsize=1)
def _nama_per_kode() -> dict[str, str]:
    return {w["kode"]: w["nama"] for w in _semua()}


_PREFIX = re.compile(
    r"^(kota|kabupaten|kab|kecamatan|kec|provinsi|prop)\.?\s+", re.IGNORECASE
)
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


def kode_wilayah_valid(kode_6_digit: str) -> bool:
    """Cek apakah kode wilayah 6 digit (prov+kab+kec) ada di data resmi.

    Dipakai validator NIK untuk NIK002.
    """
    return kode_6_digit in _kode_set()


def nama_wilayah(kode: str) -> str | None:
    """Nama wilayah dari kode (mis. '32.01.01' atau segmen NIK)."""
    return _nama_per_kode().get(kode)
