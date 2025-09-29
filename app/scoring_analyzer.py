import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DetectedNumber:
    """Represents a detected number in the text"""
    value: float
    start: int
    end: int
    context: str
    score_type: Optional[str] = None
    interpretation: Optional[str] = None


@dataclass
class ScoreAnalysis:
    """Contains the complete analysis of detected scores"""
    numbers: List[DetectedNumber]
    highlighted_text: str
    statistics: Dict[str, int]
    interpretations: List[Dict[str, str]]


class ScoringAnalyzer:
    """Analyzes text to detect numbers and identify standardized scoring patterns"""
    
    def __init__(self):
        # Patterns for different score types
        self.score_patterns = {
            'decatipo': {
                'keywords': ['decatipo', 'decátipo', 'decatype'],
                'range': (1, 10),
                'interpretations': {
                    1: 'Muy bajo',
                    2: 'Muy bajo', 
                    3: 'Bajo',
                    4: 'Medio-bajo',
                    5: 'Medio',
                    6: 'Medio',
                    7: 'Medio-alto',
                    8: 'Alto',
                    9: 'Muy alto',
                    10: 'Muy alto'
                }
            },
            'eneatipo': {
                'keywords': ['eneatipo', 'eneátipo', 'eneatype'],
                'range': (1, 9),
                'interpretations': {
                    1: 'Muy bajo',
                    2: 'Bajo',
                    3: 'Bajo-medio',
                    4: 'Medio-bajo',
                    5: 'Medio',
                    6: 'Medio-alto',
                    7: 'Alto-medio',
                    8: 'Alto',
                    9: 'Muy alto'
                }
            },
            'percentil': {
                'keywords': ['percentil', 'percentile', 'pc', 'p.'],
                'range': (1, 99),
                'interpretations': {
                    range(1, 10): 'Muy bajo (1-9 percentil)',
                    range(10, 25): 'Bajo (10-24 percentil)',
                    range(25, 75): 'Normal (25-74 percentil)',
                    range(75, 90): 'Alto (75-89 percentil)',
                    range(90, 100): 'Muy alto (90-99 percentil)'
                }
            },
            't_score': {
                'keywords': ['puntuación t', 't score', 't-score', 'puntaje t', 'score t', 'ansiedad', 'depresión', 'autoestima', 'impulsividad', 'atención'],
                'range': (20, 100),
                'mean': 50,
                'std': 10,
                'interpretations': {
                    range(20, 30): 'Muy bajo (T < 30)',
                    range(30, 40): 'Bajo (T 30-39)',
                    range(40, 60): 'Normal (T 40-59)',
                    range(60, 70): 'Alto (T 60-69)',
                    range(70, 101): 'Muy alto (T ≥ 70)'
                }
            },
            'z_score': {
                'keywords': ['puntuación z', 'z score', 'z-score', 'puntaje z', 'score z'],
                'range': (-4, 4),
                'mean': 0,
                'std': 1,
                'interpretations': {
                    'very_low': 'Muy bajo (z < -2)',
                    'low': 'Bajo (z -2 a -1)',
                    'normal': 'Normal (z -1 a 1)',
                    'high': 'Alto (z 1 a 2)',
                    'very_high': 'Muy alto (z > 2)'
                }
            },
            'wechsler_iq': {
                'keywords': ['wechsler', 'wisc', 'wais', 'wppsi', 'coeficiente intelectual', 'ci', 'iq'],
                'range': (40, 160),
                'mean': 100,
                'std': 15,
                'interpretations': {
                    range(40, 70): 'Deficiencia intelectual (CI < 70)',
                    range(70, 85): 'Límite (CI 70-84)',
                    range(85, 115): 'Normal (CI 85-114)',
                    range(115, 130): 'Superior (CI 115-129)',
                    range(130, 161): 'Muy superior (CI ≥ 130)'
                }
            },
            'wechsler_subtest': {
                'keywords': ['subtest', 'subprueba', 'escalar', 'comprensión', 'semejanzas', 'vocabulario', 'información', 'aritmética', 'dígitos', 'memoria', 'búsqueda', 'claves', 'cubos', 'matrices', 'conceptos'],
                'range': (1, 19),
                'mean': 10,
                'std': 3,
                'interpretations': {
                    range(1, 4): 'Muy bajo (1-3)',
                    range(4, 7): 'Bajo (4-6)',
                    range(7, 14): 'Normal (7-13)',
                    range(14, 17): 'Alto (14-16)',
                    range(17, 20): 'Muy alto (17-19)'
                }
            }
        }
    
    def analyze_text(self, text: str) -> ScoreAnalysis:
        """Analyzes text to detect numbers and identify scoring patterns"""
        # First, detect all numbers in the text
        numbers = self._detect_numbers(text)
        
        # Analyze each number for potential scoring patterns
        for number in numbers:
            self._analyze_number_context(number, text)
        
        # Create highlighted text
        highlighted_text = self._highlight_numbers(text, numbers)
        
        # Generate statistics
        statistics = self._generate_statistics(numbers)
        
        # Generate interpretations
        interpretations = self._generate_interpretations(numbers)
        
        return ScoreAnalysis(
            numbers=numbers,
            highlighted_text=highlighted_text,
            statistics=statistics,
            interpretations=interpretations
        )
    
    def _detect_numbers(self, text: str) -> List[DetectedNumber]:
        """Detects all numbers in the text"""
        numbers = []
        
        # Pattern to match numbers (integers and decimals)
        number_pattern = r'\b\d+(?:[.,]\d+)?\b'
        
        for match in re.finditer(number_pattern, text):
            try:
                # Convert to float, handling comma as decimal separator
                value_str = match.group().replace(',', '.')
                value = float(value_str)
                
                # Get context around the number (50 characters before and after)
                start_context = max(0, match.start() - 50)
                end_context = min(len(text), match.end() + 50)
                context = text[start_context:end_context]
                
                numbers.append(DetectedNumber(
                    value=value,
                    start=match.start(),
                    end=match.end(),
                    context=context
                ))
            except ValueError:
                continue
        
        return numbers
    
    def _analyze_number_context(self, number: DetectedNumber, full_text: str):
        """Analyzes the context around a number to identify score type"""
        context_lower = number.context.lower()
        
        # Skip common non-score numbers (ages, dates, durations, etc.)
        if any(word in context_lower for word in ['minutos', 'años', 'edad', 'fecha', 'duró', 'tiempo', 'mes', 'día']):
            return
        
        # Special handling for percentiles (look for % symbol first)
        if '%' in number.context and 1 <= number.value <= 99:
            number.score_type = 'percentil'
            number.interpretation = self._get_interpretation(number.value, 'percentil')
            return
        
        # Check for exact keyword matches in order of specificity
        # T-scores (check before Wechsler IQ due to overlapping ranges)
        if any(keyword in context_lower for keyword in self.score_patterns['t_score']['keywords']):
            if 20 <= number.value <= 100:
                number.score_type = 't_score'
                number.interpretation = self._get_interpretation(number.value, 't_score')
                return
        
        # Z-scores (check early as they have specific range)
        if any(keyword in context_lower for keyword in self.score_patterns['z_score']['keywords']):
            if -4 <= number.value <= 4:
                number.score_type = 'z_score'
                number.interpretation = self._get_interpretation(number.value, 'z_score')
                return
        
        # Decatipo (check before general ranges)
        if any(keyword in context_lower for keyword in self.score_patterns['decatipo']['keywords']):
            if 1 <= number.value <= 10:
                number.score_type = 'decatipo'
                number.interpretation = self._get_interpretation(number.value, 'decatipo')
                return
        
        # Eneatipo (check before general ranges)
        if any(keyword in context_lower for keyword in self.score_patterns['eneatipo']['keywords']):
            if 1 <= number.value <= 9:
                number.score_type = 'eneatipo'
                number.interpretation = self._get_interpretation(number.value, 'eneatipo')
                return
        
        # Wechsler subtests (check before IQ as they are more specific)
        if any(keyword in context_lower for keyword in self.score_patterns['wechsler_subtest']['keywords']):
            if 1 <= number.value <= 19:
                number.score_type = 'wechsler_subtest'
                number.interpretation = self._get_interpretation(number.value, 'wechsler_subtest')
                return
        
        # Wechsler IQ scores (check after subtests and with specific keywords)
        if any(keyword in context_lower for keyword in ['wechsler', 'wisc', 'wais', 'wppsi', 'coeficiente intelectual', 'ci', 'iq']):
            if 40 <= number.value <= 160:
                number.score_type = 'wechsler_iq'
                number.interpretation = self._get_interpretation(number.value, 'wechsler_iq')
                return
        
        # Percentiles (without % symbol, check last as most general)
        if any(keyword in context_lower for keyword in self.score_patterns['percentil']['keywords']):
            if 1 <= number.value <= 99:
                number.score_type = 'percentil'
                number.interpretation = self._get_interpretation(number.value, 'percentil')
                return
    
    def _get_interpretation(self, value: float, score_type: str) -> str:
        """Gets the interpretation for a specific score value and type"""
        pattern_info = self.score_patterns.get(score_type)
        if not pattern_info:
            return "Puntuación no interpretable"
        
        interpretations = pattern_info['interpretations']
        
        if score_type == 'percentil':
            for range_obj, interpretation in interpretations.items():
                if isinstance(range_obj, range) and value in range_obj:
                    return interpretation
            return f"Percentil {int(value)}"
        
        elif score_type == 'z_score':
            if value < -2:
                return interpretations['very_low']
            elif -2 <= value < -1:
                return interpretations['low']
            elif -1 <= value <= 1:
                return interpretations['normal']
            elif 1 < value <= 2:
                return interpretations['high']
            else:
                return interpretations['very_high']
        
        elif score_type in ['t_score', 'wechsler_iq', 'wechsler_subtest']:
            for range_obj, interpretation in interpretations.items():
                if isinstance(range_obj, range) and value in range_obj:
                    return interpretation
        
        else:  # decatipo, eneatipo
            return interpretations.get(int(value), "Puntuación no interpretable")
        
        return "Puntuación no interpretable"
    
    def _highlight_numbers(self, text: str, numbers: List[DetectedNumber]) -> str:
        """Creates highlighted version of text with numbers in red"""
        highlighted = text
        offset = 0
        
        # Sort numbers by position to apply highlighting correctly
        sorted_numbers = sorted(numbers, key=lambda x: x.start)
        
        for number in sorted_numbers:
            start = number.start + offset
            end = number.end + offset
            
            # Extract the original number text
            original_text = text[number.start:number.end]
            
            # Create highlighted version
            if number.score_type:
                # If it's a recognized score, use a different highlight
                highlighted_text = f'<span class="highlighted-score" title="{number.score_type}: {number.interpretation}">{original_text}</span>'
            else:
                # Regular number highlight
                highlighted_text = f'<span class="highlighted-number">{original_text}</span>'
            
            # Replace in the text
            highlighted = highlighted[:start] + highlighted_text + highlighted[end:]
            
            # Update offset for next replacements
            offset += len(highlighted_text) - len(original_text)
        
        return highlighted
    
    def _generate_statistics(self, numbers: List[DetectedNumber]) -> Dict[str, int]:
        """Generates statistics about detected numbers"""
        total_numbers = len(numbers)
        recognized_scores = len([n for n in numbers if n.score_type])
        
        score_types = {}
        for number in numbers:
            if number.score_type:
                score_types[number.score_type] = score_types.get(number.score_type, 0) + 1
        
        return {
            'total_numbers': total_numbers,
            'recognized_scores': recognized_scores,
            'unrecognized_numbers': total_numbers - recognized_scores,
            'score_types': score_types
        }
    
    def _generate_interpretations(self, numbers: List[DetectedNumber]) -> List[Dict[str, str]]:
        """Generates list of interpretations for recognized scores"""
        interpretations = []
        
        for number in numbers:
            if number.score_type and number.interpretation:
                interpretations.append({
                    'value': str(number.value),
                    'type': number.score_type,
                    'interpretation': number.interpretation,
                    'context': number.context.strip()[:100] + ('...' if len(number.context) > 100 else '')
                })
        
        return interpretations