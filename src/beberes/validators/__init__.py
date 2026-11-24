from .gelar import GELAR, periksa_gelar
from .hp import normalisasi_hp, periksa_hp
from .nik import periksa_nik
from .npwp import periksa_npwp
from .plat import periksa_plat
from .wilayah import normalisasi_wilayah, periksa_wilayah, saran_wilayah

__all__ = [
    "GELAR",
    "normalisasi_hp",
    "periksa_gelar",
    "periksa_hp",
    "periksa_nik",
    "periksa_npwp",
    "periksa_plat",
    "normalisasi_wilayah",
    "periksa_wilayah",
    "saran_wilayah",
]
