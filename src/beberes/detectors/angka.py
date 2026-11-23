"""Detector NUM001: angka tersimpan sebagai teks ('1 250')."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from ..profiling.tipe import parse_angka_teks
from .umum import iter_sel

_TIPE_KOLOM = {"angka", "campuran"}


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
            if parse_angka_teks(nilai) is not None:
                ketemu.append((no_excel, nilai))
        if ketemu:
            hasil.append(Temuan(
                kode="NUM001", kolom=nama, tingkat="peringatan",
                pesan="Angka tersimpan sebagai teks",
                baris=[n for n, _ in ketemu],
                contoh=[v for _, v in ketemu[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in ketemu],
            ))
    return hasil
