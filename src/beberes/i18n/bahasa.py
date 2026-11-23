"""Katalog pesan id/en. Semua teks yang dilihat user harus lewat t(), jangan hard-code (D-012)."""
import locale
import os

from .katalog_en import PESAN as PESAN_EN
from .katalog_id import PESAN as PESAN_ID

_KATALOG = {"id": PESAN_ID, "en": PESAN_EN}
_aktif: str | None = None


def _deteksi() -> str:
    env = os.environ.get("BEBERES_LANG", "").lower()
    if env in _KATALOG:
        return env
    kode = (locale.getlocale()[0] or "").lower()
    return "id" if kode.startswith("id") else "en"


def atur_bahasa(kode: str | None) -> None:
    """Set bahasa ('id' atau 'en'). None = deteksi otomatis."""
    global _aktif
    if kode is not None and kode not in _KATALOG:
        raise ValueError(f"Bahasa tidak didukung: {kode}")
    _aktif = kode


def bahasa_aktif() -> str:
    return _aktif or _deteksi()


def t(kunci: str, **kw) -> str:
    katalog = _KATALOG[bahasa_aktif()]
    teks = katalog.get(kunci) or PESAN_EN.get(kunci, kunci)
    return teks.format(**kw)
