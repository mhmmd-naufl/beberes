"""Klasifikasi tipe satu nilai sel.

Tipe yang dikenal: kosong, tanggal, uang, angka, teks.
Deteksi format Indonesia: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, dd.mm.yyyy,
'd Mon yyyy' (nama bulan Indonesia), 'Rp 25.000', '25.000,00'.
"""

import re
from datetime import datetime

TIPE_KOSONG = "kosong"
TIPE_TANGGAL = "tanggal"
TIPE_UANG = "uang"
TIPE_ANGKA = "angka"
TIPE_TEKS = "teks"

SEMUA_TIPE = (TIPE_KOSONG, TIPE_TANGGAL, TIPE_UANG, TIPE_ANGKA, TIPE_TEKS)

_BULAN_ID = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6,
    "jul": 7, "agu": 8, "ags": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
    "dec": 12,
}

_FORMAT_TANGGAL = (
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y",
    "%d %b %Y", "%d %B %Y",
)

_RE_ANGKA = re.compile(r"^[+-]?\d{1,3}([.,]\d{3})*([.,]\d+)?$|^[+-]?\d+(\.\d+)?$")
_RE_UANG = re.compile(
    r"^(rp\.?\s*)?[+-]?\d{1,3}(\.\d{3})*(,\d{1,2})?\s*(rp\.?)?$", re.IGNORECASE
)


def _coba_tanggal(teks: str) -> bool:
    for fmt in _FORMAT_TANGGAL:
        try:
            datetime.strptime(teks, fmt)
            return True
        except ValueError:
            continue
    # Format 'd Mon yyyy' dengan nama bulan Indonesia (strptime %b tidak kenal).
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", teks)
    if m and m.group(2).lower()[:3] in _BULAN_ID:
        try:
            datetime(int(m.group(3)), _BULAN_ID[m.group(2).lower()[:3]], int(m.group(1)))
            return True
        except ValueError:
            return False
    return False


def _coba_uang(teks: str) -> bool:
    """Angka dengan penanda Rp atau pemisah ribuan bertitik."""
    if not _RE_UANG.match(teks):
        return False
    return "rp" in teks.lower() or "." in teks


def _coba_angka(teks: str) -> bool:
    return bool(_RE_ANGKA.match(teks))


def deteksi_tipe(nilai) -> str:
    """Kembalikan tipe satu nilai sel."""
    if nilai is None:
        return TIPE_KOSONG
    if isinstance(nilai, bool):
        return TIPE_TEKS
    if isinstance(nilai, (int, float)):
        return TIPE_ANGKA
    teks = str(nilai).strip()
    if teks == "":
        return TIPE_KOSONG
    if _coba_tanggal(teks):
        return TIPE_TANGGAL
    if _coba_uang(teks):
        return TIPE_UANG
    if _coba_angka(teks):
        return TIPE_ANGKA
    return TIPE_TEKS
