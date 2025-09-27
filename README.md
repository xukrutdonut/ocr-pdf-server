# OCR PDF Server

Servidor web para procesamiento de PDF con OCR y análisis de pruebas psicométricas.

## Funcionalidades

- Extracción de texto de PDFs mediante OCR (Tesseract)
- Reconocimiento automático de pruebas psicométricas
- Análisis y extracción de puntuaciones (CI, Percentiles, etc.)
- Visualización con gráficos ASCII
- Interfaz web de arrastrar y soltar

## Requisitos

- Python 3.11+
- Tesseract OCR
- Poppler utils

## Instalación

1. Instalar dependencias del sistema:
   ```bash
   sudo apt-get install tesseract-ocr poppler-utils
   ```

2. Instalar dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Opción 1: Script de inicio
```bash
./start_server.sh
```

### Opción 2: Manual
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Luego abre http://localhost:8000 en tu navegador.

## Docker

```bash
docker build -t ocr-pdf-server .
docker run -p 8000:80 ocr-pdf-server
```

## Estructura del Proyecto

- `app/` - Código fuente del servidor
  - `main.py` - API FastAPI principal
  - `scraping_psicometrico.py` - Lógica de análisis psicométrico
  - `psico_test_patterns.py` - Patrones de reconocimiento de tests
- `frontend/` - Interfaz web
- `venv/` - Entorno virtual de Python
