"""DUP001: baris duplikat persis (semua sel sama)."""

from ..io import Lembar
from ..model import Temuan


def _kunci(baris: list) -> tuple:
    return tuple("" if c is None else str(c).strip().lower() for c in baris)


def deteksi(lembar: Lembar) -> list[Temuan]:
    grup: dict[tuple, list[int]] = {}
    for i, baris in enumerate(lembar.baris):
        grup.setdefault(_kunci(baris), []).append(i)

    duplikat = [idxs for idxs in grup.values() if len(idxs) > 1]
    if not duplikat:
        return []

    baris_excel = []
    contoh = []
    for idxs in duplikat:
        baris_excel.extend(lembar.baris_excel[i] for i in idxs)
        contoh.append(" | ".join(
            str(c) for c in lembar.baris[idxs[0]] if c is not None
        )[:80])

    return [Temuan(
        kode="DUP001", kolom="(baris)", tingkat="info",
        pesan=f"{sum(len(x) for x in duplikat)} baris duplikat persis "
              f"dalam {len(duplikat)} grup (tidak dihapus otomatis)",
        baris=sorted(baris_excel), contoh=contoh[:5],
    )]
