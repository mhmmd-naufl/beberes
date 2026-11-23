"""Klasifikasi tipe satu nilai sel.

Tipe yang dikenal: kosong, tanggal, uang, angka, teks.
Deteksi format Indonesia: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, dd.mm.yyyy,
'd Mon yyyy' (nama bulan Indonesia), 'Rp 25.000', '25.000,00'.
"""

import re
from datetime import datetime

TIPE_KOSONG = "kosong"
TIPE_TANGGAL = "tanggal"
TIPE_UANG = "uang"
TIPE_ANGKA = "angka"
TIPE_TEKS = "teks"

SEMUA_TIPE = (TIPE_KOSONG, TIPE_TANGGAL, TIPE_UANG, TIPE_ANGKA, TIPE_TEKS)

_BULAN_ID = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6,
    "jul": 7, "agu": 8, "ags": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
    "dec": 12,
}

_FORMAT_TANGGAL = (
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y",
    "%d %b %Y", "%d %B %Y",
)

_RE_ANGKA = re.compile(r"^[+-]?\d{1,3}([.,]\d{3})*([.,]\d+)?$|^[+-]?\d+(\.\d+)?$")
_RE_UANG = re.compile(
    r"^(rp\.?\s*)?[+-]?\d{1,3}(\.\d{3})*(,\d{1,2})?\s*(rp\.?)?$", re.IGNORECASE
)


def deteksi_format_tanggal(teks: str) -> str | None:
    """Kembalikan label format kalau teks adalah tanggal valid, else None."""
    for fmt in _FORMAT_TANGGAL:
        try:
            datetime.strptime(teks, fmt)
            return fmt
        except ValueError:
            continue
    # Format 'd Mon yyyy' dengan nama bulan Indonesia (strptime %b tidak kenal).
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", teks)
    if m and m.group(2).lower()[:3] in _BULAN_ID:
        try:
            datetime(int(m.group(3)), _BULAN_ID[m.group(2).lower()[:3]], int(m.group(1)))
            return "d Mon yyyy"
        except ValueError:
            return None
    return None


def _coba_tanggal(teks: str) -> bool:
    return deteksi_format_tanggal(teks) is not None


# Format di mana posisi hari/bulan bisa tertukar (keduanya <= 12).
_FORMAT_AMBIGU = {"%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"}


def apakah_tanggal_ambigu(teks: str) -> bool:
    """True kalau format dd/mm (atau sejenis) dengan hari & bulan <= 12."""
    fmt = deteksi_format_tanggal(teks)
    if fmt not in _FORMAT_AMBIGU:
        return False
    t = parse_tanggal(teks)
    return t is not None and t.day <= 12 and t.month <= 12


def parse_tanggal(teks: str) -> datetime | None:
    """Parse teks tanggal ke datetime. None kalau tidak valid.

    Format 'd Mon yyyy' dengan nama bulan Indonesia ditangani manual
    karena strptime %b hanya kenal Inggris.
    """
    fmt = deteksi_format_tanggal(teks)
    if fmt is None:
        return None
    if fmt == "d Mon yyyy":
        m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", teks)
        if not m:
            return None
        return datetime(
            int(m.group(3)), _BULAN_ID[m.group(2).lower()[:3]], int(m.group(1))
        )
    try:
        return datetime.strptime(teks, fmt)
    except ValueError:
        return None


def _coba_uang(teks: str) -> bool:
    """Angka dengan penanda Rp atau pemisah ribuan bertitik."""
    if not _RE_UANG.match(teks):
        return False
    return "rp" in teks.lower() or "." in teks


def _coba_angka(teks: str) -> bool:
    return bool(_RE_ANGKA.match(teks))


def parse_uang(teks: str) -> float | None:
    """Ubah teks Rupiah jadi angka. None kalau bukan format uang.

    Aturan deterministik:
    - 'Rp' boleh ada atau tidak; spasi dihapus.
    - Dua jenis pemisah ('.' dan ','): yang paling kanan = desimal.
    - Satu jenis pemisah: desimal hanya kalau digit setelahnya != 3;
      kalau tepat 3 digit dianggap ribuan ('25.000' -> 25000).
    - Tanpa 'Rp', wajib ada minimal satu grup ribuan 3 digit.
    """
    t = str(teks).strip()
    if not t:
        return None
    ada_rp = "rp" in t.lower()
    s = re.sub(r"(?i)rp\.?", "", t).replace(" ", "")
    if not re.fullmatch(r"[+-]?[\d.,]+", s):
        return None
    if not ada_rp and not re.search(r"[.,]\d{3}([.,]|$)", s):
        return None

    if "." in s and "," in s:
        if s.rfind(".") > s.rfind(","):
            s = s.replace(",", "").replace(".", "@")
        else:
            s = s.replace(".", "").replace(",", "@")
        s = s.replace("@", ".")
    else:
        sep = "." if "." in s else ("," if "," in s else None)
        if sep:
            ekor = s.rsplit(sep, 1)[1]
            s = s.replace(sep, "") if len(ekor) == 3 else s.replace(sep, ".")

    try:
        nilai = float(s)
    except ValueError:
        return None
    return int(nilai) if nilai == int(nilai) else nilai


def parse_angka_teks(teks: str) -> float | None:
    """Angka yang tertulis sebagai teks, mis. '1 250' -> 1250."""
    t = str(teks).strip()
    if not re.fullmatch(r"[+-]?[\d][\d\s]*[.,]?\d*", t) or " " not in t:
        return None
    bersih = t.replace(" ", "")
    try:
        nilai = float(bersih.replace(",", "."))
    except ValueError:
        return None
    return int(nilai) if nilai == int(nilai) else nilai


def deteksi_tipe(nilai) -> str:
    """Kembalikan tipe satu nilai sel."""
    if nilai is None:
        return TIPE_KOSONG
    if isinstance(nilai, bool):
        return TIPE_TEKS
    if isinstance(nilai, (int, float)):
        return TIPE_ANGKA
    teks = str(nilai).strip()
    if teks == "":
        return TIPE_KOSONG
    if _coba_tanggal(teks):
        return TIPE_TANGGAL
    if _coba_uang(teks):
        return TIPE_UANG
    if _coba_angka(teks):
        return TIPE_ANGKA
    return TIPE_TEKS
