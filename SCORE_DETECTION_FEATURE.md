# Score Detection Feature Documentation

## Overview

This document describes the psychometric score detection and visualization feature implemented in the OCR PDF Server.

## Problem Statement

The goal was to implement a system that:
1. Identifies numeric scores (puntuaciones/dígitos) in OCR-extracted text
2. Highlights these scores in red color in the UI
3. Generates ASCII bar charts showing normalized score values
4. Supports multiple psychometric scale types

## Implementation

### Backend (`app/main.py`)

#### Core Functions

1. **`classify_individual_score(score: float, label: str)`**
   - Classifies a single score based on its value and label
   - First tries keyword matching in labels (e.g., "CI", "Percentil", "T-Score")
   - Falls back to value-based classification
   - Returns: score type string or None

2. **`detect_score_type(scores: List[float], labels: List[str])`**
   - Detects dominant score type from a list of scores
   - Used for backward compatibility
   - Returns: most common score type

3. **`normalize_score(score: float, score_type: str)`**
   - Normalizes a score to 0-1 range based on its type
   - Each score type has specific normalization formula
   - Returns: float between 0 and 1

4. **`generate_ascii_chart(scores: List[Tuple], score_type: str)`**
   - Creates ASCII bar chart for a set of scores
   - Bars are 40 characters maximum width
   - Shows percentage based on normalized value
   - Returns: formatted string with chart

5. **`extract_scores_from_text(text: str)`**
   - Main extraction function
   - Uses regex patterns to find label-value pairs
   - Groups scores by type
   - Generates charts for each type
   - Returns: dict with scores, score_type, and ascii_chart

#### API Changes

**Two-Stage Architecture:**

1. **`/ocr` endpoint** - Returns only OCR text:
```json
{
  "text": "...",
  "success": true
}
```

2. **`/analyze-scores` endpoint** - Analyzes text for scores on demand:
```json
{
  "success": true,
  "scores": [[score, label, type], ...],
  "score_type": "wechsler" or "mixed",
  "ascii_chart": "ASCII visualization..."
}
```

### Frontend (`frontend/index.html`)

#### UI Changes

1. **Two-Stage Workflow**
   - OCR text is displayed first without score analysis
   - "Detectar Puntuaciones y Graficar" button appears below OCR text
   - Button triggers score analysis as a separate step
   - Score analysis results appear in a new card below

2. **Score Analysis Section**
   - Separate card with "Análisis de Puntuaciones" header
   - Lists all detected scores with their labels and types
   - Displays ASCII charts below the score list
   - Only visible after clicking the analysis button

3. **Visual Styling**
   - `.score-highlight` CSS class with red text and light red background
   - `.ascii-chart` CSS class with terminal-style appearance
   - Dark background (#2d2d2d) with green text (#00ff00)
   - Monospace font for proper alignment

#### Code Example

```javascript
// Button click triggers score analysis
analyzeButton.addEventListener('click', async () => {
  const res = await fetch('/analyze-scores', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: currentText })
  });
  const data = await res.json();
  showScoreAnalysis(data);
});
```

## Supported Score Types

### 1. Percentiles (0-100)
- **Range**: 0-100
- **Normalization**: score / 100
- **Keywords**: "percentil", "percentile", **"PC"**, **"p"**, **"P"** (abbreviations)
- **Use case**: Educational assessments, standardized tests

### 2. Eneatipos (1-9)
- **Range**: 1-9 (integers only)
- **Normalization**: (score - 1) / 8
- **Keywords**: "eneatipo", "eneagrama"
- **Use case**: Nine-point attention and cognitive scales

### 3. Decatipos (1-10)
- **Range**: 1-10 (integers only)
- **Normalization**: (score - 1) / 9
- **Keywords**: "decatipo", "decil"
- **Use case**: Ten-point scales, deciles

### 4. Wechsler/CI Scores (40-160)
- **Range**: 40-160
- **Normalization**: (score - 40) / 120
- **Keywords**: "ci", "coeficiente", "iq", "wechsler"
- **Use case**: Intelligence quotient tests (WISC, WAIS)

### 5. T-Scores (20-80)
- **Range**: 20-80
- **Normalization**: (score - 20) / 60
- **Keywords**: "t-score", "puntuación t", "puntaje t", **"PT"**, **"pt"** (abbreviations)
- **Use case**: Personality assessments, emotional scales

### 6. Z-Scores (-4 to +4)
- **Range**: -4 to +4
- **Normalization**: (score + 3) / 6
- **Keywords**: "z-score", "puntuación z", "puntaje z", **"z"**, **"Z"** (abbreviations)
- **Use case**: Standardized scores, statistical analysis

## Examples

### Example 1: Full Keywords

#### Input Text
```
Resultados Wechsler:
CI Total: 110
Comprensión Verbal: 115

Percentiles:
Percentil General: 75
Percentil Verbal: 84
```

#### Output
```
============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: WECHSLER
============================================================

               CI Total ( 110.0): ███████████████████████                   58.3%
     Comprensión Verbal ( 115.0): █████████████████████████                 62.5%

============================================================


============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: PERCENTIL
============================================================

   Percentil General (  75.0): ██████████████████████████████            75.0%
    Percentil Verbal (  84.0): █████████████████████████████████         84.0%

============================================================
```

### Example 2: Using Abbreviations (NEW)

#### Input Text
```
Puntuaciones Estandarizadas:
Z: 1.5
PT: 65
PC: 85
CI Total: 110
```

#### Output
```
============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: PUNTUACION_Z
============================================================

Z (   1.5): ██████████████████████████████            75.0%

============================================================


============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: PUNTUACION_T
============================================================

PT (  65.0): ██████████████████████████████            75.0%

============================================================


============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: PERCENTIL
============================================================

PC (  85.0): ██████████████████████████████████        85.0%

============================================================


============================================================
GRÁFICA DE PUNTUACIONES NORMALIZADAS
Tipo de puntuación detectado: WECHSLER
============================================================

CI Total ( 110.0): ███████████████████████                   58.3%

============================================================
```

## Testing

### Unit Tests
- Individual score classification tested for all types
- Normalization formulas verified
- Chart generation validated

### Integration Tests
- Complete text extraction with mixed score types
- API endpoint tested with real PDF
- Frontend highlighting verified visually

### Edge Cases Handled
- OCR errors in text (e.g., "Cl" instead of "CI")
- Mixed score types in same document
- Missing or incomplete labels
- Values outside expected ranges
- Special characters in labels (accents, etc.)

## Performance Considerations

- Regex patterns optimized for common score formats
- Score classification uses early returns for efficiency
- Chart generation is lightweight (string concatenation)
- Frontend highlighting uses efficient DOM manipulation

## Future Enhancements

Potential improvements:
- Support for more score types (stanines, scaled scores)
- Customizable chart width and style
- Export charts as images
- Interactive score visualization
- Confidence scores for classification
- Multi-language label support

## Maintenance Notes

When adding new score types:
1. Add classification logic to `classify_individual_score()`
2. Add normalization formula to `normalize_score()`
3. Update documentation and tests
4. Consider keyword variations for label matching
