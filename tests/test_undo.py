import json

from beberes.io import Lembar
from beberes.model import Perbaikan
from beberes.report import terapkan, tulis_audit, urungkan


def _lembar():
    return Lembar(
        nama="Data", header=["Nama", "Kota"], baris_header=1,
        baris=[["  Ani  ", "Bandung"], ["Budi", "Medan"]],
        baris_excel=[2, 3],
    )


def test_undo_mengembalikan_nilai_lama(tmp_path):
    lembar = _lembar()
    perbaikan = [Perbaikan(
        kode="FMT001", aturan="fmt001", baris_excel=2, kolom_idx=0,
        kolom="Nama", nilai_lama="  Ani  ", nilai_baru="Ani",
    )]
    baru, perubahan = terapkan(lembar, perbaikan)
    assert baru.baris[0][0] == "Ani"

    log = tmp_path / "audit.jsonl"
    tulis_audit(log, perubahan)

    # simulasi: file hasil = `baru` yang disimpan lalu dibaca ulang
    from beberes.io import simpan
    f = tmp_path / "hasil.xlsx"
    simpan(baru, f)
    dikembalikan = urungkan(f, log)
    assert dikembalikan[0].baris[0][0] == "  Ani  "
    assert dikembalikan[0].baris[1][0] == "Budi"


def test_konfirmasi_diterapkan_bila_diabaikan():
    """Perbaikan aman_otomatis=False diskip default, diterapkan bila flag."""
    lembar = _lembar()
    p = [Perbaikan(
        kode="TGL002", aturan="x", baris_excel=2, kolom_idx=0,
        kolom="Nama", nilai_lama="  Ani  ", nilai_baru="Ani",
        aman_otomatis=False,
    )]
    assert terapkan(lembar, p)[1] == []
    baru, perubahan = terapkan(lembar, p, abaikan_aman_otomatis=True)
    assert baru.baris[0][0] == "Ani"
    assert len(perubahan) == 1


def test_undo_baris_tidak_ditemukan_diabaikan(tmp_path):
    lembar = _lembar()
    _, perubahan = terapkan(lembar, [Perbaikan(
        kode="FMT001", aturan="x", baris_excel=99, kolom_idx=0,
        kolom="Nama", nilai_lama="lama", nilai_baru="baru",
    )])
    assert perubahan == []  # baris 99 tidak ada -> tidak diterapkan


def test_baca_log_jsonl(tmp_path):
    log = tmp_path / "a.jsonl"
    log.write_text(
        json.dumps({"sheet": "Data", "sel": "A2", "kolom_idx": 0,
                    "baris_excel": 2, "nilai_lama": "x"}) + "\n",
        encoding="utf-8",
    )
    from beberes.report.undo import _baca_log
    assert len(_baca_log(log)) == 1


def test_undo_setelah_baris_kosong_dibuang(tmp_path):
    """Regresi: baris_output harus dipakai, bukan baris_excel asli."""
    from openpyxl import Workbook

    from beberes.io import baca_berkas, simpan

    f = tmp_path / "asli.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["Nama", "Kota"])
    ws.append(["Ani", "Bandung"])
    ws.append([None, None])          # baris kosong di tengah -> dibuang reader
    ws.append(["  Budi  ", "Medan"]) # baris_excel=4, tapi output row=3
    wb.save(f)

    lembar = baca_berkas(f)[0]
    _, perubahan = terapkan(lembar, [Perbaikan(
        kode="FMT001", aturan="x", baris_excel=4, kolom_idx=0,
        kolom="Nama", nilai_lama="  Budi  ", nilai_baru="Budi",
    )])
    assert perubahan[0]["baris_output"] == 3
    assert perubahan[0]["baris_excel"] == 4

    log = tmp_path / "a.jsonl"
    tulis_audit(log, perubahan)
    hasil = tmp_path / "hasil.xlsx"
    simpan(terapkan(lembar, [Perbaikan(
        kode="FMT001", aturan="x", baris_excel=4, kolom_idx=0,
        kolom="Nama", nilai_lama="  Budi  ", nilai_baru="Budi",
    )])[0], hasil)
    undo = urungkan(hasil, log)
    assert undo[0].baris[1][0] == "  Budi  "
