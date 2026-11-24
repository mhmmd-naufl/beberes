"""Validator nomor HP Indonesia.

Normalisasi ke format '+62...' (docs/03 bagian 3):
  '0812-3456-7890' -> '+6281234567890'
  '81234567890'    -> '+6281234567890'
  '+62 812-...'    -> '+62812...'

Kode masalah:
  HP001 - format tidak konsisten (bisa dinormalisasi)
  HP002 - nomor tidak valid (panjang di luar akal)
"""

import re

# Panjang nomor setelah '+62': umumnya 9-11 digit (08xx -> 8xx).
_PANJANG_MIN = 9
_PANJANG_MAKS = 13


def normalisasi_hp(nilai) -> str | None:
    """Kembalikan HP ternormalisasi '+62...', atau None kalau mustahil."""
    if nilai is None:
        return None
    digit = re.sub(r"\D", "", str(nilai))
    if not digit:
        return None
    if digit.startswith("62"):
        digit = digit[2:]
    elif digit.startswith("0"):
        digit = digit[1:]
    if not (_PANJANG_MIN <= len(digit) <= _PANJANG_MAKS):
        return None
    return "+62" + digit


def periksa_hp(nilai) -> list[str]:
    """Kembalikan kode masalah: HP001 (perlu normalisasi) / HP002 (invalid)."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    normal = normalisasi_hp(teks)
    if normal is None:
        return ["HP002"]
    # Perlu dinormalisasi kalau bentuk aslinya bukan '+62...' murni.
    if not re.fullmatch(r"\+62\d+", teks.replace(" ", "")):
        return ["HP001"]
    return []
