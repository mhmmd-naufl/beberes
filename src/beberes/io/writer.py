"""Writer: simpan Lembar ke file baru (.xlsx / .csv).

Prinsip proyek: file asli tidak pernah ditimpa — pemanggil wajib memberi
tujuan path baru (docs/02, D-004).
"""

import csv
from pathlib import Path

import openpyxl

from .reader import Lembar


def tulis_xlsx(path: str | Path, lembar: Lembar) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = lembar.nama[:31]  # batas panjang nama sheet Excel
    if lembar.header:
        ws.append(lembar.header)
    for baris in lembar.baris:
        ws.append(["" if c is None else c for c in baris])
    wb.save(path)


def tulis_csv(path: str | Path, lembar: Lembar) -> None:
    # utf-8-sig supaya Excel membaca header dengan benar.
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        if lembar.header:
            w.writerow(lembar.header)
        for baris in lembar.baris:
            w.writerow(["" if c is None else c for c in baris])


def simpan(lembar: Lembar, path: str | Path) -> None:
    """Simpan Lembar ke path; format ditentukan suffix file."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        tulis_csv(path, lembar)
    elif path.suffix.lower() in (".xlsx", ".xlsm"):
        tulis_xlsx(path, lembar)
    else:
        raise ValueError(f"Format tidak didukung: {path.suffix} (dukung .xlsx dan .csv)")
