@echo off
rem Abre TortuScript (doble clic). Usa el entorno .venv si existe; si no, el Python del sistema.
chcp 65001 >nul
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
)
%PY% iniciar_web.py %*
if errorlevel 1 (
    echo.
    echo Algo salio mal. Si falta Flask:  %PY% -m pip install -r requirements.txt
    pause
)
