# Sistema de Aprendizaje Progresivo

## Descripción General

El sistema de aprendizaje progresivo permite que la detección de puntuaciones psicométricas mejore con el tiempo mediante la retroalimentación del usuario. Cada vez que se detectan puntuaciones, el usuario puede indicar si la clasificación fue correcta o incorrecta, y el sistema aprende de esta información.

## Características Principales

### 1. Retroalimentación del Usuario
- **Feedback Positivo (✅)**: Confirma que una puntuación fue detectada y clasificada correctamente
- **Feedback Negativo (❌)**: Indica que la clasificación fue incorrecta y permite especificar el tipo correcto

### 2. Almacenamiento Persistente
- Los datos de aprendizaje se almacenan en `learning_data.json`
- Incluye patrones aprendidos y historial completo de retroalimentación
- El archivo se genera automáticamente en el directorio raíz del proyecto

### 3. Sistema de Confianza
- Cada patrón aprendido tiene un nivel de confianza
- La confianza aumenta con cada confirmación positiva
- Patrones con confianza ≥ 2 se priorizan sobre las reglas predeterminadas

### 4. Estadísticas de Aprendizaje
- Total de retroalimentaciones recibidas
- Ratio de feedback positivo/negativo
- Número de patrones aprendidos
- Lista de patrones más confiables

## Uso del Sistema

### Flujo de Trabajo

1. **Cargar y Procesar PDF**
   - Sube un archivo PDF
   - Haz clic en "Detectar Puntuaciones y Graficar"

2. **Revisar Puntuaciones Detectadas**
   - El sistema muestra todas las puntuaciones encontradas
   - Cada puntuación tiene su tipo detectado (percentil, wechsler, etc.)

3. **Proporcionar Retroalimentación**
   - Haz clic en ✅ si la clasificación es correcta
   - Haz clic en ❌ si la clasificación es incorrecta
   - Si es incorrecta, selecciona el tipo correcto del menú desplegable

4. **Ver Progreso del Aprendizaje**
   - Las estadísticas se actualizan automáticamente
   - Muestra cuánto ha aprendido el sistema

### Ejemplo de Uso

```
Documento procesado contiene:
- "CI Total: 110" → Detectado como wechsler ✅ (correcto)
- "Percentil: 85" → Detectado como puntuacion_t ❌ (incorrecto)
  → Seleccionar tipo correcto: "percentil" → Enviar

Resultado:
- El sistema aprende que "Percentil" con valores 80-90 → percentil
- La próxima vez, detectará correctamente puntuaciones similares
```

## API Endpoints

### POST /feedback
Recibe retroalimentación sobre una clasificación de puntuación.

**Parámetros del cuerpo (JSON):**
```json
{
  "score": 110.0,
  "label": "CI Total",
  "detected_type": "wechsler",
  "is_correct": true,
  "correct_type": null
}
```

O para correcciones:
```json
{
  "score": 85.0,
  "label": "Percentil",
  "detected_type": "puntuacion_t",
  "is_correct": false,
  "correct_type": "percentil"
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Retroalimentación registrada exitosamente"
}
```

### GET /learning-stats
Obtiene estadísticas del sistema de aprendizaje.

**Respuesta:**
```json
{
  "success": true,
  "total_feedback": 25,
  "positive_feedback": 20,
  "negative_feedback": 5,
  "total_patterns": 8,
  "patterns": [
    {
      "label": "CI Total",
      "score_type": "wechsler",
      "confidence": 5,
      "score_min": 100,
      "score_max": 130,
      "created": "2024-01-15T10:30:00",
      "last_updated": "2024-01-20T15:45:00"
    }
  ]
}
```

## Estructura de Datos

### learning_data.json

```json
{
  "patterns": [
    {
      "label": "nombre de la puntuación",
      "score_type": "tipo detectado (percentil, wechsler, etc.)",
      "confidence": 3,
      "score_min": 70,
      "score_max": 95,
      "created": "2024-01-15T10:30:00.123456",
      "last_updated": "2024-01-20T15:45:00.123456"
    }
  ],
  "feedback_history": [
    {
      "timestamp": "2024-01-15T10:30:00.123456",
      "score": 85,
      "label": "Percentil General",
      "detected_type": "percentil",
      "is_correct": true,
      "correct_type": "percentil"
    }
  ]
}
```

## Algoritmo de Aprendizaje

### 1. Clasificación con Patrones Aprendidos

```python
def classify_individual_score(score, label):
    # 1. Primero buscar en patrones aprendidos (confianza >= 2)
    for pattern in learned_patterns:
        if pattern.confidence >= 2:
            if label_matches(pattern.label, label):
                if score_in_range(score, pattern):
                    return pattern.score_type
    
    # 2. Si no hay match, usar reglas predeterminadas
    return default_classification(score, label)
```

### 2. Actualización de Patrones

**Cuando se recibe feedback positivo:**
- Si existe un patrón para esa etiqueta y tipo: incrementar confianza
- Si no existe: crear nuevo patrón con confianza = 1
- Actualizar rango de valores (min/max)

**Cuando se recibe feedback negativo con corrección:**
- Crear o actualizar patrón con el tipo correcto
- Incrementar confianza del patrón correcto

### 3. Priorización de Patrones

Los patrones se priorizan por:
1. **Confianza**: Mayor confianza = mayor prioridad
2. **Especificidad**: Coincidencia exacta de etiqueta
3. **Rango**: Score dentro del rango aprendido

## Tipos de Puntuaciones Soportados

El sistema puede aprender a detectar:

- **Percentiles** (0-100): Evaluaciones educativas
- **Eneatipos** (1-9): Escalas de nueve puntos
- **Decatipos** (1-10): Escalas de diez puntos
- **Wechsler/CI** (40-160): Coeficiente intelectual
- **Puntuación T** (20-80): Escalas de personalidad
- **Puntuación Z** (-4 a +4): Puntuaciones estandarizadas

## Consideraciones de Privacidad

- Los datos de aprendizaje se almacenan **localmente** en el servidor
- No se envía información a servicios externos
- El archivo `learning_data.json` contiene solo:
  - Etiquetas de puntuaciones
  - Valores numéricos
  - Tipos de clasificación
  - Marcas de tiempo
- **No** se almacena contenido del PDF ni información personal

## Mantenimiento

### Reiniciar el Aprendizaje

Para borrar todo el historial de aprendizaje:
```bash
rm learning_data.json
```

El sistema creará un nuevo archivo vacío automáticamente.

### Backup del Aprendizaje

Para preservar el aprendizaje:
```bash
cp learning_data.json learning_data_backup.json
```

### Restaurar desde Backup

```bash
cp learning_data_backup.json learning_data.json
```

### Exportar Patrones

Los patrones se pueden exportar y compartir:
```bash
cat learning_data.json | jq '.patterns' > patterns_export.json
```

## Mejoras Futuras

Posibles mejoras al sistema:

1. **Ajuste de Confianza Negativa**: Reducir confianza cuando hay feedback negativo
2. **Patrones por Contexto**: Diferentes patrones según el tipo de documento
3. **Exportación de Configuración**: Compartir patrones aprendidos entre instalaciones
4. **Interfaz de Administración**: Ver y editar patrones manualmente
5. **Validación Cruzada**: Sugerir cuando hay conflictos de clasificación
6. **Machine Learning**: Usar algoritmos más sofisticados para la clasificación

## Solución de Problemas

### El sistema no aprende

**Problema**: Los patrones no se aplican después de dar feedback.

**Soluciones**:
- Verifica que `learning_data.json` se está creando en el directorio correcto
- Asegúrate de que el proceso tiene permisos de escritura
- Revisa que la confianza del patrón sea ≥ 2

### Clasificaciones inconsistentes

**Problema**: El sistema clasifica la misma etiqueta de forma diferente.

**Soluciones**:
- Da más feedback para aumentar la confianza
- Verifica que las etiquetas sean consistentes (mayúsculas/minúsculas)
- Revisa el rango de valores del patrón

### Archivo learning_data.json corrupto

**Problema**: Error al cargar datos de aprendizaje.

**Solución**:
```bash
# Respaldar el archivo corrupto
mv learning_data.json learning_data_corrupto.json

# El sistema creará uno nuevo
# O restaurar desde backup si existe
cp learning_data_backup.json learning_data.json
```

## Contribuir

Para mejorar el sistema de aprendizaje:

1. Reporta patrones que no se detectan bien
2. Sugiere nuevos tipos de puntuaciones
3. Propón mejoras al algoritmo de aprendizaje
4. Comparte tus patrones aprendidos (sin información sensible)

## Referencias

- [Score Detection Feature](./SCORE_DETECTION_FEATURE.md) - Documentación de detección de puntuaciones
- [README](./README.md) - Documentación general del proyecto
