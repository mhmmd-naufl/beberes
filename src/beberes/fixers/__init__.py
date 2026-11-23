"""Ubah Temuan menjadi usulan Perbaikan."""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from . import angka, tanggal, teks, uang

_PETA = {
    "FMT001": teks.perbaiki,
    "FMT002": teks.perbaiki,
    "UANG001": uang.perbaiki,
    "NUM001": angka.perbaiki,
    "TGL001": tanggal.perbaiki,
    "TGL002": tanggal.perbaiki,
}


def usulkan(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    """Kembalikan daftar Perbaikan untuk satu Temuan (kosong kalau tak dikenal)."""
    fungsi = _PETA.get(temuan.kode)
    return fungsi(temuan, lembar) if fungsi else []


def usulkan_semua(temuan_list: list[Temuan], lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for t in temuan_list:
        hasil.extend(usulkan(t, lembar))
    return hasil
