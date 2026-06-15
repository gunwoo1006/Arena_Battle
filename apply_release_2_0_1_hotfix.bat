@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Arena Battle Release 2.0.1 Hotfix Apply

echo.
echo ==========================================
echo   Arena Battle Release 2.0.1 Hotfix Apply
echo ==========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py apply_release_2_0_1_hotfix.py
) else (
    python apply_release_2_0_1_hotfix.py
)

echo.
pause
