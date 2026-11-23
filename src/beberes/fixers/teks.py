"""Fixer FMT001 (rapikan spasi) dan FMT002 (kapitalisasi)."""

from ..io import Lembar
from ..model import Perbaikan, Temuan


def _baris_ke_idx(lembar: Lembar, baris_excel: int) -> int | None:
    try:
        return lembar.baris_excel.index(baris_excel)
    except ValueError:
        return None


def _nilai_baru(teks: str, kode: str) -> str:
    if kode == "FMT001":
        return " ".join(teks.split())
    # FMT002: kapitalkan tiap kata, huruf lain kecil.
    return " ".join(w.capitalize() for w in teks.split())


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        if not isinstance(nilai, str):
            continue
        baru = _nilai_baru(nilai, temuan.kode)
        if baru == nilai:
            continue
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan=temuan.kode.lower(),
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
        ))
    return hasil
