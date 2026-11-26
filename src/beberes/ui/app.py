"""Backend UI lokal: FastAPI membungkus core beberes.

Alur: upload -> periksa (temuan+skor JSON) -> bersihkan (file baru + audit)
-> opsional urungkan. Semua logika tetap di core; lapisan ini hanya
menerjemahkan HTTP <-> core.
"""

import json
import sys
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
from ..report import terapkan, tulis_audit, urungkan
from ..rules import muat as muat_aturan
from ..rules import periksa as periksa_aturan


def _ui_dir() -> Path:
    """Folder aset UI: source checkout atau bundle PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "beberes" / "ui"
    return Path(__file__).parent


_TEMPLATE = _ui_dir() / "index.html"
_ICONS = _ui_dir() / "icons"
_DIR = _ui_dir()
_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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


def _kunci_grup(p) -> str:
    """Kunci unik satu grup perbaikan (kode+kolom+aturan+tingkat aman)."""
    return f"{p.kode}|{p.kolom}|{p.aturan}|{int(p.aman_otomatis)}"


def _grup_perbaikan(perbaikan) -> list[dict]:
    """Kelompokkan Perbaikan per kunci; ringkas untuk UI (maks 3 contoh)."""
    grup: dict[str, dict] = {}
    for p in perbaikan:
        k = _kunci_grup(p)
        g = grup.setdefault(k, {
            "kunci": k, "kode": p.kode, "kolom": p.kolom, "aturan": p.aturan,
            "aman": p.aman_otomatis, "jumlah": 0, "contoh": [],
        })
        g["jumlah"] += 1
        if len(g["contoh"]) < 3:
            g["contoh"].append({"lama": str(p.nilai_lama), "baru": str(p.nilai_baru)})
    return list(grup.values())


def _filter_grup(perbaikan, aktif: set[str]):
    """Saring perbaikan: hanya grup yang dicentang user yang diterapkan.

    Mencentang grup aman_otomatis=False berarti konfirmasi eksplisit,
    jadi ditandai aman agar diterapkan (D-009: tetap lewat persetujuan user).
    """
    hasil = []
    for p in perbaikan:
        if _kunci_grup(p) in aktif:
            p.aman_otomatis = True
            hasil.append(p)
    return hasil


def _aktif_per_sheet(grup_aktif: str | None) -> list[set[str]]:
    """Parse grup_aktif (JSON ["0|KODE|kolom|aturan|1", ...]) per sheet."""
    aktif_per_sheet: list[set[str]] = []
    if grup_aktif is None:
        return aktif_per_sheet
    for entri in json.loads(grup_aktif):
        i, _, kunci = entri.partition("|")
        while len(aktif_per_sheet) <= int(i):
            aktif_per_sheet.append(set())
        aktif_per_sheet[int(i)].add(kunci)
    return aktif_per_sheet


def _proses_berkas(path: Path, aturan=None):
    """Kembalikan ringkasan per sheet: temuan, grup, dan detail perbaikan."""
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
            "grup": _grup_perbaikan(perbaikan),
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


def _nama_unik(folder: Path, nama: str) -> Path:
    """Kembalikan path unik di folder (tambah _1, _2, ... bila sudah ada)."""
    tujuan = folder / nama
    stem, suf = Path(nama).stem, Path(nama).suffix
    n = 1
    while tujuan.exists():
        tujuan = folder / f"{stem}_{n}{suf}"
        n += 1
    return tujuan


def buat_app() -> FastAPI:
    app = FastAPI(title="beberes", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index():
        return _TEMPLATE.read_text(encoding="utf-8")

    @app.get("/favicon.svg")
    def favicon_svg():
        return FileResponse(_ICONS / "favicon.svg", media_type="image/svg+xml")

    @app.get("/favicon-32.png")
    def favicon_png():
        return FileResponse(_ICONS / "favicon-32.png", media_type="image/png")

    @app.get("/contoh.xlsx")
    def contoh():
        return FileResponse(_DIR / "contoh.xlsx", media_type=_XLSX)

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
        grup_aktif: str | None = Form(None),
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
            aktif_per_sheet = _aktif_per_sheet(grup_aktif)

            gid = 0
            for idx, lembar in enumerate(lembar_list):
                _, perbaikan, _ = _proses_lembar(lembar, at)
                if pilihan is not None:
                    subset = [
                        p for i, p in enumerate(perbaikan)
                        if gid + i in pilihan
                    ]
                    abaikan = True
                elif grup_aktif is not None:
                    aktif = (
                        aktif_per_sheet[idx]
                        if idx < len(aktif_per_sheet)
                        else set()
                    )
                    subset = _filter_grup(perbaikan, aktif)
                    abaikan = False
                else:
                    subset = perbaikan
                    abaikan = False
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
            tujuan = _nama_unik(folder, nama_keluar)
            simpan(keluar_lembar, tujuan)

            audit = "\n".join(
                json.dumps(p, ensure_ascii=False) for p in semua_perubahan
            )
            nama_audit = tujuan.stem + ".audit.jsonl"
            tulis_audit(folder / nama_audit, semua_perubahan)
            return {
                "unduh": f"/unduh/{tujuan.name}",
                "audit_url": f"/unduh/{nama_audit}",
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

    @app.post("/api/urungkan")
    async def urungkan_endpoint(
        berkas: str = Form(...), audit: str = Form(...)
    ):
        """Kembalikan file hasil bersih ke nilai semula pakai audit log.

        `berkas` dan `audit` adalah nama file di folder unduhan sesi ini
        (dikembalikan /api/bersihkan), jadi tidak perlu upload ulang.
        """
        folder = _folder_unduhan()
        asal = folder / berkas
        log = folder / audit
        for f in (asal, log):
            if not f.exists() or f.parent != folder:
                raise HTTPException(404, "File tidak ditemukan")
        try:
            lembar_list = urungkan(asal, log)
        except ValueError as e:
            raise HTTPException(400, f"Audit log rusak: {e}") from e
        suf = ".csv" if asal.suffix.lower() == ".csv" else ".xlsx"
        tujuan = _nama_unik(folder, f"{asal.stem}_urung{suf}")
        simpan(lembar_list, tujuan)
        return {"unduh": f"/unduh/{tujuan.name}"}

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
