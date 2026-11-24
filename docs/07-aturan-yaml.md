# 07 — Aturan YAML (`--aturan`)

> Untuk siapa: user non-programmer yang mau memberitahu `beberes` "kolom X di
> file saya isinya NIK" atau "kolom Y tanggal". Tidak perlu coding.

## 1. Cara pakai

```bash
beberes periksa data.xlsx --aturan peserta.yaml
beberes bersihkan data.xlsx --keluar hasil.xlsx --aturan peserta.yaml
```

Tanpa `--aturan`, `beberes` hanya memakai deteksi generik (format, spasi,
tanggal campur). Dengan `--aturan`, dia tahu **jenis isi** tiap kolom dan bisa
memeriksa hal yang mustahil secara domain (NIK 17 digit, HP aneh, wilayah typo).

## 2. Format file aturan

File `.yaml`/`.yml` dengan struktur:

```yaml
versi: 1          # versi skema, saat ini selalu 1
nama: peserta     # nama aturan, bebas (untuk laporan)
kolom:
  <nama kolom di file>:   # harus sama dengan header (tidak case-sensitive)
    tipe: <jenis>
```

Itu saja — sudah cukup untuk validator dasar.

## 3. Daftar tipe kolom

| Tipe | Yang diperiksa | Kode masalah |
|---|---|---|
| `teks` | spasi, kapital | FMT001, FMT002 |
| `nama` | gelar menempel (`Drs.`, `S.Kom.`) | NAMA001 |
| `angka` | angka tertulis sebagai teks | NUM001 |
| `uang` | `"Rp 25.000"` sebagai teks | UANG001 |
| `tanggal` | format campur, ambigu, mustahil | TGL001-003 |
| `hp` | format tidak konsisten / tidak valid | HP001, HP002 |
| `nik` | bukan 16 digit, kode wilayah, tgl lahir | NIK001-003 |
| `npwp` | pola 15/16 digit / format lama | NPWP001 |
| `plat` | pola huruf-angka-huruf | PLAT001 |
| `wilayah` | nama kota/provinsi tidak dikenal | WIL001 |
| `kategori` | nilai di luar daftar (wajib `aturan: [...]`) | KAT001 |
| `email` | pola email dasar | EMAIL001 |

Field tambahan opsional per kolom (untuk pengembangan lanjut):

```yaml
kolom:
  status:
    tipe: kategori
    aturan: [aktif, nonaktif]     # nilai yang diizinkan
    format_keluar: huruf_kecil    # normalisasi
```

## 4. Template bawaan

Tersedia di `src/beberes/rules/templates/`:

| File | Untuk data |
|---|---|
| `peserta.yaml` | peserta lomba/organisasi (NIK, HP, wilayah) |
| `kas.yaml` | kas/iuran (tanggal, uang) |
| `penjualan.yaml` | penjualan (tanggal, harga, qty) |

Contoh:

```bash
beberes bersihkan data_uji/berantakan_peserta.xlsx \
  --aturan src/beberes/rules/templates/peserta.yaml \
  --keluar hasil.xlsx
```

## 5. Contoh aturan lengkap

```yaml
versi: 1
nama: data-warga
kolom:
  nik:
    tipe: nik
  "No HP":
    tipe: hp
  nama:
    tipe: nama
  wilayah:
    tipe: wilayah
  tanggal_lahir:
    tipe: tanggal
  pekerjaan:
    tipe: teks
```

Aturan untuk kolom yang **tidak ada** di file diabaikan. Kolom yang tidak
disebut tetap diperiksa detektor generik.

## 6. Otomatis vs konfirmasi

| Kode | Perbaikan | Otomatis? |
|---|---|---|
| HP001 | `0812...` -> `+62812...` | Ya |
| NAMA001 | gelar dipisah dari nama (`Drs. Budi` → `Budi`) | Konfirmasi (`--konfirmasi`) |
| WIL001 | ganti typo -> nama benar | Tidak (saran tampil di laporan) |
| NIK/NPWP/PLAT | — | Tidak, hanya ditandai |
| TGL002 | tanggal ambigu dd/mm | Tidak |

Prinsip: **yang mengubah makna tidak pernah otomatis** (D-009).

## 7. Validasi aturan

File yang salah akan ditolak dengan pesan jelas:

```yaml
kolom:
  x:
    tipe: hantu        # <- error: tipe tidak dikenal, daftar pilihan ditampilkan
```

```
Tipe tidak dikenal untuk kolom 'x': hantu (pilihan: angka, email, hp, ...)
```

## 8. Membuat aturan sendiri (langkah)

1. Buka file Excel/CSV, lihat **nama kolom persisnya** (baris header).
2. Tulis YAML: satu entri per kolom, `tipe` sesuai isi kolom.
3. Jalankan `beberes periksa data.xlsx --aturan aturan.yaml` — lihat temuan.
4. Kalau nama kolom beda ejaan, sesuaikan kunci YAML-nya.

Contoh nyata ada di `data_uji/` + template di atas.
