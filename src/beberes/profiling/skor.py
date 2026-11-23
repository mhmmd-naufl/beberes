"""Skor kualitas gabungan: kemurnian tipe (profiler) dikurangi penalti temuan."""

from ..model import Temuan
from .profiler import Profil

# Penalti per sel bermasalah, dan batas maksimal penalti per kolom.
PENALTI_PER_SEL = 2.0
BATAS_PENALTI = 50.0


def hitung_skor(profil: Profil, temuan: list[Temuan]) -> float:
    """Skor 0-100: rata-rata (skor kolom - penalti temuan), dibatasi 0.

    Temuan tanpa daftar sel (mis. KSG002) dihitung dari len(baris)-nya;
    yang sama sekali tanpa sel/baris diabaikan.
    """
    penalti: dict[str, float] = {}
    for tm in temuan:
        n = len(tm.sel) or len(tm.baris)
        if n:
            penalti[tm.kolom] = penalti.get(tm.kolom, 0.0) + n

    skor = []
    for k in profil.kolom:
        p = min(BATAS_PENALTI, PENALTI_PER_SEL * penalti.get(k.nama, 0))
        skor.append(max(0.0, k.skor - p))
    return round(sum(skor) / len(skor), 1) if skor else 0.0
