"""Loader aturan YAML."""

from pathlib import Path

import yaml

from .skema import Aturan, validasi


def muat(path: str | Path) -> Aturan:
    """Baca file YAML aturan -> objek Aturan tervalidasi."""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"File aturan tidak ditemukan: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ValueError(f"YAML tidak bisa dibaca: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("Isi file aturan harus berupa mapping YAML")
    return validasi(data)
