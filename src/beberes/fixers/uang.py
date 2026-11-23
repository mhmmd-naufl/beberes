"""Fixer UANG001: teks 'Rp 25.000' -> angka 25000."""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..profiling.tipe import parse_uang


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        baru = parse_uang(nilai) if isinstance(nilai, str) else None
        if baru is None or baru == nilai:
            continue
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan="ke_angka",
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
        ))
    return hasil
