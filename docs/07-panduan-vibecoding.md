# 07. Panduan Vibecoding untuk beberes

Gaya kerja: cepat dan fungsional dulu, rapikan kemudian, tapi dengan **pagar pengaman** supaya
kecepatan AI tidak berubah jadi utang teknis atau kode yang tidak kamu pahami.

## Prinsip inti

1. **AI menulis, kamu yang memutuskan dan memahami.** Di wawancara, kamu akan ditanya "kenapa begini?".
   Bagian yang paling layak kamu kuasai penuh: audit log + undo, validator (NIK/wilayah), dan rule engine.
2. **Irisan tipis dulu (vertical slice).** Satu jalur ujung ke ujung yang jalan, baru melebar:
   `baca CSV -> 1 detector (spasi) -> 1 fixer -> laporan ringkas -> tulis file baru`.
3. **Ground truth dulu, fitur belakangan.** Bikin generator data sintetis (`scripts/buat_data_berantakan.py`)
   lebih dulu. Dengan pasangan `berantakan`/`bersih`, setiap fitur bisa dites otomatis, dan AI tidak bisa
   "merasa benar" tanpa bukti.
4. **Test sebagai kontrak.** Minta AI menulis test dulu (atau bersamaan), lalu kode. Kamu cukup baca testnya:
   kalau tes-nya benar, kodenya bisa diganti kapan saja.
5. **Satu perubahan per sesi, satu commit per perubahan.** Kalau AI mengubah 15 file sekaligus, tolak dan pecah.

## Alur kerja per fitur (loop)

```
1. Pilih 1 item dari ROADMAP (versi aktif)
2. Prompt: minta RENCANA singkat dulu (belum kode)
3. Setuju/koreksi rencana
4. Minta test + implementasi
5. Jalankan: pytest + ruff check src tests
6. Baca diff. Minta penjelasan bagian yang kamu tidak paham
7. Commit kecil. Centang ROADMAP. Catat keputusan baru di dokumen 06
```

## Alat

- **Claude Code** di terminal/VS Code: paling cocok untuk repo seperti ini karena bisa baca seluruh proyek,
  jalankan test, dan edit banyak file. `CLAUDE.md` di root repo otomatis jadi konteks tiap sesi.
- Chat biasa: untuk brainstorming desain, review keputusan, dan debugging yang butuh diskusi.
- Laptop kamu (i3, tanpa GPU) cukup: AI-nya jalan di cloud, yang lokal hanya `pytest` dan CLI.

## Template prompt (salin, ganti bagian dalam kurung)

**Mulai sesi**
```
Baca CLAUDE.md, ROADMAP.md, dan docs/03-spesifikasi-aturan-dan-laporan.md.
Hari ini aku mau mengerjakan: [item ROADMAP].
Jangan tulis kode dulu. Berikan rencana singkat: file apa yang dibuat/diubah, test apa yang ditulis,
dan apa yang sengaja TIDAK dikerjakan.
```

**Minta implementasi**
```
Rencana disetujui. Tulis test dulu di tests/ memakai fixture sintetis, lalu implementasinya.
Ikuti aturan di CLAUDE.md. Setelah selesai jalankan pytest dan ruff, dan laporkan hasilnya apa adanya.
```

**Detector/fixer baru**
```
Buat detector untuk kode [TGL001] sesuai docs/03. Input: kolom bertipe tanggal.
Output: daftar Temuan (kode, kolom, baris, contoh). Jangan ubah data.
Sertakan kasus tepi: sel kosong, tanggal ambigu (03/04/2025), tanggal mustahil (31/02).
```

**Review kritis (pakai sebelum commit)**
```
Review diff ini dengan kritis. Cari: pelanggaran aturan di CLAUDE.md, kasus tepi yang belum dites,
asumsi domain yang kamu karang, dan bagian yang bisa merusak data pengguna.
Jangan puji, langsung sebutkan masalahnya.
```

**Debug error**
```
Ini error-nya: [paste traceback]. Konteks: [perintah yang dijalankan].
Jelaskan penyebabnya dalam 2-3 kalimat, lalu beri perbaikan minimal. Jangan refactor di luar itu.
```

**Pahami kode (latihan wawancara)**
```
Jelaskan modul [nama] seolah aku harus menjelaskannya ke interviewer: apa tujuannya, alur datanya,
keputusan desain pentingnya, dan 3 pertanyaan sulit yang mungkin ditanyakan beserta jawabannya.
```

## Jebakan khas AI di proyek ini (cek manual)

| Jebakan | Kenapa berbahaya | Cara cek |
|---|---|---|
| **Aturan domain dikarang** (struktur NIK, kode wilayah, format plat, NPWP) | Validator terlihat benar tapi salah | Cocokkan dengan sumber resmi; minta AI menandai `TODO: verifikasi` bila ragu |
| **Paket/fungsi halusinasi** | Instal gagal atau paket asing berbahaya | Cek di pypi.org sebelum `pip install`; baca dokumentasi resmi |
| **Dependensi membengkak** | Package jadi berat dan rapuh | Tolak dependensi baru tanpa alasan kuat |
| **Mengubah data diam-diam** | Pelanggaran prinsip keamanan proyek | Tes: file asli tidak berubah; semua perubahan ada di audit log |
| **Tanggal ambigu diputuskan sendiri** (03/04 = 3 April atau 4 Maret?) | Data salah tanpa disadari | Tes khusus: harus jadi temuan TGL002, bukan auto-fix |
| **Tes yang menguji implementasi, bukan perilaku** | Tes lulus tapi bug tetap ada | Tes harus bersumber dari ground truth sintetis |
| **Scope creep** (AI menambah fitur "bonus") | Proyek tidak selesai | Pegang ROADMAP; tolak tambahan di luar versi aktif |
| **Refactor besar tak diminta** | Diff tidak terbaca, bug tersembunyi | Minta perubahan minimal |
| **Data asli bocor ke prompt/repo** | Masalah privasi | Hanya data sintetis di prompt; `data_asli/` di `.gitignore` |

## Kebiasaan yang membuat vibecoding bertahan lama

- **Pegang `CLAUDE.md`:** perbarui bagian "Status saat ini" tiap selesai satu fitur. Sesi baru jadi langsung nyambung.
- **Catat keputusan** di dokumen 06 saat AI dan kamu memilih sesuatu. Tanpa catatan, nanti lupa kenapa.
- **Commit sering** (setelah tes hijau). Kalau AI merusak sesuatu, tinggal kembali.
- **Sesi baru untuk tugas baru.** Konteks yang terlalu panjang bikin AI mulai lupa aturan.
- **Rilis kecil** ke PyPI tiap versi. Itu memaksa hal-hal membosankan (packaging, README, changelog) tuntas.
- **Jujur soal penggunaan AI** kalau ditanya. Yang dinilai: kamu memahami, memutuskan, dan bisa memperbaiki hasilnya.

## Urutan kerja yang disarankan (v0.1)

1. Registrasi nama (repo GitHub + PyPI `0.0.1`)
2. `scripts/buat_data_berantakan.py` (generator + ground truth)
3. Reader/Writer CSV dulu, xlsx menyusul
4. Detector + fixer satu per satu: spasi/kapital -> uang -> tanggal campur -> baris kosong
5. Profiler (tebak tipe kolom)
6. Laporan ringkas di terminal + `laporan.md`
7. Sambungkan ke CLI `periksa`/`bersihkan` (ganti stub)
8. README + GIF demo, rilis v0.1
