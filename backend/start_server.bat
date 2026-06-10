@echo off
set API_FOOTBALL_KEY=4b2c3b320e6977181410dca62d117006
set PYTHONIOENCODING=utf-8

echo Starting 2026 World Cup Dashboard...
start "Dashboard Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000

timeout /t 3 /nobreak > nul

echo Starting tunnel...
start "Dashboard Tunnel" %TEMP%\cloudflared.exe tunnel --url http://localhost:8000

timeout /t 8 /nobreak > nul

echo.
echo Dashboard is running!
echo Local: http://localhost:8000
echo Check cloudflared window for public URL
echo.
pause
