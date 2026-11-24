from pathlib import Path

import openpyxl
import pytest

from beberes.io import Lembar, baca_berkas, simpan


def _tulis_xlsx(path: Path, baris: list[list]) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    for b in baris:
        ws.append(b)
    wb.save(path)


def test_baca_xlsx_header_baris_1(tmp_path: Path):
    p = tmp_path / "a.xlsx"
    _tulis_xlsx(p, [["Nama", "Umur"], ["Ani", 30], ["Budi", 25]])
    (lembar,) = baca_berkas(p)
    assert lembar.header == ["Nama", "Umur"]
    assert lembar.baris_header == 1
    assert lembar.baris == [["Ani", 30], ["Budi", 25]]
    assert lembar.baris_excel == [2, 3]


def test_baca_xlsx_header_bergeser(tmp_path: Path):
    p = tmp_path / "a.xlsx"
    _tulis_xlsx(p, [
        ["LAPORAN PESERTA"],
        [None],
        [None],
        ["Nama", "Wilayah", "Uang"],
        ["Ani", "Bandung", 5000],
        [None, None, None],  # baris kosong di tengah -> dibuang
        ["Budi", "Medan", 7000],
    ])
    (lembar,) = baca_berkas(p)
    assert lembar.baris_header == 4
    assert lembar.header == ["Nama", "Wilayah", "Uang"]
    assert lembar.baris == [["Ani", "Bandung", 5000], ["Budi", "Medan", 7000]]
    assert lembar.baris_excel == [5, 7]


def test_baca_file_buatan_sendiri(tmp_path: Path):
    """Baca file berantakan hasil generator: header harus ketemu."""
    root = Path(__file__).parent.parent
    p = root / "data_uji" / "berantakan_peserta.xlsx"
    if not p.exists():
        pytest.skip("data_uji belum digenerate")
    lembar = baca_berkas(p)[0]
    assert lembar.header[:2] == ["Nama", "Tanggal Lahir"]
    assert len(lembar.baris) > 100
    # baris pertama data harus nama orang, bukan judul laporan
    assert lembar.baris[0][0] is not None


def test_baca_csv_koma_dan_titik_koma(tmp_path: Path):
    p1 = tmp_path / "a.csv"
    p1.write_text("nama,umur\nAni,30\n", encoding="utf-8")
    (l1,) = baca_berkas(p1)
    assert l1.header == ["nama", "umur"]
    assert l1.baris == [["Ani", "30"]]

    p2 = tmp_path / "b.csv"
    p2.write_text("nama;umur\nAni;30\n", encoding="utf-8")
    (l2,) = baca_berkas(p2)
    assert l2.header == ["nama", "umur"]
    assert l2.baris == [["Ani", "30"]]


def test_baca_csv_encoding_cp1252(tmp_path: Path):
    p = tmp_path / "a.csv"
    p.write_bytes("nama,kota\nJosé,São Paulo\n".encode("cp1252"))
    (lembar,) = baca_berkas(p)
    assert lembar.baris[0][0] == "José"


def test_baca_csv_kosong(tmp_path: Path):
    p = tmp_path / "kosong.csv"
    p.write_text("", encoding="utf-8")
    (lembar,) = baca_berkas(p)
    assert lembar.header == []
    assert lembar.baris == []


def test_simpan_dan_baca_lagi_xlsx(tmp_path: Path):
    p = tmp_path / "hasil.xlsx"
    lembar = Lembar(
        nama="Data",
        header=["Nama", "Umur"],
        baris_header=1,
        baris=[["Ani", 30], ["Budi", None]],
        baris_excel=[2, 3],
    )
    simpan(lembar, p)
    (baca,) = baca_berkas(p)
    assert baca.header == ["Nama", "Umur"]
    assert baca.baris[0] == ["Ani", 30]


def test_simpan_csv_utf8_sig(tmp_path: Path):
    p = tmp_path / "hasil.csv"
    lembar = Lembar(nama="Data", header=["Nama"], baris_header=1, baris=[["Ani"]])
    simpan(lembar, p)
    assert p.read_bytes().startswith(b"\xef\xbb\xbf")  # BOM utf-8
    (baca,) = baca_berkas(p)
    assert baca.baris == [["Ani"]]


def test_format_tidak_didukung(tmp_path: Path):
    p = tmp_path / "a.txt"
    p.write_text("x")
    with pytest.raises(ValueError, match="tidak didukung"):
        baca_berkas(p)


def test_baris_hantu_dibuang(tmp_path: Path):
    """Baris yang hanya berisi nomor urut di kolom pertama dibuang."""
    p = tmp_path / "hantu.xlsx"
    _tulis_xlsx(p, [
        ["k", "Nama", "Total"],
        [1, "Ani", 5000],
        [2, "Budi", 7000],
        [3, None, None],   # hantu: cuma nomor urut
        [4, None, None],   # hantu
        [5, "Citra", 9000],
    ])
    (lembar,) = baca_berkas(p)
    assert len(lembar.baris) == 3
    assert lembar.baris_hantu_dibuang == 2
    assert lembar.baris_excel == [2, 3, 6]


def test_kolom_hantu_tanpa_header_dibuang(tmp_path: Path):
    """Kolom tanpa nama header + isinya <10% baris dibuang."""
    p = tmp_path / "kolom.xlsx"
    _tulis_xlsx(p, [
        ["Nama", "Total", None, None],
        ["Ani", 5000, None, None],
        ["Budi", 7000, None, None],
        ["Citra", 9000, None, None],
        ["Dedi", 1000, None, None],
        ["Eko", 2000, None, None],
        ["Fajar", 3000, None, None],
        ["Gita", 4000, None, None],
        ["Hadi", 5000, None, None],
        ["Ika", 6000, None, None],
        ["Joko", 7000, None, None],
        ["Kiki", 8000, None, None],
        ["Lala", 9000, None, None],
        ["Maman", 10000, "TOTAL", None],
    ])
    (lembar,) = baca_berkas(p)
    assert lembar.header == ["Nama", "Total"]
    assert all(len(b) == 2 for b in lembar.baris)


def test_kolom_tanpa_header_berisi_banyak_tidak_dibuang(tmp_path: Path):
    """Kolom tanpa header tapi banyak isinya TIDAK dibuang (data asli)."""
    p = tmp_path / "kolom2.xlsx"
    _tulis_xlsx(p, [
        ["Nama", "Total", None],
        ["Ani", 5000, "catatan1"],
        ["Budi", 7000, "catatan2"],
        ["Citra", 9000, "catatan3"],
        ["Dedi", 1000, "catatan4"],
        ["Eko", 2000, "catatan5"],
    ])
    (lembar,) = baca_berkas(p)
    assert len(lembar.header) == 3


def test_baris_satu_sel_bukan_hantu(tmp_path: Path):
    """Baris 1 sel terisi tapi di kolom bukan pertama TIDAK dibuang."""
    p = tmp_path / "satu.xlsx"
    _tulis_xlsx(p, [
        ["Nama", "Total", "Kota"],
        ["Ani", 5000, "Bandung"],
        ["Budi", 7000, "Medan"],
        [None, None, "Solo"],   # cuma kota terisi -> data asli, jangan hapus
    ])
    (lembar,) = baca_berkas(p)
    assert len(lembar.baris) == 3
    assert lembar.baris_hantu_dibuang == 0
