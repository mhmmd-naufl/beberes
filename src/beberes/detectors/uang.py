"""Detector UANG001: uang tersimpan sebagai teks ('Rp 25.000')."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from ..profiling.tipe import parse_uang
from .umum import iter_sel

# Hanya kolom yang memang bertipe angka/uangka/campuran — teks biasa tidak.
_TIPE_KOLOM = {"angka", "uang", "campuran"}


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    hasil = []
    for c, k in enumerate(profil.kolom):
        if k.tipe_utama not in _TIPE_KOLOM:
            continue
        nama = lembar.header[c] if c < len(lembar.header) else f"kolom_{c + 1}"
        ketemu = []
        for ci, nilai, no_excel in iter_sel(lembar):
            if ci != c or not isinstance(nilai, str):
                continue
            if parse_uang(nilai) is not None:
                ketemu.append((no_excel, nilai))
        if ketemu:
            hasil.append(Temuan(
                kode="UANG001", kolom=nama, tingkat="peringatan",
                pesan="Uang tersimpan sebagai teks",
                baris=[n for n, _ in ketemu],
                contoh=[v for _, v in ketemu[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in ketemu],
            ))
    return hasil
