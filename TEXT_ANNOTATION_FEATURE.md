# Text Selection and Annotation Feature

## Overview

This feature allows users to select text from OCR results and add annotations, notes, and corrections. It enhances the system's learning capabilities by allowing users to teach it new abbreviations and correct misidentified score types.

## Features

### 1. Text Selection
- Users can select any portion of the extracted OCR text using their cursor
- Selected text is highlighted with a custom purple selection style
- Selection works only within the OCR result area

### 2. Floating Annotation Button
- When text is selected, a floating 📌 button appears in the bottom-right corner
- Button includes a tooltip: "Selecciona texto y haz clic aquí para añadir una anotación"
- Clicking the button opens the annotation modal

### 3. Annotation Modal
The modal includes:
- **Selected Text Display**: Shows the text that was selected
- **Note/Comment Field**: Free-text area for user observations
- **Score Type Dropdown** (optional): Allows correction of misidentified score types
  - Percentil (0-100)
  - Eneatipo (1-9)
  - Decatipo (1-10)
  - Wechsler/CI (40-160)
  - Puntuación T (20-80)
  - Puntuación Z (-4 a +4)
- **Abbreviation Field** (optional): For teaching the system new abbreviations

### 4. Automatic Pattern Learning
- When both abbreviation and score type are provided, the system automatically creates a new pattern
- Patterns from annotations are marked with `from_annotation: true`
- These patterns are used in future score detection
- Patterns are displayed in learning statistics with a 📝 icon

## Use Cases

### Case 1: Adding a Comment
```
Selected Text: "El paciente muestra un desempeño dentro del rango promedio-alto"
Note: "Importante: considerar contexto socioeconómico"
Score Type: (none)
Abbreviation: (none)
```
Result: Annotation saved for future reference

### Case 2: Teaching a New Abbreviation
```
Selected Text: "PT Atención: 65"
Note: "Esta es una puntuación T que indica nivel de atención"
Score Type: "Puntuación T (20-80)"
Abbreviation: "PT"
```
Result: 
- Annotation saved
- New pattern created: "PT" → "puntuacion_t"
- Future PDFs with "PT" will be correctly identified

### Case 3: Correcting a Misidentification
```
Selected Text: "PC: 85"
Note: "El sistema identificó esto como percentil, pero es correcto"
Score Type: "Percentil (0-100)"
Abbreviation: "PC"
```
Result:
- Annotation saved
- Pattern reinforced or created for "PC" → "percentil"

## Technical Implementation

### Backend (`app/main.py`)

#### New Endpoint: `/save-annotation`
```python
@app.post("/save-annotation")
async def save_annotation(
    selected_text: str = Body(...),
    note: str = Body(...),
    score_type: Optional[str] = Body(None),
    abbreviation: Optional[str] = Body(None)
)
```

**Functionality:**
1. Validates input (note is required)
2. Creates annotation entry with timestamp
3. If abbreviation + score_type provided:
   - Checks for existing pattern
   - Updates existing pattern (increments confidence) OR
   - Creates new pattern with initial confidence of 1
4. Extracts numeric score from selected text if available
5. Saves to `learning_data.json`

**Response:**
```json
{
  "success": true,
  "message": "Anotación guardada exitosamente",
  "annotation_saved": true,
  "pattern_added": true
}
```

#### Updated Endpoint: `/learning-stats`
Now includes:
```json
{
  "total_annotations": 5,
  ...
}
```

### Frontend (`frontend/index.html`)

#### CSS Classes
- `.result-content`: Now includes `user-select: text` for text selection
- `.result-content::selection`: Purple highlight for selected text
- `.annotation-modal`: Overlay modal with backdrop
- `.annotation-modal-content`: Modal dialog box
- `.annotation-floating-btn`: Floating button that appears on selection

#### JavaScript Functions

**Text Selection Detection:**
```javascript
function handleTextSelection() {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  
  if (text && text.length > 0) {
    // Check if selection is within result-content
    const resultContent = document.querySelector('.result-content');
    if (resultContent && resultContent.contains(selection.anchorNode)) {
      selectedText = text;
      annotationFloatingBtn.classList.add('show');
    }
  }
}
```

**Opening Modal:**
```javascript
function openAnnotationModal(text) {
  document.getElementById('selected-text-display').textContent = text;
  annotationModal.classList.add('show');
  // Focus on note field
  document.getElementById('annotation-note').focus();
}
```

**Saving Annotation:**
```javascript
async function saveAnnotation() {
  const note = document.getElementById('annotation-note').value.trim();
  const scoreType = document.getElementById('annotation-score-type').value;
  const abbreviation = document.getElementById('annotation-abbreviation').value.trim();
  
  // Validation
  if (!note) {
    alert('Por favor, escribe una nota o comentario.');
    return;
  }
  
  if (abbreviation && !scoreType) {
    alert('Por favor, selecciona un tipo de puntuación si especificas una abreviatura.');
    return;
  }
  
  // Send to backend
  const res = await fetch('/save-annotation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_text: selectedText,
      note: note,
      score_type: scoreType || null,
      abbreviation: abbreviation || null
    })
  });
  
  // Handle response and reload stats
  await loadLearningStats();
}
```

## Data Storage

Annotations are stored in `learning_data.json`:

```json
{
  "annotations": [
    {
      "timestamp": "2025-09-30T20:53:07.441238",
      "selected_text": "PT Atención: 65",
      "note": "Esta es una puntuación T que indica nivel de atención",
      "score_type": "puntuacion_t",
      "abbreviation": "PT"
    }
  ],
  "patterns": [
    {
      "label": "PT",
      "score_type": "puntuacion_t",
      "confidence": 1,
      "score_min": 65.0,
      "score_max": 65.0,
      "created": "2025-09-30T20:53:07.441355",
      "last_updated": "2025-09-30T20:53:07.441359",
      "from_annotation": true
    }
  ],
  "feedback_history": []
}
```

## User Interface Flow

1. **Upload PDF** → OCR extracts text
2. **View Results** → Text displayed in `.result-content`
3. **Select Text** → User drags cursor to select text
4. **Floating Button Appears** → 📌 button shows in bottom-right
5. **Click Button** → Annotation modal opens
6. **Fill Form:**
   - Type note/comment (required)
   - Select score type (optional)
   - Enter abbreviation (optional)
7. **Click "Guardar"** → Annotation saved
8. **Success Message** → "Anotación guardada exitosamente"
9. **Modal Closes** → Learning stats updated
10. **Pattern Created** → System learns from annotation

## Screenshots

### Annotation Modal
![Annotation Modal](https://github.com/user-attachments/assets/c740afc0-6ecf-452b-af25-eb5609b35279)

The modal shows:
- Selected text highlighted in a bordered box
- Note/comment text area with sample text
- Score type dropdown with "Puntuación T (20-80)" selected
- Abbreviation field with "PT" entered
- Cancel and Save buttons

## Benefits

1. **User Control**: Users can add context and notes to OCR results
2. **System Learning**: Teaching new abbreviations improves future detections
3. **Error Correction**: Misidentified scores can be corrected
4. **Knowledge Base**: Annotations create a searchable knowledge base
5. **Progressive Improvement**: System gets smarter with each annotation

## Integration with Existing Features

### Works With:
- ✅ OCR text extraction
- ✅ Score detection system
- ✅ Progressive learning system
- ✅ Feedback mechanism
- ✅ Learning statistics

### Enhances:
- Pattern recognition accuracy
- Abbreviation detection
- User engagement
- System intelligence

## Future Enhancements

Potential improvements:
- Search through annotations
- Export annotations to PDF/CSV
- Annotation history view
- Edit/delete existing annotations
- Annotation categories/tags
- Multi-user annotation support
- Annotation approval workflow
- AI-powered suggestion of score types based on context

## Maintenance Notes

- Annotations are stored persistently in `learning_data.json`
- Large annotation files should be periodically archived
- Consider adding pagination for annotations view
- Monitor file size and implement rotation if needed
- Patterns from annotations are prioritized in classification logic
