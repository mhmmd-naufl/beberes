# 06. Keputusan dan Risiko

## Log keputusan

Format: ID, keputusan, alasan, status (`Diputuskan` / `Terbuka`).

| ID | Keputusan | Alasan | Status |
|---|---|---|---|
| D-001 | Core dipisah dari antarmuka; CLI dan UI hanya memanggil core | Satu logika, banyak antarmuka; mudah dites | Diputuskan |
| D-002 | Semua proses lokal, tidak ada data keluar | Data sensitif (NIK, nama); tidak perlu hosting | Diputuskan |
| D-003 | Aturan inti deterministik; LLM hanya saran opsional dan offline-first | Hasil bisa diprediksi dan diaudit | Diputuskan |
| D-004 | Default hanya memeriksa (dry-run); menulis butuh perintah/flag eksplisit; file asli tidak pernah ditimpa | Keamanan data pengguna | Diputuskan |
| D-005 | pandas vs polars sebagai mesin tabel | Polars lebih hemat RAM/cepat; pandas lebih dikenal. Putuskan setelah uji di file 50k baris | Terbuka |
| D-006 | CLI punya alias dua bahasa: `periksa`/`check`, `bersihkan`/`clean`, `urungkan`/`undo`; flag juga ganda | Ramah user lokal sekaligus bisa dipakai orang luar | Diputuskan |
| D-007 | Lisensi: MIT | Ringan, adopsi luas, cocok untuk library + tool | Diputuskan |
| D-008 | UI dikerjakan setelah v0.3 (core terbukti berguna) | Cegah habis waktu di tampilan sebelum engine matang | Diputuskan |
| D-009 | Perbaikan yang mengubah makna (tanggal ambigu, hapus duplikat) tidak pernah otomatis | Cegah kerusakan data diam-diam | Diputuskan |
| D-010 | Nama proyek: `beberes` ("tidying up"), tagline Inggris *"Tidy up messy Indonesian spreadsheets."* | Unik, mudah diingat, nuansa ramah; PyPI kosong saat dicek. Daftarkan secepatnya | Diputuskan |
| D-011 | README dua bahasa (Inggris `README.md`, Indonesia `README.id.md`) sejak v0.1; dokumen detail Indonesia dulu, Inggris menyusul | Terbaca orang luar di GitHub tanpa menunda dokumentasi detail | Diputuskan |
| D-012 | Modul `i18n` (katalog pesan id/en) dipasang sejak v0.1; pesan user tidak boleh hard-code | Jauh lebih murah daripada refactor belakangan | Diputuskan |
| D-013 | Kunci YAML aturan: Indonesia saja, atau tambah alias Inggris (`columns`, `rules`, ...) | Alias memudahkan user asing, tapi menambah beban skema | Terbuka |

Tambahkan entri baru di bawah dengan format yang sama. Jangan hapus keputusan lama, ubah statusnya.

## Daftar risiko

| Risiko | Dampak | Kemungkinan | Mitigasi |
|---|---|---|---|
| Scope creep ("Excel-nya Indonesia") | Proyek tidak selesai | Tinggi | Pegang non-goals; kerjakan per versi; UI belakangan |
| Alat sudah ada / tumpang tindih | Nilai unik berkurang | Sedang | Riset PyPI/GitHub di awal; fokus ke celah khas Indonesia + audit/undo |
| Nama diambil orang sebelum didaftarkan | Harus ganti nama | Rendah-sedang | Daftarkan `beberes` di PyPI (rilis `0.0.1` placeholder) dan GitHub secepatnya |
| Nama Indonesia susah ditemukan orang luar | Adopsi internasional rendah | Sedang | Tagline Inggris, kata kunci `data-cleaning`/`excel`/`csv`/`indonesia` di PyPI & topik GitHub |
| Tidak ada user nyata | Tidak ada bukti dampak | Sedang | Cari 3-5 user sejak awal (dokumen 05) |
| Salah ubah data pengguna | Kehilangan kepercayaan | Sedang | Dry-run default, audit log, undo, aturan yang mengubah makna tidak otomatis |
| Kebocoran data pribadi di repo | Masalah privasi/hukum | Rendah-sedang | `.gitignore`, hanya data sintetis di repo, cek sebelum push |
| Performa buruk di file besar / laptop terbatas | Frustrasi, tidak terpakai | Sedang | Chunking, polars, benchmark jujur, batasi ekspektasi |
| Lisensi data wilayah tidak jelas | Tidak bisa dibundel | Sedang | Cek lisensi; bila perlu unduh saat install atau buat sendiri dari sumber resmi |
| Fuzzy dedupe banyak alarm palsu | Pengguna tidak percaya | Sedang | Ambang konfigurasi, selalu minta konfirmasi, ukur precision/recall |
| Motivasi turun di tengah | Setengah jadi | Sedang | Rilis kecil dan sering; kriteria selesai yang jelas |
| Banyak proyek paralel | Tidak ada yang tuntas | Sedang | Satu proyek dirilis rapi dulu |

## Pertanyaan terbuka

- [ ] Apakah ada library serupa di PyPI yang perlu dibandingkan secara resmi? (nama `beberes` sendiri sudah dicek kosong)
- [ ] Format laporan mana yang paling dibutuhkan user (terminal, Markdown, HTML, JSON)?
- [ ] Apakah UI cukup sebagai viewer laporan + konfirmasi, atau editor penuh?
- [ ] Bagaimana menangani file `.xls` lama dan makro?
