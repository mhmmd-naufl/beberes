# Sumber data referensi

## `wilayah.json`

- **Sumber**: https://github.com/cahyadsn/wilayah — lisensi **MIT**
- **Data**: Kode & nama wilayah sesuai **Kepmendagri No 300.2.2-2138 Tahun 2025**
- **Isi**: provinsi (38), kabupaten/kota (514), kecamatan (7.265)
- **Format SQL asli**: `db/wilayah.sql` di repo tersebut (di-parse ke JSON)
- **Level desa/kelurahan (83.345)**: belum dibundel — ukuran file terlalu
  besar untuk package inti. Bisa ditambah sebagai file opsional nanti.

### Atribusi

Data wilayah di file ini berasal dari cahyadsn/wilayah (MIT License),
yang merujuk Keputusan Menteri Dalam Negeri terbaru.

### regenerasi

```bash
curl -sL -o /tmp/wilayah.sql \
  https://raw.githubusercontent.com/cahyadsn/wilayah/master/db/wilayah.sql
# lalu parse INSERT INTO wilayah VALUES (...) -> JSON
```
