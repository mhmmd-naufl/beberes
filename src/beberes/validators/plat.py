"""Validator plat nomor kendaraan Indonesia.

Pola umum: 1-2 huruf opsional + 1-4 digit + sampai 3 huruf opsional
mis. 'B 1234 ABC', 'AB 123 CD', 'D 4567 E'.

TODO: verifikasi sumber - format plat resmi (Permenhub) bisa lebih
ketat soal jumlah digit dan kode wilayah huruf. Versi ini longgar.
"""

import re

# huruf opsional di depan, spasi, 1-4 digit, spasi opsional + huruf opsional
_RE_PLAT = re.compile(
    r"^[A-Z]{1,2}\s*\d{1,4}\s*[A-Z]{0,3}$", re.IGNORECASE
)


def periksa_plat(nilai) -> list[str]:
    """Kembalikan ['PLAT001'] kalau tidak cocok pola umum."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    if _RE_PLAT.match(teks.upper()):
        return []
    return ["PLAT001"]
