"""
Database module for storing learned score patterns
"""
import sqlite3
import json
from typing import List, Dict, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "score_patterns.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create patterns table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abbreviation TEXT NOT NULL,
            full_context TEXT,
            score_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        )
    """)
    
    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score_value REAL NOT NULL,
            label TEXT NOT NULL,
            detected_type TEXT,
            correct_type TEXT,
            is_correct BOOLEAN,
            text_context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def add_pattern(abbreviation: str, score_type: str, full_context: str = None) -> int:
    """Add a new score pattern to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if pattern already exists
    cursor.execute("""
        SELECT id FROM score_patterns 
        WHERE LOWER(abbreviation) = LOWER(?) AND score_type = ?
    """, (abbreviation, score_type))
    
    existing = cursor.fetchone()
    if existing:
        # Update usage count
        cursor.execute("""
            UPDATE score_patterns 
            SET usage_count = usage_count + 1 
            WHERE id = ?
        """, (existing[0],))
        conn.commit()
        conn.close()
        return existing[0]
    
    # Insert new pattern
    cursor.execute("""
        INSERT INTO score_patterns (abbreviation, full_context, score_type, usage_count)
        VALUES (?, ?, ?, 1)
    """, (abbreviation, full_context, score_type))
    
    pattern_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pattern_id

def get_all_patterns() -> List[Dict]:
    """Get all learned patterns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, abbreviation, full_context, score_type, usage_count, created_at
        FROM score_patterns
        ORDER BY usage_count DESC
    """)
    
    patterns = []
    for row in cursor.fetchall():
        patterns.append({
            "id": row[0],
            "abbreviation": row[1],
            "full_context": row[2],
            "score_type": row[3],
            "usage_count": row[4],
            "created_at": row[5]
        })
    
    conn.close()
    return patterns

def add_feedback(score_value: float, label: str, detected_type: Optional[str], 
                 correct_type: str, is_correct: bool, text_context: str = None) -> int:
    """Add feedback about score detection"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO score_feedback 
        (score_value, label, detected_type, correct_type, is_correct, text_context)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (score_value, label, detected_type, correct_type, is_correct, text_context))
    
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id

def get_patterns_for_detection() -> Dict[str, List[str]]:
    """Get patterns organized by score type for detection"""
    patterns = get_all_patterns()
    
    patterns_by_type = {}
    for pattern in patterns:
        score_type = pattern['score_type']
        if score_type not in patterns_by_type:
            patterns_by_type[score_type] = []
        
        patterns_by_type[score_type].append(pattern['abbreviation'].lower())
    
    return patterns_by_type

def delete_pattern(pattern_id: int) -> bool:
    """Delete a pattern by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM score_patterns WHERE id = ?", (pattern_id,))
    affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    return affected > 0

# Initialize database on module import
init_db()
