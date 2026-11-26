# CLAUDE.md: konteks proyek untuk asisten AI

> Baca file ini di awal setiap sesi. Salin juga sebagai `AGENTS.md` (Codex/Cursor/dll.) bila perlu.

## Apa ini
`beberes`: tools Python (library + CLI, UI lokal nanti) untuk merapikan file Excel/CSV berantakan
dengan kebiasaan data Indonesia (Rupiah, tanggal dd/mm/yyyy, NIK, NPWP, HP, wilayah, gelar).
Tagline: "Tidy up messy Indonesian spreadsheets."

## Dokumen acuan (baca sebelum mengubah desain)
- `docs/01-visi-dan-ruang-lingkup.md`: tujuan, non-goals
- `docs/02-arsitektur.md`: modul, alur data, struktur folder
- `docs/03-spesifikasi-aturan-dan-laporan.md`: format YAML, kode masalah, laporan, audit log
- `docs/06-keputusan-dan-risiko.md`: keputusan yang sudah final (D-xxx). Jangan dilanggar tanpa bilang
- `ROADMAP.md`: versi aktif dan checklist

## Aturan tidak boleh dilanggar
1. **Aman dulu:** default hanya memeriksa; file asli tidak pernah ditimpa; setiap perubahan masuk audit log dan bisa di-undo.
2. **Perbaikan yang mengubah makna** (tanggal ambigu, hapus duplikat, gabung nama mirip) tidak pernah otomatis.
3. **Core murni:** `src/beberes/` selain `cli/` dan `ui/` tidak boleh import CLI/UI dan tidak boleh `print`/`input`.
4. **Deterministik & lokal:** tidak ada panggilan jaringan, tidak ada LLM di jalur inti.
5. **Semua teks untuk user lewat `i18n.t()`** (id + en). Jangan hard-code string.
6. **Jangan pernah** masukkan data asli (NIK, nama, HP, alamat) ke kode, test, fixture, atau contoh. Pakai data sintetis.
7. **Jangan menebak aturan domain.** Struktur NIK/NPWP, kode wilayah, format plat: kalau tidak yakin, tulis `TODO: verifikasi sumber` dan tanya. Jangan mengarang.
8. **Jangan menambah dependensi** tanpa bilang alasannya. Pastikan paketnya benar-benar ada di PyPI.
9. **Jangan memperluas scope** di luar versi aktif di ROADMAP.md.

## Cara kerja yang diharapkan
- Kerjakan **satu hal kecil per sesi/perubahan**. Jelaskan rencana singkat sebelum menulis kode.
- **Test dulu atau bersamaan:** tiap detector/fixer/validator punya test dengan fixture sintetis.
- Setelah selesai, jalankan `pytest` dan `ruff check src tests`, lalu laporkan hasilnya jujur (termasuk yang gagal).
- Jelaskan kode yang ditulis dengan bahasa sederhana: pemilik proyek harus bisa menjelaskannya sendiri di wawancara.
- Kalau ada keputusan desain baru, usulkan entri untuk `docs/06-keputusan-dan-risiko.md`.

## Perintah
```bash
pip install -e ".[dev]"      # pasang mode dev
pytest                       # tes
ruff check src tests         # lint
beberes --help               # coba CLI
```

## Konvensi
- Python 3.10+, type hints untuk fungsi publik, nama modul/fungsi Indonesia untuk domain (`tanggal`, `uang`, `periksa`), Inggris untuk istilah teknis umum.
- Pesan error: jelas, beri saran perbaikan, dua bahasa.
- Commit kecil dengan pesan jelas (mis. `feat(detectors): deteksi format tanggal campur (TGL001)`).

## Status saat ini
Rilis terakhir: **v0.5.0** (PyPI, tag `v0.5.0`). `beberes versi` membaca versi dari metadata paket. CI hijau.

v0.5 UI (selesai, dirilis v0.5.0):
- `beberes ui` -> FastAPI + satu halaman `src/beberes/ui/index.html` (vanilla JS, i18n id/en, anti-slop cleaned)
- Endpoint: GET /, POST /api/periksa, POST /api/bersihkan, POST /api/urungkan, GET /unduh/{file}
- Deps baru: fastapi, uvicorn, python-multipart; dev: httpx2 (wajib untuk TestClient)
- Selesai: upload->periksa->bersihkan->unduh+audit; centang perbaikan per grup di UI (`grup_aktif`, ambigu = konfirmasi eksplisit) + API pilihan per sel (`terpilih` indeks / `detail` perbaikan, deterministik); `terapkan()` punya `abaikan_aman_otomatis` untuk konfirmasi eksplisit; field `diff` sebelum→sesudah di respons bersihkan; audit `.audit.jsonl` bisa diunduh + tabel; tombol **Urungkan** (`POST /api/urungkan`, pakai nama file sesi); UI bilingual id/en; semua string UI lewat `t()`; lolos audit anti-slop 12 temuan (`anti-slop/audit-001-2026-11-26.md`); test_ui.py generate fixture sendiri (data_uji TIDAK ikut repo — gitignored!)
- Belum: tes user nyata (docs/05); diff per sel di UI hanya via tabel audit (maks 200 baris tampil)
- Catatan perf: dedupe fuzzy sudah dioptimasi (blokir huruf+bucket panjang, maks grup 200) — BANUA 15 sheet ~20rb baris butuh ~1 menit untuk periksa; `/api/periksa` mengembalikan `detail` per sel (bisa besar di file raksasa — pantau bila lambat)
- Server dev: `beberes ui --port 8000`

Sudah ada (semua di `src/beberes/`):
- `io/` reader .xlsx/.xlsm/.xls/.csv (baris+kolom hantu dibuang), writer .xlsx/.csv
- `profiling/` inferensi tipe + skor kualitas
- `detectors/` FMT/UANG/NUM/TGL/KSG + `dedupe/` DUP001/002 (fuzzy difflib, tidak auto-hapus)
- `fixers/` perbaikan aman otomatis; ambigu -> `aman_otomatis=False`
- `validators/` NIK, HP, NPWP, plat, gelar, wilayah (data resmi Kepmendagri 2025, MIT), email
- `rules/` engine YAML + template (peserta/kas/penjualan/servis); tipe: teks/nama/angka/uang/tanggal/hp/nik/npwp/plat/wilayah/kategori/email; field `induk:` untuk WIL002
- `report/` ringkasan, laporan md, audit .jsonl (ada `baris_output` untuk undo akurat)
- `cli/` periksa/check, bersihkan/clean, urungkan/undo, versi/version, `--konfirmasi`, `--aturan`, `--keluar`, `--laporan`, `--bahasa`
- `scripts/` buat_data_berantakan.py (generator+ground truth), benchmark.py, buat_gif_demo.py
- CI: pytest+ruff tiap push; release.yml auto-publish PyPI via trusted publishing (tag v*)

Keputusan yang ditunda:
- D-005 pandas vs polars — core masih pure Python, belum butuh
- Level desa/kelurahan wilayah (83rb) — backlog, file terlalu besar untuk bundle
- Partial undo by kode/sel — spek "nanti"
- TGL002 agak noisy untuk tanggal dd/mm/yyyy kanonik (diketahui, bukan bug)

Data asli di `data_asli/` (gitignored): Komang SAC (servis), BANUA 2025 (multi-sheet+formula), Data_Nasabah (kontrol bersih). Jangan commit/share — BANUA punya string mirip API token, sarankan user regenerate.

Next kandidat: v0.5 UI lokal (FastAPI+React), atau polish kecil (partial undo, TGL002 noise).
