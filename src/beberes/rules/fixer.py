"""Fixer untuk temuan dari rules engine.

Baru HP001 yang punya perbaikan aman (normalisasi +62).
NAMA001 (gelar) butuh keputusan kolom tujuan -> tidak otomatis.
"""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..validators import normalisasi_hp

PETA = {"HP001": "normalisasi_hp"}


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        if temuan.kode == "HP001":
            baru = normalisasi_hp(nilai)
        else:
            continue
        if baru is None or baru == nilai:
            continue
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan=PETA.get(temuan.kode, temuan.kode.lower()),
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
        ))
    return hasil
