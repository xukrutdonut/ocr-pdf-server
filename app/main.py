from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse, FileResponse
import tempfile
from pdf2image import convert_from_bytes
import pytesseract
import re
import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime

app = FastAPI()

# Path for storing learning data
LEARNING_DATA_PATH = "learning_data.json"

def load_learning_data() -> Dict:
    """Carga los datos de aprendizaje desde el archivo JSON"""
    if os.path.exists(LEARNING_DATA_PATH):
        try:
            with open(LEARNING_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando datos de aprendizaje: {e}")
            return {"patterns": [], "feedback_history": []}
    return {"patterns": [], "feedback_history": []}

def save_learning_data(data: Dict) -> bool:
    """Guarda los datos de aprendizaje en el archivo JSON"""
    try:
        with open(LEARNING_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando datos de aprendizaje: {e}")
        return False

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
            # Puntuación Escalar: incluye abreviaturas PE, pe
            elif 'puntuación escalar' in label or 'puntaje escalar' in label or 'escalar' in label or re.search(r'\bpe\b', label):
                score_type_counts['puntuacion_escalar'] = score_type_counts.get('puntuacion_escalar', 0) + 1
        
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
    
    # Puntuación Escalar: media 10, SD 3, rango típico 1-19
    if all(1 <= s <= 19 and s == int(s) for s in scores) and any(7 <= s <= 13 for s in scores):
        return "puntuacion_escalar"
    
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
    elif score_type == "puntuacion_escalar":
        # Puntuación Escalar: media 10, SD 3, rango típico 1-19
        return max(0, min(1, (score - 1) / 18))
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
    
    # Primero, intentar usar patrones aprendidos
    learning_data = load_learning_data()
    for pattern in learning_data.get("patterns", []):
        if pattern.get("confidence", 0) >= 2:  # Al menos 2 confirmaciones positivas
            pattern_label = pattern.get("label", "").lower()
            pattern_type = pattern.get("score_type")
            
            # Buscar coincidencia parcial o exacta
            if pattern_label in label_lower or label_lower in pattern_label:
                # Verificar que el score esté en un rango razonable para ese tipo
                score_min = pattern.get("score_min", score - 10)
                score_max = pattern.get("score_max", score + 10)
                if score_min <= score <= score_max:
                    return pattern_type
    
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
    # Puntuación Escalar: incluye abreviaturas PE, pe
    if 'puntuación escalar' in label_lower or 'puntaje escalar' in label_lower or 'escalar' in label_lower or re.search(r'\bpe\b', label_lower):
        return "puntuacion_escalar"
    
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
    
    # Puntuación Escalar: media 10, SD 3, rango típico 1-19
    if 1 <= score <= 19 and score == int(score):
        return "puntuacion_escalar"
    
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

@app.post("/feedback")
async def submit_feedback(
    score: float = Body(...),
    label: str = Body(...),
    detected_type: str = Body(...),
    is_correct: bool = Body(...),
    correct_type: Optional[str] = Body(None)
):
    """Recibe retroalimentación sobre la clasificación de puntuaciones"""
    try:
        learning_data = load_learning_data()
        
        # Registrar el feedback
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "label": label,
            "detected_type": detected_type,
            "is_correct": is_correct,
            "correct_type": correct_type if not is_correct else detected_type
        }
        
        if "feedback_history" not in learning_data:
            learning_data["feedback_history"] = []
        learning_data["feedback_history"].append(feedback_entry)
        
        # Actualizar patrones aprendidos
        if "patterns" not in learning_data:
            learning_data["patterns"] = []
        
        final_type = correct_type if not is_correct and correct_type else detected_type
        
        # Buscar si ya existe un patrón similar
        pattern_found = False
        for pattern in learning_data["patterns"]:
            if pattern["label"].lower() == label.lower() and pattern["score_type"] == final_type:
                # Actualizar el patrón existente
                if is_correct or (not is_correct and correct_type):
                    pattern["confidence"] = pattern.get("confidence", 0) + 1
                    pattern["score_min"] = min(pattern.get("score_min", score), score)
                    pattern["score_max"] = max(pattern.get("score_max", score), score)
                    pattern["last_updated"] = datetime.now().isoformat()
                pattern_found = True
                break
        
        # Si no existe, crear un nuevo patrón
        if not pattern_found and (is_correct or (not is_correct and correct_type)):
            learning_data["patterns"].append({
                "label": label,
                "score_type": final_type,
                "confidence": 1,
                "score_min": score,
                "score_max": score,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            })
        
        # Guardar los datos actualizados
        if save_learning_data(learning_data):
            return JSONResponse({
                "success": True,
                "message": "Retroalimentación registrada exitosamente"
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Error guardando la retroalimentación"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error procesando retroalimentación: {str(e)}"}
        )

@app.post("/save-annotation")
async def save_annotation(
    selected_text: str = Body(...),
    note: str = Body(...),
    score_type: Optional[str] = Body(None),
    abbreviation: Optional[str] = Body(None),
    test_name: Optional[str] = Body(None)
):
    """Guarda una anotación sobre texto seleccionado, incluyendo tipo de puntuación y abreviatura"""
    try:
        learning_data = load_learning_data()
        
        # Inicializar sección de anotaciones si no existe
        if "annotations" not in learning_data:
            learning_data["annotations"] = []
        
        # Crear entrada de anotación
        annotation_entry = {
            "timestamp": datetime.now().isoformat(),
            "selected_text": selected_text.strip(),
            "note": note.strip(),
            "score_type": score_type,
            "abbreviation": abbreviation,
            "test_name": test_name
        }
        
        learning_data["annotations"].append(annotation_entry)
        
        # Si se proporciona una abreviatura y tipo de puntuación, agregarla a patrones
        if abbreviation and score_type:
            if "patterns" not in learning_data:
                learning_data["patterns"] = []
            
            # Buscar si ya existe un patrón con esta abreviatura
            pattern_found = False
            for pattern in learning_data["patterns"]:
                if pattern["label"].lower() == abbreviation.lower() and pattern["score_type"] == score_type:
                    # Actualizar patrón existente
                    pattern["confidence"] = pattern.get("confidence", 0) + 1
                    pattern["last_updated"] = datetime.now().isoformat()
                    pattern_found = True
                    break
            
            # Si no existe, crear nuevo patrón
            if not pattern_found:
                # Intentar extraer el valor numérico del texto seleccionado
                score_value = None
                numbers = re.findall(r'-?\d+\.?\d*', selected_text)
                if numbers:
                    try:
                        score_value = float(numbers[0])
                    except ValueError:
                        pass
                
                learning_data["patterns"].append({
                    "label": abbreviation,
                    "score_type": score_type,
                    "confidence": 1,
                    "score_min": score_value if score_value else 0,
                    "score_max": score_value if score_value else 100,
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "from_annotation": True
                })
        
        # Guardar los datos actualizados
        if save_learning_data(learning_data):
            return JSONResponse({
                "success": True,
                "message": "Anotación guardada exitosamente",
                "annotation_saved": True,
                "pattern_added": bool(abbreviation and score_type)
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Error guardando la anotación"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error procesando anotación: {str(e)}"}
        )

@app.get("/learning-stats")
async def get_learning_stats():
    """Obtiene estadísticas sobre el aprendizaje del sistema"""
    try:
        learning_data = load_learning_data()
        
        total_feedback = len(learning_data.get("feedback_history", []))
        total_patterns = len(learning_data.get("patterns", []))
        total_annotations = len(learning_data.get("annotations", []))
        
        # Contar feedback positivo y negativo
        positive_feedback = sum(1 for f in learning_data.get("feedback_history", []) if f.get("is_correct", False))
        negative_feedback = total_feedback - positive_feedback
        
        return JSONResponse({
            "success": True,
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "total_patterns": total_patterns,
            "total_annotations": total_annotations,
            "patterns": learning_data.get("patterns", [])
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error obteniendo estadísticas: {str(e)}"}
        )

@app.get("/learning-data")
async def get_learning_data_endpoint():
    """Obtiene todos los datos de aprendizaje para el editor"""
    try:
        learning_data = load_learning_data()
        return JSONResponse({
            "success": True,
            "data": learning_data
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error obteniendo datos: {str(e)}"}
        )

@app.put("/learning-data")
async def update_learning_data_endpoint(data: Dict = Body(...)):
    """Actualiza los datos de aprendizaje completos"""
    try:
        if save_learning_data(data):
            return JSONResponse({
                "success": True,
                "message": "Datos actualizados exitosamente"
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Error guardando los datos"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error actualizando datos: {str(e)}"}
        )

@app.delete("/learning-data/{data_type}/{index}")
async def delete_learning_data_item(data_type: str, index: int):
    """Elimina un elemento específico de los datos de aprendizaje"""
    try:
        learning_data = load_learning_data()
        
        if data_type not in ["patterns", "feedback_history", "annotations"]:
            return JSONResponse(
                status_code=400,
                content={"error": "Tipo de dato inválido"}
            )
        
        if data_type not in learning_data:
            learning_data[data_type] = []
        
        if 0 <= index < len(learning_data[data_type]):
            deleted_item = learning_data[data_type].pop(index)
            if save_learning_data(learning_data):
                return JSONResponse({
                    "success": True,
                    "message": "Elemento eliminado exitosamente",
                    "deleted_item": deleted_item
                })
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Error guardando los datos"}
                )
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Índice fuera de rango"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error eliminando elemento: {str(e)}"}
        )

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")

@app.get("/editor")
async def editor():
    return FileResponse("frontend/editor.html")

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
