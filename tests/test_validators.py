import pytest

from beberes.validators import (
    normalisasi_hp,
    normalisasi_wilayah,
    periksa_gelar,
    periksa_hp,
    periksa_nik,
    periksa_npwp,
    periksa_plat,
    periksa_wilayah,
    pisah_gelar,
    saran_wilayah,
)

# --- NIK -------------------------------------------------------------------

# NIK sintetis: provinsi 32 (Jabar), kab 01, kec 01, tgl 010190, urut 0001
NIK_VALID = "3201010101900001"


@pytest.mark.parametrize("nilai,ekspektasi", [
    (NIK_VALID, []),
    ("3201010101900001".replace("32", "99"), ["NIK002"]),   # provinsi tidak dikenal
    ("3201013201900001", ["NIK003"]),                      # bulan 32 mustahil
    ("3201014111900001", []),                              # perempuan: hari+40 -> 41 ok? cek
    ("12345", ["NIK001"]),
    ("32010101019000011", ["NIK001"]),                     # 17 digit
    (None, []),
])
def test_periksa_nik(nilai, ekspektasi):
    assert periksa_nik(nilai) == ekspektasi


def test_nik_perempuan_hari_plus_40():
    # digit tgl lahir 710190 -> hari 71-40=31, bulan 01, tahun 90 -> valid
    assert periksa_nik("3201017101900001") == []


# --- HP --------------------------------------------------------------------

@pytest.mark.parametrize("nilai,norm", [
    ("081234567890", "+6281234567890"),
    ("+62 812-3456-7890", "+6281234567890"),
    ("6281234567890", "+6281234567890"),
    ("8123456789", "+628123456789"),
])
def test_normalisasi_hp(nilai, norm):
    assert normalisasi_hp(nilai) == norm


@pytest.mark.parametrize("nilai,kode", [
    ("081234567890", ["HP001"]),
    ("123", ["HP002"]),
    ("+6281234567890", []),
    (None, []),
])
def test_periksa_hp(nilai, kode):
    assert periksa_hp(nilai) == kode


# --- NPWP ------------------------------------------------------------------

@pytest.mark.parametrize("nilai,kode", [
    ("12.345.678.9-012.345", []),
    ("123456789012345", []),
    ("3201010101900001", []),   # format baru 16 digit
    ("12.345", ["NPWP001"]),
    ("bukan npwp", ["NPWP001"]),
    (None, []),
])
def test_periksa_npwp(nilai, kode):
    assert periksa_npwp(nilai) == kode


# --- Plat ------------------------------------------------------------------

@pytest.mark.parametrize("nilai,kode", [
    ("B 1234 ABC", []),
    ("AB 123 CD", []),
    ("D 4567", []),
    ("bukan plat!!", ["PLAT001"]),
    (None, []),
])
def test_periksa_plat(nilai, kode):
    assert periksa_plat(nilai) == kode


# --- Gelar -----------------------------------------------------------------

@pytest.mark.parametrize("nilai,kode", [
    ("Drs. Budi Santoso", ["NAMA001"]),
    ("Budi Santoso, S.Kom.", ["NAMA001"]),
    ("H. Ahmad, M.A.", ["NAMA001"]),
    ("Budi Santoso", []),
    ("Siti Aminah", []),   # 'Siti' bukan gelar
    (None, []),
])
def test_periksa_gelar(nilai, kode):
    assert periksa_gelar(nilai) == kode


# --- Wilayah ---------------------------------------------------------------

def test_normalisasi_wilayah():
    assert normalisasi_wilayah("kota bandung") == "Bandung"
    assert normalisasi_wilayah("  Kab. Malang  ") == "Malang"
    assert normalisasi_wilayah("jawa barat") == "Jawa Barat"


@pytest.mark.parametrize("nilai,kode", [
    ("Bandung", []),
    ("Kota Bandung", []),
    ("Jawa Barat", []),
    ("B.wangi", ["WIL001"]),
    ("Atlantis", ["WIL001"]),
    (None, []),
])
def test_periksa_wilayah(nilai, kode):
    assert periksa_wilayah(nilai) == kode


def test_saran_wilayah():
    assert saran_wilayah("Banyuwamgi") == "Banyuwangi"
    assert saran_wilayah("Bandung") == "Bandung"
    assert saran_wilayah("zzzz") is None


# --- Pisah gelar ------------------------------------------------------------

@pytest.mark.parametrize("nilai,hasil", [
    ("Drs. Budi Santoso", "Budi Santoso"),
    ("Budi Santoso, S.Kom.", "Budi Santoso"),
    ("H. Ahmad, M.A.", "Ahmad"),
    ("Budi Santoso", None),
    (None, None),
])
def test_pisah_gelar(nilai, hasil):
    assert pisah_gelar(nilai) == hasil
