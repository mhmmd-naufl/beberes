"""CLI beberes. Perintah punya alias dua bahasa (D-006). Masih stub: belum ada logika core."""
from pathlib import Path

import typer

from beberes import __version__
from beberes.i18n import atur_bahasa, t

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


def periksa(berkas: Path = BERKAS, bahasa: str | None = BAHASA) -> None:
    """Lihat masalah tanpa mengubah apa pun  |  Inspect only, change nothing."""
    _siapkan(berkas, bahasa)
    typer.echo(t("belum_ada", perintah="periksa/check", berkas=berkas))


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
    typer.echo(t("belum_ada", perintah="bersihkan/clean", berkas=berkas))


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
