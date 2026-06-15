@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Arena Battle Sound Patch V5

echo.
echo ==========================================
echo   Arena Battle Sound Patch V5
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
    py apply_sound_patch_v5.py
) else (
    python apply_sound_patch_v5.py
)

echo.
pause
