"""Fixer TGL001/TGL002: tanggal -> format ISO yyyy-mm-dd.

Tanggal ambigu (TGL002, dan sel ambigu di dalam TGL001) tetap dibuatkan
pratinjau dengan asumsi dd/mm/yyyy (kebiasaan Indonesia), tapi ditandai
aman_otomatis=False — butuh konfirmasi sesuai D-009.
"""

from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..profiling.tipe import apakah_tanggal_ambigu, parse_tanggal


def perbaiki(temuan: Temuan, lembar: Lembar) -> list[Perbaikan]:
    hasil = []
    for s in temuan.sel:
        nilai = s["nilai"]
        if not isinstance(nilai, str):
            continue
        tgl = parse_tanggal(nilai.strip())
        if tgl is None:
            continue
        baru = tgl.date().isoformat()
        ambigu = apakah_tanggal_ambigu(nilai.strip()) or temuan.kode == "TGL002"
        hasil.append(Perbaikan(
            kode=temuan.kode, aturan="ke_tanggal",
            baris_excel=s["baris_excel"], kolom_idx=s["kolom_idx"],
            kolom=temuan.kolom, nilai_lama=nilai, nilai_baru=baru,
            aman_otomatis=not ambigu,
        ))
    return hasil
