from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse, FileResponse
import tempfile
from pdf2image import convert_from_bytes
import pytesseract
import re
from typing import List, Dict, Tuple, Optional

app = FastAPI()

def detect_score_type(scores: List[float], labels: List[str] = None) -> Optional[str]:
    """Detecta el tipo de puntuación basándose en los valores y etiquetas encontradas"""
    if not scores:
        return None
    
    min_score = min(scores)
    max_score = max(scores)
    
    # Separar scores por label para detectar múltiples tipos
    score_type_counts = {}
    
    # Si tenemos labels, buscar keywords y dar prioridad
    if labels:
        labels_lower = [l.lower() for l in labels]
        
        # Contar menciones de cada tipo
        for i, label in enumerate(labels_lower):
            # Percentil: incluye abreviaturas PC, p, P
            if 'percentil' in label or re.search(r'\bpc\b', label) or re.search(r'\bp\b', label):
                score_type_counts['percentil'] = score_type_counts.get('percentil', 0) + 1
            elif 'ci' in label or 'coeficiente' in label or 'iq' in label or 'wechsler' in label:
                score_type_counts['wechsler'] = score_type_counts.get('wechsler', 0) + 1
            elif 'eneatipo' in label:
                score_type_counts['eneatipo'] = score_type_counts.get('eneatipo', 0) + 1
            elif 'decatipo' in label or 'decil' in label:
                score_type_counts['decatipo'] = score_type_counts.get('decatipo', 0) + 1
            # Puntuación T: incluye abreviaturas PT, pt
            elif 'puntuación t' in label or 'puntaje t' in label or 't-score' in label or re.search(r'\bpt\b', label):
                score_type_counts['puntuacion_t'] = score_type_counts.get('puntuacion_t', 0) + 1
            # Puntuación Z: incluye abreviaturas Z, z
            elif 'puntuación z' in label or 'puntaje z' in label or 'z-score' in label or re.search(r'\bz\b', label):
                score_type_counts['puntuacion_z'] = score_type_counts.get('puntuacion_z', 0) + 1
        
        # Si hay un tipo dominante, usarlo
        if score_type_counts:
            return max(score_type_counts, key=score_type_counts.get)
    
    # Si no hay labels claros, inferir por valores
    
    # Eneatipos: 1-9
    if all(1 <= s <= 9 and s == int(s) for s in scores) and max_score <= 9:
        return "eneatipo"
    
    # Decatipos: 1-10
    if all(1 <= s <= 10 and s == int(s) for s in scores) and max_score <= 10:
        return "decatipo"
    
    # Percentiles: 0-100
    if all(0 <= s <= 100 for s in scores) and max_score <= 100:
        return "percentil"
    
    # Puntuación de Wechsler/CI: típicamente 85-130, pero puede ir de 40-160
    if any(s > 100 for s in scores) and all(40 <= s <= 160 for s in scores):
        return "wechsler"
    
    # Puntuación T: media 50, SD 10, rango típico 20-80
    if all(20 <= s <= 80 for s in scores) and any(40 <= s <= 60 for s in scores):
        return "puntuacion_t"
    
    # Puntuación Z: típicamente -3 a +3
    if all(-4 <= s <= 4 for s in scores) and any(s < 0 for s in scores):
        return "puntuacion_z"
    
    return None

def normalize_score(score: float, score_type: str) -> float:
    """Normaliza una puntuación al rango 0-1 según su tipo"""
    if score_type == "eneatipo":
        return (score - 1) / 8  # 1-9 -> 0-1
    elif score_type == "decatipo":
        return (score - 1) / 9  # 1-10 -> 0-1
    elif score_type == "percentil":
        return score / 100  # 0-100 -> 0-1
    elif score_type == "wechsler":
        # Wechsler/CI: 40-160, media 100, normalizar al rango común
        return max(0, min(1, (score - 40) / 120))
    elif score_type == "puntuacion_t":
        # T-score: mean 50, SD 10, rango típico 20-80
        return max(0, min(1, (score - 20) / 60))
    elif score_type == "puntuacion_z":
        # Z-score: -3 a +3 -> 0-1
        return max(0, min(1, (score + 3) / 6))
    return 0.5

def generate_ascii_chart(scores: List[Tuple[float, str]], score_type: str) -> str:
    """Genera un gráfico ASCII horizontal de las puntuaciones normalizadas"""
    if not scores:
        return ""
    
    chart_lines = []
    chart_lines.append("\n" + "="*60)
    chart_lines.append("GRÁFICA DE PUNTUACIONES NORMALIZADAS")
    chart_lines.append(f"Tipo de puntuación detectado: {score_type.upper()}")
    chart_lines.append("="*60 + "\n")
    
    max_label_len = max(len(label) for _, label in scores) if scores else 20
    
    for score, label in scores:
        normalized = normalize_score(score, score_type)
        bar_length = int(normalized * 40)  # 40 caracteres de ancho máximo
        bar = "█" * bar_length
        percentage = normalized * 100
        
        # Formato: "Label (score): [barra] XX.X%"
        line = f"{label[:max_label_len]:>{max_label_len}} ({score:6.1f}): {bar:<40} {percentage:5.1f}%"
        chart_lines.append(line)
    
    chart_lines.append("\n" + "="*60)
    return "\n".join(chart_lines)

def classify_individual_score(score: float, label: str) -> Optional[str]:
    """Clasifica una puntuación individual basándose en su valor y etiqueta"""
    label_lower = label.lower()
    
    # Detección por etiqueta (más específico primero)
    # Percentil: incluye abreviaturas PC, p, P
    if 'percentil' in label_lower or 'percentile' in label_lower or re.search(r'\bpc\b', label_lower) or re.search(r'\bp\b', label_lower):
        return "percentil"
    # CI debe ser palabra separada, no parte de otra palabra
    if re.search(r'\bci\b', label_lower) or 'coeficiente' in label_lower or re.search(r'\biq\b', label_lower) or 'wechsler' in label_lower:
        return "wechsler"
    if 'eneatipo' in label_lower or 'eneagrama' in label_lower:
        return "eneatipo"
    if 'decatipo' in label_lower or 'decil' in label_lower:
        return "decatipo"
    # Puntuación T: incluye abreviaturas PT, pt
    if 't-score' in label_lower or 'puntuación t' in label_lower or 'puntaje t' in label_lower or 'puntaje-t' in label_lower or 'puntuacion-t' in label_lower or re.search(r'\bpt\b', label_lower):
        return "puntuacion_t"
    # Puntuación Z: incluye abreviaturas Z, z
    if 'z-score' in label_lower or 'puntuación z' in label_lower or 'puntaje z' in label_lower or 'puntaje-z' in label_lower or 'puntuacion-z' in label_lower or re.search(r'\bz\b', label_lower):
        return "puntuacion_z"
    
    # Detección por valor (menos específico)
    # Priorizar rangos más específicos/restrictivos primero
    
    # Puntuación Z: típicamente -4 a +4 (más restrictivo, incluye negativos)
    if -4 <= score <= 4:
        return "puntuacion_z"
    
    # Eneatipos: 1-9 (valores pequeños, enteros)
    if 1 <= score <= 9 and score == int(score):
        return "eneatipo"
    
    # Decatipos: 1-10 (valores pequeños, enteros)
    if 1 <= score <= 10 and score == int(score):
        return "decatipo"
    
    # Puntuación T: media 50, SD 10, rango típico 20-80
    if 20 <= score <= 80:
        return "puntuacion_t"
    
    # Percentiles: 0-100 (más común)
    if 0 <= score <= 100:
        return "percentil"
    
    # Puntuación de Wechsler/CI: típicamente 40-160 (más amplio, va al final)
    if 40 <= score <= 160:
        return "wechsler"
    
    return None

def extract_scores_from_text(text: str) -> Dict:
    """Extrae puntuaciones del texto y genera análisis"""
    # Buscar patrones comunes de puntuaciones en textos psicométricos
    
    score_patterns = [
        # Patrones con etiquetas comunes
        r'([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+):\s*(-?\d+\.?\d*)',
        # Números seguidos de contexto
        r'(-?\d+\.?\d*)\s*\(([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)\)',
        # Líneas que terminan en número
        r'([A-Za-zÁÉÍÓÚáéíóúñÑ\s]{3,})\s+(-?\d+\.?\d*)$'
    ]
    
    found_scores = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        for pattern in score_patterns:
            matches = re.finditer(pattern, line, re.MULTILINE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 2:
                    # Determinar cuál es el label y cuál el score
                    if groups[0].replace('.', '').replace('-', '').isdigit():
                        score_str, label = groups[0], groups[1]
                    else:
                        label, score_str = groups[0], groups[1]
                    
                    try:
                        score = float(score_str)
                        # Filtrar valores que probablemente no son puntuaciones
                        if -100 <= score <= 200:
                            score_type = classify_individual_score(score, label)
                            found_scores.append((score, label.strip(), score_type))
                    except ValueError:
                        continue
    
    if not found_scores:
        return {
            "scores": [],
            "score_type": None,
            "ascii_chart": ""
        }
    
    # Agrupar por tipo de puntuación
    scores_by_type = {}
    for score, label, score_type in found_scores:
        if score_type:
            if score_type not in scores_by_type:
                scores_by_type[score_type] = []
            scores_by_type[score_type].append((score, label))
    
    # Generar gráficas para cada tipo
    ascii_charts = []
    all_scores_formatted = []
    
    for score_type, scores_data in scores_by_type.items():
        chart = generate_ascii_chart(scores_data, score_type)
        ascii_charts.append(chart)
        all_scores_formatted.extend([(s[0], s[1], score_type) for s in scores_data])
    
    combined_chart = "\n\n".join(ascii_charts) if ascii_charts else ""
    
    return {
        "scores": all_scores_formatted,
        "score_type": list(scores_by_type.keys())[0] if len(scores_by_type) == 1 else "mixed",
        "ascii_chart": combined_chart
    }

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
    
    return JSONResponse({
        "text": text.strip(),
        "success": True
    })

@app.post("/analyze-scores")
async def analyze_scores(text: str = Body(..., embed=True)):
    """Analiza un texto para detectar puntuaciones y generar gráficos ASCII"""
    if not text or not text.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "El texto no puede estar vacío"}
        )
    
    try:
        score_analysis = extract_scores_from_text(text)
        
        return JSONResponse({
            "success": True,
            "scores": score_analysis["scores"],
            "score_type": score_analysis["score_type"],
            "ascii_chart": score_analysis["ascii_chart"]
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error analizando puntuaciones: {str(e)}"}
        )

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
