"""Validator email — cek pola dasar saja."""

import re

_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def periksa_email(nilai) -> list[str]:
    """Kembalikan ['EMAIL001'] kalau bukan pola email."""
    if nilai is None:
        return []
    teks = str(nilai).strip()
    if teks == "":
        return []
    if _RE.match(teks):
        return []
    return ["EMAIL001"]
