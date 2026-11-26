@echo off
title Beberes - pasang dan jalankan UI
chcp 65001 >nul

echo ============================================
echo   Beberes - perapih file Excel/CSV berantakan
echo ============================================
echo.

REM Cari Python: utamakan launcher "py", lalu "python" di PATH
set "PY_CMD="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3"
if not defined PY_CMD (
    python --version >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo Python belum terinstall di komputer ini.
    echo.
    echo 1. Buka https://www.python.org/downloads/
    echo 2. Download Python versi terbaru
    echo 3. Saat install, CENTANG tulisan "Add python.exe to PATH"
    echo    sebelum klik Install Now
    echo 4. Jalankan ulang install.bat ini
    echo.
    pause
    exit /b 1
)

echo Python ditemukan: %PY_CMD%
echo.
echo Memasang beberes dari PyPI...
%PY_CMD% -m pip install --upgrade beberes
if errorlevel 1 (
    echo.
    echo Gagal memasang beberes. Coba jalankan lagi, atau kabari
    echo masalahnya di https://github.com/mhmmd-naufl/beberes/issues
    pause
    exit /b 1
)

echo.
echo Memulai UI. Browser akan terbuka sendiri.
echo Tutup jendela ini untuk menghentikan server.
echo.
%PY_CMD% -m beberes ui
pause
