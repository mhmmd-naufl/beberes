# Skenario demo GIF untuk README (~30-45 detik)
# Jalankan perintah di bawah BERURUTAN di terminal, lalu export GIF.

# 0. Opsional: bersihkan terminal biar GIF rapi
cls

# 1. Versi (tampil cepat)
beberes versi

# 2. PERIKSA file berantakan — tidak mengubah apa pun
beberes periksa data_uji/berantakan_peserta.xlsx --aturan src/beberes/rules/templates/peserta.yaml --lang id

# 3. BERSIHKAN -> file baru + audit log
beberes bersihkan data_uji/berantakan_peserta.xlsx --aturan src/beberes/rules/templates/peserta.yaml --keluar data_uji/hasil_demo.xlsx --laporan --lang id

# 4. (opsional) Undo — tunjukkan reversibility
beberes urungkan data_uji/hasil_demo.xlsx --log data_uji/hasil_demo.audit.jsonl --keluar data_uji/dibalik.xlsx --lang id
