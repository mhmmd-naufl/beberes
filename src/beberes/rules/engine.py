"""Engine aturan: terapkan aturan YAML ke Lembar -> Temuan.

Kolom yang disebut di aturan dipetakan ke validator yang sesuai
tipe-nya (docs/03). Nama kolom dicocokkan persis (case-insensitive).
"""

from ..io import Lembar
from ..model import Temuan
from ..validators import (
    periksa_gelar,
    periksa_hp,
    periksa_nik,
    periksa_npwp,
    periksa_plat,
    periksa_wilayah,
    saran_wilayah,
)
from .skema import Aturan

# Tipe kolom -> fungsi validator (nilai -> list kode masalah).
# Wilayah butuh data referensi (belum ada), email belum ada validator.
VALIDATOR = {
    "nik": periksa_nik,
    "hp": periksa_hp,
    "npwp": periksa_npwp,
    "plat": periksa_plat,
    "nama": periksa_gelar,
    "wilayah": periksa_wilayah,
}

PESAN = {
    "NIK001": "NIK bukan 16 digit",
    "NIK002": "Kode wilayah NIK tidak dikenal",
    "NIK003": "Tanggal lahir di NIK tidak valid",
    "HP001": "Format nomor HP tidak konsisten",
    "HP002": "Nomor HP tidak valid",
    "NPWP001": "Format NPWP tidak valid",
    "PLAT001": "Format plat nomor tidak dikenal",
    "NAMA001": "Gelar menempel di nama",
    "WIL001": "Nama wilayah tidak dikenal",
}


def _cari_kolom(lembar: Lembar, nama: str) -> int | None:
    target = nama.strip().lower()
    for i, h in enumerate(lembar.header):
        if h and h.strip().lower() == target:
            return i
    return None


def periksa(lembar: Lembar, aturan: Aturan) -> list[Temuan]:
    """Jalankan validator sesuai aturan ke satu Lembar."""
    hasil = []
    for nama_kolom, spec in aturan.kolom.items():
        fungsi = VALIDATOR.get(spec.tipe)
        if fungsi is None:
            continue
        c = _cari_kolom(lembar, nama_kolom)
        if c is None:
            continue
        ketemu: dict[str, list] = {}
        for baris, no_excel in zip(lembar.baris, lembar.baris_excel, strict=False):
            nilai = baris[c] if c < len(baris) else None
            if nilai is None or str(nilai).strip() == "":
                continue
            for kode in fungsi(nilai):
                ketemu.setdefault(kode, []).append((no_excel, nilai))
        for kode, sel_daftar in ketemu.items():
            pesan = PESAN.get(kode, kode)
            if kode == "WIL001":
                saran = saran_wilayah(sel_daftar[0][1])
                if saran:
                    pesan = f"{pesan} (saran: {saran})"
            hasil.append(Temuan(
                kode=kode, kolom=nama_kolom, tingkat="peringatan",
                pesan=pesan,
                baris=[n for n, _ in sel_daftar],
                contoh=[str(v) for _, v in sel_daftar[:3]],
                sel=[{"baris_excel": n, "kolom_idx": c, "nilai": v}
                     for n, v in sel_daftar],
            ))
    return hasil
