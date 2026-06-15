@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Arena Battle EXE Builder

echo.
echo ==========================================
echo   Arena Battle EXE Builder V2
echo ==========================================
echo.

if not exist "main.py" (
    echo [ERROR] main.py was not found in this folder.
    echo.
    echo Put these files in the SAME folder as main.py:
    echo   - build_exe_v2.bat
    echo   - build_exe_v2.py
    echo.
    pause
    exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python was not found.
        echo Install Python first, and check "Add python.exe to PATH".
        echo.
        pause
        exit /b 1
    )
)

echo [1/3] Installing build tools...
%PYTHON_CMD% -m pip install --upgrade pip >nul
%PYTHON_CMD% -m pip install pyinstaller pygame
if errorlevel 1 (
    echo.
    echo [ERROR] Package install failed.
    echo Try running this again after checking your internet connection.
    pause
    exit /b 1
)

echo.
echo [2/3] Building Arena_Battle.exe...
%PYTHON_CMD% build_exe_v2.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done.
echo.
echo Send this file to your friends:
echo   release\Arena_Battle_for_friends.zip
echo.
pause
