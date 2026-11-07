#!/bin/bash
# Doble clic para abrir el Optimizador de Cargas en Mac.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "No se encontró Python 3. Revisa la sección 'Instalar Python' del README."
  read -n 1 -s -r -p "Presiona cualquier tecla para cerrar..."
  exit 1
fi

echo "Revisando librerías..."
if ! python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt; then
  python3 -m pip install --quiet --user --disable-pip-version-check -r requirements.txt || {
    echo "No se pudo instalar openpyxl. Revisa la sección 'Solución de problemas' del README."
    read -n 1 -s -r -p "Presiona cualquier tecla para cerrar..."
    exit 1
  }
fi

echo "Abriendo el programa en el navegador..."
python3 app_web.py
