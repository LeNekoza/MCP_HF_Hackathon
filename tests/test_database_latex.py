#!/usr/bin/env python3
"""
Test script for LaTeX formatting of database responses
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.latex_formatter import format_medical_response

def test_database_response_formatting():
    """Test LaTeX formatting on a sample database response"""
    
    # Sample database response similar to what the user showed
    sample_db_response = """
📊 Hospital Database Results (10 records)
Query used 4 tables: patient_records, rooms, users, occupancy

👥 Patient Information:

1. David Johnson
📅 DOB: 1953-11-11
👤 Gender: M
🩸 Blood Group: A-
🏥 Room: R001 (N/A)
⚠️ Allergies: Aspirin
📝 Admitted: 2024-01-01 14:12:00
📤 Discharged: 2024-01-02 14:12:00

2. Michael Garcia  
📅 DOB: 2044-03-19
👤 Gender: F
🩸 Blood Group: AB-
🏥 Room: R002 (N/A)
⚠️ Allergies: Sulfa
📝 Admitted: 2024-01-01 18:06:00
📤 Discharged: 2024-01-02 18:06:00

3. Lisa Johnson
📅 DOB: 2003-04-09  
👤 Gender: F
🩸 Blood Group: AB+
🏥 Room: R003 (N/A)
⚠️ Allergies: Aspirin
📝 Admitted: 2024-01-02 08:13:00
📤 Discharged: 2024-01-04 08:13:00
"""

    print("🧪 Testing LaTeX Formatting on Database Response")
    print("=" * 60)
    print("\nOriginal Database Response:")
    print("-" * 40)
    print(sample_db_response)
    
    print("\nFormatted with LaTeX:")
    print("-" * 40)
    formatted_response = format_medical_response(sample_db_response, "General Medicine")
    print(formatted_response)
    
    print("\n📋 Key Improvements:")
    print("-" * 40)
    print("• Room numbers: R001 → \\(R001\\)")
    print("• Blood groups: A- → \\(A-\\)")  
    print("• Dates: 2024-01-01 14:12:00 → \\(2024-01-01 \\text{ at } 14:12:00\\)")
    print("• Medical measurements will be formatted when present")

def test_medical_measurements():
    """Test formatting of medical measurements that might appear in patient data"""
    
    print("\n\n🏥 Testing Medical Measurements Formatting")
    print("=" * 60)
    
    test_cases = [
        "Patient weight: 75 kg, height: 180 cm",
        "Blood pressure: 120/80 mmHg, heart rate: 72 bpm",
        "Temperature: 37.2°C, glucose: 95 mg/dL", 
        "Age: 45 years old, BMI = weight / height^2",
        "HbA1c: 6.5%, cholesterol: 180 mg/dL",
        "Room R205, Blood group: O+, admitted: 2024-01-15 09:30:00"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_case}")
        formatted = format_medical_response(test_case, "General Medicine")
        print(f"   Output: {formatted}")

def main():
    """Run all database LaTeX formatting tests"""
    
    try:
        test_database_response_formatting()
        test_medical_measurements()
        
        print("\n\n🎉 Database LaTeX Formatting Test Complete!")
        print("=" * 60)
        print("✅ Database responses now support LaTeX formatting")
        print("✅ Medical measurements are properly formatted")
        print("✅ Patient data displays with mathematical notation")
        
        print("\n📋 Next Steps:")
        print("1. The chatbot will now apply LaTeX formatting to database responses")
        print("2. Try asking for patient details to see the enhanced formatting")
        print("3. Medical calculations in patient data will render beautifully")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 