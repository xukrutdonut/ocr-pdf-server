# OCR PDF Server

Servidor web para extracción de texto de archivos PDF mediante OCR (Reconocimiento Óptico de Caracteres).

## Funcionalidades

- Extracción de texto de PDFs mediante OCR (Tesseract)
- Interfaz web moderna con funcionalidad de arrastrar y soltar
- Soporte para múltiples idiomas (Español e Inglés)
- API REST simple y eficiente
- Estadísticas básicas del texto extraído
- **✨ NUEVO:** Detección automática de puntuaciones psicométricas
  - Identifica y resalta puntuaciones en rojo
  - Genera gráficos ASCII de barras normalizadas
  - Soporta múltiples tipos de escalas:
    - Percentiles (0-100)
    - Eneatipos (1-9)
    - Decatipos (1-10)
    - Puntuaciones Wechsler/CI (40-160)
    - Puntuaciones T (media 50, SD 10)
    - Puntuaciones Z (estandarizadas)

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
  "success": true,
  "scores": [
    [110.0, "CI Total", "wechsler"],
    [75.0, "Percentil General", "percentil"]
  ],
  "score_type": "mixed",
  "ascii_chart": "Gráfico ASCII de las puntuaciones normalizadas..."
}
```

**Campos de respuesta:**
- `text`: Texto extraído del PDF
- `success`: Indica si la extracción fue exitosa
- `scores`: Lista de puntuaciones detectadas (valor, etiqueta, tipo)
- `score_type`: Tipo de puntuación detectada o "mixed" para múltiples tipos
- `ascii_chart`: Representación visual ASCII de las puntuaciones normalizadas

### GET /health
Verifica el estado de los servicios.

## Estructura del Proyecto

- `app/` - Código fuente del servidor
  - `main.py` - API FastAPI principal
- `frontend/` - Interfaz web moderna
- `venv/` - Entorno virtual de Python
