"""Jalankan detector dedupe."""

from ..io import Lembar
from ..model import Temuan
from ..profiling.profiler import Profil
from . import mirip, persis


def deteksi(lembar: Lembar, profil: Profil) -> list[Temuan]:
    hasil = persis.deteksi(lembar)
    hasil.extend(mirip.deteksi(lembar, profil))
    return hasil
