"""Deteksi gelar akademik/keagamaan yang menempel di nama.

Contoh: 'Drs. Budi Santoso', 'Budi Santoso, S.Kom.', 'H. Ahmad, M.A.'

Kode masalah:
  NAMA001 - gelar menempel di nama (bisa dipisah ke kolom lain)
"""

import re

# Daftar gelar umum Indonesia. Dapat diperluas.
# TODO: verifikasi sumber - daftar lengkap gelar akademik resmi.
GELAR = {
    "dr", "drs", "dra", "ir", "h", "hj", "kh", "ny", "prof",
    "s", "st", "sh", "se", "si", "ss", "m", "mh", "mt", "ma",
    "mba", "mkom", "msi", "mk", "mm", "mp", "ak", "apt", "amd",
    "phd", "drh", "drg",
}

# 'S.Kom', 'M.Kom' -> setelah strip titik = 'skom' -> perlu cek awalan 's','m'
_AWALAN_GELAR = {"dr", "drs", "dra", "ir", "h", "hj", "kh", "ny", "prof"}

_RE_CALON = re.compile(r"[A-Za-z.]+")


def _adalah_gelar(teks: str) -> bool:
    """Cek apakah satu token (boleh bertitik) adalah gelar."""
    bersih = teks.strip(".").lower()
    if not bersih:
        return False
    # 'S.Kom' -> 's.kom' -> ambil segmen pertama
    segmen_pertama = bersih.split(".")[0]
    return segmen_pertama in GELAR or bersih in GELAR


def periksa_gelar(nilai) -> list[str]:
    """Kembalikan ['NAMA001'] kalau nama mengandung gelar."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    for token in re.split(r"[\s,]+", teks):
        token = token.strip(".")
        if token and _adalah_gelar(token):
            return ["NAMA001"]
    return []
