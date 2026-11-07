@echo off
title Optimizador de Cargas
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
echo Revisando librerias...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo.
  echo No se pudo usar Python. Revisa la seccion "Instalar Python" del README.
  pause
  exit /b 1
)
echo Abriendo el programa en el navegador...
%PY% app_web.py
pause
