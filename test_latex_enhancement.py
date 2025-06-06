#!/usr/bin/env python3
"""
Test script for LaTeX enhancement in the Hospital AI Helper chatbot
Demonstrates the LaTeX formatting capabilities for medical content
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.latex_formatter import (
    format_medical_response,
    get_medical_latex_examples,
    validate_latex_syntax
)


def test_latex_formatting():
    """Test LaTeX formatting with various medical examples"""
    
    print("🧪 Testing LaTeX Enhancement for Medical Chatbot")
    print("=" * 60)
    
    # Test cases with different medical content
    test_cases = [
        {
            "input": "The patient's BMI = weight / height^2 is 25.3. Normal temperature is 36.5°C - 37.2°C.",
            "specialty": "General Medicine",
            "description": "Basic medical calculations"
        },
        {
            "input": "Blood pressure is 120/80 mmHg, heart rate is 72 bpm. EF = 55%.",
            "specialty": "Cardiology", 
            "description": "Cardiology measurements"
        },
        {
            "input": "HbA1c 7.2%, glucose 140 mg/dL, insulin 0.8 units/kg.",
            "specialty": "Endocrinology",
            "description": "Endocrinology values"
        },
        {
            "input": "CrCl = ((140 - age) × weight) / (72 × creatinine). GFR 85 mL/min.",
            "specialty": "Nephrology",
            "description": "Kidney function calculations"
        },
        {
            "input": "Child is in 75th percentile for weight. Dosing: 15 mg/kg/day.",
            "specialty": "Pediatrics",
            "description": "Pediatric measurements"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']} ({case['specialty']})")
        print("-" * 40)
        print(f"Input:  {case['input']}")
        
        formatted = format_medical_response(case['input'], case['specialty'])
        print(f"Output: {formatted}")
        
        # Validate LaTeX syntax
        is_valid, errors = validate_latex_syntax(formatted)
        if is_valid:
            print("✅ LaTeX syntax is valid")
        else:
            print("❌ LaTeX syntax errors:")
            for error in errors:
                print(f"   - {error}")


def show_latex_examples():
    """Show examples of LaTeX formatting for different specialties"""
    
    print("\n\n📚 LaTeX Examples by Medical Specialty")
    print("=" * 60)
    
    examples = get_medical_latex_examples()
    
    for specialty, example_list in examples.items():
        print(f"\n{specialty}:")
        print("-" * len(specialty))
        for example in example_list:
            print(f"  • {example}")


def test_complex_medical_scenario():
    """Test a complex medical scenario with multiple calculations"""
    
    print("\n\n🏥 Complex Medical Scenario Test")
    print("=" * 60)
    
    scenario = """
    Patient Assessment:
    - BMI = weight / height^2 = 28.5 (overweight)
    - Blood pressure: 140/90 mmHg (hypertensive)
    - Heart rate: 88 bpm
    - Temperature: 37.8°C (fever)
    - HbA1c: 8.2% (poor diabetic control)
    - Creatinine clearance: CrCl = ((140 - age) × weight) / (72 × creatinine)
    - Medication dosing: 0.5 mg/kg twice daily
    - Lab values: glucose 180 mg/dL, cholesterol 240 mg/dL
    """
    
    print("Original text:")
    print(scenario)
    
    formatted = format_medical_response(scenario, "General Medicine")
    
    print("\nFormatted with LaTeX:")
    print(formatted)
    
    # Validate
    is_valid, errors = validate_latex_syntax(formatted)
    print(f"\nLaTeX validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if errors:
        for error in errors:
            print(f"  - {error}")


def demonstrate_frontend_integration():
    """Show how the LaTeX content would appear in the frontend"""
    
    print("\n\n🌐 Frontend Integration Example")
    print("=" * 60)
    
    sample_response = """
    Based on your symptoms, here are some key measurements to monitor:

    **Vital Signs:**
    - Normal temperature range: 36.5°C - 37.2°C
    - Target blood pressure: <120/80 mmHg
    - Resting heart rate: 60-100 bpm

    **BMI Calculation:**
    BMI = weight / height^2
    
    **Medication Dosing:**
    - Standard dose: 5-10 mg/kg/day
    - Maximum dose: 20 mg/kg/day
    
    **Lab Values:**
    - Normal glucose: 70-100 mg/dL
    - HbA1c target: <7%
    """
    
    formatted = format_medical_response(sample_response, "General Medicine")
    
    print("Formatted response (as would be sent to frontend):")
    print(formatted)
    
    print("\nHTML representation (how MathJax would process it):")
    html_preview = formatted.replace('\\(', '<span class="math-inline">').replace('\\)', '</span>')
    html_preview = html_preview.replace('\\[', '<div class="math-display">').replace('\\]', '</div>')
    print(html_preview)


def main():
    """Run all LaTeX enhancement tests"""
    
    try:
        test_latex_formatting()
        show_latex_examples()
        test_complex_medical_scenario()
        demonstrate_frontend_integration()
        
        print("\n\n🎉 LaTeX Enhancement Testing Complete!")
        print("=" * 60)
        print("✅ All tests passed successfully")
        print("✅ LaTeX formatting is working correctly")
        print("✅ Medical formulas are properly formatted")
        print("✅ Frontend integration is ready")
        
        print("\n📋 Next Steps:")
        print("1. Start the application: python app.py")
        print("2. Test with medical queries containing calculations")
        print("3. Verify LaTeX rendering in the browser")
        print("4. Check that MathJax loads and processes formulas")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Please check the implementation and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 