"""
Nebius API Usage Examples for Hospital AI Helper
Demonstrates various medical consultation scenarios using the Nebius integration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.nebius_model import NebiusModel
from infer import NebiusInference


def example_basic_consultation():
    """Example 1: Basic medical consultation"""
    print("🏥 Example 1: Basic Medical Consultation")
    print("-" * 50)
    
    # Direct API usage
    try:
        nebius = NebiusInference()
        
        response = nebius.medical_consultation(
            patient_query="I have been experiencing persistent headaches for the past week. Should I be concerned?",
            specialty="Neurology"
        )
        
        print("Patient Query: I have been experiencing persistent headaches for the past week. Should I be concerned?")
        print(f"AI Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to set your NEBIUS_API_KEY environment variable")
    
    print("\n")


def example_symptom_analysis():
    """Example 2: Symptom analysis with context"""
    print("🔍 Example 2: Symptom Analysis with Context")
    print("-" * 50)
    
    try:
        model = NebiusModel()
        
        if not model.is_available():
            print("❌ Nebius model not available (API key not configured)")
            return
        
        symptoms = [
            "chest pain when exercising",
            "shortness of breath",
            "irregular heartbeat",
            "fatigue"
        ]
        
        analysis = model.analyze_symptoms(symptoms, specialty="Cardiology")
        
        print(f"Symptoms: {', '.join(symptoms)}")
        print(f"Analysis: {analysis}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def example_medical_summary():
    """Example 3: Comprehensive medical summary"""
    print("📋 Example 3: Medical Summary Generation")
    print("-" * 50)
    
    try:
        model = NebiusModel()
        
        if not model.is_available():
            print("❌ Nebius model not available (API key not configured)")
            return
        
        patient_data = {
            "symptoms": "chronic lower back pain, leg numbness, difficulty walking long distances",
            "medical_history": "previous herniated disc L4-L5, physical therapy completed 6 months ago",
            "current_medications": "ibuprofen 400mg as needed, gabapentin 300mg twice daily",
            "vital_signs": "BP: 130/85, HR: 72, Temp: 98.6°F",
            "specialty": "Orthopedics"
        }
        
        summary = model.create_medical_summary(patient_data, include_recommendations=True)
        
        print("Patient Data:")
        for key, value in patient_data.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nGenerated Summary:\n{summary}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def example_streaming_consultation():
    """Example 4: Streaming medical consultation"""
    print("🌊 Example 4: Streaming Medical Consultation")
    print("-" * 50)
    
    try:
        model = NebiusModel()
        
        if not model.is_available():
            print("❌ Nebius model not available (API key not configured)")
            return
        
        prompt = "Explain the key differences between Type 1 and Type 2 diabetes, including symptoms, causes, and treatment approaches."
        
        print(f"Query: {prompt}")
        print("\nStreaming Response:")
        print("-" * 30)
        
        response_generator = model.generate_response(
            prompt=prompt,
            specialty="Endocrinology",
            stream=True,
            max_tokens=800,
            temperature=0.5
        )
        
        full_response = ""
        for chunk in response_generator:
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print(f"\n\nFull Response Length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def example_multiple_specialties():
    """Example 5: Consultations across multiple specialties"""
    print("🏥 Example 5: Multi-Specialty Consultations")
    print("-" * 50)
    
    consultations = [
        {
            "query": "What exercises are safe for someone with mild arthritis?",
            "specialty": "Rheumatology",
            "context": "Patient is 65 years old with osteoarthritis in knees"
        },
        {
            "query": "How can I manage anxiety before medical procedures?",
            "specialty": "Psychiatry",
            "context": "Patient has upcoming surgery and experiencing pre-operative anxiety"
        },
        {
            "query": "What dietary changes can help with acid reflux?",
            "specialty": "Gastroenterology",
            "context": "Patient experiences heartburn 3-4 times per week"
        }
    ]
    
    try:
        model = NebiusModel()
        
        if not model.is_available():
            print("❌ Nebius model not available (API key not configured)")
            return
        
        for i, consultation in enumerate(consultations, 1):
            print(f"Consultation {i} - {consultation['specialty']}:")
            print(f"Query: {consultation['query']}")
            print(f"Context: {consultation['context']}")
            
            response = model.generate_response(
                prompt=consultation['query'],
                context=consultation['context'],
                specialty=consultation['specialty'],
                temperature=0.4  # Lower temperature for medical accuracy
            )
            
            print(f"Response: {response[:200]}...")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def example_emergency_triage():
    """Example 6: Emergency triage assessment"""
    print("🚨 Example 6: Emergency Triage Assessment")
    print("-" * 50)
    
    emergency_scenarios = [
        {
            "symptoms": "severe chest pain radiating to left arm, sweating, nausea",
            "priority": "HIGH",
            "specialty": "Emergency Medicine"
        },
        {
            "symptoms": "mild fever, runny nose, cough for 2 days",
            "priority": "LOW",
            "specialty": "Family Medicine"
        },
        {
            "symptoms": "sudden severe headache, vision changes, confusion",
            "priority": "CRITICAL",
            "specialty": "Emergency Medicine"
        }
    ]
    
    try:
        nebius = NebiusInference()
        
        for scenario in emergency_scenarios:
            prompt = f"""
            Emergency Triage Assessment:
            Symptoms: {scenario['symptoms']}
            
            Please provide:
            1. Urgency level assessment
            2. Possible conditions to consider
            3. Immediate actions recommended
            4. When to seek emergency care
            """
            
            response = nebius.medical_consultation(
                patient_query=prompt,
                specialty=scenario['specialty']
            )
            
            print(f"🏥 Scenario ({scenario['priority']} Priority):")
            print(f"Symptoms: {scenario['symptoms']}")
            print(f"Assessment: {response[:300]}...")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def setup_instructions():
    """Display setup instructions for using Nebius API"""
    print("🛠️  Nebius API Setup Instructions")
    print("=" * 60)
    print()
    print("To use the Nebius API integration, you need to:")
    print()
    print("1. Get API Key:")
    print("   - Visit https://studio.nebius.com")
    print("   - Sign up for an account")
    print("   - Navigate to API section")
    print("   - Generate a new API key")
    print()
    print("2. Configure API Key (choose one method):")
    print()
    print("   Method 1 - Environment Variable:")
    print("   set NEBIUS_API_KEY=your-actual-api-key-here")
    print("   (or on Linux/Mac: export NEBIUS_API_KEY=your-actual-api-key-here)")
    print()
    print("   Method 2 - Configuration File:")
    print("   Edit config/nebius_config.json and replace:")
    print('   "api_key": "your-nebius-api-key-here"')
    print("   with your actual API key")
    print()
    print("3. Test the Integration:")
    print("   python infer.py")
    print("   python examples/nebius_usage.py")
    print()
    print("📚 API Reference: https://studio.nebius.com/api-reference")
    print("🤖 Model: meta-llama/Llama-3.3-70B-Instruct")
    print()


def main():
    """Run all examples"""
    print("🏥 Nebius API Integration Examples for Hospital AI Helper")
    print("=" * 70)
    print()
    
    # Check if API key is configured
    api_key = os.getenv("NEBIUS_API_KEY")
    config_path = Path("config/nebius_config.json")
    
    if not api_key and config_path.exists():
        try:
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                api_key = config_data.get("api_key")
                if api_key == "your-nebius-api-key-here":
                    api_key = None
        except:
            pass
    
    if not api_key:
        setup_instructions()
        print("⚠️  API key not configured. Examples will show expected errors.")
        print("   Configure your API key to see full functionality.")
        print()
    
    # Run examples
    example_basic_consultation()
    example_symptom_analysis()
    example_medical_summary()
    example_streaming_consultation()
    example_multiple_specialties()
    example_emergency_triage()
    
    print("✅ All examples completed!")
    print()
    print("💡 Next steps:")
    print("   - Configure your Nebius API key to test with real responses")
    print("   - Integrate Nebius model into your Gradio interface")
    print("   - Customize medical prompts for your specific use case")
    print("   - Add error handling and user feedback in your application")


if __name__ == "__main__":
    main() 