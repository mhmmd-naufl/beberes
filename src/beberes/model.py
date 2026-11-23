"""Model data inti: Temuan (masalah) dan Perbaikan (usulan perubahan).

Sesuai docs/03 bagian 2 dan docs/02 "Model data inti".
"""

from dataclasses import dataclass, field


@dataclass
class Temuan:
    """Satu jenis masalah di satu kolom."""

    kode: str                 # FMT001, TGL001, dst (docs/03 bagian 2)
    kolom: str                # nama kolom
    tingkat: str              # info | peringatan | error
    pesan: str
    baris: list = field(default_factory=list)   # nomor baris Excel
    contoh: list = field(default_factory=list)  # contoh nilai
    sel: list = field(default_factory=list)     # {baris_excel, kolom_idx, nilai}


@dataclass
class Perbaikan:
    """Usulan perubahan satu sel. Belum tentu diterapkan."""

    kode: str                 # kode temuan asal
    aturan: str               # nama aturan/fixer
    baris_excel: int
    kolom_idx: int
    kolom: str
    nilai_lama: object
    nilai_baru: object
    aman_otomatis: bool = True  # False = mengubah makna, butuh konfirmasi (D-009)
