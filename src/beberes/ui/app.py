"""Backend UI lokal: FastAPI membungkus core beberes.

Alur: upload -> periksa (temuan+skor JSON) -> bersihkan (file baru + audit).
Semua logika tetap di core; lapisan ini hanya terjemahkan HTTP <-> core.
"""

import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from openpyxl.utils import get_column_letter

from ..detectors import jalankan as deteksi_semua
from ..fixers import usulkan_semua
from ..io import Lembar, baca_berkas, simpan
from ..model import Perbaikan
from ..profiling import hitung_skor, profil_lbr
from ..report import terapkan
from ..rules import muat as muat_aturan
from ..rules import periksa as periksa_aturan

_TEMPLATE = Path(__file__).parent / "index.html"


def _proses_lembar(lembar: Lembar, aturan) -> tuple[list, list[Perbaikan], int]:
    """Deteksi + usulkan perbaikan untuk satu sheet."""
    profil = profil_lbr(lembar)
    temuan = deteksi_semua(lembar, profil)
    if aturan is not None:
        temuan.extend(periksa_aturan(lembar, aturan))
    skor = hitung_skor(profil, temuan)
    perbaikan = usulkan_semua(temuan, lembar)
    return temuan, perbaikan, skor


def _perbaikan_json(p: Perbaikan, gid: int) -> dict:
    return {
        "id": gid,
        "kode": p.kode,
        "aturan": p.aturan,
        "kolom": p.kolom,
        "baris_excel": p.baris_excel,
        "sel": f"{get_column_letter(p.kolom_idx + 1)}{p.baris_excel}",
        "nilai_lama": str(p.nilai_lama),
        "nilai_baru": str(p.nilai_baru),
        "aman_otomatis": p.aman_otomatis,
    }


def _proses_berkas(path: Path, aturan=None):
    """Kembalikan (lembar_list, ringkasan per sheet) dengan detail perbaikan."""
    ringkasan = []
    gid = 0
    for lembar in baca_berkas(path):
        temuan, perbaikan, skor = _proses_lembar(lembar, aturan)
        ringkasan.append({
            "sheet": lembar.nama,
            "baris": len(lembar.baris),
            "kolom": len(lembar.header),
            "skor": skor,
            "temuan": [
                {"kode": t.kode, "kolom": t.kolom, "tingkat": t.tingkat,
                 "pesan": t.pesan, "contoh": t.contoh[:5]}
                for t in temuan
            ],
            "perbaikan": len(perbaikan),
            "konfirmasi": sum(1 for p in perbaikan if not p.aman_otomatis),
            "detail": [_perbaikan_json(p, gid + i) for i, p in enumerate(perbaikan)],
        })
        gid += len(perbaikan)
    return ringkasan


async def _simpan_unggahan(file: UploadFile) -> Path:
    with tempfile.NamedTemporaryFile(
        suffix=Path(file.filename or "data.xlsx").suffix, delete=False
    ) as tmp:
        tmp.write(await file.read())
        return Path(tmp.name)


def _muat_aturan(aturan: str | None):
    if not aturan:
        return None
    with tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w", encoding="utf-8"
    ) as yf:
        yf.write(aturan)
    return muat_aturan(Path(yf.name))


def buat_app() -> FastAPI:
    app = FastAPI(title="beberes", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index():
        return _TEMPLATE.read_text(encoding="utf-8")

    @app.post("/api/periksa")
    async def periksa(file: UploadFile = File(...), aturan: str | None = Form(None)):
        path = await _simpan_unggahan(file)
        try:
            return {"lembar": _proses_berkas(path, _muat_aturan(aturan))}
        except Exception as e:
            raise HTTPException(400, f"Gagal memproses: {e}") from e
        finally:
            path.unlink(missing_ok=True)

    @app.post("/api/bersihkan")
    async def bersihkan(
        file: UploadFile = File(...),
        aturan: str | None = Form(None),
        terpilih: str | None = Form(None),
    ):
        path = await _simpan_unggahan(file)
        try:
            at = _muat_aturan(aturan)
            lembar_list = baca_berkas(path)
            semua_perubahan = []
            keluar_lembar = []

            # indeks perbaikan bersifat deterministik: file sama -> urutan sama,
            # jadi pilihan dari /api/periksa tetap valid di sini.
            pilihan = None
            if terpilih is not None:
                pilihan = set(json.loads(terpilih))

            gid = 0
            for lembar in lembar_list:
                _, perbaikan, _ = _proses_lembar(lembar, at)
                if pilihan is None:
                    subset = perbaikan
                    abaikan = False
                else:
                    subset = [
                        p for i, p in enumerate(perbaikan)
                        if gid + i in pilihan
                    ]
                    abaikan = True
                gid += len(perbaikan)
                baru, perubahan = terapkan(
                    lembar, subset, abaikan_aman_otomatis=abaikan
                )
                keluar_lembar.append(baru)
                semua_perubahan.extend(perubahan)

            # simpan ke folder unduhan temporer sesi ini; disajikan /unduh/
            folder = _folder_unduhan()
            suf = ".csv" if path.suffix.lower() == ".csv" else ".xlsx"
            if len(keluar_lembar) > 1:
                suf = ".xlsx"
            nama_keluar = (
                Path(file.filename or "data").stem + "_bersih" + suf
            )
            tujuan = folder / nama_keluar
            simpan(keluar_lembar, tujuan)

            audit = "\n".join(
                json.dumps(p, ensure_ascii=False) for p in semua_perubahan
            )
            return {
                "unduh": f"/unduh/{nama_keluar}",
                "audit": audit,
                "perubahan": len(semua_perubahan),
                "diff": [
                    {
                        "sheet": p["sheet"], "sel": p["sel"],
                        "kolom": p["kolom"], "kode": p["kode"],
                        "nilai_lama": str(p["nilai_lama"]),
                        "nilai_baru": str(p["nilai_baru"]),
                    }
                    for p in semua_perubahan
                ],
            }
        except Exception as e:
            raise HTTPException(400, f"Gagal membersihkan: {e}") from e
        finally:
            path.unlink(missing_ok=True)

    @app.get("/unduh/{nama}")
    def unduh(nama: str):
        file = _folder_unduhan() / nama
        if not file.exists() or file.parent != _folder_unduhan():
            raise HTTPException(404, "File tidak ditemukan")
        return FileResponse(file, filename=nama)

    return app


_UNDUHAN: Path | None = None


def _folder_unduhan() -> Path:
    global _UNDUHAN
    if _UNDUHAN is None:
        _UNDUHAN = Path(tempfile.mkdtemp(prefix="beberes_"))
    return _UNDUHAN
