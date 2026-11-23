"""Jalankan semua detector batch 1."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from . import angka, kosong, tanggal, teks, uang

SEMUA = (teks.deteksi, uang.deteksi, angka.deteksi, tanggal.deteksi, kosong.deteksi)


def jalankan(lembar: Lembar, profil: Profil) -> list[Temuan]:
    """Kembalikan semua temuan untuk satu lembar."""
    temuan = []
    for detektor in SEMUA:
        temuan.extend(detektor(lembar, profil))
    return temuan
