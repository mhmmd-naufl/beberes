# 04. Rencana Data Uji

Data uji itu bahan baku proyek. Fitur yang ditulis di awal hanyalah tebakan, file nyata adalah kebenaran.

## Aturan privasi (wajib)

1. **Jangan pernah commit data asli** (NIK, nama, HP, alamat) ke repo publik.
2. Folder `data_asli/` masuk `.gitignore` sejak hari pertama.
3. Data dari orang lain: minta izin, samarkan sebelum dipakai.
4. Repo publik hanya berisi data **sintetis** atau yang sudah disamarkan penuh.
5. README menegaskan: semua proses lokal, tidak ada data keluar.

## Sumber data (gabungan tiga lapis)

### A. Data nyata yang disamarkan (untuk menemukan masalah sebenarnya)

Target awal: 5-10 file berantakan dari konteks nyata.

- [ ] Daftar peserta/pendaftar lomba atau acara kampung
- [ ] Data iuran/kas (warga, panitia, arisan)
- [ ] Rekap penjualan warung/toko
- [ ] Inventaris (sekolah, kantor, masjid)
- [ ] Daftar warga/penerima bantuan
- [ ] Ekspor Google Form dengan jawaban teks bebas
- [ ] Data absensi

Prosedur penyamaran: ganti nama, NIK, HP, alamat dengan data palsu (Faker `id_ID`) sambil
**mempertahankan pola kerusakan aslinya** (format tanggal campur, typo, dst.). Simpan catatan "kerusakan apa yang ada".

### B. Data sintetis berantakan (untuk skala + pengukuran akurasi)

`scripts/buat_data_berantakan.py`:

1. Hasilkan data **bersih** (Faker `id_ID`): nama, tgl lahir, HP, alamat, harga, wilayah valid.
2. Simpan sebagai **ground truth** (`bersih_*.xlsx`).
3. Suntikkan kerusakan secara acak dan terkontrol (seed tetap):

| Penyuntik | Efek |
|---|---|
| format_tanggal_campur | beberapa format tanggal dalam satu kolom |
| uang_jadi_teks | `25000` -> `"Rp 25.000"` |
| spasi_dan_kapital | spasi ganda, huruf acak |
| typo_wilayah | `Banyuwangi` -> `B.wangi`, `Banyuwamgi` |
| duplikat_variasi | `Muhammad Naufal` -> `M. Naufal`, `Moh Naufal` |
| sel_kosong | hapus nilai acak |
| gelar_menempel | tambah `Drs.`, `S.Kom.` ke nama |
| header_bergeser | judul/baris kosong sebelum header |

4. Simpan hasil sebagai `berantakan_*.xlsx` + `kunci_kerusakan_*.json` (apa yang disuntikkan, di sel mana).

### C. Data referensi publik (untuk validator, bukan data kotor)

- data.go.id (Satu Data Indonesia)
- bps.go.id (statistik dan kode wilayah)
- Portal data pemda (cek Banyuwangi)
- Repo GitHub kode wilayah Indonesia (**cek lisensi** sebelum dibundel; catat sumber di `src/beberes/data/SUMBER.md`)

Catatan: data publik biasanya relatif bersih, jadi dipakai untuk referensi/tes validator.

## Metrik evaluasi

Karena ground truth diketahui, ukur per jenis masalah:

- **Recall deteksi:** berapa persen kerusakan yang suntikan berhasil ditemukan
- **Precision deteksi:** berapa persen temuan yang memang kerusakan (bukan alarm palsu)
- **Akurasi perbaikan:** berapa persen sel hasil perbaikan sama persis dengan ground truth
- **Dedupe:** precision/recall pasangan duplikat
- **Kinerja:** waktu dan RAM per ukuran file (1k, 10k, 50k baris) di laptop i3 / 12GB RAM

Hasil dicatat di `docs/benchmark.md` per rilis (tabel jujur, termasuk spesifikasi mesin).

## Fixture uji

- `tests/fixtures/berantakan_*.xlsx` dan pasangan `bersih_*.xlsx`
- Kasus tepi: sheet banyak, sel digabung, header di baris 3, encoding CSV aneh, file kosong, satu kolom saja
- Semua fixture harus sintetis atau tersamarkan penuh
