from .email import periksa_email
from .gelar import GELAR, periksa_gelar, pisah_gelar
from .hp import normalisasi_hp, periksa_hp
from .nik import periksa_nik
from .npwp import periksa_npwp
from .plat import periksa_plat
from .wilayah import (
    induk_wilayah,
    normalisasi_wilayah,
    periksa_wilayah,
    saran_wilayah,
)

__all__ = [
    "GELAR",
    "normalisasi_hp",
    "periksa_gelar",
    "pisah_gelar",
    "periksa_hp",
    "periksa_nik",
    "periksa_npwp",
    "periksa_plat",
    "normalisasi_wilayah",
    "periksa_wilayah",
    "saran_wilayah",
    "induk_wilayah",
    "kode_wilayah_valid",
    "nama_wilayah",
    "periksa_email",
]
