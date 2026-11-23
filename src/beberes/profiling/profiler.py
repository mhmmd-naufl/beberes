"""Profiler: tebak tipe tiap kolom + skor kualitas.

Sesuai docs/02: deteksi tipe kolom, hitung % kosong/valid, nilai janggal.
"""

from dataclasses import dataclass, field

from beberes.io import Lembar

from .tipe import SEMUA_TIPE, TIPE_KOSONG, deteksi_tipe


@dataclass
class ProfilKolom:
    """Hasil profiling satu kolom."""

    nama: str
    tipe_utama: str = ""               # tanggal/uang/angka/teks/campuran/kosong
    persen_kosong: float = 0.0
    persen_per_tipe: dict = field(default_factory=dict)
    contoh: list = field(default_factory=list)  # contoh nilai non-kosong
    skor: float = 0.0                  # 0-100


@dataclass
class Profil:
    """Hasil profiling satu lembar."""

    lembar: str
    kolom: list = field(default_factory=list)


def _tipe_utama(hitung: dict, total_terisi: int) -> str:
    """Tipe dominan; 'campuran' kalau tidak ada yang >= 80% dari terisi."""
    if total_terisi == 0:
        return "kosong"
    dominan, n = max(hitung.items(), key=lambda kv: kv[1])
    return dominan if n / total_terisi >= 0.8 else "campuran"


def profil_lbr(lembar: Lembar, contoh_maks: int = 3) -> Profil:
    """Profile semua kolom satu Lembar."""
    lebar = len(lembar.header)
    hasil = Profil(lembar=lembar.nama)

    for c in range(lebar):
        nama = lembar.header[c] or f"kolom_{c + 1}"
        hitung = {t: 0 for t in SEMUA_TIPE}
        contoh = []
        total = 0

        for baris in lembar.baris:
            nilai = baris[c] if c < len(baris) else None
            tipe = deteksi_tipe(nilai)
            hitung[tipe] += 1
            total += 1
            if tipe != TIPE_KOSONG and len(contoh) < contoh_maks:
                contoh.append(nilai)

        total_terisi = total - hitung[TIPE_KOSONG]
        persen_kosong = hitung[TIPE_KOSONG] / total * 100 if total else 0.0
        persen_per_tipe = {
            t: round(n / total_terisi * 100, 1)
            for t, n in hitung.items()
            if n and t != TIPE_KOSONG
        }

        # Skor: proporsi terisi x kemurnian tipe dominan.
        kemurnian = (
            max((v for k, v in persen_per_tipe.items() if k != TIPE_KOSONG), default=0.0)
            / 100.0
        )
        skor = round((100 - persen_kosong) * kemurnian, 1)

        hitung_isi = {k: v for k, v in hitung.items() if k != TIPE_KOSONG}
        hasil.kolom.append(ProfilKolom(
            nama=nama,
            tipe_utama=_tipe_utama(hitung_isi, total_terisi),
            persen_kosong=round(persen_kosong, 1),
            persen_per_tipe=persen_per_tipe,
            contoh=[str(x) for x in contoh],
            skor=skor,
        ))
    return hasil
