import re
from pathlib import Path

from typer.testing import CliRunner

from beberes.cli.main import app
from beberes.i18n import atur_bahasa, t

runner = CliRunner()


def test_versi():
    hasil = runner.invoke(app, ["versi", "--lang", "en"])
    assert hasil.exit_code == 0
    assert re.search(r"\d+\.\d+\.\d+", hasil.output)


def test_alias_dua_bahasa(tmp_path: Path):
    berkas = tmp_path / "x.csv"
    berkas.write_text("a,b\n1,2\n")
    for perintah in ("periksa", "check", "bersihkan", "clean"):
        hasil = runner.invoke(app, [perintah, str(berkas), "--lang", "en"])
        assert hasil.exit_code == 0, perintah


def test_berkas_tidak_ada():
    hasil = runner.invoke(app, ["check", "tidak_ada.xlsx", "--lang", "en"])
    assert hasil.exit_code == 3


def test_i18n_dua_bahasa():
    atur_bahasa("id")
    assert "Berkas tidak ditemukan" in t("berkas_tidak_ada", berkas="a")
    atur_bahasa("en")
    assert "File not found" in t("berkas_tidak_ada", berkas="a")
    atur_bahasa(None)
