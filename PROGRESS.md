# PROGRESS.md — log kerja per sesi

> Catatan ringkas apa yang dikerjakan tiap sesi. Detail teknis tetap di
> commit message, CHANGELOG, dan docs/. File ini untuk melihat laju proyek
> tanpa baca git log.

## 2026-11-26 — v0.5.1 rilis + persiapan user testing

- **v0.5.0 dirilis** ke PyPI (merge dua lini UI: centang per grup + centang per sel, undo, i18n, anti-slop)
- **v0.5.1 dirilis** ke PyPI: `beberes ui` auto-buka browser, file contoh `/contoh.xlsx`, `install.bat` Windows, `python -m beberes`, favicon/ikon teal (mark-c) di UI + README
- **README** diperprofesionalisasi: logo center + badge PyPI/Python/License/CI
- **Skill anti-slop** dipasang global (`~/.config/devin/skills/`); audit UI 12 temuan diperbaiki
- **Skill icon-designer** dipasang; mark-c jadi ikon resmi
- **User testing disiapkan**: form Google (12 pertanyaan, docs/05), draft LinkedIn/Threads di `draft-linkedin-threads.txt` (lokal, gitignored) — menunggu diposting user
- **Exe PyInstaller POC berhasil**: `dist/beberes-ui.exe` (27MB) jalan end-to-end
  (index, favicon, contoh.xlsx, /api/periksa semua 200). Perlu `--add-data`
  untuk `ui/` + `data/` dan resolver `sys._MEIPASS` di `ui/app.py` +
  `validators/wilayah.py`. Build: `scripts/build_exe.bat`
- **CI exe jalan** (`.github/workflows/exe.yml`): tag `v*` auto-build +
  attach exe ke GitHub Release; `workflow_dispatch` upload artifact.
  Tervalidasi via dispatch manual (artifact 18MB, 1m15s)

## Berikutnya

- Exe rilis pertama akan menyertakan `beberes-ui.exe` di GitHub Release
  v0.5.2+; masih console (pywebview menyusul, D-014)
- Posting draft sosmed, kumpulkan respons form -> docs/05
- Kandidat v0.6: heuristik TGL002, partial undo
