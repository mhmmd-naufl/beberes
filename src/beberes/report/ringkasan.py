"""Ringkasan laporan: teks untuk terminal dan laporan.md."""

from collections import Counter
from pathlib import Path

from ..i18n import t
from ..io import Lembar
from ..model import Perbaikan, Temuan
from ..profiling.profiler import Profil


def _hitung_tingkat(temuan: list[Temuan]) -> Counter:
    return Counter(x.tingkat for x in temuan)


def buat_baris(
    berkas: str,
    lembar: Lembar,
    profil: Profil,
    temuan: list[Temuan],
    perbaikan: list[Perbaikan],
) -> list[str]:
    """Baris-baris laporan ringkas (dua bahasa via i18n)."""
    tingkat = _hitung_tingkat(temuan)
    otomatis = sum(1 for p in perbaikan if p.aman_otomatis)
    konfirmasi = len(perbaikan) - otomatis
    skor_rata = (
        sum(k.skor for k in profil.kolom) / len(profil.kolom) if profil.kolom else 0
    )

    baris = [
        t("laporan_judul", berkas=berkas),
        t(
            "laporan_lembar",
            sheet=lembar.nama, baris=len(lembar.baris), kolom=len(lembar.header),
        ),
        "",
        t("skor_kualitas", skor=f"{skor_rata:.0f}"),
        t(
            "temuan_ringkas",
            total=len(temuan),
            error=tingkat.get("error", 0),
            peringatan=tingkat.get("peringatan", 0),
            info=tingkat.get("info", 0),
        ),
        t(
            "perbaikan_ringkas",
            total=len(perbaikan), otomatis=otomatis, konfirmasi=konfirmasi,
        ),
        "",
        t("per_kolom", judul=""),
    ]

    # Ringkasan per kolom: kode masalah + jumlah sel.
    per_kolom: dict[str, Counter] = {}
    for tm in temuan:
        if tm.sel:
            per_kolom.setdefault(tm.kolom, Counter())[tm.kode] += len(tm.sel)
        elif tm.baris:
            per_kolom.setdefault(tm.kolom, Counter())[tm.kode] += len(tm.baris)
    for kolom, hitung in per_kolom.items():
        detail = ", ".join(f"{kode} x{n}" for kode, n in hitung.most_common())
        baris.append(f"  {kolom}: {detail}")
    return baris


def tulis_laporan(
    path: str | Path,
    berkas: str,
    lembar: Lembar,
    profil: Profil,
    temuan: list[Temuan],
    perbaikan: list[Perbaikan],
) -> None:
    baris = buat_baris(berkas, lembar, profil, temuan, perbaikan)
    Path(path).write_text("\n".join(baris) + "\n", encoding="utf-8")
