"""Applier + audit log.

Menerapkan Perbaikan yang aman_otomatis=True ke salinan Lembar dan
mencatat tiap perubahan untuk undo (docs/03 bagian 5).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl.utils import get_column_letter

from ..io import Lembar
from ..model import Perbaikan


def _sel_ref(kolom_idx: int, baris_excel: int) -> str:
    return f"{get_column_letter(kolom_idx + 1)}{baris_excel}"


def terapkan(lembar: Lembar, perbaikan: list[Perbaikan]) -> tuple[Lembar, list[dict]]:
    """Terapkan perbaikan otomatis ke salinan data.

    Hanya Perbaikan dengan aman_otomatis=True yang diterapkan (D-009).
    Mengembalikan (Lembar baru, daftar catatan perubahan).
    """
    baris = [list(b) for b in lembar.baris]
    baris_excel = list(lembar.baris_excel)
    perubahan = []

    for p in perbaikan:
        if not p.aman_otomatis:
            continue
        try:
            r = baris_excel.index(p.baris_excel)
        except ValueError:
            continue
        if p.kolom_idx >= len(baris[r]):
            continue
        lama = baris[r][p.kolom_idx]
        if lama == p.nilai_baru:
            continue
        baris[r][p.kolom_idx] = p.nilai_baru
        perubahan.append({
            "sheet": lembar.nama,
            "sel": _sel_ref(p.kolom_idx, p.baris_excel),
            "kolom": p.kolom,
            "nilai_lama": lama,
            "nilai_baru": p.nilai_baru,
            "kode": p.kode,
            "aturan": p.aturan,
        })

    baru = Lembar(
        nama=lembar.nama,
        header=list(lembar.header),
        baris_header=lembar.baris_header,
        baris=baris,
        baris_excel=baris_excel,
        baris_kosong_dibuang=lembar.baris_kosong_dibuang,
    )
    return baru, perubahan


def tulis_audit(path: str | Path, perubahan: list[dict]) -> None:
    """Tulis audit log .jsonl (satu baris per perubahan)."""
    waktu = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        for i, p in enumerate(perubahan, start=1):
            catatan = {"id": i, "waktu": waktu, **p}
            f.write(json.dumps(catatan, ensure_ascii=False) + "\n")
