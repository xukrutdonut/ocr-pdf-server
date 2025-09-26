import re
from app.psico_tests_patterns import PSICOMETRIC_TESTS

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
