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

### Opción 1: Docker Compose (Recomendado)

**Instalación inicial o después de cambios en el código:**
```bash
docker compose up -d --build
```

**Para iniciar el servicio existente:**
```bash
docker compose up -d
```

**Para detener el servicio:**
```bash
docker compose down
```

El servidor estará disponible en http://localhost:8330

**Solución de problemas:**
Si después de hacer `docker compose up -d --build` sigues viendo una versión antigua, prueba:
```bash
# Detener y eliminar el contenedor
docker compose down

# Limpiar la caché de Docker para forzar una reconstrucción completa
docker compose build --no-cache

# Iniciar el servicio
docker compose up -d
```

También puede ser necesario limpiar el caché del navegador (Ctrl+F5 o Cmd+Shift+R).

### Opción 2: Docker manual
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

**Respuesta:**
```json
{
  "status": "healthy",
  "checks": {
    "tesseract": {"status": "ok", "version": "4.1.1"},
    "pdf2image": {"status": "ok"}
  }
}
```

## Estructura del Proyecto

- `app/` - Código fuente del servidor
  - `main.py` - API FastAPI principal
- `frontend/` - Interfaz web moderna
- `venv/` - Entorno virtual de Python
