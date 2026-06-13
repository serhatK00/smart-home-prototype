@echo off
title Akilli Ev Sistemi Baslatici

set ROOT=%~dp0

echo Sistemler baslatiliyor...
echo.

:: .venv yoksa otomatik kur
if not exist "%ROOT%python\.venv\" (
    echo Bagimliliklar yukleniyor, lutfen bekleyin...
    python -m venv "%ROOT%python\.venv"
    "%ROOT%python\.venv\Scripts\pip" install -r "%ROOT%python\requirements.txt"
    echo Yukleme tamamlandi.
    echo.
)

:: Python uygulamasini gizli baslat
powershell -WindowStyle Hidden -Command "Start-Process \"%ROOT%python\.venv\Scripts\python.exe\" -ArgumentList \"%ROOT%python\main.py\" -WindowStyle Hidden"

:: C# uygulamasini gizli baslat
powershell -WindowStyle Hidden -Command "Start-Process 'dotnet' -ArgumentList 'run --urls http://0.0.0.0:5049' -WorkingDirectory \"%ROOT%csharp\" -WindowStyle Hidden"

:: IPv4 adresini al
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%a
)

:: Bastaki boslugu temizle
set IP=%IP: =%

echo ============================
echo Web Sunucusuna Baglanma Adresi:
echo ============================
echo http://%IP%:5049
echo.
echo ============================
echo Kullanici Adi ve Sifre: admin / 1234
echo ============================
echo.
echo Her iki sistem de arka planda baslatildi.
pause