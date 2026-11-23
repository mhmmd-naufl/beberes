"""Fixer NUM001: angka sebagai teks ('1 250') -> angka."""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..profiling.tipe import parse_angka_teks


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        baru = parse_angka_teks(nilai) if isinstance(nilai, str) else None
        if baru is None or baru == nilai:
            continue
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan="ke_angka",
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
        ))
    return hasil
