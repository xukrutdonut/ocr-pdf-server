# Puntuación Estandarizada (PE) - Documentación

## Descripción

La Puntuación Estandarizada (PE) es un tipo de puntuación utilizado en evaluaciones psicométricas que tiene las siguientes características:

- **Rango**: 1 a 19
- **Media (M)**: 10
- **Desviación Estándar (SD)**: 3

## Uso en Pruebas Psicométricas

Las PE son comúnmente utilizadas en:
- WISC-V (Wechsler Intelligence Scale for Children - Fifth Edition)
- WAIS-IV (Wechsler Adult Intelligence Scale - Fourth Edition)
- Otras escalas Wechsler

Se utilizan para reportar puntuaciones de subpruebas individuales, mientras que el CI Total usa una escala diferente (media 100, SD 15).

## Interpretación

| PE Score | Percentil Aprox. | Clasificación |
|----------|------------------|---------------|
| 1-3      | < 2              | Muy bajo |
| 4-5      | 2-9              | Bajo |
| 6-7      | 9-25             | Bajo promedio |
| 8-12     | 25-75            | Promedio |
| 13-14    | 75-91            | Alto promedio |
| 15-16    | 91-98            | Alto |
| 17-19    | > 98             | Muy alto |

## Implementación en OCR PDF Server

### Detección Automática

El sistema detecta PE scores mediante:

1. **Palabras clave en la etiqueta**:
   - "PE"
   - "pe"
   - "Puntuación Estandarizada"
   - "Puntuacion Estandarizada"

2. **Rango de valores**:
   - Valores entre 1 y 19
   - Presencia de valores cercanos a la media (7-13)

### Normalización

Para graficar las PE junto con otros tipos de puntuaciones, se normalizan al rango 0-1:

```python
normalized = (score - 1) / 18
```

Esto permite:
- PE = 1  → 0.0 (0%)
- PE = 10 → 0.5 (50%) [media]
- PE = 19 → 1.0 (100%)

### Ejemplos de Detección

```python
# Estos textos serán detectados como PE:
"PE Comprensión Verbal: 12"
"pe visoespacial: 14"
"Puntuación Estandarizada Memoria: 11"
```

### Visualización

Las PE scores se grafican en un gráfico ASCII normalizado junto con otros tipos de puntuaciones:

```
============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: PUNTUACION_ESTANDARIZADA
============================================================

PE Comprensión Verbal (  12.0): ████████████████████████    61.1%
      PE Visoespacial (  14.0): ████████████████████████████ 72.2%
 PE Razonamiento Fluido (  11.0): ██████████████████████     55.6%

============================================================
```

## Uso en el Editor de Base de Datos

El editor de base de datos permite:

1. **Ver patrones PE aprendidos**: Filtrar y visualizar patrones de PE scores
2. **Editar configuración**: Ajustar rangos de confianza para detección de PE
3. **Agregar nuevas abreviaturas**: Enseñar al sistema nuevas formas de detectar PE scores

### Acceso

1. Ir a la página principal del OCR PDF Server
2. Hacer clic en el botón "🗄️ Editor de Base de Datos"
3. Navegar a la pestaña "Patrones" para ver/editar PE scores

## Ejemplos de Uso

### Ejemplo 1: Informe WISC-V

```
WISC-V Resultados:
CI Total: 115
PE Comprensión Verbal: 12
PE Visoespacial: 14
PE Razonamiento Fluido: 11
```

Detección esperada:
- CI Total → wechsler
- PE Comprensión Verbal → puntuacion_estandarizada
- PE Visoespacial → puntuacion_estandarizada
- PE Razonamiento Fluido → puntuacion_estandarizada

### Ejemplo 2: Uso de Abreviaturas

```
Resultados:
CV (PE): 12
VS (PE): 14
RF (PE): 11
```

Para que el sistema detecte correctamente, se puede agregar una anotación indicando que "PE" es una abreviatura de "Puntuación Estandarizada".

## Referencias

- Wechsler, D. (2014). WISC-V Technical and Interpretive Manual. Bloomington, MN: Pearson.
- Wechsler, D. (2008). WAIS-IV Technical and Interpretive Manual. San Antonio, TX: Pearson.
