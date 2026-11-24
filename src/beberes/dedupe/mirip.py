"""DUP002: baris mirip (fuzzy) pada kolom teks pertama yang dominan.

Membandingkan nama/kunci teks antar baris dengan rasio kemiripan
difflib >= AMBANG. Blocking per huruf pertama agar tidak O(n²).
"""

import difflib
import re

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil

AMBANG = 0.85
_MAKS_CONTOH = 10
_MAKS_GRUP_BLOKIR = 500  # blok terlalu besar -> lewati (file raksasa)

_RE_NONALFA = re.compile(r"[^a-z0-9 ]+")
_SPASI = re.compile(r"\s+")


def _norm(teks) -> str:
    if teks is None:
        return ""
    t = _RE_NONALFA.sub("", str(teks).lower())
    return _SPASI.sub(" ", t).strip()


def _kolom_kunci(lembar: Lembar, profil: Profil) -> int | None:
    """Kolom teks pertama dengan isi >50% — biasanya nama/kunci."""
    for c, k in enumerate(profil.kolom):
        if k.tipe_utama == "teks" and k.persen_kosong < 50:
            return c
    return None


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    c = _kolom_kunci(lembar, profil)
    if c is None:
        return []

    blok: dict[str, list[tuple[int, str]]] = {}
    for i, baris in enumerate(lembar.baris):
        if c >= len(baris):
            continue
        nilai = _norm(baris[c])
        if len(nilai) < 3:
            continue
        blok.setdefault(nilai[0], []).append((i, nilai))

    pasangan = []
    for grup in blok.values():
        if len(grup) > _MAKS_GRUP_BLOKIR:
            continue
        for a in range(len(grup)):
            for b in range(a + 1, len(grup)):
                i, x = grup[a]
                j, y = grup[b]
                if x == y:
                    continue  # duplikat persis -> DUP001
                rasio = difflib.SequenceMatcher(None, x, y).ratio()
                if rasio >= AMBANG:
                    pasangan.append((rasio, i, j, x, y))

    if not pasangan:
        return []
    pasangan.sort(reverse=True)
    contoh = [f"{x!r} ~ {y!r}" for _, _, _, x, y in pasangan[:_MAKS_CONTOH]]
    baris = sorted({
        lembar.baris_excel[i] for _, i, j, _, _ in pasangan
    } | {lembar.baris_excel[j] for _, i, j, _, _ in pasangan})

    return [Temuan(
        kode="DUP002", kolom=lembar.header[c] if c < len(lembar.header) else "?",
        tingkat="peringatan",
        pesan=f"{len(pasangan)} pasangan baris mirip (kemiripan >= {AMBANG})",
        baris=baris, contoh=contoh,
    )]
