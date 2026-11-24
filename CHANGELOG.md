# Changelog

Mengikuti [Keep a Changelog](https://keepachangelog.com/) dan [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-11-24

Validator Indonesia + aturan YAML.

### Ditambahkan
- `validators/`: NIK (struktur 16 digit + kode provinsi + tanggal lahir), HP (normalisasi `+62`), NPWP, plat, gelar di nama, wilayah (fuzzy-match)
- `rules/`: rule engine YAML + skema pydantic + loader + fixer rules (HP001 otomatis dinormalisasi)
- CLI: opsi `--aturan`/`--rules` untuk `periksa` dan `bersihkan`; flag `--version`/`-v`
- Template aturan bawaan: `peserta.yaml`, `kas.yaml`, `penjualan.yaml`
- Data wilayah subset awal (`src/beberes/data/wilayah.json`) + `SUMBER.md`
- Dokumentasi aturan: `docs/07-aturan-yaml.md`
- Kode masalah baru: NIK001-003, HP001-002, NPWP001, PLAT001, NAMA001, WIL001

### Diketahui
- Data wilayah masih subset (34 provinsi + kota); versi resmi menyusul
- Tipe `kategori` dan `email` di skema belum punya validator
- Perbaikan NAMA001/WIL001 hanya diberi saran, tidak otomatis

## [0.1.0] - 2026-11-23

Rilis pertama: core dasar + CLI fungsional.

### Ditambahkan
- `io`: reader/writer `.xlsx` + `.csv` — deteksi header bergeser, sel kosong, encoding CSV non-UTF8, delimiter `;`, multi-sheet
- `profiling`: deteksi tipe kolom (tanggal/uang/angka/teks), persen kosong, skor kualitas
- `detectors` batch 1: FMT001/002 (spasi, kapitalisasi), UANG001 (Rp sebagai teks), NUM001 (angka sebagai teks), TGL001/002/003 (tanggal campur/ambigu/mustahil), KSG001/002 (sel/baris kosong)
- `fixers` batch 1: perbaikan otomatis untuk temuan di atas; tanggal ambigu ditandai butuh konfirmasi (D-009)
- `report`: ringkasan terminal + `laporan.md`, audit log `.jsonl`, skor kualitas sebelum→sesudah
- CLI dua bahasa berfungsi: `periksa`/`check` (dry-run), `bersihkan`/`clean`, `--keluar`, `--laporan`; exit code sesuai docs/03
- `scripts/buat_data_berantakan.py`: generator data sintetis + ground truth + kunci kerusakan (seed tetap)
- Lisensi MIT (D-007)

### Diketahui
- File `.xls` lama belum didukung
- Sel digabung (merged cells) belum ditangani
- Mode konfirmasi interaktif untuk perbaikan non-otomatis belum ada (baru ditandai)

## [0.0.1] - 2026-11-23

Placeholder pendaftaran nama di PyPI.

## [Belum dirilis]

### Ditambahkan
- Dokumentasi perencanaan awal (visi, arsitektur, spesifikasi aturan, rencana data uji, validasi user, keputusan & risiko)
- Roadmap v0.1 sampai v1.0
- README dua bahasa (Inggris + Indonesia)

### Diubah
- Nama proyek dari `datarapi` (nama kerja) menjadi `beberes`
- CLI direncanakan dengan alias dua bahasa; modul `i18n` ditambahkan ke rencana arsitektur
