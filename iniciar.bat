@echo off
title Soil Taxonomy App
cd /d "%~dp0"
echo Iniciando Soil Taxonomy en Streamlit...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
) else (
    python -m streamlit run app.py --browser.gatherUsageStats false
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al iniciar la aplicacion.
    pause
)
