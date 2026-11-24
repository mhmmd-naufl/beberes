"""Detector KSG001/KSG002: sel kosong dan baris kosong."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    hasil = []
    if lembar.baris_kosong_dibuang:
        hasil.append(Temuan(
            kode="KSG002", kolom="(baris)", tingkat="info",
            pesan=f"{lembar.baris_kosong_dibuang} baris kosong dibuang",
            baris=[], contoh=[],
        ))
    if lembar.baris_hantu_dibuang:
        hasil.append(Temuan(
            kode="KSG003", kolom="(baris)", tingkat="info",
            pesan=(
                f"{lembar.baris_hantu_dibuang} baris hanya berisi nomor "
                "urut dibuang (sisa formula/template)"
            ),
            baris=[], contoh=[],
        ))

    # KSG001: sel kosong — butuh aturan kolom wajib (v0.2), untuk sekarang
    # hanya catat kolom dengan >30% kosong sebagai peringatan.
    for c, k in enumerate(profil.kolom):
        if k.persen_kosong > 30:
            nama = lembar.header[c] if c < len(lembar.header) else f"kolom_{c + 1}"
            hasil.append(Temuan(
                kode="KSG001", kolom=nama, tingkat="peringatan",
                pesan=f"{k.persen_kosong}% sel kosong pada kolom ini",
                baris=[], contoh=[],
            ))
    return hasil
