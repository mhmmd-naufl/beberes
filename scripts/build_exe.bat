@echo off
REM Build beberes-ui.exe (Windows) via PyInstaller.
REM Butuh: pip install pyinstaller + package ter-install (pip install -e .)
REM Hasil: dist\beberes-ui.exe

pyinstaller --onefile --name beberes-ui --console ^
  --add-data "src/beberes/ui;beberes/ui" ^
  --add-data "src/beberes/data;beberes/data" ^
  scripts/beberes_ui.py

echo.
echo Selesai: dist\beberes-ui.exe
pause
