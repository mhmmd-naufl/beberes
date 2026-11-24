"""Validator NPWP (Nomor Pokok Wajib Pajak).

Dua format yang beredar (docs/03 bagian 3):
  - lama: 15 digit, format XX.XXX.XXX.X-XXX.XXX
  - baru: 16 digit (mengikuti struktur NIK)

Yang dicek di sini hanya POLA, bukan keaslian di database pajak.

Kode masalah:
  NPWP001 - format tidak valid
"""

import re

# NPWP lama: 2 digit, titik, 3 digit, titik, 3 digit, titik, 1 digit,
# strip, 3 digit, titik, 3 digit  -> total 15 digit.
_RE_NPWP_LAMA = re.compile(r"^\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}$")
_RE_15_DIGIT = re.compile(r"^\d{15}$")
_RE_16_DIGIT = re.compile(r"^\d{16}$")


def periksa_npwp(nilai) -> list[str]:
    """Kembalikan ['NPWP001'] kalau format tidak valid."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    if _RE_NPWP_LAMA.match(teks) or _RE_15_DIGIT.match(teks) or _RE_16_DIGIT.match(teks):
        return []
    return ["NPWP001"]
