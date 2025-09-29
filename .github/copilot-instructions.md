# GitHub Copilot Instructions for OCR PDF Server

## Repository Overview

This is an OCR PDF Server that extracts text from PDF files using Optical Character Recognition (OCR). The server provides:

- Web API for PDF text extraction using Tesseract OCR
- Modern web interface with drag-and-drop functionality  
- Support for multiple languages (Spanish and English)
- Simple and efficient REST API
- Basic text statistics from extracted content

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **OCR Engine**: Tesseract OCR
- **PDF Processing**: pdf2image, Pillow
- **Web Server**: Uvicorn (ASGI server)
- **Frontend**: Static HTML/CSS/JavaScript
- **Deployment**: Docker, Docker Compose

## Project Structure

```
/
├── app/                    # Main application code
│   ├── __init__.py
│   └── main.py            # FastAPI application with OCR endpoints
├── frontend/              # Static web interface
│   └── index.html        # Main web UI
├── .github/               # GitHub configuration
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service setup
├── requirements.txt      # Python dependencies
├── start_server.sh      # Development server script
└── ecosystem.config.js   # PM2 configuration
```

## Development Setup

### System Dependencies
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

### Python Environment
```bash
pip install -r requirements.txt
```

### Running the Server

**Option 1: Using start script**
```bash
./start_server.sh
```

**Option 2: Manual start**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Docker**
```bash
docker compose up -d  # Runs on port 8330
```

## API Endpoints

### POST /ocr
Extracts text from uploaded PDF files.

**Parameters:**
- `file`: PDF file (multipart/form-data)

**Response:**
```json
{
  "text": "Extracted text from PDF",
  "success": true
}
```

**Error Response:**
```json
{
  "error": "Error description"
}
```

### GET /health
Health check endpoint that verifies:
- Tesseract OCR availability and version
- pdf2image module functionality

### GET /
Serves the main web interface (frontend/index.html)

## Code Style and Conventions

### Python Code Style
- Use FastAPI async/await patterns
- Handle errors gracefully with proper HTTP status codes
- Validate file uploads (PDF format, size, corruption)
- Use temporary directories for file processing
- Clean up resources properly (use context managers)

### Error Handling
- Return 400 for client errors (invalid files, format issues)
- Return 500 for server errors (processing failures)
- Always include descriptive error messages
- Use JSONResponse for consistent API responses

### File Processing Patterns
```python
# Always use temporary directories
with tempfile.TemporaryDirectory() as tmpdir:
    # Process files here
    pass

# Validate file formats
if not file.filename.lower().endswith('.pdf'):
    return JSONResponse(status_code=400, content={"error": "..."})

# Check file size/content
if not pdf_bytes or len(pdf_bytes) < 100:
    return JSONResponse(status_code=400, content={"error": "..."})
```

## Testing Approach

Currently, this repository does not have automated tests. When adding tests, consider:

- Unit tests for OCR processing functions
- Integration tests for API endpoints
- File upload validation tests
- Error handling tests
- Health check endpoint tests

Use pytest as the testing framework if implementing tests.

## Dependencies and Libraries

### Core Dependencies
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `python-multipart`: File upload handling
- `pytesseract`: Tesseract OCR Python wrapper
- `pdf2image`: PDF to image conversion
- `Pillow`: Image processing

### System Requirements
- Tesseract OCR binary
- Poppler utilities (for PDF processing)

## Deployment

### Docker Deployment
The application is containerized and can be deployed using:
- Docker Compose (recommended): `docker compose up -d`
- Standalone Docker: `docker build -t ocr-pdf-server . && docker run -p 8000:80 ocr-pdf-server`

### Production Considerations
- The server runs on port 8000 (development) or 80 (container)
- Docker Compose setup exposes port 8330
- Health checks are available at `/health`
- Static files are served directly by FastAPI

## Language and Localization

- OCR supports Spanish and English (`lang='spa+eng'`)
- Web interface and error messages are primarily in Spanish
- Consider this when adding new features or documentation

## Common Patterns

### Adding New Endpoints
```python
@app.post("/new-endpoint")
async def new_endpoint(file: UploadFile = File(...)):
    # Validate file
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"error": "..."})
    
    # Process file
    try:
        # Your processing logic
        pass
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error: {str(e)}"})
    
    return JSONResponse({"success": True, "result": "..."})
```

### File Validation Pattern
Always validate:
1. File extension (.pdf)
2. File size (not empty, reasonable size)
3. File content (not corrupted)

## Security Considerations

- File upload size limits should be considered
- Only PDF files are accepted
- Temporary files are cleaned up automatically
- No persistent storage of uploaded files

## Maintenance Notes

- Monitor Tesseract version compatibility
- Keep Python dependencies updated
- Verify Docker image builds successfully
- Test OCR accuracy with sample documents

## When Contributing

1. Maintain existing code style and patterns
2. Add proper error handling for new features
3. Update this documentation if adding new functionality
4. Test with both Spanish and English text
5. Verify Docker deployment still works