"""Validator NIK (Nomor Induk Kependudukan).

Struktur (docs/03 bagian 3): 16 digit
  - 6 digit pertama: kode wilayah (provinsi 2, kab/kota 2, kecamatan 2)
  - 6 digit berikutnya: tanggal lahir DDMMYY (perempuan: hari + 40)
  - 4 digit terakhir: nomor urut

Hanya memeriksa STRUKTUR, bukan keaslian data (bukan cek Dukcapil).

Kode masalah:
  NIK001 - bukan 16 digit
  NIK002 - kode wilayah tidak dikenal (butuh data resmi, lihat TODO)
  NIK003 - tanggal lahir di NIK tidak valid
"""

import re
from datetime import date

_RE_16_DIGIT = re.compile(r"^\d{16}$")

# Kode provinsi yang pernah dipakai (11-94, tidak semua terpakai).
# TODO: verifikasi sumber - idealnya cocokkan dengan data wilayah resmi
# (docs/04 bagian C) saat modul wilayah jadi.
_KODE_PROVINSI_VALID = {
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31, 32, 33, 34, 35, 36,
    51, 52, 53, 61, 62, 63, 64, 65, 71, 72, 73, 74, 75, 76,
    81, 82, 91, 92, 93, 94, 95, 96,
}


def _tanggal_lahir_valid(enam_digit: str) -> bool:
    """Cek DDMMYY di digit 7-12 NIK. Perempuan: hari ditambah 40."""
    try:
        hari = int(enam_digit[0:2])
        bulan = int(enam_digit[2:4])
        tahun = int(enam_digit[4:6])
    except ValueError:
        return False
    if hari > 40:
        hari -= 40  # perempuan
    if not (1 <= hari <= 31 and 1 <= bulan <= 12):
        return False
    try:
        date(2000 + tahun, bulan, hari)
    except ValueError:
        return False
    return True


def periksa_nik(nilai) -> list[str]:
    """Kembalikan daftar kode masalah untuk satu nilai NIK."""
    if nilai is None:
        return []
    teks = re.sub(r"\D", "", str(nilai))
    if not _RE_16_DIGIT.match(teks):
        return ["NIK001"]

    kode = []
    provinsi = int(teks[0:2])
    if provinsi not in _KODE_PROVINSI_VALID:
        kode.append("NIK002")
    if not _tanggal_lahir_valid(teks[6:12]):
        kode.append("NIK003")
    return kode
