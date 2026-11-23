from pathlib import Path

import pytest

from beberes.detectors import jalankan
from beberes.fixers import usulkan_semua
from beberes.io import Lembar, baca_berkas
from beberes.profiling import profil_lbr


def _lembar(header, baris):
    return Lembar(
        nama="T", header=header, baris_header=1, baris=baris,
        baris_excel=list(range(2, 2 + len(baris))),
    )


def _temuan(temuan_list, kode):
    return [t for t in temuan_list if t.kode == kode]


def test_fmt001_spasi():
    lembar = _lembar(["Nama"], [["  Budi  Santoso "], ["Ani"]])
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    fmt = _temuan(temuan, "FMT001")
    assert len(fmt) == 1
    assert fmt[0].baris == [2]


def test_fmt002_kapital_acak():
    lembar = _lembar(["Barang"], [["pROfounD EnCoMpasSing"], ["Normal Item"]])
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    assert len(_temuan(temuan, "FMT002")) == 1


def test_uang001():
    lembar = _lembar(["Harga"], [[25000], ["Rp 25.000"], ["Rp5.500,00"]])
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    uang = _temuan(temuan, "UANG001")
    assert len(uang) == 1
    assert uang[0].baris == [3, 4]


def test_tgl001_campuran_dan_tgl002_ambigu():
    lembar = _lembar(["Tgl"], [
        ["14/05/2007"],      # day=14 >12 -> tidak ambigu
        ["03/04/2025"],      # ambigu
        ["2020-01-01"],      # yyyy-mm-dd
        ["5 Jan 1990"],      # d Mon yyyy
    ])
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    assert len(_temuan(temuan, "TGL001")) == 1
    tgl2 = _temuan(temuan, "TGL002")
    assert len(tgl2) == 1 and tgl2[0].baris == [3]


def test_tgl003_mustahil():
    lembar = _lembar(["Tgl"], [["12/05/1990"], ["31/02/2025"], ["2020-01-01"]])
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    tgl3 = _temuan(temuan, "TGL003")
    assert len(tgl3) == 1 and tgl3[0].baris == [3]


def test_fix_uang():
    lembar = _lembar(["Harga"], [[25000], ["Rp 25.000"]])
    p = profil_lbr(lembar)
    perbaikan = usulkan_semua(jalankan(lembar, p), lembar)
    uang = [b for b in perbaikan if b.kode == "UANG001"]
    assert len(uang) == 1
    assert uang[0].nilai_lama == "Rp 25.000"
    assert uang[0].nilai_baru == 25000


def test_fix_tanggal_ambigu_tidak_otomatis():
    lembar = _lembar(["Tgl"], [["03/04/2025"], ["14 Jan 2007"]])
    p = profil_lbr(lembar)
    perbaikan = usulkan_semua(jalankan(lembar, p), lembar)
    tgl = [b for b in perbaikan if b.kode in ("TGL001", "TGL002")]
    ambigu = [b for b in tgl if b.nilai_lama == "03/04/2025"]
    pasti = [b for b in tgl if b.nilai_lama == "14 Jan 2007"]
    assert ambigu and ambigu[0].aman_otomatis is False
    assert pasti and pasti[0].aman_otomatis is True
    assert pasti[0].nilai_baru == "2007-01-14"


def test_ksg002_baris_kosong():
    lembar = _lembar(["Nama"], [["Ani"]])
    lembar.baris_kosong_dibuang = 3
    p = profil_lbr(lembar)
    temuan = jalankan(lembar, p)
    ksg = _temuan(temuan, "KSG002")
    assert len(ksg) == 1 and "3" in ksg[0].pesan


def test_integrasi_file_berantakan():
    """Detector batch 1 harus menemukan masalah di data_uji."""
    root = Path(__file__).parent.parent
    p = root / "data_uji" / "berantakan_peserta.xlsx"
    if not p.exists():
        pytest.skip("data_uji belum digenerate")
    lembar = baca_berkas(p)[0]
    profil = profil_lbr(lembar)
    temuan = jalankan(lembar, profil)
    kode = {t.kode for t in temuan}
    assert "FMT001" in kode or "FMT002" in kode
    assert "TGL001" in kode
    perbaikan = usulkan_semua(temuan, lembar)
    assert len(perbaikan) > 50
