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
    - **Puntuaciones Escalares/PE (1-19, media 10, DE 3)** 🆕
- **🎓 NUEVO:** Sistema de Aprendizaje Progresivo
  - El sistema mejora con tu retroalimentación
  - Marca puntuaciones correctas (✅) o incorrectas (❌)
  - Corrige clasificaciones erróneas
  - Patrones aprendidos se priorizan en futuras detecciones
  - Estadísticas de aprendizaje en tiempo real
  - Ver [PROGRESSIVE_LEARNING.md](./PROGRESSIVE_LEARNING.md) para más detalles
- **📝 NUEVO:** Selección de Texto y Anotaciones
  - Selecciona cualquier texto del OCR con el cursor
  - Añade notas y comentarios sobre el texto seleccionado
  - Especifica el tipo de puntuación si no se identificó correctamente
  - **Guarda el nombre del test (ej: WISC-V, NEPSY-II) para proporcionar contexto** 🆕
  - Guarda abreviaturas nuevas para enseñar al sistema
  - Las anotaciones se almacenan y mejoran futuras detecciones
- **🗄️ NUEVO:** Editor de Base de Datos 🆕
  - Interfaz web completa para gestionar datos de aprendizaje
  - Ver y editar patrones, anotaciones y retroalimentación
  - Eliminar entradas incorrectas o duplicadas
  - Dashboard con estadísticas en tiempo real
  - Acceso directo desde la página principal

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

### POST /feedback
Envía retroalimentación sobre la clasificación de una puntuación.

**Parámetros (JSON):**
```json
{
  "score": 110.0,
  "label": "CI Total",
  "detected_type": "wechsler",
  "is_correct": true,
  "correct_type": null
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Retroalimentación registrada exitosamente"
}
```

### GET /learning-stats
Obtiene estadísticas del sistema de aprendizaje progresivo.

**Respuesta:**
```json
{
  "success": true,
  "total_feedback": 42,
  "positive_feedback": 35,
  "negative_feedback": 7,
  "total_patterns": 12,
  "total_annotations": 5,
  "patterns": [...]
}
```

### POST /save-annotation
Guarda una anotación sobre texto seleccionado del OCR.

**Parámetros (JSON):**
```json
{
  "selected_text": "PE Verbal: 12",
  "note": "Puntuación escalar del WISC-V en comprensión verbal",
  "score_type": "puntuacion_escalar",
  "abbreviation": "PE",
  "test_name": "WISC-V"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Anotación guardada exitosamente",
  "annotation_saved": true,
  "pattern_added": true
}
```

**Descripción:**
- `selected_text`: El texto seleccionado por el usuario del resultado del OCR
- `note`: Comentario o anotación del usuario sobre el texto
- `score_type`: (Opcional) Tipo de puntuación si debe corregirse
- `abbreviation`: (Opcional) Abreviatura para añadir al sistema de aprendizaje
- `test_name`: (Opcional) **🆕 Nombre del test (ej: WISC-V, NEPSY-II) para proporcionar contexto**

Si se proporciona una abreviatura y un tipo de puntuación, el sistema crea automáticamente un nuevo patrón de reconocimiento.

### GET /learning-data 🆕
Obtiene todos los datos de aprendizaje almacenados (patrones, anotaciones, retroalimentación).

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "patterns": [...],
    "annotations": [...],
    "feedback_history": [...]
  }
}
```

### PUT /learning-data 🆕
Actualiza los datos de aprendizaje completos. Útil para el editor de base de datos.

**Parámetros (JSON):**
```json
{
  "patterns": [...],
  "annotations": [...],
  "feedback_history": [...]
}
```

### DELETE /learning-data/{data_type}/{index} 🆕
Elimina un elemento específico de los datos de aprendizaje.

**Parámetros de ruta:**
- `data_type`: "patterns", "annotations", o "feedback_history"
- `index`: Índice del elemento a eliminar (empezando en 0)

**Respuesta:**
```json
{
  "success": true,
  "message": "Elemento eliminado exitosamente",
  "deleted_item": {...}
}
```

### GET /editor 🆕
Sirve la interfaz web del editor de base de datos.

Accede a http://localhost:8000/editor para gestionar los datos de aprendizaje del sistema.

## Estructura del Proyecto

- `app/` - Código fuente del servidor
  - `main.py` - API FastAPI principal
- `frontend/` - Interfaz web moderna
- `venv/` - Entorno virtual de Python
