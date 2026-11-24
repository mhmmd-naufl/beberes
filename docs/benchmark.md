# Benchmark akurasi

Data sintetis dari `scripts/buat_data_berantakan.py` (seed tetap).
Recall deteksi = kerusakan yang disuntik & ditemukan detector yang tepat.
Akurasi perbaikan = % sel hasil `bersihkan` yang identik dengan ground truth.

| Dataset | Recall deteksi per jenis | Akurasi perbaikan |
|---|---|---|
| kas | duplikat_variasi: 0/26 (0%) | format_tanggal_campur: 21/27 (78%) | gelar_menempel: 0/27 (0%) | sel_kosong: 0/31 (0%) | spasi_dan_kapital: 33/49 (67%) | uang_jadi_teks: 24/24 (100%) | 72.1% |
| penjualan | format_tanggal_campur: 18/19 (95%) | sel_kosong: 0/38 (0%) | spasi_dan_kapital: 35/43 (81%) | uang_jadi_teks: 23/24 (96%) | 80.8% |
| peserta | duplikat_variasi: 0/24 (0%) | format_tanggal_campur: 21/28 (75%) | gelar_menempel: 0/21 (0%) | sel_kosong: 0/48 (0%) | spasi_dan_kapital: 48/89 (54%) | typo_wilayah: 0/18 (0%) | 74.1% |
