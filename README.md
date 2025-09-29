# OCR PDF Server

Servidor web para extracción de texto de archivos PDF mediante OCR (Reconocimiento Óptico de Caracteres).

## Funcionalidades

- Extracción de texto de PDFs mediante OCR (Tesseract)
- Interfaz web moderna con funcionalidad de arrastrar y soltar
- Soporte para múltiples idiomas (Español e Inglés)
- API REST simple y eficiente
- Estadísticas básicas del texto extraído

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

## API

### POST /ocr
Extrae texto de un archivo PDF.

**Parámetros:**
- `file`: Archivo PDF (form-data)

**Respuesta:**
```json
{
  "text": "Texto extraído del PDF",
  "success": true
}
```

### GET /health
Verifica el estado de los servicios.

## Estructura del Proyecto

- `app/` - Código fuente del servidor
  - `main.py` - API FastAPI principal
- `frontend/` - Interfaz web moderna
- `venv/` - Entorno virtual de Python
