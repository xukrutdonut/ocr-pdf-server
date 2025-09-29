import re
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ScoreType(Enum):
    """Types of psychological/educational scores"""
    DECATIPO = "decatipo"  # D1-D10
    ENEATIPO = "eneatipo"  # E1-E9  
    PERCENTIL = "percentil"  # P1-P99
    WECHSLER_CI = "wechsler_ci"  # Wechsler CI scores (typically 40-160)
    T_SCORE = "t_score"  # T scores (typically 20-80, mean=50, sd=10)
    Z_SCORE = "z_score"  # Z scores (typically -3 to +3, mean=0, sd=1)
    DIRECT_SCORE = "direct_score"  # Direct/raw scores (not normalized)


@dataclass
class Score:
    """Represents an identified score from OCR text"""
    value: float
    score_type: ScoreType
    raw_text: str
    context: str = ""
    

class ScoreDetector:
    """Detects and classifies psychological/educational scores in OCR text"""
    
    def __init__(self):
        # Patterns for different score types
        self.patterns = {
            ScoreType.DECATIPO: [
                r'\bD\s*([1-9]|10)\b',
                r'\bdecatipo\s*([1-9]|10)\b',
                r'\bDT\s*([1-9]|10)\b'
            ],
            ScoreType.ENEATIPO: [
                r'\bE\s*([1-9])\b',
                r'\beneatipo\s*([1-9])\b',
                r'\bEN\s*([1-9])\b'
            ],
            ScoreType.PERCENTIL: [
                r'\bP\s*([1-9][0-9]?)\b',
                r'\bpercentil\s*([1-9][0-9]?)\b',
                r'\bPC\s*([1-9][0-9]?)\b',
                r'\b([1-9][0-9]?)(?:\s*percentil|\s*%ile)\b'
            ],
            ScoreType.WECHSLER_CI: [
                r'\bCI\s*([4-9][0-9]|1[0-6][0-9])\b',
                r'\bIQ\s*([4-9][0-9]|1[0-6][0-9])\b',
                r'\bwechsler\s*([4-9][0-9]|1[0-6][0-9])\b',
                r':\s*CI\s*([4-9][0-9]|1[0-6][0-9])\b',
                r'total:\s*([4-9][0-9]|1[0-6][0-9])\b'
            ],
            ScoreType.T_SCORE: [
                r'\bT\s*([2-8][0-9])\b',
                r'\bt-score\s*([2-8][0-9])\b',
                r'\bpuntuación\s+t\s*([2-8][0-9])\b'
            ],
            ScoreType.Z_SCORE: [
                r'\bZ\s*([-+]?[0-3](?:\.[0-9]+)?)\b',
                r'\bz-score\s*([-+]?[0-3](?:\.[0-9]+)?)\b',
                r'\bpuntuación\s+z\s*([-+]?[0-3](?:\.[0-9]+)?)\b'
            ]
        }
        
    def detect_scores(self, text: str) -> List[Score]:
        """Detect all scores in the given text"""
        scores = []
        text_lower = text.lower()
        
        for score_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    try:
                        # Extract the numeric value
                        value_str = match.group(1)
                        value = float(value_str)
                        
                        # Validate score range
                        if self._is_valid_score(value, score_type):
                            score = Score(
                                value=value,
                                score_type=score_type,
                                raw_text=match.group(0),
                                context=self._extract_context(text, match.start(), match.end())
                            )
                            scores.append(score)
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates (same position, different patterns)
        return self._remove_duplicates(scores)
    
    def _is_valid_score(self, value: float, score_type: ScoreType) -> bool:
        """Validate if a score value is within expected range for its type"""
        ranges = {
            ScoreType.DECATIPO: (1, 10),
            ScoreType.ENEATIPO: (1, 9),
            ScoreType.PERCENTIL: (1, 99),
            ScoreType.WECHSLER_CI: (40, 160),
            ScoreType.T_SCORE: (20, 80),
            ScoreType.Z_SCORE: (-3, 3)
        }
        
        if score_type in ranges:
            min_val, max_val = ranges[score_type]
            return min_val <= value <= max_val
        
        return True  # For DIRECT_SCORE, accept any value
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Extract surrounding context for a matched score"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return text[context_start:context_end].strip()
    
    def _remove_duplicates(self, scores: List[Score]) -> List[Score]:
        """Remove duplicate scores based on position in text"""
        seen_contexts = set()
        unique_scores = []
        
        for score in scores:
            # Use context as a way to identify duplicates
            context_key = (score.value, score.score_type, score.context[:20])
            if context_key not in seen_contexts:
                seen_contexts.add(context_key)
                unique_scores.append(score)
        
        return unique_scores


class ASCIIGraphGenerator:
    """Generates ASCII graphs for psychological/educational scores"""
    
    def __init__(self, width: int = 60, height: int = 10):
        self.width = width
        self.height = height
    
    def generate_graph(self, scores: List[Score]) -> str:
        """Generate ASCII graph for a list of scores"""
        if not scores:
            return "No hay puntuaciones para graficar."
        
        # Group scores by type
        score_groups = self._group_scores_by_type(scores)
        
        graphs = []
        for score_type, type_scores in score_groups.items():
            graph = self._create_single_graph(type_scores, score_type)
            graphs.append(graph)
        
        return "\n\n".join(graphs)
    
    def _group_scores_by_type(self, scores: List[Score]) -> Dict[ScoreType, List[Score]]:
        """Group scores by their type"""
        groups = {}
        for score in scores:
            if score.score_type not in groups:
                groups[score.score_type] = []
            groups[score.score_type].append(score)
        return groups
    
    def _create_single_graph(self, scores: List[Score], score_type: ScoreType) -> str:
        """Create ASCII graph for scores of a single type"""
        if not scores:
            return ""
        
        # Get scale info for this score type
        scale_info = self._get_scale_info(score_type)
        type_name = self._get_type_name(score_type)
        
        # Create title
        title = f"{type_name} (n={len(scores)})"
        graph_lines = [title, "=" * len(title)]
        
        # Create horizontal bar chart
        max_value = scale_info['max']
        min_value = scale_info['min']
        
        # Sort scores for better visualization
        sorted_scores = sorted(scores, key=lambda x: x.value, reverse=True)
        
        for i, score in enumerate(sorted_scores):
            # Calculate bar length (proportional to scale)
            if max_value > min_value:
                bar_length = int(((score.value - min_value) / (max_value - min_value)) * (self.width - 15))
            else:
                bar_length = self.width // 2
                
            bar_length = max(1, bar_length)  # Minimum bar length of 1
            
            # Create bar
            bar = "█" * bar_length
            score_label = f"{score.value:>6.1f}"
            
            # Add context if available
            context_preview = score.context[:20] + "..." if len(score.context) > 20 else score.context
            
            line = f"{score_label} |{bar} ({context_preview})"
            graph_lines.append(line)
        
        # Add scale reference
        graph_lines.append("")
        scale_line = f"Escala: {min_value} ──────────── {max_value}"
        graph_lines.append(scale_line)
        
        return "\n".join(graph_lines)
    
    def _get_scale_info(self, score_type: ScoreType) -> Dict[str, Union[float, str]]:
        """Get scale information for each score type"""
        scales = {
            ScoreType.DECATIPO: {'min': 1, 'max': 10, 'mean': 5.5},
            ScoreType.ENEATIPO: {'min': 1, 'max': 9, 'mean': 5},
            ScoreType.PERCENTIL: {'min': 1, 'max': 99, 'mean': 50},
            ScoreType.WECHSLER_CI: {'min': 40, 'max': 160, 'mean': 100},
            ScoreType.T_SCORE: {'min': 20, 'max': 80, 'mean': 50},
            ScoreType.Z_SCORE: {'min': -3, 'max': 3, 'mean': 0},
            ScoreType.DIRECT_SCORE: {'min': 0, 'max': 100, 'mean': 50}  # Default for unscaled
        }
        return scales.get(score_type, scales[ScoreType.DIRECT_SCORE])
    
    def _get_type_name(self, score_type: ScoreType) -> str:
        """Get readable name for score type"""
        names = {
            ScoreType.DECATIPO: "Puntuaciones Decatipo",
            ScoreType.ENEATIPO: "Puntuaciones Eneatipo",
            ScoreType.PERCENTIL: "Percentiles",
            ScoreType.WECHSLER_CI: "CI Wechsler",
            ScoreType.T_SCORE: "Puntuaciones T",
            ScoreType.Z_SCORE: "Puntuaciones Z",
            ScoreType.DIRECT_SCORE: "Puntuaciones Directas"
        }
        return names.get(score_type, "Puntuaciones")


class ScoreAnalyzer:
    """Main class that combines score detection and graph generation"""
    
    def __init__(self):
        self.detector = ScoreDetector()
        self.graph_generator = ASCIIGraphGenerator()
    
    def analyze_text(self, text: str) -> Dict[str, Union[List[Dict], str, int]]:
        """Analyze text for scores and generate visualizations"""
        # Detect scores
        scores = self.detector.detect_scores(text)
        
        # Generate graphs
        graph = self.graph_generator.generate_graph(scores) if scores else ""
        
        # Convert scores to serializable format
        scores_data = []
        for score in scores:
            scores_data.append({
                'value': score.value,
                'type': score.score_type.value,
                'raw_text': score.raw_text,
                'context': score.context
            })
        
        return {
            'scores': scores_data,
            'graph': graph,
            'total_scores': len(scores)
        }