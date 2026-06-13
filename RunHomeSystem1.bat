@echo off
title Akilli Ev Sistemi Baslatici
set ROOT=%~dp0

echo Sistemler baslatiliyor...
echo.

powershell -WindowStyle Hidden -Command "Start-Process '%ROOT%python\.venv\Scripts\python.exe' -ArgumentList '%ROOT%python\main.py' -WindowStyle Hidden"
powershell -WindowStyle Hidden -Command "Start-Process 'dotnet' -ArgumentList 'run --urls http://0.0.0.0:5049' -WorkingDirectory '%ROOT%csharp' -WindowStyle Hidden"

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set IP=%%a
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