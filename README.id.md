# beberes

> *Tidy up messy Indonesian spreadsheets.*
> Engine kualitas data untuk file Excel/CSV yang berantakan, dibuat untuk kebiasaan data Indonesia.

🇬🇧 [English version](README.md)

**Status:** perencanaan (pra-v0.1)

## Masalahnya

Data dari kantor desa, sekolah, panitia kegiatan, dan UMKM hampir selalu berantakan:
tanggal campur format, "Rp 25.000" tersimpan sebagai teks, nama dobel dengan ejaan beda,
nama daerah typo, kolom kosong di mana-mana. Dirapikan manual itu lama dan rawan salah.
Tools data cleaning yang ada umumnya ditujukan ke data scientist, bukan admin non-teknis,
dan tidak paham format Indonesia (NIK, NPWP, plat, Rupiah, gelar, wilayah).

## Cara kerja (alur)

```
baca file -> profil kolom -> deteksi masalah -> usul perbaikan -> terapkan -> laporan + audit log
```

Semua proses berjalan **lokal**. Tidak ada data yang dikirim keluar dari komputer.

## Rencana penggunaan

```bash
pip install beberes

# lihat masalah tanpa mengubah apa pun (default aman)
beberes periksa data.xlsx          # alias Inggris: beberes check

# terapkan perbaikan, simpan ke file baru + laporan
beberes bersihkan data.xlsx --keluar data_bersih.xlsx --laporan   # alias: beberes clean

# pakai aturan sendiri
beberes bersihkan data.xlsx --aturan aturan.yaml

# bahasa pesan/laporan: id atau en (default mengikuti bahasa sistem)
beberes periksa data.xlsx --bahasa en

# (v0.5) antarmuka lokal di browser
beberes ui
```

## Dokumentasi

| File | Isi |
|---|---|
| [docs/01-visi-dan-ruang-lingkup.md](docs/01-visi-dan-ruang-lingkup.md) | Tujuan, target user, non-goals, kriteria sukses |
| [docs/02-arsitektur.md](docs/02-arsitektur.md) | Lapisan, modul, alur data, struktur folder |
| [docs/03-spesifikasi-aturan-dan-laporan.md](docs/03-spesifikasi-aturan-dan-laporan.md) | Format YAML, kode masalah, format laporan & audit log |
| [docs/04-rencana-data-uji.md](docs/04-rencana-data-uji.md) | Sumber data, generator data sintetis, metrik, aturan privasi |
| [docs/05-validasi-user.md](docs/05-validasi-user.md) | Cara cari user, pertanyaan wawancara, log umpan balik |
| [docs/06-keputusan-dan-risiko.md](docs/06-keputusan-dan-risiko.md) | Log keputusan desain + daftar risiko |
| [docs/07-panduan-vibecoding.md](docs/07-panduan-vibecoding.md) | Panduan kerja dengan AI (vibecoding) |
| [CLAUDE.md](CLAUDE.md) | File konteks untuk asisten AI coding |
| [ROADMAP.md](ROADMAP.md) | Versi dan checklist per versi (tanpa tanggal) |
| [CHANGELOG.md](CHANGELOG.md) | Riwayat perubahan |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cara berkontribusi |

## Lisensi

Belum ditentukan (lihat keputusan D-007).
