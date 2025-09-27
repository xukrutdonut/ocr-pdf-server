import re
import json
import os
import requests
from bs4 import BeautifulSoup
from .psico_test_patterns import PSICOMETRIC_TESTS

# Patrones para puntuaciones tipificadas (CI, percentil, compuesta, verbal, manip, etc)
TIPIFICADAS_PATTERNS = [
    r"\bCI\s*[:=]\s*(\d+)",
    r"\bPercentil\s*[:=]\s*(\d+)",
    r"P\.?\s?compuesta\s?=\s?(\d+)",
    r"PC\s*[:=]\s*([\d\.,]+)",
    r"Clasificaci[oó]n\s+(\w+)",
    r"Verbal\s*[:=]\s*(\d+)",
    r"Manipulativa\s*[:=]\s*(\d+)",
    r"Velocidad.*procesamiento\s*[:=]\s*(\d+)",
    r"PPL\s*[:=]\s*(\d+)",
    r"Total\s*[:=]\s*([\d\.,]+)",
    r"Inatenc[ií]on\s*[:=]\s*([\d\.,]+)",
    r"Hiperactividad\s*[:=]\s*([\d\.,]+)",
    # Añade más patrones según tus necesidades
]

def buscar_pruebas(texto):
    """
    Busca pruebas psicométricas en el texto y extrae sus datos relevantes.
    Retorna una lista de dicts con nombre, variante detectada y resultados.
    """
    resultados = []
    for nombre, patrones in PSICOMETRIC_TESTS.items():
        for patron in patrones:
            if re.search(patron, texto, re.IGNORECASE):
                # Extrae resultados si hay patrones
                datos = []
                for patt in TIPIFICADAS_PATTERNS:
                    datos += re.findall(patt, texto, re.IGNORECASE)
                resultados.append({
                    "prueba": nombre,
                    "patron_detectado": patron,
                    "resultados": datos
                })
                break  # Solo la primera coincidencia
    return resultados

def buscar_tipificadas(texto):
    """
    Busca puntuaciones tipificadas no asociadas a un test reconocido.
    """
    resultados = []
    for patt in TIPIFICADAS_PATTERNS:
        resultados += re.findall(patt, texto, re.IGNORECASE)
    return resultados

def interpretar_resultados(texto):
    """
    Devuelve una interpretación estructurada de las pruebas psicométricas y puntuaciones tipificadas encontradas en el texto.
    """
    pruebas = buscar_pruebas(texto)
    tipificadas = buscar_tipificadas(texto)

    # Filtra puntuaciones tipificadas que ya están incluidas en pruebas reconocidas
    tipificadas_sin_prueba = []
    for punto in tipificadas:
        if not any(punto in p["resultados"] for p in pruebas):
            tipificadas_sin_prueba.append(punto)

    return {
        "exito": bool(pruebas or tipificadas_sin_prueba),
        "mensaje": "Pruebas reconocidas y puntuaciones tipificadas encontradas.",
        "pruebas": pruebas,
        "puntuaciones_tipificadas_no_asociadas": tipificadas_sin_prueba
    }

# Ejemplo de uso (para desarrollo):
if __name__ == "__main__":
    with open("informe.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    resultado = interpretar_resultados(texto)
    from pprint import pprint
    pprint(resultado)

# Funciones adicionales requeridas por main.py
def scrape_psicometricas():
    """
    Scrape para obtener nuevas pruebas psicométricas de fuentes en línea
    Por ahora retorna las pruebas ya conocidas
    """
    # En una implementación real, aquí harías scraping de sitios web
    # Por ahora, retornamos las pruebas que ya conocemos
    return list(PSICOMETRIC_TESTS.keys())

def save_pruebas(pruebas):
    """
    Guarda las pruebas en un archivo JSON
    """
    pruebas_file = os.path.join(os.path.dirname(__file__), 'pruebas_psicometricas.json')
    try:
        with open(pruebas_file, 'w', encoding='utf-8') as f:
            json.dump(pruebas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar pruebas: {e}")

def load_pruebas():
    """
    Carga las pruebas desde el archivo JSON o retorna las por defecto
    """
    pruebas_file = os.path.join(os.path.dirname(__file__), 'pruebas_psicometricas.json')
    try:
        if os.path.exists(pruebas_file):
            with open(pruebas_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar pruebas: {e}")
    
    # Si no se puede cargar el archivo, retornar las pruebas por defecto
    return list(PSICOMETRIC_TESTS.keys())
