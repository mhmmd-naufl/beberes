"""Helper iterasi sel kolom untuk detector."""

from ..io import Lembar
from ..profiling.profiler import Profil


def tipe_kolom(profil: Profil) -> dict[int, str]:
    """Peta indeks kolom -> tipe_utama."""
    return {i: k.tipe_utama for i, k in enumerate(profil.kolom)}


def iter_sel(lembar: Lembar):
    """Yield (kolom_idx, nilai, baris_excel) untuk tiap sel non-kosong."""
    for baris, no_excel in zip(lembar.baris, lembar.baris_excel, strict=False):
        for c, nilai in enumerate(baris):
            if nilai is not None and str(nilai).strip() != "":
                yield c, nilai, no_excel
