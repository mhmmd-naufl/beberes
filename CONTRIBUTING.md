# Berkontribusi

Terima kasih sudah tertarik. Issue dan PR boleh dalam bahasa Indonesia atau Inggris. / Issues and PRs are welcome in Indonesian or English. Proyek ini masih tahap awal, jadi masukan paling berharga saat ini adalah
**contoh file berantakan** (yang sudah disamarkan) dan **kasus penggunaan nyata**.

## Cara membantu

1. **Bagikan kasus data berantakan:** buka issue "Kasus data" dengan gambaran kerusakan (tanpa data pribadi asli).
2. **Laporkan bug:** sertakan perintah yang dijalankan, pesan error, dan contoh file sintetis bila bisa.
3. **Usul fitur:** jelaskan masalah yang kamu hadapi, bukan hanya solusinya.
4. **Kode:** kerjakan issue berlabel `good first issue`, atau diskusi dulu untuk perubahan besar.

## Aturan privasi

- **Jangan** unggah data asli (NIK, nama, HP, alamat) ke issue, PR, atau repo.
- Gunakan data sintetis atau yang sudah disamarkan penuh.

## Alur pengembangan

```bash
git clone <repo>
cd beberes
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

- Satu perubahan per PR, kecil dan fokus.
- Tambahkan/ubah test untuk setiap perubahan perilaku.
- Perubahan yang berdampak ke pengguna dicatat di `CHANGELOG.md`.
- Keputusan desain besar dicatat di `docs/06-keputusan-dan-risiko.md`.

## Gaya kode

- Python 3.10+, type hints untuk fungsi publik.
- Satu tanggung jawab per fungsi/modul; core tidak boleh bergantung pada CLI/UI.
- Pesan error dalam bahasa Indonesia yang jelas dan memberi saran perbaikan.

## Prinsip yang dijaga

1. Aman dulu (dry-run, audit log, undo).
2. Perbaikan yang mengubah makna tidak pernah otomatis.
3. Semua proses lokal.
