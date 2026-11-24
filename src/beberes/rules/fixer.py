"""Fixer untuk temuan dari rules engine.

Baru HP001 yang punya perbaikan aman (normalisasi +62).
NAMA001 (gelar) butuh keputusan kolom tujuan -> tidak otomatis.
"""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..validators import normalisasi_hp, pisah_gelar

PETA = {"HP001": "normalisasi_hp", "NAMA001": "pisah_gelar"}


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        if temuan.kode == "HP001":
            baru = normalisasi_hp(nilai)
        elif temuan.kode == "NAMA001":
            baru = pisah_gelar(nilai)
        else:
            continue
        if baru is None or baru == nilai:
            continue
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan=PETA.get(temuan.kode, temuan.kode.lower()),
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
            # NAMA001 mengubah makna (gelar hilang dari kolom nama) -> konfirmasi
            aman_otomatis=temuan.kode != "NAMA001",
        ))
    return hasil
