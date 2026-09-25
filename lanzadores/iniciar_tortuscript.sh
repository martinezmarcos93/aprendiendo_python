#!/usr/bin/env sh
# Abre TortuScript. Usa el entorno .venv si existe; si no, python3 del sistema.
cd "$(dirname "$0")/.." || exit 1
if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
else
    PY="python3"
fi
"$PY" iniciar_web.py "$@" || {
    echo
    echo "Algo salió mal. Si falta Flask:  $PY -m pip install -r requirements.txt"
    exit 1
}
