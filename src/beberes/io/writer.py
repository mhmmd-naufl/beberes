"""Writer: simpan Lembar ke file baru (.xlsx / .csv).

Prinsip proyek: file asli tidak pernah ditimpa — pemanggil wajib memberi
tujuan path baru (docs/02, D-004).
"""

import csv
from pathlib import Path

import openpyxl

from .reader import Lembar


def _tulis_sheet(ws, lembar: Lembar) -> None:
    ws.title = lembar.nama[:31]  # batas panjang nama sheet Excel
    if lembar.header:
        ws.append(lembar.header)
    for baris in lembar.baris:
        ws.append(["" if c is None else c for c in baris])


def tulis_xlsx(path: str | Path, lembar_list: list[Lembar]) -> None:
    """Tulis satu atau lebih Lembar sebagai sheet di satu workbook."""
    if not lembar_list:
        raise ValueError("Tidak ada lembar untuk ditulis")
    wb = openpyxl.Workbook()
    for i, lembar in enumerate(lembar_list):
        ws = wb.active if i == 0 else wb.create_sheet()
        _tulis_sheet(ws, lembar)
    wb.save(path)


def tulis_csv(path: str | Path, lembar: Lembar) -> None:
    # utf-8-sig supaya Excel membaca header dengan benar.
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        if lembar.header:
            w.writerow(lembar.header)
        for baris in lembar.baris:
            w.writerow(["" if c is None else c for c in baris])


def simpan(lembar: Lembar | list[Lembar], path: str | Path) -> None:
    """Simpan Lembar (atau daftar Lembar) ke path; format dari suffix."""
    path = Path(path)
    daftar = lembar if isinstance(lembar, list) else [lembar]
    if path.suffix.lower() == ".csv":
        if len(daftar) > 1:
            raise ValueError("CSV hanya mendukung satu sheet")
        tulis_csv(path, daftar[0])
    elif path.suffix.lower() in (".xlsx", ".xlsm"):
        tulis_xlsx(path, daftar)
    else:
        raise ValueError(f"Format tidak didukung: {path.suffix} (dukung .xlsx dan .csv)")
