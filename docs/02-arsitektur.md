# 02. Arsitektur

## Gambaran besar

Satu **core** yang murni (tanpa UI, tanpa I/O interaktif). Semua antarmuka hanya "kulit" yang memanggil core.

```
   CLI        UI lokal (v0.5)      Integrasi (v1.0)        <- antarmuka
     \             |                  /
      \            |                 /
       +------- beberes.core -------+                      <- satu-satunya logika bisnis
                   |
   reader -> profiler -> detector -> fixer -> reporter/audit
                   ^
            validators (ID) + rule engine (YAML) + plugins
```

## Alur data

1. **Reader** membaca file ke representasi internal (tabel + metadata sel/sheet).
2. **Profiler** menebak tipe tiap kolom dan menghitung skor kualitas.
3. **Detector** menghasilkan daftar `Temuan` (masalah terstruktur, lihat dokumen 03).
4. **Fixer** menyiapkan `Perbaikan` untuk tiap temuan. Belum diterapkan.
5. Pengguna/aturan memilih perbaikan yang diterapkan (atau `--dry-run` berhenti di sini).
6. **Applier** menerapkan perbaikan ke salinan data dan mencatat `Perubahan` di audit log.
7. **Reporter** membuat ringkasan sebelum/sesudah. **Writer** menulis file baru.

## Modul

| Modul | Tanggung jawab |
|---|---|
| `io` | Baca/tulis xlsx, xls, csv. Tangani header bukan di baris 1, sel digabung, banyak sheet, encoding aneh |
| `profiling` | Deteksi tipe kolom, hitung % kosong/valid, nilai janggal |
| `detectors` | Satu detector per jenis masalah (tanggal campur, Rp sebagai teks, spasi, duplikat, dst.) |
| `fixers` | Satu fixer per jenis perbaikan, deterministik |
| `validators` | NIK, NPWP, HP, plat, wilayah, gelar. Masing-masing berdiri sendiri |
| `rules` | Loader + engine aturan YAML |
| `report` | Ringkasan, audit log, undo |
| `dedupe` | Duplikat persis + fuzzy (blocking + similarity), mulai v0.3 |
| `i18n` | Katalog pesan `id`/`en` untuk CLI, laporan, dan pesan error. Dipasang sejak v0.1 |
| `cli` | Perintah baris perintah (Typer), alias perintah dua bahasa |
| `ui` | FastAPI + React, jalan di localhost (v0.5) |
| `plugins` | Titik ekstensi untuk validator/fixer pihak ketiga (v1.0) |

## Model data inti (konseptual)

- **Temuan:** `kode`, `kolom`, `baris[]`, `tingkat` (info/peringatan/error), `pesan`, `contoh`
- **Perbaikan:** `kode_temuan`, `aturan`, `pratinjau (lama -> baru)`, `aman_otomatis (bool)`
- **Perubahan (audit):** `id`, `sheet`, `sel`, `nilai_lama`, `nilai_baru`, `aturan`, `waktu`
- **Laporan:** ringkasan jumlah temuan/perbaikan, skor kualitas sebelum/sesudah, daftar perubahan

## Struktur folder repo (target)

```
beberes/
  pyproject.toml
  README.md  README.id.md  ROADMAP.md  CHANGELOG.md  CONTRIBUTING.md  LICENSE
  .gitignore
  src/beberes/
    __init__.py
    io/            reader.py  writer.py
    profiling/     profiler.py  tipe.py
    detectors/     tanggal.py  uang.py  teks.py  duplikat.py  ...
    fixers/        tanggal.py  uang.py  teks.py  ...
    validators/    nik.py  npwp.py  hp.py  plat.py  wilayah.py  gelar.py
    rules/         loader.py  engine.py  skema.py
    report/        ringkasan.py  audit.py
    dedupe/        blocking.py  similarity.py
    i18n/          katalog_id.py  katalog_en.py  bahasa.py
    cli/           main.py
    ui/            (v0.5) api/  web/
    plugins/       (v1.0)
    data/          kode_wilayah.csv  (sumber + lisensi dicatat)
  tests/
    fixtures/      berantakan_*.xlsx  bersih_*.xlsx  (sintetis, aman dipublikasi)
    test_*.py
  scripts/
    buat_data_berantakan.py
  docs/
  data_asli/       <- DI-.gitignore, data nyata tidak pernah masuk repo
```

## Pilihan teknologi

| Kebutuhan | Pilihan | Catatan |
|---|---|---|
| Bahasa | Python 3.10+ | Stack utama |
| Tabel | pandas atau polars | Terbuka (D-005). Pertimbangkan RAM 12GB |
| Baca/tulis Excel | openpyxl (+ xlrd bila perlu .xls) | |
| CLI | Typer | Perintah punya alias Indonesia + Inggris |
| i18n | Katalog sederhana (dict/gettext) | Semua teks yang dilihat user lewat katalog, bukan hard-code |
| Aturan | YAML (PyYAML/ruamel) + validasi skema (pydantic) | |
| Fuzzy matching | rapidfuzz | |
| UI lokal | FastAPI + React (Vite) | Mulai v0.5 |
| Test | pytest | Fixture dari data sintetis |
| Packaging | pyproject.toml + PyPI | |

## Kinerja

- Target: file puluhan ribu baris nyaman di laptop 12GB RAM.
- Proses per chunk bila file besar. Hindari memuat semua sheet sekaligus.
- Dedupe fuzzy memakai blocking agar tidak O(n^2).
