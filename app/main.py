import re
import threading
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import tempfile
from pdf2image import convert_from_bytes
import pytesseract
from scraping_psicometrico import scrape_psicometricas, save_pruebas, load_pruebas

app = FastAPI()

ESCALAS = {
    "CI": {"min": 40, "max": 160, "label": "CI (media 100, DE 15)", "barlen": 20},
    "PT": {"min": 10, "max": 90, "label": "PT (media 50, DE 10)", "barlen": 20},
    "Percentil": {"min": 1, "max": 99, "label": "Percentil (1-99)", "barlen": 20},
    "Decatipo": {"min": 1, "max": 10, "label": "Decatipo (1-10)", "barlen": 20},
    "Eneatipo": {"min": 1, "max": 9, "label": "Eneatipo (1-9)", "barlen": 20},
    "PD": {"min": 0, "max": 40, "label": "Puntuación Directa", "barlen": 20},
}

def ascii_bar(value, escala):
    minv = ESCALAS[escala]["min"]
    maxv = ESCALAS[escala]["max"]
    barlen = ESCALAS[escala]["barlen"]
    value = max(minv, min(value, maxv))
    filled = int((value - minv) / (maxv - minv) * barlen)
    bar = "█" * filled + "." * (barlen - filled)
    return f"|{bar}|"

def find_pruebas_en_texto(text, pruebas):
    found = set()
    for prueba in pruebas:
        pattern = r"\b{}\b".format(re.escape(prueba))
        if re.search(pattern, text, re.IGNORECASE):
            found.add(prueba)
    return found

def extract_puntuaciones(text, pruebas):
    resultados = []
    pruebas_encontradas = find_pruebas_en_texto(text, pruebas)
    for prueba in pruebas_encontradas:
        for escala in ESCALAS:
            regex = rf"{prueba}.*?{escala}\s*[:\-]?\s*(\d+)"
            for match in re.finditer(regex, text, re.IGNORECASE):
                puntuacion = int(match.group(1))
                resultados.append({
                    "nombre": prueba,
                    "escala": escala,
                    "puntuacion": puntuacion
                })
    return resultados, pruebas_encontradas

def generate_ascii_graph(pruebas):
    lines = []
    for prueba in pruebas:
        nombre = prueba["nombre"]
        escala = prueba["escala"]
        puntuacion = prueba["puntuacion"]
        label = ESCALAS[escala]["label"]
        bar = ascii_bar(puntuacion, escala)
        lines.append(f"{nombre:<30} [ {puntuacion:>3} ] {bar} {label}")
    return "\n".join(lines)

def mark_unknown_pruebas(text, unknown_pruebas):
    for prueba in unknown_pruebas:
        pattern = r"({})".format(re.escape(prueba))
        text = re.sub(pattern, r'<span style="color:red; font-weight:bold;">\1</span>', text, flags=re.IGNORECASE)
    return text

def detect_posibles_pruebas(text):
    # Busca patrones de nombres de pruebas tipo "WISC-IV", "RAVEN", etc.
    return set(re.findall(r"\b[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9\- ]{2,}\b", text))

def scraping_and_reprocess(text, pdf_bytes):
    nuevas_pruebas = scrape_psicometricas()
    save_pruebas(nuevas_pruebas)
    pruebas_actualizadas = load_pruebas()
    resultados, pruebas_encontradas = extract_puntuaciones(text, pruebas_actualizadas)
    ascii_graph = generate_ascii_graph(resultados)
    posibles_pruebas = detect_posibles_pruebas(text)
    unknown_pruebas = posibles_pruebas - set(pruebas_actualizadas)
    text_html = mark_unknown_pruebas(text, unknown_pruebas)
    # Aquí podrías guardar el resultado para mostrarlo en la próxima subida
    # o notificar al usuario por websocket/sse
    return {
        "text": text_html,
        "ascii_graph": ascii_graph,
        "pruebas": resultados,
        "unknown_pruebas": list(unknown_pruebas)
    }

@app.post("/ocr")
async def ocr_pdf(file: UploadFile = File(...)):
    pruebas = load_pruebas()
    pdf_bytes = await file.read()
    with tempfile.TemporaryDirectory() as tmpdir:
        images = convert_from_bytes(pdf_bytes, output_folder=tmpdir)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    resultados, pruebas_encontradas = extract_puntuaciones(text, pruebas)
    posibles_pruebas = detect_posibles_pruebas(text)
    unknown_pruebas = posibles_pruebas - set(pruebas)
    ascii_graph = generate_ascii_graph(resultados)
    text_html = mark_unknown_pruebas(text, unknown_pruebas)
    # Si hay pruebas desconocidas, activa scraping asíncrono y reprocesa
    if unknown_pruebas:
        def async_scraping():
            scraping_and_reprocess(text, pdf_bytes)
        threading.Thread(target=async_scraping).start()
    return JSONResponse({
        "text": text_html,
        "ascii_graph": ascii_graph,
        "pruebas": resultados,
        "unknown_pruebas": list(unknown_pruebas),
        "reproceso_pendiente": bool(unknown_pruebas)
    })

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")
