#!/bin/bash

# Script para iniciar el servidor OCR PDF
echo "Iniciando servidor OCR PDF..."

# Navegar al directorio del proyecto
cd "$(dirname "$0")"

# Activar el entorno virtual
source venv/bin/activate

# Iniciar el servidor
echo "Servidor disponible en: http://localhost:8000"
echo "Presiona Ctrl+C para detener el servidor"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload