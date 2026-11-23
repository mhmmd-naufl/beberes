"""Generator data berantakan (sintetis) + ground truth.

Lihat docs/04-rencana-data-uji.md. Untuk setiap dataset menghasilkan:
  - bersih_<dataset>.xlsx      : data bersih (ground truth)
  - berantakan_<dataset>.xlsx  : data dengan kerusakan tersuntik
  - kunci_kerusakan_<dataset>.json : apa yang disuntikkan, di sel mana

Semua data sintetis (Faker id_ID + nilai buatan sendiri). Jangan masukkan
data asli ke script ini.
"""

import argparse
import json
import random
import string
from datetime import date, timedelta
from pathlib import Path

import openpyxl
from faker import Faker

# --- Bahan kerusakan (semua sintetis) -------------------------------------

GELAR = ["Drs.", "Dr.", "Ir.", "H.", "S.Kom.", "S.E.", "A.Md."]

# Prefiks nama yang bisa bervariasi ejaannya (pola umum di data Indonesia).
PREFIKS_NAMA = {
    "muhammad": ["muhammad", "mohamad", "mohd", "muh", "md"],
    "muhamad": ["muhammad", "mohamad", "mohd", "muh"],
    "muh": ["muhammad", "mohamad", "muh"],
}

# Kota sintetis untuk kolom wilayah + varian typo buatan sendiri.
# TODO: verifikasi sumber - nanti ganti dengan data wilayah resmi (docs/04 bagian C).
KOTA = [
    "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Semarang", "Medan",
    "Makassar", "Denpasar", "Palembang", "Balikpapan", "Banyuwangi", "Malang",
    "Bogor", "Bekasi", "Depok", "Tangerang", "Padang", "Manado", "Pontianak",
    "Samarinda", "Kediri", "Jember", "Probolinggo", "Lumajang", "Bondowoso",
    "Situbondo",
]

KETERANGAN_KAS = ["Iuran bulanan", "Kas lingkungan", "Arisan", "Donasi", "Lainnya"]
SATUAN = ["pcs", "pak", "lusin", "box", "unit"]

# Peluang tiap kerusakan per sel yang memenuhi syarat (0-1).
PELUANG_KERUSAKAN = 0.12
PELUANG_HEADER_BERGESER = 0.35

# Definisi dataset: nama -> daftar (kolom, tipe).
# Tipe menentukan kerusakan yang mungkin mengenai sel itu.
DATASET = {
    "peserta": [
        ("Nama", "nama"),
        ("Tanggal Lahir", "tanggal"),
        ("No HP", "hp"),
        ("Wilayah", "wilayah"),
        ("Pekerjaan", "teks"),
    ],
    "kas": [
        ("Nama", "nama"),
        ("Tanggal", "tanggal"),
        ("Uang", "uang"),
        ("Keterangan", "teks"),
    ],
    "penjualan": [
        ("Barang", "teks"),
        ("Tanggal", "tanggal"),
        ("Harga", "uang"),
        ("Qty", "angka"),
        ("Satuan", "satuan"),
    ],
}


def tanggal_acak(rng: random.Random, awal: int, akhir: int) -> date:
    """Tanggal acak antara tahun awal-akhir (inklusif)."""
    hari = (date(akhir, 12, 31) - date(awal, 1, 1)).days
    return date(awal, 1, 1) + timedelta(days=rng.randrange(hari + 1))


def nomor_hp(rng: random.Random) -> str:
    """Nomor HP sintetis: 08 + 8-10 digit."""
    return "08" + "".join(rng.choice(string.digits) for _ in range(rng.choice([8, 9, 10])))


def harga_acak(rng: random.Random) -> int:
    """Harga/iuran dalam Rupiah, kelipatan 500."""
    return rng.randrange(10, 10_000) * 500


def qty_acak(rng: random.Random) -> int:
    return rng.randrange(1, 500)


def generate_baris(dataset: str, faker: Faker, rng: random.Random, n: int) -> list[list]:
    """Hasilkan n baris data bersih untuk satu dataset."""
    baris = []
    for _ in range(n):
        nilai_per_tipe = {
            "nama": faker.name(),
            "tanggal": tanggal_acak(rng, 1950, 2010).strftime("%d/%m/%Y"),
            "hp": nomor_hp(rng),
            "wilayah": rng.choice(KOTA),
            "uang": harga_acak(rng),
            "angka": qty_acak(rng),
            "teks": faker.catch_phrase() if dataset != "kas" else rng.choice(KETERANGAN_KAS),
            "satuan": rng.choice(SATUAN),
        }
        # Kolom tanggal transaksi (kas, penjualan) pakai rentang lebih baru.
        if dataset != "peserta":
            nilai_per_tipe["tanggal"] = tanggal_acak(rng, 2020, 2025).strftime("%d/%m/%Y")
        baris.append([nilai_per_tipe[tipe] for _, tipe in DATASET[dataset]])
    return baris


# --- Penyuntik kerusakan ---------------------------------------------------
# Tiap fungsi menerima nilai bersih + rng/faker dan mengembalikan nilai kotor.
# Semua deterministik selama rng/faker di-seed.


def fmt_tanggal_campur(nilai: str, rng: random.Random) -> str:
    """Ubah 'dd/mm/yyyy' ke format lain yang umum di file berantakan."""
    tgl, bln, thn = nilai.split("/")
    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
             "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    pilihan = rng.choice([
        f"{int(tgl)}-{int(bln)}-{thn}",               # dd-mm-yyyy
        f"{thn}-{int(bln):02d}-{int(tgl):02d}",        # yyyy-mm-dd
        f"{int(tgl)} {bulan[int(bln) - 1]} {thn}",     # d Mon yyyy
        f"{int(bln)}/{int(tgl)}/{thn}",                # dd/mm -> tertukar (ambigu)
        f"{tgl}.{bln}.{thn}",                          # dd.mm.yyyy
    ])
    return pilihan


def uang_jadi_teks(nilai: int, rng: random.Random) -> str:
    """Angka -> teks Rupiah: '25000' -> 'Rp 25.000'."""
    ribuan = f"{nilai:,}".replace(",", ".")
    gaya = rng.choice([f"Rp {ribuan}", f"Rp{ribuan}", f"{ribuan} Rp", f"Rp {ribuan},00"])
    return gaya


def spasi_dan_kapital(nilai: str, rng: random.Random) -> str:
    """Sisipkan spasi ganda / spasi di tengah / ubah kapitalisasi acak."""
    if not nilai:
        return nilai
    gaya = rng.choice([
        "spasi_ganda",
        "spasi_depan_belakang",
        "huruf_kecil_semua",
        "huruf_besar_semua",
        "kapital_acak",
    ])
    if gaya == "spasi_ganda":
        return re_sub_spasi(nilai)
    if gaya == "spasi_depan_belakang":
        return f"  {nilai.strip()}  "
    if gaya == "huruf_kecil_semua":
        return nilai.lower()
    if gaya == "huruf_besar_semua":
        return nilai.upper()
    return "".join(c.upper() if rng.random() < 0.3 else c.lower() for c in nilai)


def re_sub_spasi(teks: str) -> str:
    """Ganti spasi tunggal jadi ganda."""
    return " ".join(teks.split(" ")).replace(" ", "  ") if " " in teks else teks + "  "


def typo_wilayah(nilai: str, rng: random.Random) -> str:
    """Tiru typo kota: tukar/hapus/hitup huruf, atau singkatan."""
    gaya = rng.choice(["tukar_huruf", "hapus_huruf", "dobel_huruf", "singkatan"])
    if gaya == "singkatan" and len(nilai) > 4:
        return nilai[0] + "." + nilai.split()[-1][:3] if " " in nilai else nilai[:3] + "."
    # Mutasi huruf mulai dari posisi 1 supaya huruf kapital pertama tidak rusak.
    i = rng.randrange(1, len(nilai) - 1)
    if gaya == "tukar_huruf":
        return nilai[:i] + nilai[i + 1] + nilai[i] + nilai[i + 2:]
    if gaya == "hapus_huruf":
        return nilai[:i] + nilai[i + 1:]
    return nilai[:i] + nilai[i] + nilai[i:]


def variasi_nama(nilai: str, rng: random.Random) -> str:
    """Variasi ejaan nama: 'Muhammad X' -> 'M. X' / 'Moh X', dsb."""
    bagian = nilai.split()
    if len(bagian) < 2:
        return nilai
    pertama, sisa = bagian[0], " ".join(bagian[1:])
    kunci = pertama.lower().rstrip(".")
    for prefiks, varian in PREFIKS_NAMA.items():
        if kunci == prefiks:
            return f"{rng.choice(varian)} {sisa}"
    return f"{pertama[0]}. {sisa}"


def tambah_gelar(nilai: str, rng: random.Random) -> str:
    """Tambahkan gelar di depan nama."""
    return f"{rng.choice(GELAR)} {nilai}"


def sel_kosong(_: str, rng: random.Random) -> str:
    """Hapus isi sel."""
    return ""


# Peta tipe kolom -> daftar (nama_kerusakan, fungsi, apakah boleh mengosongkan)
KERUSAKAN_PER_TIPE = {
    "nama": [
        ("spasi_dan_kapital", spasi_dan_kapital),
        ("duplikat_variasi", variasi_nama),
        ("gelar_menempel", tambah_gelar),
    ],
    "tanggal": [("format_tanggal_campur", fmt_tanggal_campur)],
    "hp": [("spasi_dan_kapital", spasi_dan_kapital)],
    "wilayah": [("typo_wilayah", typo_wilayah), ("spasi_dan_kapital", spasi_dan_kapital)],
    "uang": [("uang_jadi_teks", uang_jadi_teks)],
    "teks": [("spasi_dan_kapital", spasi_dan_kapital)],
    "satuan": [("spasi_dan_kapital", spasi_dan_kapital)],
    "angka": [],
}


def suntik_kerusakan(
    baris_bersih: list[list],
    kolom: list[tuple[str, str]],
    rng: random.Random,
) -> tuple[list[list], list[dict]]:
    """Salin data bersih lalu suntik kerusakan. Kembalikan (data_kotor, kunci)."""
    kotor = [list(b) for b in baris_bersih]
    kunci = []
    for r, baris in enumerate(kotor, start=1):  # baris data, header di baris 1
        for c, (_, tipe) in enumerate(kolom, start=1):
            nilai_bersih = baris[c - 1]
            if nilai_bersih in (None, ""):
                continue
            for nama, fungsi in KERUSAKAN_PER_TIPE.get(tipe, []):
                if rng.random() >= PELUANG_KERUSAKAN:
                    continue
                try:
                    nilai_kotor = fungsi(nilai_bersih, rng)
                except (ValueError, IndexError, TypeError):
                    continue
                if nilai_kotor == nilai_bersih:
                    continue
                kotor[r - 1][c - 1] = nilai_kotor
                kunci.append({
                    "jenis": nama,
                    "baris": r,
                    "kolom": kolom[c - 1][0],
                    "nilai_bersih": nilai_bersih,
                    "nilai_kotor": nilai_kotor,
                })
                nilai_bersih = nilai_kotor  # kerusakan berikutnya menumpuk di atas
            # Sel kosong: peluang kecil, bisa mengenai tipe apa pun.
            # Lewati kalau sel sudah kosong (mis. hasil kerusakan sebelumnya).
            if kotor[r - 1][c - 1] not in (None, "") and rng.random() < PELUANG_KERUSAKAN / 3:
                kotor[r - 1][c - 1] = ""
                kunci.append({
                    "jenis": "sel_kosong",
                    "baris": r,
                    "kolom": kolom[c - 1][0],
                    "nilai_bersih": baris_bersih[r - 1][c - 1],
                    "nilai_kotor": "",
                })
    return kotor, kunci


def geser_header(
    lebar: int, rng: random.Random, pasti: bool = False
) -> tuple[list[list], dict]:
    """Buat baris sisipan judul/kosong sebelum header (pola umum di Excel).

    Mengembalikan (baris_sisipan, info). Baris data di kunci bernomor mulai 1;
    info["offset_baris"] dipakai sebagai: baris_excel = baris + offset_baris.
    """
    if not pasti and rng.random() >= PELUANG_HEADER_BERGESER:
        return [], {}
    n_judul = rng.choice([1, 1, 2, 3])
    judul = "LAPORAN " + rng.choice(["KEUANGAN", "PESERTA", "PENJUALAN", "WARGA"])
    # 1 baris judul + n_judul baris kosong, lalu header, lalu data.
    sisipan = [[judul]] + [[""] * lebar for _ in range(n_judul)]
    # offset_baris: baris_excel = baris + offset_baris (lihat docstring).
    info = {"baris_judul": n_judul, "judul": judul, "offset_baris": n_judul + 2}
    return sisipan, info


def tulis_xlsx(path: Path, semua_baris: list[list]) -> None:
    """Tulis xlsx; semua_baris sudah termasuk baris header di indeks 0."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"
    for baris_data in semua_baris:
        ws.append(baris_data)
    wb.save(path)


def buat_dataset(
    dataset: str,
    n: int,
    seed: int,
    keluar: Path,
    geser_pasti: bool = False,
) -> dict:
    """Bangkitkan satu dataset: bersih + berantakan + kunci."""
    faker = Faker("id_ID")
    faker.seed_instance(seed)
    rng = random.Random(seed)

    kolom = DATASET[dataset]
    header = [nama for nama, _ in kolom]
    baris_bersih = generate_baris(dataset, faker, rng, n)

    baris_kotor, kunci = suntik_kerusakan(baris_bersih, kolom, rng)
    sisipan, info_header = geser_header(len(header), rng, pasti=geser_pasti)
    if info_header:
        kunci.insert(0, {"jenis": "header_bergeser", **info_header})

    berkas_bersih = keluar / f"bersih_{dataset}.xlsx"
    berkas_kotor = keluar / f"berantakan_{dataset}.xlsx"
    berkas_kunci = keluar / f"kunci_kerusakan_{dataset}.json"

    tulis_xlsx(berkas_bersih, [header] + baris_bersih)
    tulis_xlsx(berkas_kotor, sisipan + [header] + baris_kotor)
    berkas_kunci.write_text(json.dumps({
        "dataset": dataset,
        "baris": n,
        "seed": seed,
        "berkas_bersih": berkas_bersih.name,
        "berkas_berantakan": berkas_kotor.name,
        "jumlah_kerusakan": len(kunci),
        "kerusakan": kunci,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "dataset": dataset,
        "kerusakan": len(kunci),
        "header_bergeser": bool(info_header),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baris", type=int, default=200, help="Jumlah baris per dataset")
    parser.add_argument("--seed", type=int, default=42, help="Seed acak (reprodusibel)")
    parser.add_argument(
        "--keluar", type=Path, default=Path("data_uji"),
        help="Folder keluaran (default: data_uji/)",
    )
    parser.add_argument(
        "--dataset", choices=[*DATASET, "semua"], default="semua",
        help="Dataset yang dibuat",
    )
    args = parser.parse_args()

    args.keluar.mkdir(parents=True, exist_ok=True)
    daftar = list(DATASET) if args.dataset == "semua" else [args.dataset]
    for i, dataset in enumerate(daftar):
        # Geser seed per dataset supaya tiap dataset punya data yang berbeda.
        # Dataset pertama selalu mendapat header bergeser supaya pola itu pasti teruji.
        hasil = buat_dataset(
            dataset, args.baris, args.seed + i * 1000, args.keluar, geser_pasti=(i == 0)
        )
        print(
            f"{hasil['dataset']}: {hasil['kerusakan']} kerusakan"
            + (" (+header bergeser)" if hasil["header_bergeser"] else "")
        )
    print(f"Selesai. Keluaran di {args.keluar}/")


if __name__ == "__main__":
    main()
