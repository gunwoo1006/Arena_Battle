@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Arena Battle Sound Options Patch V4

echo.
echo ==========================================
echo   Arena Battle Sound Options Patch V4
echo ==========================================
echo.

if not exist "main.py" (
    echo [ERROR] main.py was not found in this folder.
    echo Put this patch in the SAME folder as main.py.
    echo.
    pause
    exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
    py apply_sound_options_patch_v4.py
) else (
    python apply_sound_options_patch_v4.py
)

echo.
pause
