# Puntuación Escalar (PE) y Editor de Base de Datos

## Resumen

Este documento describe las nuevas funcionalidades añadidas al OCR PDF Server:

1. **Soporte para Puntuación Escalar (PE)** - Sistema de puntuación con media 10 y desviación estándar 3
2. **Campo de Nombre de Test** - Para proporcionar contexto sobre el test psicométrico utilizado
3. **Editor de Base de Datos** - Interfaz web completa para gestionar datos de aprendizaje

## 1. Puntuación Escalar (PE)

### ¿Qué es la Puntuación Escalar?

La puntuación escalar es un tipo de puntuación estandarizada comúnmente utilizada en tests psicométricos como:
- WISC-V (Escala de Inteligencia de Wechsler para Niños)
- WAIS-IV (Escala de Inteligencia de Wechsler para Adultos)
- NEPSY-II (Evaluación Neuropsicológica del Desarrollo)

**Características:**
- **Rango:** 1-19 (valores enteros)
- **Media:** 10
- **Desviación Estándar:** 3
- **Interpretación:**
  - 7-13: Rango promedio (±1 DE)
  - 4-6 o 14-16: Por debajo/encima del promedio (±2 DE)
  - 1-3 o 17-19: Muy por debajo/muy por encima del promedio (±3 DE)

### Detección Automática

El sistema detecta puntuaciones escalares mediante:

1. **Detección por etiqueta:**
   - "PE", "pe"
   - "Puntuación Escalar", "Puntaje Escalar"
   - "Escalar"

2. **Detección por valor:**
   - Valores entre 1-19 (enteros)
   - Cuando existen múltiples puntuaciones en este rango

### Ejemplo de Uso

```
WISC-V - Comprensión Verbal

PE Semejanzas: 12
PE Vocabulario: 10  
PE Información: 8
```

El sistema detectará automáticamente:
- Tipo: `puntuacion_escalar`
- Normalización: 12 → 61.1%, 10 → 50%, 8 → 38.9%

### Normalización

Fórmula: `(score - 1) / 18`

Ejemplos:
- PE = 1 → 0% (mínimo)
- PE = 10 → 50% (promedio)
- PE = 19 → 100% (máximo)

## 2. Campo de Nombre de Test

### Propósito

El campo `test_name` permite especificar qué test psicométrico se está evaluando, proporcionando contexto valioso para:

- **Futuras interpretaciones:** El sistema puede aprender qué tipos de puntuaciones usar cada test
- **Organización:** Facilita filtrar y buscar anotaciones por test
- **Documentación:** Mantiene un registro claro de qué test generó cada puntuación

### Uso en Anotaciones

Al crear una anotación, ahora puedes especificar:

```json
{
  "selected_text": "PE Verbal: 12",
  "note": "Puntuación escalar de comprensión verbal",
  "score_type": "puntuacion_escalar",
  "abbreviation": "PE",
  "test_name": "WISC-V"
}
```

### Tests Comunes

Ejemplos de nombres de tests que puedes usar:

**Tests de Inteligencia:**
- WISC-V (niños 6-16 años)
- WAIS-IV (adultos)
- Stanford-Binet V

**Tests Neuropsicológicos:**
- NEPSY-II
- RIST (Test de Inteligencia Breve de Reynolds)
- BRIEF (Evaluación de Función Ejecutiva)

**Tests de Personalidad:**
- MMPI-2
- 16PF
- NEO-PI-R

**Tests de Atención:**
- CPT-3 (Test de Rendimiento Continuo)
- TOVA (Test de Variables de Atención)

## 3. Editor de Base de Datos

### Acceso

El editor está disponible en: `http://localhost:8000/editor`

También hay un botón en la esquina superior derecha de la página principal: **"🗄️ Editor de Base de Datos"**

### Funcionalidades

#### Dashboard de Estadísticas

Muestra en tiempo real:
- **Patrones aprendidos:** Número de abreviaturas y tipos de puntuación registrados
- **Anotaciones guardadas:** Total de anotaciones con contexto
- **Retroalimentación recibida:** Cantidad de correcciones hechas por usuarios

#### Pestañas de Datos

**1. Patrones**
- Lista de todas las abreviaturas aprendidas
- Muestra: etiqueta, tipo de puntuación, confianza, rango de valores
- Indica patrones creados desde anotaciones con 🏷️
- Permite editar y eliminar patrones

**2. Anotaciones**
- Lista completa de anotaciones guardadas
- Muestra: fecha, texto seleccionado, nota, tipo, abreviatura, **nombre del test**
- Permite ver, editar y eliminar anotaciones
- Campo test_name visible y editable

**3. Retroalimentación**
- Historial de correcciones de clasificación
- Muestra: fecha, etiqueta, puntuación, tipo detectado, si fue correcto
- Permite eliminar entradas incorrectas

#### Operaciones CRUD

**Ver (Read):**
- Visualización en tablas organizadas
- Información completa de cada entrada

**Editar (Update):**
- Modal con formulario pre-rellenado
- Validación de campos
- Confirmación de cambios

**Eliminar (Delete):**
- Botón de eliminar en cada fila
- Confirmación antes de borrar
- Notificación de éxito

**Crear (Create):**
- Se realiza desde la página principal mediante anotaciones
- Los patrones se crean automáticamente al guardar anotaciones con abreviatura

### Casos de Uso

#### 1. Corregir Patrón Erróneo

Si el sistema aprendió incorrectamente que "PT" es "Puntuación T" cuando debería ser "Percentil Total":

1. Ir al editor (`/editor`)
2. Pestaña "Patrones"
3. Buscar el patrón "PT"
4. Clic en ✏️ (editar)
5. Cambiar `score_type` de `puntuacion_t` a `percentil`
6. Guardar

#### 2. Eliminar Anotación Duplicada

Si accidentalmente guardaste la misma anotación dos veces:

1. Ir al editor (`/editor`)
2. Pestaña "Anotaciones"
3. Identificar la anotación duplicada
4. Clic en 🗑️ (eliminar)
5. Confirmar eliminación

#### 3. Añadir Contexto a Anotación Existente

Si olvidaste especificar el nombre del test en una anotación:

1. Ir al editor (`/editor`)
2. Pestaña "Anotaciones"
3. Buscar la anotación
4. Clic en ✏️ (editar)
5. Llenar campo "Nombre del Test" con "WISC-V" (o el test correspondiente)
6. Guardar

#### 4. Revisar Aprendizaje del Sistema

Para ver qué ha aprendido el sistema:

1. Ir al editor (`/editor`)
2. Ver estadísticas en el dashboard
3. Revisar pestaña "Patrones" para ver abreviaturas aprendidas
4. Revisar pestaña "Retroalimentación" para ver correcciones

## Endpoints de API

### GET /learning-data

Obtiene todos los datos de aprendizaje.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "label": "PE",
        "score_type": "puntuacion_escalar",
        "confidence": 1,
        "score_min": 8.0,
        "score_max": 15.0,
        "created": "2025-10-01T10:54:52.963727",
        "last_updated": "2025-10-01T10:54:52.963731",
        "from_annotation": true
      }
    ],
    "annotations": [
      {
        "timestamp": "2025-10-01T10:54:52.963566",
        "selected_text": "PE Verbal: 12",
        "note": "Puntuación escalar del WISC-V",
        "score_type": "puntuacion_escalar",
        "abbreviation": "PE",
        "test_name": "WISC-V"
      }
    ],
    "feedback_history": []
  }
}
```

### PUT /learning-data

Actualiza los datos de aprendizaje completos.

**Body:**
```json
{
  "patterns": [...],
  "annotations": [...],
  "feedback_history": [...]
}
```

### DELETE /learning-data/{data_type}/{index}

Elimina un elemento específico.

**Parámetros:**
- `data_type`: "patterns", "annotations", o "feedback_history"
- `index`: Índice del elemento (empezando en 0)

**Ejemplo:**
```bash
DELETE /learning-data/annotations/0
```

## Flujo de Trabajo Recomendado

### Primer Uso

1. **Subir PDF con resultados de test**
   - Arrastra tu archivo PDF al OCR
   - Espera la extracción de texto

2. **Revisar puntuaciones detectadas**
   - El sistema detectará automáticamente PE y otras puntuaciones
   - Verifica que los tipos sean correctos

3. **Anotar con contexto**
   - Selecciona texto con puntuaciones
   - Añade nota explicativa
   - **Especifica el nombre del test** (ej: "WISC-V")
   - Si hay abreviaturas nuevas, añádelas

4. **Verificar en editor**
   - Ve al editor (`/editor`)
   - Revisa que todo se guardó correctamente
   - Corrige cualquier error

### Uso Continuo

1. **El sistema mejora automáticamente**
   - Los patrones aprendidos se aplican en futuros análisis
   - Las anotaciones con test_name ayudan a interpretar contexto

2. **Corrección de errores**
   - Marca puntuaciones incorrectas con ❌
   - Especifica el tipo correcto
   - El sistema aprende de tus correcciones

3. **Mantenimiento periódico**
   - Revisa el editor mensualmente
   - Elimina patrones obsoletos
   - Actualiza anotaciones con mejor información

## Preguntas Frecuentes

### ¿Cómo sabe el sistema que una puntuación es PE?

1. **Por etiqueta:** Si el texto contiene "PE", "Puntuación Escalar", etc.
2. **Por valor:** Si hay múltiples valores entre 1-19
3. **Por patrones aprendidos:** Si previamente anotaste similar puntuación

### ¿Debo especificar siempre el nombre del test?

No es obligatorio, pero es muy recomendable porque:
- Proporciona contexto para futuras interpretaciones
- Ayuda a organizar y filtrar datos
- Mejora la documentación de resultados

### ¿Puedo editar datos directamente en learning_data.json?

Sí, pero **no se recomienda** porque:
- Riesgo de formato JSON inválido
- No hay validación de datos
- Puede causar errores en la aplicación

Es mejor usar el **Editor de Base de Datos** que tiene:
- Validación automática
- Interfaz amigable
- Confirmación de cambios

### ¿Qué pasa si elimino algo por error?

Los datos se guardan en `learning_data.json`. Puedes:
1. Hacer backup manual del archivo antes de cambios importantes
2. Usar control de versiones (Git) si trabajas en equipo
3. El archivo se puede restaurar desde backup

### ¿El editor funciona con múltiples usuarios?

El `learning_data.json` es un archivo compartido, por lo que:
- Múltiples usuarios ven los mismos datos
- Los cambios son inmediatos para todos
- **Precaución:** No hay bloqueo concurrente, evita ediciones simultáneas

## Mejores Prácticas

### 1. Nomenclatura Consistente de Tests

Usa siempre el mismo nombre para cada test:
- ✅ Correcto: "WISC-V"
- ❌ Evitar: "wisc v", "WISC 5", "Wisc-V"

### 2. Anotaciones Descriptivas

Las notas deben ser claras y concisas:
- ✅ Bueno: "PE de comprensión verbal, indica nivel promedio"
- ❌ Evitar: "bien", "ok", "normal"

### 3. Especificar Abreviaturas Nuevas

Cuando encuentres una abreviatura nueva:
1. Añádela en el campo "Abreviatura"
2. Especifica su tipo de puntuación
3. El sistema la recordará para futuros usos

### 4. Revisión Periódica

Revisa el editor regularmente:
- Verifica que los patrones aprendidos sean correctos
- Elimina duplicados o errores
- Actualiza anotaciones con mejor información

### 5. Backup de Datos

Haz backup de `learning_data.json`:
```bash
cp learning_data.json learning_data_backup_$(date +%Y%m%d).json
```

## Soporte Técnico

Si encuentras problemas:

1. **Verifica el formato JSON:**
   ```bash
   python3 -m json.tool learning_data.json
   ```

2. **Revisa los logs del servidor:**
   - Errores de validación
   - Problemas de formato

3. **Restaura desde backup si es necesario:**
   ```bash
   cp learning_data_backup.json learning_data.json
   ```

4. **Reinicia el servidor después de cambios manuales:**
   ```bash
   # Detén el servidor
   # Inicia nuevamente
   uvicorn app.main:app --reload
   ```

## Conclusión

Las nuevas funcionalidades añaden:
- **Soporte completo para PE:** Detección, normalización y visualización
- **Contexto con test_name:** Mejor documentación y organización
- **Editor robusto:** Gestión completa de datos de aprendizaje

Estas herramientas permiten un flujo de trabajo más profesional y organizado en el análisis de resultados psicométricos.
