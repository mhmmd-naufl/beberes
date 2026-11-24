from beberes.dedupe import deteksi
from beberes.io import Lembar
from beberes.profiling import profil_lbr


def _lembar(baris, header=("Nama", "Kota")):
    return Lembar(
        nama="S", header=list(header), baris_header=1,
        baris=baris, baris_excel=list(range(2, 2 + len(baris))),
    )


def test_duplikat_persis():
    lm = _lembar([
        ["Ani", "Bandung"], ["Budi", "Medan"], ["Ani", "Bandung"],
    ])
    temuan = deteksi(lm, profil_lbr(lm))
    dup = [t for t in temuan if t.kode == "DUP001"]
    assert len(dup) == 1
    assert sorted(dup[0].baris) == [2, 4]


def test_duplikat_mirip():
    lm = _lembar([
        ["Muhammad Naufal", "Bandung"],
        ["Mohammad Naufal", "Bandung"],
        ["Siti Aminah", "Medan"],
    ])
    temuan = deteksi(lm, profil_lbr(lm))
    dup = [t for t in temuan if t.kode == "DUP002"]
    assert len(dup) == 1
    assert "muhammad naufal" in dup[0].contoh[0]


def test_tidak_ada_duplikat():
    lm = _lembar([["Ani", "Bandung"], ["Budi", "Medan"]])
    assert deteksi(lm, profil_lbr(lm)) == []
