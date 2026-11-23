"""Detector FMT001 (spasi berlebih/di tepi) dan FMT002 (kapitalisasi acak)."""

import re

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from .umum import iter_sel

_TIPE_TARIK = {"teks", "campuran"}

_RE_SPASI_BURUK = re.compile(r"^\s|\s$|\s{2,}")
# Huruf kecil diikuti huruf besar di tengah kata: 'pROfounD', 'sItUmOrAnG'.
_RE_KAPITAL_ACAK = re.compile(r"[a-zà-ÿ][A-ZÀ-Þ]")


def _adalah_kapital_acak(teks: str) -> bool:
    """Ada kata dengan kapital di tengah yang bukan singkatan bermakna."""
    for kata in re.findall(r"[A-Za-zÀ-ÿ]+", teks):
        if len(kata) > 2 and _RE_KAPITAL_ACAK.search(kata):
            return True
    return False


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    hasil = []
    tipe_per_kolom = {i: k.tipe_utama for i, k in enumerate(profil.kolom)}

    for c, tipe in tipe_per_kolom.items():
        if tipe not in _TIPE_TARIK:
            continue
        nama = lembar.header[c] if c < len(lembar.header) else f"kolom_{c + 1}"
        spasi, kapital = [], []
        for ci, nilai, no_excel in iter_sel(lembar):
            if ci != c or not isinstance(nilai, str):
                continue
            if _RE_SPASI_BURUK.search(nilai):
                spasi.append((no_excel, nilai))
            if _adalah_kapital_acak(nilai):
                kapital.append((no_excel, nilai))

        if spasi:
            hasil.append(Temuan(
                kode="FMT001", kolom=nama, tingkat="peringatan",
                pesan="Spasi berlebih atau di tepi sel",
                baris=[n for n, _ in spasi],
                contoh=[v for _, v in spasi[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in spasi],
            ))
        if kapital:
            hasil.append(Temuan(
                kode="FMT002", kolom=nama, tingkat="peringatan",
                pesan="Kapitalisasi huruf tidak konsisten",
                baris=[n for n, _ in kapital],
                contoh=[v for _, v in kapital[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v} for n, v in kapital],
            ))
    return hasil
