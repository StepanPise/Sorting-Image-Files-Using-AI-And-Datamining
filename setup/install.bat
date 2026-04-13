@echo off
title AI Photo Manager - Installer

:: Hned na zacatku se prepneme o uroven vys do hlavni slozky projektu
cd ..

echo ==========================================
echo    Installing AI Photo Manager...
echo ==========================================

echo [1/3] Checking Python installation...
python --version > NUL 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10 or newer and try again.
    pause
    exit
)

echo [2/3] Creating isolated Virtual Environment (venv)...
:: Vytvori venv primo v hlavni slozce (tam, kde ma byt)
python -m venv venv

echo [3/3] Downloading libraries from requirements.txt...
:: Cteme requirements.txt ze slozky setup, kam jsi ho presunul
venv\Scripts\python.exe -m pip install --upgrade pip > NUL
venv\Scripts\python.exe -m pip install -r setup\requirements.txt

echo.
echo ==========================================
echo   INSTALLATION COMPLETE!
echo   You can now run start.bat
echo ==========================================
pause