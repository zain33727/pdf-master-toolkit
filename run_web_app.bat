@echo off
title PDF Master Toolkit - Web App (iLovePDF Offline)
echo ========================================================
echo   Launching PDF Master Toolkit in your browser ...
echo ========================================================
streamlit run app_web.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while launching Streamlit.
    pause
)
