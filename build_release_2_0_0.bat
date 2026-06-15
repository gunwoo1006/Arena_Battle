@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Arena Battle Release 2.0.0 Builder

echo.
echo ==========================================
echo   Arena Battle Release 2.0.0 Builder
echo ==========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python was not found.
        echo Install Python first and check "Add python.exe to PATH".
        echo.
        pause
        exit /b 1
    )
)

echo [1/3] Installing build tools...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install pyinstaller pygame
if errorlevel 1 (
    echo.
    echo [ERROR] Package install failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Building release 2.0.0...
%PYTHON_CMD% build_release_2_0_0.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done.
echo Send this file to friends:
echo   release\Arena_Battle_release_2.0.0_for_friends.zip
echo.
pause
