"""Detector TGL001/002/003: format tanggal campur, ambigu, mustahil."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from ..profiling.tipe import apakah_tanggal_ambigu, deteksi_format_tanggal
from .umum import iter_sel

_TIPE_KOLOM = {"tanggal", "campuran"}


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    hasil = []
    for c, k in enumerate(profil.kolom):
        if k.tipe_utama not in _TIPE_KOLOM:
            continue
        nama = lembar.header[c] if c < len(lembar.header) else f"kolom_{c + 1}"
        format_ditemukan = set()
        semua_tanggal, ambigu, mustahil = [], [], []
        for ci, nilai, no_excel in iter_sel(lembar):
            if ci != c or not isinstance(nilai, str):
                continue
            fmt = deteksi_format_tanggal(nilai.strip())
            if fmt is None:
                mustahil.append((no_excel, nilai))
            else:
                format_ditemukan.add(fmt)
                semua_tanggal.append((no_excel, nilai))
                if apakah_tanggal_ambigu(nilai.strip()):
                    ambigu.append((no_excel, nilai))

        if len(format_ditemukan) > 1:
            hasil.append(Temuan(
                kode="TGL001", kolom=nama, tingkat="peringatan",
                pesan=f"{len(format_ditemukan)} format tanggal berbeda dalam satu kolom",
                baris=[n for n, _ in semua_tanggal],
                contoh=sorted(format_ditemukan),
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in semua_tanggal],
            ))
        if ambigu:
            hasil.append(Temuan(
                kode="TGL002", kolom=nama, tingkat="peringatan",
                pesan="Tanggal ambigu (dd/mm vs mm/dd) — butuh konfirmasi",
                baris=[n for n, _ in ambigu],
                contoh=[v for _, v in ambigu[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in ambigu],
            ))
        if mustahil:
            hasil.append(Temuan(
                kode="TGL003", kolom=nama, tingkat="error",
                pesan="Nilai tidak bisa dibaca sebagai tanggal",
                baris=[n for n, _ in mustahil],
                contoh=[v for _, v in mustahil[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in mustahil],
            ))
    return hasil
