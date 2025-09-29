from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import tempfile
from pdf2image import convert_from_bytes
import pytesseract
from .scoring_analyzer import ScoringAnalyzer

app = FastAPI()
analyzer = ScoringAnalyzer()

@app.post("/ocr")
async def ocr_pdf(file: UploadFile = File(...)):
    # Validar que el archivo sea un PDF válido
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={"error": "Solo se permiten archivos PDF"}
        )
    
    pdf_bytes = await file.read()
    
    # Validar que el archivo no esté vacío
    if not pdf_bytes or len(pdf_bytes) < 100:  # Un PDF mínimo tiene al menos 100 bytes
        return JSONResponse(
            status_code=400,
            content={"error": "El archivo PDF está vacío o corrupto"}
        )
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            images = convert_from_bytes(pdf_bytes, output_folder=tmpdir)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang='spa+eng') + "\n"
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Error procesando el PDF: {str(e)}"}
        )
    
    # Analyze the text for numbers and scoring patterns
    analysis = analyzer.analyze_text(text.strip())
    
    return JSONResponse({
        "text": text.strip(),
        "highlighted_text": analysis.highlighted_text,
        "detected_numbers": [
            {
                "value": num.value,
                "score_type": num.score_type,
                "interpretation": num.interpretation,
                "context": num.context[:100] + ('...' if len(num.context) > 100 else '')
            }
            for num in analysis.numbers
        ],
        "statistics": analysis.statistics,
        "interpretations": analysis.interpretations,
        "success": True
    })

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que todos los servicios estén funcionando"""
    health_status = {"status": "healthy", "checks": {}}
    
    try:
        # Verificar que Tesseract está disponible
        import pytesseract
        version = pytesseract.get_tesseract_version()
        health_status["checks"]["tesseract"] = {
            "status": "ok", 
            "version": str(version)
        }
    except Exception as e:
        health_status["status"] = "unhealthy" 
        health_status["checks"]["tesseract"] = {
            "status": "error", 
            "error": str(e)
        }
    
    try:
        # Verificar que pdf2image puede importarse
        from pdf2image import convert_from_bytes
        health_status["checks"]["pdf2image"] = {"status": "ok"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["pdf2image"] = {
            "status": "error", 
            "error": str(e)
        }
    
    return JSONResponse(health_status)
