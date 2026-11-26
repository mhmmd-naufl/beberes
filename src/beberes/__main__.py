"""Memungkinkan `python -m beberes` — dipakai install.bat agar tidak
bergantung pada folder Scripts yang mungkin belum ada di PATH."""

from beberes.cli.main import app

if __name__ == "__main__":
    app()
