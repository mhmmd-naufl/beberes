"""CLI beberes. Perintah punya alias dua bahasa (D-006)."""
from pathlib import Path

import typer

from beberes import __version__
from beberes.detectors import jalankan as deteksi_semua
from beberes.fixers import usulkan_semua
from beberes.i18n import atur_bahasa, t
from beberes.io import baca_berkas, simpan
from beberes.profiling import profil_lbr
from beberes.report import buat_baris, terapkan, tulis_audit, tulis_laporan

app = typer.Typer(
    help="beberes: Tidy up messy Indonesian spreadsheets.",
    no_args_is_help=True,
    add_completion=False,
)

BERKAS = typer.Argument(..., help="Berkas .xlsx / .csv  |  File to process")
BAHASA = typer.Option(None, "--bahasa", "--lang", help="id | en")


def _siapkan(berkas: Path, bahasa: str | None) -> None:
    atur_bahasa(bahasa)
    if not berkas.exists():
        typer.echo(t("berkas_tidak_ada", berkas=berkas), err=True)
        raise typer.Exit(code=3)


def _proses(berkas: Path):
    """Baca -> profil -> deteksi -> usulkan. Kembalikan hasil per lembar."""
    try:
        lembar_list = baca_berkas(berkas)
    except (ValueError, OSError) as e:
        typer.echo(t("error_baca", detail=e), err=True)
        raise typer.Exit(code=3) from e

    hasil = []
    for lembar in lembar_list:
        profil = profil_lbr(lembar)
        temuan = deteksi_semua(lembar, profil)
        perbaikan = usulkan_semua(temuan, lembar)
        hasil.append((lembar, profil, temuan, perbaikan))
    return hasil


def _ada_yang_perlu_keputusan(hasil) -> bool:
    for _, _, temuan, perbaikan in hasil:
        if any(x.tingkat == "error" for x in temuan):
            return True
        if any(not p.aman_otomatis for p in perbaikan):
            return True
    return False


def _cetak_ringkasan(berkas: Path, hasil, profil_sesudah=None) -> None:
    for i, (lembar, profil, temuan, perbaikan) in enumerate(hasil):
        ps = profil_sesudah[i] if profil_sesudah else None
        for baris in buat_baris(str(berkas), lembar, profil, temuan, perbaikan, ps):
            typer.echo(baris)
        typer.echo("")


def periksa(berkas: Path = BERKAS, bahasa: str | None = BAHASA) -> None:
    """Lihat masalah tanpa mengubah apa pun  |  Inspect only, change nothing."""
    _siapkan(berkas, bahasa)
    hasil = _proses(berkas)
    _cetak_ringkasan(berkas, hasil)
    if not any(tm for _, _, temuan, _ in hasil for tm in temuan):
        typer.echo(t("tidak_ada_temuan"))
    raise typer.Exit(code=1 if _ada_yang_perlu_keputusan(hasil) else 0)


def bersihkan(
    berkas: Path = BERKAS,
    keluar: Path | None = typer.Option(
        None, "--keluar", "--out", help="Berkas keluaran | Output file"
    ),
    laporan: bool = typer.Option(
        False, "--laporan", "--report", help="Buat laporan | Write report"
    ),
    bahasa: str | None = BAHASA,
) -> None:
    """Terapkan perbaikan ke berkas baru  |  Apply fixes to a new file."""
    _siapkan(berkas, bahasa)
    hasil = _proses(berkas)

    if keluar is None:
        keluar = berkas.with_stem(berkas.stem + "_bersih").with_suffix(berkas.suffix)

    lembar_baru = []
    semua_perubahan = []
    for lembar, _, _, perbaikan in hasil:
        baru, perubahan = terapkan(lembar, perbaikan)
        lembar_baru.append((baru, profil_lbr(baru)))
        semua_perubahan.extend(perubahan)

    simpan([b for b, _ in lembar_baru], keluar)

    for i, (_, profil_sesudah) in enumerate(lembar_baru):
        lembar_asal, profil_asal, temuan_asal, perbaikan_asal = hasil[i]
        if laporan:
            tulis_laporan(
                keluar.with_suffix(".laporan.md"), str(berkas), lembar_asal,
                profil_asal, temuan_asal, perbaikan_asal, profil_sesudah,
            )
            typer.echo(t("laporan_tersimpan", path=keluar.with_suffix(".laporan.md")))

    if semua_perubahan:
        audit = keluar.parent / (keluar.stem + ".audit.jsonl")
        tulis_audit(audit, semua_perubahan)
        typer.echo(t("audit_tersimpan", path=audit))

    _cetak_ringkasan(berkas, hasil, [p for _, p in lembar_baru])
    n_konfirmasi = sum(
        1 for _, _, _, perbaikan in hasil for p in perbaikan if not p.aman_otomatis
    )
    if n_konfirmasi:
        typer.echo(t("butuh_keputusan", n=n_konfirmasi))
    typer.echo(t("diterapkan", n=len(semua_perubahan), keluar=keluar))
    raise typer.Exit(code=1 if _ada_yang_perlu_keputusan(hasil) else 0)


def versi(bahasa: str | None = BAHASA) -> None:
    """Tampilkan versi  |  Show version."""
    atur_bahasa(bahasa)
    typer.echo(t("versi", versi=__version__))


# Alias dua bahasa: satu fungsi, dua nama perintah.
app.command("periksa")(periksa)
app.command("check")(periksa)
app.command("bersihkan")(bersihkan)
app.command("clean")(bersihkan)
app.command("versi")(versi)
app.command("version")(versi)


if __name__ == "__main__":
    app()
