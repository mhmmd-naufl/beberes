# 03. Spesifikasi Aturan, Kode Masalah, dan Laporan

> Draf awal. Berubah seiring v0.1-v0.3. Catat perubahan penting di CHANGELOG.

## 1. Format aturan YAML

```yaml
versi: 1
nama: "Daftar peserta lomba"

kolom:
  nama:
    tipe: nama
    aturan:
      - rapikan_spasi
      - kapital_judul
      - pisah_gelar: true

  tgl_lahir:
    tipe: tanggal
    format_masuk: ["dd/mm/yyyy", "d-m-yy", "d MMMM yyyy"]
    format_keluar: "yyyy-mm-dd"

  harga:
    tipe: uang
    aturan:
      - hapus: ["Rp", ".", " "]
      - ke_angka
      - tolak_jika: "< 0"

  hp:
    tipe: hp
    aturan:
      - normalisasi_hp: "+62"

  kecamatan:
    tipe: wilayah
    tingkat: kecamatan
    induk: kabupaten      # nama kolom induk untuk validasi bertingkat

global:
  hapus_baris_kosong: true
  tandai_duplikat:
    kolom: [nama, tgl_lahir]
    mode: fuzzy           # persis | fuzzy
    ambang: 0.9
```

Aturan harus: (1) jelas dibaca non-programmer, (2) divalidasi skemanya sebelum jalan,
(3) deterministik, (4) punya pesan error yang menunjuk baris YAML yang salah.

### Tipe kolom yang didukung (awal)

`teks`, `nama`, `angka`, `uang`, `tanggal`, `hp`, `nik`, `npwp`, `plat`, `wilayah`, `kategori`, `email`

### Aturan bawaan (awal)

`rapikan_spasi`, `huruf_kecil`, `huruf_besar`, `kapital_judul`, `hapus: [...]`, `ke_angka`,
`ke_tanggal`, `normalisasi_hp`, `pisah_gelar`, `ganti: {dari: ke}`, `tolak_jika: "<ekspresi>"`, `isi_kosong: <nilai>`

## 2. Kode masalah (daftar temuan)

Awalan menunjukkan kategori. Tingkat: `info`, `peringatan`, `error`.

| Kode | Masalah | Contoh | Perbaikan otomatis aman? |
|---|---|---|---|
| FMT001 | Spasi berlebih / di tepi sel | `"  Budi  Santoso "` | Ya |
| FMT002 | Huruf besar/kecil tidak konsisten | `"bUDI santoso"` | Ya |
| TGL001 | Format tanggal campur dalam satu kolom | `01/02/2025`, `2-Feb-25` | Ya jika tidak ambigu |
| TGL002 | Tanggal ambigu (dd/mm vs mm/dd) | `03/04/2025` | Tidak, minta konfirmasi |
| TGL003 | Tanggal mustahil | `31/02/2025` | Tidak |
| UANG001 | Uang tersimpan sebagai teks | `"Rp 25.000"` | Ya |
| UANG002 | Pemisah ribuan/desimal campur | `25.000,50` vs `25,000.50` | Hati-hati |
| NUM001 | Angka tersimpan sebagai teks | `"1 250"` | Ya |
| KSG001 | Sel kosong pada kolom wajib | | Tidak |
| KSG002 | Baris kosong seluruhnya | | Ya |
| DUP001 | Duplikat persis | | Ditandai, tidak dihapus otomatis |
| DUP002 | Duplikat mirip (fuzzy) | `M. Naufal` vs `Muhammad Naufal` | Tidak, minta konfirmasi |
| HP001 | Format nomor HP tidak konsisten | `0812-...`, `+62 812...` | Ya |
| HP002 | Nomor HP tidak valid | | Tidak |
| NIK001 | NIK bukan 16 digit | | Tidak |
| NIK002 | Kode wilayah NIK tidak dikenal | | Tidak |
| NIK003 | Tanggal lahir di NIK tidak valid | | Tidak |
| NPWP001 | Format NPWP tidak valid | | Tidak |
| WIL001 | Nama wilayah typo/variasi | `B.wangi` | Saran, minta konfirmasi |
| WIL002 | Wilayah tidak cocok dengan induknya | kecamatan bukan milik kabupaten | Tidak |
| NAMA001 | Gelar menempel di nama | `Drs. H. Budi, S.Kom.` | Ya (dipisah) |
| STR001 | Struktur: header bukan di baris 1 / sel digabung | | Deteksi + saran |

Prinsip: perbaikan yang **mengubah makna** (tanggal ambigu, hapus duplikat) tidak pernah otomatis.

## 3. Catatan validator Indonesia

- **NIK (16 digit):** 6 digit pertama kode wilayah (provinsi 2, kabupaten/kota 2, kecamatan 2),
  6 digit berikutnya tanggal lahir `DDMMYY` (untuk perempuan, hari ditambah 40), 4 digit terakhir nomor urut.
  Validator hanya memeriksa **struktur**, bukan keaslian di database Dukcapil.
- **NPWP:** 15 atau 16 digit (format baru mengikuti NIK). Periksa panjang dan pola, bukan keaslian.
- **HP:** normalisasi ke `+62...`. Awalan `0` -> `+62`, hilangkan spasi/strip.
- **Plat nomor:** pola huruf-angka-huruf, kode wilayah huruf depan.
- **Wilayah:** cocokkan dengan daftar resmi (sumber dan lisensi dicatat di `src/beberes/data/`).
- **Gelar:** daftar gelar akademik/keagamaan umum (Drs., Dr., H., Hj., S.Kom., M.T., dst.), dapat diperluas.

## 4. Format laporan

Ringkasan (cetak di terminal dan simpan sebagai `laporan.md`/`laporan.json`):

```
beberes laporan: data.xlsx (sheet "Peserta", 312 baris, 9 kolom)

Skor kualitas   : 61 -> 94
Temuan          : 48   (error 3, peringatan 17, info 28)
Diperbaiki      : 41   (otomatis 36, atas konfirmasi 5)
Butuh keputusan : 7

Per kolom:
  tgl_lahir   TGL001  4 format berbeda -> 1 format       (312 sel)
  harga       UANG001 "Rp ..." -> angka                  (289 sel)
  nama        FMT001  spasi dirapikan                    (57 sel)
  nama        DUP002  14 pasangan mirip, perlu cek       (butuh keputusan)
```

Versi JSON memuat struktur yang sama agar bisa dibaca program lain.

## 5. Format audit log

Satu baris per perubahan sel. Disimpan sebagai `.jsonl` berdampingan dengan file keluaran.

```json
{"id": 101, "sheet": "Peserta", "sel": "D17", "kolom": "tgl_lahir",
 "nilai_lama": "2-Feb-25", "nilai_baru": "2025-02-02",
 "kode": "TGL001", "aturan": "ke_tanggal", "waktu": "2026-11-23T10:15:00+07:00"}
```

**Undo:** `beberes urungkan data_bersih.xlsx --log data_bersih.audit.jsonl` mengembalikan nilai lama
berdasarkan log. Undo bisa parsial (per kode atau per sel).

## 6. Perintah CLI (dua bahasa)

| Indonesia | Inggris | Fungsi |
|---|---|---|
| `beberes periksa` | `beberes check` | Lihat masalah, tidak mengubah apa pun |
| `beberes bersihkan` | `beberes clean` | Terapkan perbaikan ke file baru |
| `beberes urungkan` | `beberes undo` | Kembalikan perubahan dari audit log |
| `beberes ui` | `beberes ui` | Buka antarmuka lokal (v0.5) |

| Flag Indonesia | Flag Inggris |
|---|---|
| `--keluar` | `--out` |
| `--laporan` | `--report` |
| `--aturan` | `--rules` |
| `--bahasa id\|en` | `--lang id\|en` |
| `--dry-run` | `--dry-run` |

Bahasa pesan default mengikuti bahasa sistem; `--bahasa`/`--lang` menimpanya.
Kunci YAML saat ini berbahasa Indonesia; alias kunci Inggris (`columns`, `rules`, dst.) dipertimbangkan di D-013.

## 7. Kode keluar CLI

| Kode | Arti |
|---|---|
| 0 | Sukses, tidak ada masalah / semua diperbaiki |
| 1 | Sukses, tetapi ada temuan yang butuh keputusan |
| 2 | Kesalahan pemakaian (argumen, aturan YAML tidak valid) |
| 3 | Kesalahan baca/tulis file |
