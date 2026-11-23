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
Pra-v0.1. Sudah ada: kerangka paket, CLI stub dengan alias dua bahasa, modul i18n, smoke test.
Belum ada: reader/writer, profiler, detector, fixer, validator, rule engine, laporan, audit log.
Langkah berikutnya yang disarankan: `scripts/buat_data_berantakan.py` (generator data sintetis + ground truth).
