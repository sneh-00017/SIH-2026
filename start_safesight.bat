@echo off
setlocal
cd /d "%~dp0"
start "SafeSight Backend" powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '%~dp0~~~~Sneh Backend~~~~'; & '%~dp0.venv\Scripts\python.exe' app.py"
start "SafeSight Frontend" powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '%~dp0frontend'; & npm.cmd run dev -- --host 0.0.0.0 --port 5179"
echo.
echo SafeSight is starting on port 5179.
echo On this computer: http://localhost:5179/
echo On a phone using the same Wi-Fi: http://YOUR-COMPUTER-IP:5179/
echo Find YOUR-COMPUTER-IP with ipconfig, using the IPv4 Address of the active Wi-Fi adapter.
pause
