# 01. Visi dan Ruang Lingkup

## Visi

Siapa pun yang memegang file Excel/CSV berantakan, termasuk yang tidak bisa coding, bisa merapikannya
dengan aman, cepat, dan transparan: tahu persis apa yang diubah, dan bisa membatalkannya.

## Tujuan

1. Mendeteksi masalah kualitas data umum secara otomatis (format, duplikat, kosong, nilai janggal).
2. Memahami format khas Indonesia (Rupiah, tanggal dd/mm/yyyy, NIK, NPWP, HP, plat, gelar, wilayah).
3. Aman: default hanya memeriksa, tidak menimpa data asli, semua perubahan tercatat dan bisa di-undo.
4. Bisa dipakai tiga cara dari satu core yang sama: library Python, CLI, UI lokal.
5. Berjalan offline di laptop biasa (RAM 8-12GB, tanpa GPU).
6. Dua bahasa sejak awal: nama Indonesia (`beberes`), tagline dan README Inggris, CLI dan pesan laporan `id`/`en`.

## Target user

**Utama:** admin non-teknis di organisasi kecil (kantor desa/kelurahan, sekolah/TPQ, panitia kegiatan,
koperasi, RT/RW) dan UMKM.

**Sekunder:** mahasiswa/peneliti kecil (data survei), freelancer/analis junior, developer yang butuh
core library di pipeline mereka.

**Internasional:** peneliti, NGO, perusahaan, dan developer asing yang menangani data Indonesia dan butuh
validator NIK/NPWP, normalisasi wilayah, serta format Rupiah/tanggal Indonesia. Framing: *"the missing toolkit for Indonesian data"*.

**Fokus awal:** admin organisasi kecil. Keputusan fitur dinilai dari "apakah ini menolong mereka?".

## Non-goals (sengaja tidak dikerjakan)

- Bukan spreadsheet/Excel pengganti.
- Bukan layanan cloud/SaaS multi-user (auth, biaya, kepatuhan data pribadi = proyek lain).
- Bukan model ML sendiri untuk "memahami" data.
- Bukan pendukung semua format file dan semua jenis data.
- Bukan alat analisis/visualisasi data. Fokus hanya pada **kebersihan** data.

## Prinsip desain

1. **Aman dulu:** dry-run, file asli tidak disentuh, ada audit log + undo.
2. **Deterministik:** aturan inti harus menghasilkan hasil sama setiap kali. LLM (jika ada) hanya saran opsional.
3. **Lokal:** tidak ada data keluar dari komputer.
4. **Transparan:** setiap perubahan bisa dijelaskan (sel mana, nilai lama, nilai baru, aturan apa).
5. **Fungsional dulu, rapikan kemudian**, tapi core harus dipisah dari antarmuka sejak awal.

## Kriteria sukses (v1.0)

- Dipakai oleh minimal 5 orang nyata di luar pembuat.
- Minimal 1-3 testimoni terukur (mis. "rekap dari 2 jam jadi 5 menit").
- Terpublikasi di PyPI dengan README, contoh before/after, dan dokumentasi lengkap.
- Ada angka akurasi pada data uji sintetis (precision/recall per jenis masalah).
- Target sinyal komunitas: sekitar 30 bintang GitHub/unduhan (indikator, bukan syarat mutlak).

## Cerita untuk portfolio / CV

"Dari CLI sederhana menjadi engine kualitas data khas Indonesia: profiling otomatis, validator NIK/NPWP/wilayah,
rule engine YAML, deduplikasi fuzzy, audit log + undo, dan UI lokal. Diuji dengan data nyata yang disamarkan
dan data sintetis dengan metrik akurasi terukur."
