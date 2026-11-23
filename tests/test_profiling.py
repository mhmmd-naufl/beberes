from pathlib import Path

import pytest

from beberes.io import Lembar, baca_berkas
from beberes.profiling import deteksi_tipe, profil_lbr


@pytest.mark.parametrize("nilai,tipe", [
    (None, "kosong"),
    ("", "kosong"),
    ("   ", "kosong"),
    (30, "angka"),
    (3.14, "angka"),
    ("25000", "angka"),
    ("12/05/1990", "tanggal"),
    ("12-05-1990", "tanggal"),
    ("1990-05-12", "tanggal"),
    ("12.05.1990", "tanggal"),
    ("5 Jan 1990", "tanggal"),
    ("5 Januari 1990", "tanggal"),  # nama bulan Indonesia lengkap dikenali
    ("5 Foo 1990", "teks"),
    ("Rp 25.000", "uang"),
    ("Rp25.000", "uang"),
    ("25.000,00 Rp", "uang"),
    ("Ani", "teks"),
    ("08012345678", "angka"),   # HP terlihat sebagai angka (validator nanti)
    (True, "teks"),
])
def test_deteksi_tipe(nilai, tipe):
    assert deteksi_tipe(nilai) == tipe


def _lembar(header, baris):
    return Lembar(nama="T", header=header, baris_header=1, baris=baris)


def test_profil_kolom_bersih():
    lembar = _lembar(["Nama", "Umur"], [["Ani", 30], ["Budi", 25], ["Citra", 40]])
    p = profil_lbr(lembar)
    assert p.kolom[0].tipe_utama == "teks"
    assert p.kolom[0].skor == 100.0
    assert p.kolom[1].tipe_utama == "angka"
    assert p.kolom[1].skor == 100.0


def test_profil_kolom_campuran_dan_kosong():
    lembar = _lembar(["Tgl"], [["12/05/1990"], ["2020-01-01"], ["bukan tanggal"], [None]])
    p = profil_lbr(lembar)
    k = p.kolom[0]
    assert k.tipe_utama == "campuran"
    assert k.persen_kosong == 25.0
    assert k.skor < 100.0


def test_profil_file_berantakan_sendiri():
    """Kolom Tanggal Lahir peserta harus terdeteksi campuran."""
    root = Path(__file__).parent.parent
    p = root / "data_uji" / "berantakan_peserta.xlsx"
    if not p.exists():
        pytest.skip("data_uji belum digenerate")
    lembar = baca_berkas(p)[0]
    profil = profil_lbr(lembar)
    per_kolom = {k.nama: k for k in profil.kolom}
    # Semua format korupsi tanggal tetap bertipe 'tanggal'; campuran format
    # adalah tugas detector, bukan profiler.
    assert per_kolom["Tanggal Lahir"].tipe_utama == "tanggal"
    assert per_kolom["Wilayah"].tipe_utama == "teks"
    # Kolom uang: mayoritas angka + sebagian 'Rp ...' -> tetap 'angka' dominan
    # tapi porsi 'uang' harus terlihat.
    assert per_kolom["No HP"].tipe_utama == "angka"
