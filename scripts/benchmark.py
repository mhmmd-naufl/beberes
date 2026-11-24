"""Benchmark akurasi beberes pada data sintetis (docs/04 bagian metrik).

Untuk tiap dataset di data_uji/:
  1. Jalankan pipeline deteksi pada berkas berantakan.
  2. Recall deteksi per jenis kerusakan (bandingkan dengan kunci_kerusakan).
  3. Akurasi perbaikan: jalankan bersihkan, bandingkan hasil vs berkas bersih.

Jalankan: python scripts/benchmark.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from beberes.detectors import jalankan as deteksi_semua
from beberes.fixers import usulkan_semua
from beberes.io import baca_berkas
from beberes.profiling import hitung_skor, profil_lbr
from beberes.report import terapkan

DASAR = Path(__file__).resolve().parent.parent / "data_uji"

# jenis kerusakan -> kode temuan yang diharapkan mendeteksinya
PETA_KODE = {
    "format_tanggal_campur": {"TGL001"},
    "uang_jadi_teks": {"UANG001"},
    "spasi_dan_kapital": {"FMT001", "FMT002"},
    "typo_wilayah": {"WIL001"},
    "duplikat_variasi": {"DUP001", "DUP002"},
    "sel_kosong": {"KSG001"},
    "gelar_menempel": {"NAMA001"},
    "header_bergeser": set(),   # ditangani reader, bukan detector
}


def _nilai_cocok(temuan, nilai_kotor) -> bool:
    target = str(nilai_kotor).strip().lower()
    for s in temuan.sel:
        if str(s.get("nilai", "")).strip().lower() == target:
            return True
    return any(target in str(c).lower() for c in temuan.contoh)


def recall_deteksi(berkas_berantakan: Path, kunci: dict) -> dict:
    """Per jenis kerusakan: berapa % yang tertangkap temuan yang tepat."""
    temuan = []
    for lembar in baca_berkas(berkas_berantakan):
        profil = profil_lbr(lembar)
        temuan.extend(deteksi_semua(lembar, profil))

    per_jenis = {}
    for k in kunci["kerusakan"]:
        jenis = k["jenis"]
        if jenis == "header_bergeser":
            continue  # bukan detector
        kode_diharapkan = PETA_KODE.get(jenis, set())
        ketemu = any(
            t.kode in kode_diharapkan and _nilai_cocok(t, k["nilai_kotor"])
            for t in temuan
        )
        stat = per_jenis.setdefault(jenis, {"total": 0, "ketemu": 0})
        stat["total"] += 1
        stat["ketemu"] += int(ketemu)
    return per_jenis


def akurasi_perbaikan(berkas_berantakan: Path, berkas_bersih: Path) -> float:
    """% sel hasil bersih yang identik dengan ground truth."""
    lembar_kotor = baca_berkas(berkas_berantakan)
    perbaikan_semua = []
    for lembar in lembar_kotor:
        profil = profil_lbr(lembar)
        temuan = deteksi_semua(lembar, profil)
        perbaikan_semua.append(usulkan_semua(temuan, lembar))

    hasil = []
    for lembar, perbaikan in zip(lembar_kotor, perbaikan_semua, strict=False):
        baru, _ = terapkan(lembar, perbaikan)
        hasil.append(baru)

    kebenaran = baca_berkas(berkas_bersih)
    total = sama = 0
    for l_hasil, l_asli in zip(hasil, kebenaran, strict=False):
        for b_hasil, b_asli in zip(l_hasil.baris, l_asli.baris, strict=False):
            for v_hasil, v_asli in zip(b_hasil, b_asli, strict=False):
                if v_asli is None:
                    continue
                total += 1
                if str(v_hasil).strip() == str(v_asli).strip():
                    sama += 1
    return (sama / total * 100) if total else 0.0


def main() -> None:
    baris_md = [
        "# Benchmark akurasi",
        "",
        "Data sintetis dari `scripts/buat_data_berantakan.py` (seed tetap).",
        "Recall deteksi = kerusakan yang disuntik & ditemukan detector yang tepat.",
        "Akurasi perbaikan = % sel hasil `bersihkan` yang identik dengan ground truth.",
        "",
        "| Dataset | Recall deteksi per jenis | Akurasi perbaikan |",
        "|---|---|---|",
    ]
    for berkas in sorted(DASAR.glob("berantakan_*.xlsx")):
        nama = berkas.stem.replace("berantakan_", "")
        kunci = json.loads(
            (DASAR / f"kunci_kerusakan_{nama}.json").read_text(encoding="utf-8")
        )
        bersih = DASAR / f"bersih_{nama}.xlsx"

        per_jenis = recall_deteksi(berkas, kunci)
        bagian = []
        for jenis, stat in sorted(per_jenis.items()):
            pct = stat["ketemu"] / stat["total"] * 100 if stat["total"] else 0
            bagian.append(f"{jenis}: {stat['ketemu']}/{stat['total']} ({pct:.0f}%)")
        recall = " | ".join(bagian) if bagian else "-"

        acc = akurasi_perbaikan(berkas, bersih)
        baris_md.append(f"| {nama} | {recall} | {acc:.1f}% |")
        print(f"{nama}: acc={acc:.1f}%")

    (Path(__file__).resolve().parent.parent / "docs" / "benchmark.md").write_text(
        "\n".join(baris_md) + "\n", encoding="utf-8"
    )
    print("-> docs/benchmark.md")


if __name__ == "__main__":
    main()
