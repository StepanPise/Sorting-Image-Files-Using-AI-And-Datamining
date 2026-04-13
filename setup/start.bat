@echo off
title AI Photo Manager - Engine

:: Opet se nejprve prepneme do hlavni slozky
cd ..

:: 1. SMART CHECK: Is the server already running?
netstat -ano | find "LISTENING" | find ":8000" > NUL
if %errorlevel% equ 0 (
    start chrome --app="http://127.0.0.1:8000/"
    exit
)

:: 2. FIRST TIME STARTUP
echo        Starting application

echo [1/3] Starting PostgreSQL via Docker...
:: Diky cd .. jsme ted v hlavni slozce, takze cd docker funguje spravne
cd docker
docker compose up -d
cd ..

:: 3. SMART BROWSER LAUNCH (Waits for HTTP 200 OK)
echo [2/3] Waiting for AI models to load...
start /B cmd /c "for /l %%i in (1,1,60) do (curl -s http://127.0.0.1:8000/ > NUL && (start chrome --app=http://127.0.0.1:8000/ & exit) || timeout /t 1 > NUL)"

:: 4. RUN MAIN SERVER
echo [3/3] Starting Python Server...
echo.
echo ============================================================
echo   [!] ENGINE IS RUNNING [!]
echo   - Closing the app window does NOT stop this server.
echo   - To completely STOP the application, CLOSE THIS WINDOW or CTRL + C.
echo ============================================================
echo.

:: Booting the server via venv in the main directory
if exist "venv\Scripts\python.exe" (
    echo [INFO] Booting server via local venv...
    venv\Scripts\python.exe server.py
) else (
    echo [INFO] Venv not found, booting via global Python...
    python server.py
)