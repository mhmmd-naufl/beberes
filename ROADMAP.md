# Roadmap

Berbasis versi dan checklist, **tanpa tanggal**. Rilis ke PyPI setiap versi selesai.
Centang kotak saat selesai. Kalau ada yang diubah, catat di CHANGELOG.

## Kriteria selesai proyek (v1.0)

- [ ] Dipakai 5+ orang nyata di luar pembuat
- [ ] 1-3 testimoni terukur
- [ ] Ada di PyPI, README + contoh + dokumentasi lengkap
- [ ] Angka akurasi tercatat di `docs/benchmark.md`

## Persiapan (sebelum v0.1)

- [x] Daftarkan nama `beberes`: rilis `0.0.1` placeholder di PyPI + buat repo GitHub (D-010)
- [ ] Set deskripsi PyPI dan topik GitHub berbahasa Inggris (`data-cleaning`, `excel`, `csv`, `indonesia`, `nik-validator`)
- [ ] Riset library serupa; tulis ringkasan perbandingan
- [x] Putuskan lisensi (D-007) — MIT
- [ ] Kumpulkan 3-5 file berantakan nyata (disamarkan) + folder `data_asli/` di `.gitignore` (folder siap, menunggu data)
- [ ] Siapkan repo, `pyproject.toml`, struktur folder, CI uji dasar (repo + struktur selesai; CI belum)
- [x] Tulis `scripts/buat_data_berantakan.py` versi awal

## v0.1: Core dasar + CLI

Cerita demo: "file peserta lomba berantakan jadi bersih dalam hitungan detik".

- [x] Reader/Writer xlsx + csv (header bergeser, banyak sheet; sel digabung belum)
- [x] Profiler: tebak tipe kolom + skor kualitas
- [x] Detector + fixer: spasi/kapital, tanggal campur, Rp sebagai teks, angka sebagai teks, baris kosong
- [x] Laporan ringkas di terminal + `laporan.md` (`--laporan`)
- [x] CLI dua bahasa: `periksa`/`check`, `bersihkan`/`clean`, `--keluar`/`--out` (dry-run = default `periksa`)
- [x] Modul `i18n`: katalog pesan `id`/`en` + flag `--bahasa`/`--lang` (D-012)
- [x] README Inggris (`README.md`) + Indonesia (`README.id.md`) (D-011)
- [x] Test dengan fixture sintetis (data_uji + tests/fixtures)
- [ ] GIF demo, rilis ke PyPI (v0.1.0)

## v0.2: Validator Indonesia + aturan YAML

Cerita demo: "data warga dengan NIK, HP, dan wilayah yang dicek otomatis".

- [x] Validator: NIK (struktur), HP (normalisasi +62), NPWP, plat, gelar di nama
- [ ] Data wilayah resmi (cek lisensi) + normalisasi nama wilayah (typo) — subset awal ada di `src/beberes/data/wilayah.json`, menunggu data resmi
- [x] Rule engine YAML + validasi skema + pesan error yang jelas
- [x] Aturan bawaan (template) untuk jenis data umum: peserta, kas, penjualan
- [x] Dokumentasi aturan lengkap (`docs/07-aturan-yaml.md`)

## v0.3: Dedupe + audit log + undo

Cerita demo: "14 pasangan nama mirip ditemukan, dicek, dan digabung dengan aman".

- [x] Duplikat persis + fuzzy (difflib + blocking; rapidfuzz ditunda)
- [x] Mode konfirmasi untuk perbaikan yang mengubah makna (`--konfirmasi`)
- [x] Audit log `.jsonl` + perintah `urungkan`/`undo`
- [x] Benchmark akurasi (precision/recall) pada data sintetis (`docs/benchmark.md`)
- [ ] Putuskan pandas vs polars berdasarkan hasil ukur (D-005) — ditunda, core belum butuh

## v0.5: UI lokal

Cerita demo: "admin non-teknis rapikan data lewat browser, tanpa terminal".

- [x] `beberes ui`: FastAPI + React di localhost (React via CDN, Vite menyusul)
- [x] Upload, tampilan temuan per sheet, skor kualitas
- [x] Unduh hasil + audit log (semua fix aman otomatis diterapkan)
- [x] Centang perbaikan individual / mode konfirmasi di UI
- [x] Before/after diff (tabel perubahan sebelum→sesudah setelah bersihkan)
- [ ] Tes dengan 2-3 user nyata, catat di dokumen 05

## v1.0: Ekosistem

- [ ] Sistem plugin (validator/fixer tambahan)
- [ ] Integrasi n8n dan/atau Google Sheets (Apps Script)
- [ ] Dokumentasi detail lengkap dalam bahasa Inggris (menyusul versi Indonesia), contoh kasus penggunaan
- [ ] Putuskan alias kunci YAML Inggris (D-013)
- [ ] Artikel "kenapa aku bikin ini" + distribusi (dokumen 05)
- [ ] Rilis stabil, tag versi, changelog rapi

## Di luar rencana (sengaja ditunda/ditolak)

Lihat non-goals di `docs/01-visi-dan-ruang-lingkup.md`: SaaS multi-user, model ML sendiri,
dukungan semua format, alat analisis/visualisasi.

## Ide di backlog (belum dijadwalkan)

- Saran berbasis LLM untuk kolom ambigu (opsional, offline-first)
- Dukungan format tambahan (ODS, JSON)
- Mode pantau folder (bersihkan otomatis tiap file masuk)
- Template aturan komunitas
