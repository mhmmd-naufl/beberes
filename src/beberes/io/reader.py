"""Reader file .xlsx / .csv -> representasi internal Lembar.

Menangani pola umum file berantakan (docs/02):
- header tidak di baris 1 (ada baris judul/kosong di atasnya)
- sel kosong -> None
- csv dengan encoding non-UTF8 dan delimiter ';'

TODO: sel digabung (merged cells) dan sheet tersembunyi belum ditangani penuh.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path

import openpyxl

# Berapa baris awal yang discan untuk mencari baris header.
MAKS_CARI_HEADER = 10


@dataclass
class Lembar:
    """Satu sheet/tabel hasil bacaan.

    baris_header: nomor baris Excel (1-based) tempat header berada.
    baris: baris data (tanpa header), tiap sel None kalau kosong.
    baris_excel: nomor baris Excel (1-based) untuk tiap baris di `baris`.
    """

    nama: str
    header: list[str]
    baris_header: int
    baris: list[list] = field(default_factory=list)
    baris_excel: list[int] = field(default_factory=list)
    baris_kosong_dibuang: int = 0  # baris kosong yang dibuang dari data


def _sel_terisi(baris: list) -> list:
    return [c for c in baris if c is not None and str(c).strip() != ""]


def _cari_header(kandidat: list[list]) -> int:
    """Index (0-based) baris header dalam kandidat.

    Header = baris pertama (dari atas) yang punya jumlah sel terisi maksimum
    di antara MAKS_CARI_HEADER baris awal, minimal 2 sel.
    """
    hitung = [len(_sel_terisi(b)) for b in kandidat[:MAKS_CARI_HEADER]]
    maks = max(hitung, default=0)
    if maks < 2:
        return 0
    return hitung.index(maks)


def _rapikan(baris: list[list], lebar: int) -> list[list]:
    """Samakan panjang tiap baris ke `lebar` dengan None."""
    return [list(b) + [None] * (lebar - len(b)) for b in baris]


def _buat_lembar(nama: str, semua_baris: list[list]) -> Lembar:
    """Ubah daftar baris mentah (dari openpyxl/csv) jadi Lembar."""
    if not semua_baris:
        return Lembar(nama=nama, header=[], baris_header=1)

    idx_header = _cari_header(semua_baris)
    mentah_header = semua_baris[idx_header]
    header = ["" if c is None else str(c).strip() for c in mentah_header]

    # Buang baris kosong di antara data; catat nomor baris Excel-nya.
    baris_data: list[list] = []
    baris_excel: list[int] = []
    dibuang = 0
    for i, baris in enumerate(semua_baris[idx_header + 1 :], start=idx_header + 2):
        if not _sel_terisi(baris):
            dibuang += 1
            continue
        baris_data.append(baris)
        baris_excel.append(i)

    lebar = max([len(header), *(len(b) for b in baris_data)])
    return Lembar(
        nama=nama,
        header=_rapikan([header], lebar)[0],
        baris_header=idx_header + 1,
        baris=_rapikan(baris_data, lebar),
        baris_excel=baris_excel,
        baris_kosong_dibuang=dibuang,
    )


def _baca_xlsx(path: Path) -> list[Lembar]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    lembar = []
    for ws in wb.worksheets:
        semua = [list(b) for b in ws.iter_rows(values_only=True)]
        lembar.append(_buat_lembar(ws.title, semua))
    wb.close()
    return lembar


def _deteksi_encoding(path: Path) -> str:
    """Coba utf-8-sig dulu, lalu cp1252, terakhir latin-1 (tidak pernah gagal)."""
    data = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"


def _deteksi_delimiter(baris_pertama: str) -> str:
    """Pilih ';' kalau koma tidak menghasilkan lebih dari satu kolom."""
    if baris_pertama.count(";") > baris_pertama.count(","):
        return ";"
    return ","


def _baca_csv(path: Path) -> list[Lembar]:
    enc = _deteksi_encoding(path)
    teks = path.read_text(encoding=enc)
    baris_teks = teks.splitlines()
    if not baris_teks:
        return [_buat_lembar(path.stem, [])]
    delim = _deteksi_delimiter(baris_teks[0])
    semua = [list(b) for b in csv.reader(baris_teks, delimiter=delim)]
    return [_buat_lembar(path.stem, semua)]


def baca_berkas(path: str | Path) -> list[Lembar]:
    """Baca .xlsx atau .csv, kembalikan daftar Lembar (csv selalu 1)."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return _baca_csv(path)
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        return _baca_xlsx(path)
    raise ValueError(f"Format tidak didukung: {path.suffix} (dukung .xlsx dan .csv)")
