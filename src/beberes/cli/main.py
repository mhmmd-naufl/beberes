"""CLI beberes. Perintah punya alias dua bahasa (D-006)."""
from collections import defaultdict
from pathlib import Path

import typer

from beberes import __version__
from beberes.detectors import jalankan as deteksi_semua
from beberes.fixers import usulkan_semua
from beberes.i18n import atur_bahasa, t
from beberes.io import baca_berkas, simpan
from beberes.profiling import hitung_skor, profil_lbr
from beberes.report import (
    buat_baris,
    terapkan,
    tulis_audit,
    tulis_laporan,
    urungkan,
)
from beberes.rules import muat as muat_aturan
from beberes.rules import periksa as periksa_aturan

app = typer.Typer(
    help="beberes: Tidy up messy Indonesian spreadsheets.",
    no_args_is_help=True,
    add_completion=False,
)

@app.callback(invoke_without_command=True)
def _root(
    versi_flag: bool = typer.Option(
        False, "--version", "-v", is_eager=True,
        help="Tampilkan versi | Show version",
    ),
) -> None:
    if versi_flag:
        atur_bahasa(None)
        typer.echo(t("versi", versi=__version__))
        raise typer.Exit()


BERKAS = typer.Argument(..., help="Berkas .xlsx / .csv  |  File to process")
BAHASA = typer.Option(None, "--bahasa", "--lang", help="id | en")


def _siapkan(berkas: Path, bahasa: str | None) -> None:
    atur_bahasa(bahasa)
    if not berkas.exists():
        typer.echo(t("berkas_tidak_ada", berkas=berkas), err=True)
        raise typer.Exit(code=3)


def _proses(berkas: Path, aturan=None):
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
        if aturan is not None:
            temuan.extend(periksa_aturan(lembar, aturan))
        perbaikan = usulkan_semua(temuan, lembar)
        hasil.append((lembar, profil, temuan, perbaikan))
    return hasil


def _muat_aturan(aturan: Path | None):
    if aturan is None:
        return None
    try:
        return muat_aturan(aturan)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=2) from e


def _ada_yang_perlu_keputusan(hasil) -> bool:
    for _, _, temuan, perbaikan in hasil:
        if any(x.tingkat == "error" for x in temuan):
            return True
        if any(not p.aman_otomatis for p in perbaikan):
            return True
    return False


def _cetak_ringkasan(berkas: Path, hasil, skor_sesudah=None) -> None:
    for i, (lembar, profil, temuan, perbaikan) in enumerate(hasil):
        ss = skor_sesudah[i] if skor_sesudah else None
        for baris in buat_baris(str(berkas), lembar, profil, temuan, perbaikan, ss):
            typer.echo(baris)
        typer.echo("")


OPSI_ATURAN = typer.Option(
    None, "--aturan", "--rules", help="File aturan YAML | Rules file"
)


def periksa(
    berkas: Path = BERKAS,
    aturan: Path | None = OPSI_ATURAN,
    bahasa: str | None = BAHASA,
) -> None:
    """Lihat masalah tanpa mengubah apa pun  |  Inspect only, change nothing."""
    _siapkan(berkas, bahasa)
    hasil = _proses(berkas, _muat_aturan(aturan))
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
    aturan: Path | None = OPSI_ATURAN,
    konfirmasi: bool = typer.Option(
        False, "--konfirmasi", "--confirm",
        help="Tanya sebelum terapkan perbaikan ambigu | Ask before ambiguous fixes",
    ),
    bahasa: str | None = BAHASA,
) -> None:
    """Terapkan perbaikan ke berkas baru  |  Apply fixes to a new file."""
    _siapkan(berkas, bahasa)
    hasil = _proses(berkas, _muat_aturan(aturan))

    if konfirmasi:
        _konfirmasi_perbaikan(hasil)

    if keluar is None:
        keluar = berkas.with_stem(berkas.stem + "_bersih").with_suffix(berkas.suffix)

    lembar_baru = []
    skor_sesudah = []
    semua_perubahan = []
    for lembar, _, _, perbaikan in hasil:
        baru, perubahan = terapkan(lembar, perbaikan)
        profil_sesudah = profil_lbr(baru)
        temuan_sesudah = deteksi_semua(baru, profil_sesudah)
        skor_sesudah.append(hitung_skor(profil_sesudah, temuan_sesudah))
        lembar_baru.append(baru)
        semua_perubahan.extend(perubahan)

    simpan(lembar_baru, keluar)

    if laporan:
        for i, skor in enumerate(skor_sesudah):
            lembar_asal, profil_asal, temuan_asal, perbaikan_asal = hasil[i]
            tulis_laporan(
                keluar.with_suffix(".laporan.md"), str(berkas), lembar_asal,
                profil_asal, temuan_asal, perbaikan_asal, skor,
            )
            typer.echo(t("laporan_tersimpan", path=keluar.with_suffix(".laporan.md")))

    if semua_perubahan:
        audit = keluar.parent / (keluar.stem + ".audit.jsonl")
        tulis_audit(audit, semua_perubahan)
        typer.echo(t("audit_tersimpan", path=audit))

    _cetak_ringkasan(berkas, hasil, skor_sesudah)
    n_konfirmasi = sum(
        1 for _, _, _, perbaikan in hasil for p in perbaikan if not p.aman_otomatis
    )
    if n_konfirmasi:
        typer.echo(t("butuh_keputusan", n=n_konfirmasi))
    typer.echo(t("diterapkan", n=len(semua_perubahan), keluar=keluar))
    raise typer.Exit(code=1 if _ada_yang_perlu_keputusan(hasil) else 0)


def _konfirmasi_perbaikan(hasil) -> None:
    """Tanya y/n per kelompok kode untuk Perbaikan non-otomatis."""
    grup: dict[str, list] = defaultdict(list)
    for _, _, _, perbaikan in hasil:
        for p in perbaikan:
            if not p.aman_otomatis:
                grup[p.kode].append(p)

    for kode, daftar in grup.items():
        contoh = ", ".join(
            f"{p.nilai_lama!r}->{p.nilai_baru!r}" for p in daftar[:3]
        )
        setuju = typer.confirm(
            t("konfirmasi_tanya", kode=kode, n=len(daftar), contoh=contoh)
        )
        if setuju:
            for p in daftar:
                p.aman_otomatis = True
        else:
            for p in daftar:
                p.aman_otomatis = False


def urungkan_cmd(
    berkas: Path = BERKAS,
    log: Path = typer.Option(
        ..., "--log", help="File audit .jsonl | Audit log file"
    ),
    keluar: Path | None = typer.Option(
        None, "--keluar", "--out", help="Berkas keluaran | Output file"
    ),
    bahasa: str | None = BAHASA,
) -> None:
    """Kembalikan perubahan dari audit log  |  Undo changes from audit log."""
    _siapkan(berkas, bahasa)
    if not log.exists():
        typer.echo(t("log_tidak_ada", log=log), err=True)
        raise typer.Exit(code=3)
    try:
        lembar_list = urungkan(berkas, log)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=3) from e
    if keluar is None:
        keluar = berkas.with_stem(berkas.stem + "_undo").with_suffix(berkas.suffix)
    simpan(lembar_list, keluar)
    typer.echo(t("urungkan_selesai", keluar=keluar))


def versi(bahasa: str | None = BAHASA) -> None:
    """Tampilkan versi  |  Show version."""
    atur_bahasa(bahasa)
    typer.echo(t("versi", versi=__version__))


# Alias dua bahasa: satu fungsi, dua nama perintah.
app.command("periksa")(periksa)
app.command("check")(periksa)
app.command("bersihkan")(bersihkan)
app.command("clean")(bersihkan)
app.command("urungkan")(urungkan_cmd)
app.command("undo")(urungkan_cmd)
app.command("versi")(versi)
app.command("version")(versi)


if __name__ == "__main__":
    app()
