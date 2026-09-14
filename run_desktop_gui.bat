@echo off
title PDF Master Toolkit - Desktop GUI
echo ========================================================
echo   Starting PDF Master Toolkit (Desktop GUI) ...
echo ========================================================
python gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the application.
    pause
)
