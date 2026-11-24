"""Undo: kembalikan nilai lama berdasarkan audit log .jsonl (docs/03 bagian 5).

Membaca file hasil bersih + log audit, lalu menulis file baru dengan
nilai_lama dipulihkan. File input tidak pernah ditimpa.
"""

import json
from pathlib import Path

from openpyxl.utils import column_index_from_string

from ..io import Lembar, baca_berkas, simpan


def _baca_log(path: Path) -> list[dict]:
    entri = []
    for i, baris in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        baris = baris.strip()
        if not baris:
            continue
        try:
            entri.append(json.loads(baris))
        except json.JSONDecodeError as e:
            raise ValueError(f"Baris {i} audit log bukan JSON valid: {e}") from e
    return entri


def _posisi_sel(entri: dict) -> tuple[int, int] | None:
    """(kolom_idx, baris_excel) dari entri audit.

    Utama: kolom_idx + baris_excel (format baru). Cadangan: parse "E6".
    """
    if "kolom_idx" in entri and "baris_excel" in entri:
        return int(entri["kolom_idx"]), int(entri["baris_excel"])
    sel = entri.get("sel", "")
    if not sel:
        return None
    huruf = ""
    for ch in sel:
        if ch.isalpha():
            huruf += ch
        else:
            break
    if not huruf:
        return None
    try:
        return column_index_from_string(huruf) - 1, int(sel[len(huruf):])
    except ValueError:
        return None


def urungkan(berkas: str | Path, log: str | Path) -> list[Lembar]:
    """Kembalikan daftar Lembar dengan nilai_lama dipulihkan."""
    lembar_list = baca_berkas(berkas)
    entri = _baca_log(Path(log))

    for e in entri:
        sheet = e.get("sheet")
        pos = _posisi_sel(e)
        if pos is None:
            continue
        c, no_excel = pos
        lembar = next((x for x in lembar_list if x.nama == sheet), None)
        if lembar is None:
            continue
        try:
            r = lembar.baris_excel.index(no_excel)
        except ValueError:
            continue
        if c < len(lembar.baris[r]):
            lembar.baris[r][c] = e.get("nilai_lama")

    return lembar_list


def simpan_hasil(lembar_list: list[Lembar], keluar: str | Path) -> None:
    simpan(lembar_list, keluar)
