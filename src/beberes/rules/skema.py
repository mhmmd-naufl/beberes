"""Skema aturan YAML (docs/03 bagian 1). Validasi dengan pydantic."""

from pydantic import BaseModel, Field, ValidationError

# Tipe kolom yang didukung rules engine (docs/03).
TIPE_VALID = {
    "teks", "nama", "angka", "uang", "tanggal", "hp", "nik", "npwp",
    "plat", "wilayah", "kategori", "email",
}


class AturanKolom(BaseModel):
    tipe: str
    format_masuk: list[str] | None = None
    format_keluar: str | None = None
    aturan: list[str] | None = None
    tingkat: str | None = None      # untuk wilayah
    induk: str | None = None        # nama kolom induk (wilayah)


class AturanGlobal(BaseModel):
    hapus_baris_kosong: bool = True
    tandai_duplikat: dict | None = None


class Aturan(BaseModel):
    versi: int = 1
    nama: str = ""
    kolom: dict[str, AturanKolom] = Field(default_factory=dict)
    global_: AturanGlobal | None = Field(default=None, alias="global")

    model_config = {"populate_by_name": True}


def validasi(data: dict) -> Aturan:
    """Ubah dict -> Aturan. Lempar ValidationError dengan pesan jelas."""
    try:
        aturan = Aturan.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Aturan tidak valid: {e}") from e
    for nama_kolom, k in aturan.kolom.items():
        if k.tipe not in TIPE_VALID:
            raise ValueError(
                f"Tipe tidak dikenal untuk kolom '{nama_kolom}': {k.tipe} "
                f"(pilihan: {', '.join(sorted(TIPE_VALID))})"
            )
    return aturan
