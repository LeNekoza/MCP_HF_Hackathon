#!/usr/bin/env python3
"""
Demo script for LaTeX-enhanced Hospital AI Helper Chatbot
Shows how to start the application and test LaTeX functionality
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print a welcome banner"""
    print("=" * 70)
    print("🏥 Hospital AI Helper - LaTeX Enhanced Chatbot Demo")
    print("=" * 70)
    print()
    print("✨ Features:")
    print("  • LaTeX mathematical formatting")
    print("  • Medical calculation support")
    print("  • Real-time formula rendering")
    print("  • Specialty-specific formatting")
    print()

def show_latex_examples():
    """Show examples of LaTeX formatting"""
    print("📚 LaTeX Formatting Examples:")
    print("-" * 40)
    
    examples = [
        ("BMI Calculation", "\\(BMI = \\frac{weight \\text{ (kg)}}{height^2 \\text{ (m)}}\\)"),
        ("Blood Pressure", "\\(120/80 \\text{ mmHg}\\)"),
        ("Heart Rate", "\\(72 \\text{ bpm}\\)"),
        ("Temperature Range", "\\(36.5°C - 37.2°C\\)"),
        ("HbA1c Target", "\\(HbA1c < 7\\%\\)"),
        ("Creatinine Clearance", "\\[CrCl = \\frac{(140 - age) \\times weight}{72 \\times serum\\_creatinine}\\]"),
        ("Ejection Fraction", "\\(EF = 55\\%\\)"),
        ("Medication Dosing", "\\(5-10 \\text{ mg/kg/day}\\)")
    ]
    
    for name, formula in examples:
        print(f"  {name}: {formula}")
    
    print()

def show_test_queries():
    """Show example queries to test LaTeX functionality"""
    print("🧪 Test Queries to Try:")
    print("-" * 40)
    
    queries = [
        "What is the BMI calculation formula?",
        "What are normal vital signs ranges?",
        "How do you calculate creatinine clearance?",
        "What is the normal ejection fraction?",
        "What are normal blood pressure ranges?",
        "How do you calculate pediatric medication dosing?",
        "What are normal HbA1c targets for diabetics?",
        "What is the cardiac output formula?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    
    print()

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking Dependencies:")
    print("-" * 40)
    
    try:
        import gradio as gr
        print("  ✅ Gradio: Available")
    except ImportError:
        print("  ❌ Gradio: Not installed (pip install gradio)")
        return False
    
    try:
        from src.utils.latex_formatter import format_medical_response
        print("  ✅ LaTeX Formatter: Available")
    except ImportError:
        print("  ❌ LaTeX Formatter: Not available")
        return False
    
    try:
        from src.components.interface import create_main_interface
        print("  ✅ Main Interface: Available")
    except ImportError:
        print("  ❌ Main Interface: Not available")
        return False
    
    # Check if static files exist
    static_files = [
        "static/js/latex-renderer.js",
        "static/js/app.js",
        "static/css/styles.css"
    ]
    
    for file_path in static_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}: Available")
        else:
            print(f"  ❌ {file_path}: Missing")
            return False
    
    print("  ✅ All dependencies are available!")
    print()
    return True

def start_application():
    """Start the LaTeX-enhanced chatbot application"""
    print("🚀 Starting LaTeX-Enhanced Chatbot...")
    print("-" * 40)
    
    try:
        # Import the main application
        from app import main
        
        print("  • Loading configuration...")
        print("  • Initializing LaTeX support...")
        print("  • Starting Gradio interface...")
        print()
        print("🌐 Application will open in your browser shortly...")
        print("📝 Try the test queries above to see LaTeX formatting in action!")
        print()
        print("Press Ctrl+C to stop the application")
        print("=" * 70)
        
        # Start the application
        main()
        
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed")
        print("2. Check that config files are properly set up")
        print("3. Verify Nebius API key is configured (if using)")
        return False
    
    return True

def main():
    """Main demo function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install missing dependencies and try again.")
        return 1
    
    # Show examples
    show_latex_examples()
    show_test_queries()
    
    # Ask user if they want to start the application
    try:
        response = input("Would you like to start the chatbot now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            start_application()
        else:
            print("\n📋 To start the application later, run:")
            print("   python3 app.py")
            print("\n📖 For more information, see:")
            print("   LATEX_ENHANCEMENT_README.md")
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
    
    return 0

if __name__ == "__main__":
    exit(main()) 