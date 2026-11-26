# Changelog

Mengikuti [Keep a Changelog](https://keepachangelog.com/) dan [Semantic Versioning](https://semver.org/).

## [0.5.1] - 2026-11-26

Polish onboarding untuk user awam.

### Ditambahkan
- `beberes ui` otomatis membuka browser setelah server siap
- UI: tautan "unduh contoh" (`/contoh.xlsx`, data sintetis 40 baris) untuk yang belum punya file
- `install.bat` di root repo: panduan Windows satu-klik (cek Python -> pasang -> jalankan UI)
- `python -m beberes` kini didukung (`__main__.py`), dipakai `install.bat` agar tidak bergantung PATH
- Ikon/favicon `beberes` (mark-c, tile teal) di UI, README, dan tab browser

## [0.5.0] - 2026-11-26

UI lokal di browser (`beberes ui`) — FastAPI + satu halaman HTML.

### Ditambahkan
- `beberes ui`: UI lokal FastAPI — upload -> periksa -> centang perbaikan per grup -> bersihkan -> unduh + audit
- UI: centang perbaikan per grup (kode+kolom+aturan+tingkat aman); grup ambigu perlu centang eksplisit (konfirmasi, D-009)
- UI: audit log `.audit.jsonl` bisa diunduh + ditampilkan sebagai tabel; nama file unduhan unik
- UI: tombol **Urungkan** (`POST /api/urungkan`) memulihkan nilai semula dari audit log tanpa upload ulang
- UI bilingual id/en (toggle ID/EN, tersimpan di localStorage); semua teks UI lewat kamus `I18N` + `t()`
- UI lolos audit anti-slop: 12 temuan diperbaiki (em dash, label form, viewport, landmark, escaping konsisten, tap target, dsb — `anti-slop/audit-001-2026-11-26.md`)
- `beberes versi` kini membaca versi dari metadata paket (sebelumnya `__version__` hard-code dan basi)
- Dependency baru: fastapi, uvicorn, python-multipart (untuk UI lokal)

### Diperbaiki
- `dedupe`: fuzzy matching dioptimasi (blocking huruf+bucket panjang, maks grup 200) — BANUA 15 sheet ~20rb baris kini ~1 menit untuk periksa (sebelumnya jauh lebih lama)

## [0.3.2] - 2026-11-24

Audit QA + validator tambahan.

### Ditambahkan
- `email` validator (EMAIL001) + `kategori` check via `aturan: [...]` (KAT001)
- WIL001 kini punya perbaikan konfirmasi (saran typo wilayah -> `--konfirmasi`)

### Diperbaiki
- `urungkan`: audit kini menyimpan `baris_output` — undo akurat walau baris kosong/hantu dibuang reader
- `urungkan`: fallback 1-sheet untuk CSV (nama sheet = nama file, bisa beda)
- `wilayah`: nama resmi dinormalisasi (`"Kabupaten Bogor"` cocok input `"Bogor"`)
- `dedupe`: fuzzy skip nilai non-alfabet (kolom tanggal tidak lagi false positive)

## [0.3.1] - 2026-11-24

Polish: data wilayah resmi + GIF demo + .xls.

### Ditambahkan
- Data wilayah resmi: 38 provinsi + 514 kab/kota + 7.265 kecamatan sesuai Kepmendagri 300.2.2-2138/2025 (sumber cahyadsn/wilayah, MIT)
- NIK002 kini cek kode prov+kab+kec ke data wilayah resmi
- WIL002: kecamatan vs kabupaten induk (via `induk:` di YAML)
- Reader dukung `.xls` lama via `xlrd`
- `docs/demo.gif` + `scripts/buat_gif_demo.py` (GIF demo reproducible)
- CI workflow: pytest + ruff tiap push/PR
- Fixer NAMA001: pisah gelar dari nama (konfirmasi)

### Diketahui
- Level desa/kelurahan (83rb) belum dibundel — diputuskan opsional/backlog
- Writer tetap hanya `.xlsx`/`.csv` (input `.xls` -> output `.xlsx`)

## [0.3.0] - 2026-11-24

Dedupe + audit undo + mode konfirmasi + benchmark.

### Ditambahkan
- `dedupe/`: DUP001 (duplikat persis) + DUP002 (duplikat mirip fuzzy via difflib + blocking) — hanya ditandai, tidak pernah dihapus otomatis
- `urungkan`/`undo`: kembalikan perubahan dari audit log `.jsonl` ke file baru
- Audit log kini menyimpan `kolom_idx` + `baris_excel` untuk undo presisi
- CLI: `--konfirmasi`/`--confirm` — tanya y/n per kelompok perbaikan ambigu sebelum diterapkan
- `scripts/benchmark.py` + `docs/benchmark.md`: recall deteksi per jenis kerusakan + akurasi perbaikan vs ground truth
- `io`: buang baris hantu (sisa nomor urut formula) + kolom tanpa header yang isinya <10% — ditemukan dari data asli
- Kode masalah baru: DUP001, DUP002, KSG003

### Diketahui
- Fuzzy dedupe pakai difflib (stdlib); rapidfuzz dipertimbangkan untuk file besar
- Akurasi benchmark 72–81% — sisanya perbaikan ambigu yang sengaja ditahan (D-009)
- D-005 (pandas vs polars) masih terbuka — core belum membutuhkannya

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
