"""Engine aturan: terapkan aturan YAML ke Lembar -> Temuan.

Kolom yang disebut di aturan dipetakan ke validator yang sesuai
tipe-nya (docs/03). Nama kolom dicocokkan persis (case-insensitive).
"""

from ..io import Lembar
from ..model import Temuan
from ..validators import (
    induk_wilayah,
    normalisasi_wilayah,
    periksa_email,
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
    "email": periksa_email,
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
    "WIL002": "Kecamatan tidak cocok dengan kabupaten induknya",
    "EMAIL001": "Format email tidak valid",
    "KAT001": "Nilai di luar daftar yang diizinkan",
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
        if fungsi is None and not (spec.tipe == "kategori" and spec.aturan):
            continue
        c = _cari_kolom(lembar, nama_kolom)
        if c is None:
            continue
        ketemu: dict[str, list] = {}
        if fungsi is not None:
            for baris, no_excel in zip(lembar.baris, lembar.baris_excel, strict=False):
                nilai = baris[c] if c < len(baris) else None
                if nilai is None or str(nilai).strip() == "":
                    continue
                for kode in fungsi(nilai):
                    ketemu.setdefault(kode, []).append((no_excel, nilai))
        # Kategori: nilai harus ada di daftar spec.aturan
        if spec.tipe == "kategori" and spec.aturan:
            diizinkan = {str(x).strip().lower() for x in spec.aturan}
            for baris, no_excel in zip(lembar.baris, lembar.baris_excel, strict=False):
                if c >= len(baris):
                    continue
                nilai = baris[c]
                if nilai is None or str(nilai).strip() == "":
                    continue
                if str(nilai).strip().lower() not in diizinkan:
                    ketemu.setdefault("KAT001", []).append((no_excel, nilai))

        # WIL002: kecamatan vs kabupaten induk (kolom induk di YAML)
        if spec.tipe == "wilayah" and spec.induk:
            ci = _cari_kolom(lembar, spec.induk)
            if ci is not None:
                for baris, no_excel in zip(lembar.baris, lembar.baris_excel, strict=False):
                    if c >= len(baris) or ci >= len(baris):
                        continue
                    kec = baris[c]
                    induk_nilai = baris[ci]
                    if kec is None or induk_nilai is None:
                        continue
                    induk_benar = induk_wilayah(kec)
                    if induk_benar is None:
                        continue  # bukan kecamatan / tak dikenal -> WIL001 saja
                    nama_induk = normalisasi_wilayah(induk_nilai)
                    if induk_benar != nama_induk.strip().lower():
                        ketemu.setdefault("WIL002", []).append((no_excel, kec))

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
