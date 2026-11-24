from beberes.io import Lembar
from beberes.rules import muat, perbaiki, periksa
from beberes.rules.skema import validasi


def _aturan():
    return validasi({"kolom": {"nik": {"tipe": "nik"}, "hp": {"tipe": "hp"}}})


def _lembar():
    return Lembar(
        nama="Sheet1", header=["Nama", "nik", "hp"], baris_header=1,
        baris=[
            ["A", "3201010101900001", "081234567890"],
            ["B", "3201013201900001", "+6281234567890"],
            ["C", "12345", "081234567890"],
        ],
        baris_excel=[2, 3, 4],
    )


def test_engine_menemukan_kode():
    temuan = periksa(_lembar(), _aturan())
    kode = {t.kode for t in temuan}
    assert "NIK003" in kode      # baris B: bulan 32
    assert "NIK001" in kode      # baris C: bukan 16 digit
    assert "HP001" in kode       # 0812... perlu +62


def test_engine_baris_excel_benar():
    temuan = [t for t in periksa(_lembar(), _aturan()) if t.kode == "NIK001"][0]
    assert temuan.baris == [4]   # baris excel asli


def test_fixer_hp001():
    temuan = [t for t in periksa(_lembar(), _aturan()) if t.kode == "HP001"][0]
    perbaikan = perbaiki(temuan, _lembar())
    assert len(perbaikan) == 2
    assert perbaikan[0].nilai_baru == "+6281234567890"
    assert perbaikan[0].aman_otomatis


def test_yaml_salah_tipe_ditolak(tmp_path):
    p = tmp_path / "salah.yaml"
    p.write_text("kolom:\n  x:\n    tipe: hantu\n", encoding="utf-8")
    try:
        muat(p)
        raise AssertionError("harus error")
    except ValueError as e:
        assert "hantu" in str(e)


def test_email_validator():
    from beberes.validators import periksa_email
    assert periksa_email("budi@contoh.id") == []
    assert periksa_email("bukan-email") == ["EMAIL001"]
    assert periksa_email(None) == []


def test_kategori_di_luar_daftar(tmp_path):
    from beberes.rules.engine import periksa
    from beberes.rules.loader import muat

    p = tmp_path / "kat.yaml"
    p.write_text(
        "versi: 1\nkolom:\n  Status:\n    tipe: kategori\n"
        "    aturan: [Lunas, Belum]\n",
        encoding="utf-8",
    )
    aturan = muat(p)
    lembar = Lembar(
        nama="S", header=["Status"], baris_header=1,
        baris=[["Lunas"], ["HILANG"], ["Belum"]],
        baris_excel=[2, 3, 4],
    )
    temuan = periksa(lembar, aturan)
    kat = [t for t in temuan if t.kode == "KAT001"]
    assert len(kat) == 1
    assert kat[0].baris == [3]
