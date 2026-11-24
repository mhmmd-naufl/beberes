"""Buat docs/demo.gif: render output terminal beberes menjadi GIF.

Menjalankan perintah demo asli dan menggambar ulang outputnya
sebagai frame terminal (monospace, tema gelap) -> GIF animasi.
Jalankan: python scripts/buat_gif_demo.py
"""

import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DASAR = Path(__file__).resolve().parent.parent
LEBAR, TINGGI = 1100, 640
FONT = ImageFont.truetype("consola.ttf", 17)
FONT_CMD = ImageFont.truetype("consola.ttf", 18)

BG = (24, 26, 30)
FG = (220, 224, 230)
HIJAU = (110, 220, 130)
KUNING = (240, 200, 90)

def _ukur(teks: str) -> tuple[int, int]:
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    b = d.textbbox((0, 0), teks, font=FONT)
    return b[2] - b[0], b[3] - b[1]

CHAR_W = _ukur("M")[0]
BARIS_H = _ukur("Ay")[1] + 6
PAD = 18
MAKS_KAR = (LEBAR - 2 * PAD) // CHAR_W


def _potong(teks: str) -> list[str]:
    baris = []
    for ln in teks.splitlines():
        while len(ln) > MAKS_KAR:
            baris.append(ln[:MAKS_KAR])
            ln = ln[MAKS_KAR:]
        baris.append(ln)
    return baris


def _frame(teks: list[str], judul: str = "") -> Image.Image:
    img = Image.new("RGB", (LEBAR, TINGGI), BG)
    d = ImageDraw.Draw(img)
    y = PAD
    if judul:
        d.text((PAD, y), judul, font=FONT_CMD, fill=KUNING)
        y += BARIS_H + 8
    for ln in teks[: (TINGGI - y) // BARIS_H]:
        warna = HIJAU if ln.startswith("$") else (
            KUNING if ln.startswith("#") else FG
        )
        isi = ln[2:] if ln[:1] in ("$", "#") else ln
        d.text((PAD, y), isi, font=FONT, fill=warna)
        y += BARIS_H
    return img


def _jalankan(cmd: list[str]) -> str:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(
        cmd, cwd=DASAR, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env, timeout=120,
    )
    return r.stdout + r.stderr


def main() -> None:
    perintah = [
        (["beberes", "versi", "--lang", "id"], "beberes versi --lang id"),
        (
            ["beberes", "periksa", "data_uji/berantakan_peserta.xlsx",
             "--aturan", "src/beberes/rules/templates/peserta.yaml",
             "--lang", "id"],
            "beberes periksa data_uji/berantakan_peserta.xlsx --aturan peserta.yaml",
        ),
        (
            ["beberes", "bersihkan", "data_uji/berantakan_peserta.xlsx",
             "--aturan", "src/beberes/rules/templates/peserta.yaml",
             "--keluar", "data_uji/hasil_demo.xlsx",
             "--laporan", "--lang", "id"],
            "beberes bersihkan ... --keluar hasil_demo.xlsx --laporan",
        ),
        (
            ["beberes", "urungkan", "data_uji/hasil_demo.xlsx",
             "--log", "data_uji/hasil_demo.audit.jsonl",
             "--keluar", "data_uji/dibalik.xlsx", "--lang", "id"],
            "beberes urungkan hasil_demo.xlsx --log hasil_demo.audit.jsonl",
        ),
    ]

    frames: list[tuple[Image.Image, int]] = []  # (frame, durasi ms)

    # frame judul
    frames.append((_frame(
        ["# beberes", "", "# Tidy up messy Indonesian spreadsheets.",
         "# demo: periksa -> bersihkan -> urungkan"], "beberes demo",
    ), 2000))
    for cmd, label in perintah:
        frames.append((_frame([f"$ {label}"], ""), 1200))
        keluaran = _jalankan(cmd)
        akumulasi: list[str] = []
        for ln in _potong(keluaran):
            akumulasi.append(ln)
            frames.append((_frame(akumulasi[-18:]), 380))
        # jeda baca di akhir tiap perintah: ulang frame terakhir 2x
        frames.append((frames[-1][0], 1400))
        frames.append((frames[-1][0], 700))

    durasi = [d for _, d in frames]
    imgs = [f for f, _ in frames]

    out = DASAR / "docs" / "demo.gif"
    imgs[0].save(
        out, save_all=True, append_images=imgs[1:],
        duration=durasi, loop=0, optimize=True,
    )
    print(f"GIF tersimpan: {out} ({len(frames)} frame, {out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
