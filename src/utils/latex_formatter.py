"""
LaTeX Formatter for Medical Responses
Enhances AI responses with proper LaTeX formatting for medical calculations and formulas
"""

import re
from typing import Dict, List, Tuple


def format_medical_response(response: str, specialty: str = None) -> str:
    """
    Format a medical response with appropriate LaTeX syntax
    
    Args:
        response: The AI response text
        specialty: Medical specialty for context-specific formatting
        
    Returns:
        Formatted response with LaTeX syntax
    """
    # Apply general medical formatting
    formatted_response = apply_general_medical_latex(response)
    
    # Apply specialty-specific formatting
    if specialty:
        formatted_response = apply_specialty_latex(formatted_response, specialty)
    
    # Ensure proper LaTeX delimiters
    formatted_response = fix_latex_delimiters(formatted_response)
    
    return formatted_response


def apply_general_medical_latex(text: str) -> str:
    """Apply general medical LaTeX formatting"""
    
    # BMI calculations
    text = re.sub(
        r'BMI\s*=\s*weight\s*/\s*height\^?2',
        r'\\(BMI = \\frac{weight \\text{ (kg)}}{height^2 \\text{ (m)}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Temperature ranges
    text = re.sub(
        r'(\d+\.?\d*)\s*°?C\s*-\s*(\d+\.?\d*)\s*°?C',
        lambda m: f'\\({m.group(1)}°C - {m.group(2)}°C\\)',
        text
    )
    
    # Blood pressure (specific pattern to avoid conflicts)
    text = re.sub(
        r'(\d+)/(\d+)\s*mmHg',
        lambda m: f'\\({m.group(1)}/{m.group(2)} \\text{{ mmHg}}\\)',
        text
    )
    
    # Heart rate
    text = re.sub(
        r'(\d+)\s*bpm',
        lambda m: f'\\({m.group(1)} \\text{{ bpm}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Dosage calculations (more specific patterns first)
    text = re.sub(
        r'(\d+\.?\d*)\s*mg/kg/day',
        lambda m: f'\\({m.group(1)} \\text{{ mg/kg/day}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    text = re.sub(
        r'(\d+\.?\d*)\s*mg/kg(?!/day)',
        lambda m: f'\\({m.group(1)} \\text{{ mg/kg}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    text = re.sub(
        r'(\d+\.?\d*)\s*units/kg',
        lambda m: f'\\({m.group(1)} \\text{{ units/kg}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Lab values with ranges
    text = re.sub(
        r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*(mg/dL|mmol/L|g/dL|mEq/L|°C|°F)',
        lambda m: f'\\({m.group(1)} - {m.group(2)} \\text{{ {m.group(3)}}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Individual lab values
    text = re.sub(
        r'(\d+\.?\d*)\s*(mg/dL|mmol/L|g/dL|mEq/L)(?!\s*\\text)',
        lambda m: f'\\({m.group(1)} \\text{{ {m.group(2)}}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Age formatting
    text = re.sub(
        r'(\d+)\s*years?\s*old',
        lambda m: f'\\({m.group(1)} \\text{{ years old}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Weight and height
    text = re.sub(
        r'(\d+\.?\d*)\s*(kg|lbs?|pounds?)(?!\s*\\text)',
        lambda m: f'\\({m.group(1)} \\text{{ {m.group(2)}}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    text = re.sub(
        r'(\d+\.?\d*)\s*(cm|ft|inches?|in)(?!\s*\\text)',
        lambda m: f'\\({m.group(1)} \\text{{ {m.group(2)}}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Percentages in medical context
    text = re.sub(
        r'(\d+\.?\d*)%',
        lambda m: f'\\({m.group(1)}\\%\\)',
        text
    )
    
    # Room numbers (optional formatting)
    text = re.sub(
        r'\bR(\d+)\b',
        lambda m: f'\\(R{m.group(1)}\\)',
        text
    )
    
    # Blood groups
    text = re.sub(
        r'\b([ABO]+[+-])\b',
        lambda m: f'\\({m.group(1)}\\)',
        text
    )
    
    # Date and time formatting for medical context
    text = re.sub(
        r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})',
        lambda m: f'\\({m.group(1)} \\text{{ at }} {m.group(2)}\\)',
        text
    )
    
    return text


def apply_specialty_latex(text: str, specialty: str) -> str:
    """Apply specialty-specific LaTeX formatting"""
    
    specialty_lower = specialty.lower()
    
    if 'cardiology' in specialty_lower:
        text = apply_cardiology_latex(text)
    elif 'endocrinology' in specialty_lower:
        text = apply_endocrinology_latex(text)
    elif 'nephrology' in specialty_lower or 'kidney' in specialty_lower:
        text = apply_nephrology_latex(text)
    elif 'pediatrics' in specialty_lower:
        text = apply_pediatrics_latex(text)
    elif 'emergency' in specialty_lower:
        text = apply_emergency_latex(text)
    
    return text


def apply_cardiology_latex(text: str) -> str:
    """Apply cardiology-specific LaTeX formatting"""
    
    # Ejection fraction
    text = re.sub(
        r'EF\s*=?\s*(\d+)%',
        lambda m: f'\\(EF = {m.group(1)}\\%\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Cardiac output
    text = re.sub(
        r'CO\s*=\s*SV\s*×\s*HR',
        r'\\(CO = SV \\times HR\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # QT interval correction
    text = re.sub(
        r'QTc\s*=\s*QT\s*/\s*√RR',
        r'\\(QTc = \\frac{QT}{\\sqrt{RR}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def apply_endocrinology_latex(text: str) -> str:
    """Apply endocrinology-specific LaTeX formatting"""
    
    # HbA1c (specific pattern)
    text = re.sub(
        r'HbA1c\s*(\d+\.?\d*)%',
        lambda m: f'\\(HbA1c = {m.group(1)}\\%\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # Glucose levels (specific pattern)
    text = re.sub(
        r'glucose\s*(\d+)\s*mg/dL',
        lambda m: f'glucose \\({m.group(1)} \\text{{ mg/dL}}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def apply_nephrology_latex(text: str) -> str:
    """Apply nephrology-specific LaTeX formatting"""
    
    # Creatinine clearance (Cockcroft-Gault)
    text = re.sub(
        r'CrCl\s*=\s*\(\(140\s*-\s*age\)\s*×\s*weight\)\s*/\s*\(72\s*×\s*creatinine\)',
        r'\\[CrCl = \\frac{(140 - age) \\times weight \\text{ (kg)}}{72 \\times serum\\_creatinine \\text{ (mg/dL)}}\\]',
        text,
        flags=re.IGNORECASE
    )
    
    # GFR
    text = re.sub(
        r'GFR\s*(\d+)\s*mL/min',
        lambda m: f'\\(GFR = {m.group(1)} \\text{{ mL/min/1.73m}}^2\\)',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def apply_pediatrics_latex(text: str) -> str:
    """Apply pediatrics-specific LaTeX formatting"""
    
    # Weight percentiles
    text = re.sub(
        r'(\d+)(st|nd|rd|th)\s*percentile',
        lambda m: f'\\({m.group(1)}^{{\\text{{{m.group(2)}}}}}\\) percentile',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def apply_emergency_latex(text: str) -> str:
    """Apply emergency medicine-specific LaTeX formatting"""
    
    # Glasgow Coma Scale
    text = re.sub(
        r'GCS\s*(\d+)',
        lambda m: f'\\(GCS = {m.group(1)}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    # APACHE scores
    text = re.sub(
        r'APACHE\s*II\s*(\d+)',
        lambda m: f'\\(APACHE\\text{{ }}II = {m.group(1)}\\)',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def fix_latex_delimiters(text: str) -> str:
    """Ensure proper LaTeX delimiters and fix common issues"""
    
    # Fix double delimiters
    text = re.sub(r'\\\(\\\(', r'\\(', text)
    text = re.sub(r'\\\)\\\)', r'\\)', text)
    text = re.sub(r'\\\[\\\[', r'\\[', text)
    text = re.sub(r'\\\]\\\]', r'\\]', text)
    
    # Ensure spaces around display math
    text = re.sub(r'(\S)\\\[', r'\\1 \\[', text)
    text = re.sub(r'\\\](\S)', r'\\] \\1', text)
    
    # Fix common LaTeX syntax issues
    text = re.sub(r'\\text\s*\{([^}]*)\}', r'\\text{\\1}', text)
    text = re.sub(r'\\frac\s*\{([^}]*)\}\s*\{([^}]*)\}', r'\\frac{\\1}{\\2}', text)
    
    return text


def get_medical_latex_examples() -> Dict[str, List[str]]:
    """Get examples of medical LaTeX formatting for different specialties"""
    
    examples = {
        "General Medicine": [
            "BMI calculation: \\(BMI = \\frac{weight \\text{ (kg)}}{height^2 \\text{ (m)}}\\)",
            "Normal temperature: \\(36.5°C - 37.2°C\\) (\\(97.7°F - 99°F\\))",
            "Blood pressure: \\(120/80 \\text{ mmHg}\\)",
            "Heart rate: \\(60-100 \\text{ bpm}\\)"
        ],
        "Cardiology": [
            "Ejection fraction: \\(EF = 55\\%\\)",
            "Cardiac output: \\(CO = SV \\times HR\\)",
            "QT correction: \\(QTc = \\frac{QT}{\\sqrt{RR}}\\)"
        ],
        "Endocrinology": [
            "HbA1c target: \\(HbA1c < 7\\%\\)",
            "Fasting glucose: \\(70-100 \\text{ mg/dL}\\)",
            "Insulin dosing: \\(0.5-1.0 \\text{ units/kg/day}\\)"
        ],
        "Nephrology": [
            "Creatinine clearance: \\[CrCl = \\frac{(140 - age) \\times weight}{72 \\times serum\\_creatinine}\\]",
            "Normal GFR: \\(GFR > 90 \\text{ mL/min/1.73m}^2\\)"
        ]
    }
    
    return examples


def validate_latex_syntax(text: str) -> Tuple[bool, List[str]]:
    """
    Validate LaTeX syntax in text
    
    Args:
        text: Text containing LaTeX
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for unmatched delimiters
    inline_open = text.count('\\(')
    inline_close = text.count('\\)')
    if inline_open != inline_close:
        errors.append(f"Unmatched inline math delimiters: {inline_open} open, {inline_close} close")
    
    display_open = text.count('\\[')
    display_close = text.count('\\]')
    if display_open != display_close:
        errors.append(f"Unmatched display math delimiters: {display_open} open, {display_close} close")
    
    # Check for common LaTeX errors
    if re.search(r'\\frac\{[^}]*\}\{[^}]*$', text):
        errors.append("Incomplete \\frac command")
    
    if re.search(r'\\text\{[^}]*$', text):
        errors.append("Incomplete \\text command")
    
    return len(errors) == 0, errors 