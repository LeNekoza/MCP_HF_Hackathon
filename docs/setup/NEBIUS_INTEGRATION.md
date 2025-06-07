# Nebius API Integration for Hospital AI Helper

This document describes the integration of [Nebius Studio API](https://studio.nebius.com/api-reference) with the Hospital AI Helper project, specifically using the **meta-llama/Llama-3.3-70B-Instruct** model for medical consultations and AI-powered healthcare assistance.

## 🏥 Overview

The Nebius integration provides advanced AI capabilities for medical consultations, symptom analysis, and healthcare guidance through the powerful Llama 3.3 70B model. This integration offers:

- **Medical Consultations**: Specialized medical advice with specialty-specific prompts
- **Symptom Analysis**: Intelligent analysis of patient symptoms with context
- **Medical Summaries**: Comprehensive patient data summaries
- **Streaming Responses**: Real-time AI responses for better user experience
- **Emergency Triage**: Quick assessment for emergency scenarios
- **Multi-Specialty Support**: Coverage across different medical specialties

## 🚀 Quick Start

### 1. Get Your API Key

1. Visit [Nebius Studio](https://studio.nebius.com)
2. Sign up for an account
3. Navigate to the API section
4. Generate a new API key

### 2. Configure the Integration

Choose one of these methods to configure your API key:

**Method 1: Environment Variable (Recommended)**
```bash
# Windows
set NEBIUS_API_KEY=your-actual-api-key-here

# Linux/Mac
export NEBIUS_API_KEY=your-actual-api-key-here
```

**Method 2: Configuration File**
Edit `config/nebius_config.json`:
```json
{
  "api_key": "your-actual-api-key-here",
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "max_tokens": 2048,
  "temperature": 0.7,
  "top_p": 0.9,
  "timeout": 30
}
```

### 3. Test the Integration

```bash
# Test the basic integration
python infer.py

# Run comprehensive examples
python examples/nebius_usage.py

# Test the model wrapper
python src/models/nebius_model.py
```

## 📁 File Structure

```
hospital-ai-helper-aid/
├── infer.py                     # Core Nebius API integration
├── src/models/nebius_model.py   # Hospital AI wrapper class
├── examples/nebius_usage.py     # Usage examples and demos
├── config/
│   ├── nebius_config.json       # Nebius configuration file
│   └── app_config.json          # Updated with Nebius model option
└── requirements.txt             # Updated with requests dependency
```

## 🔧 Core Components

### 1. `infer.py` - Core Integration

The main integration file provides direct access to the Nebius API:

```python
from infer import NebiusInference

# Initialize the client
nebius = NebiusInference()

# Basic medical consultation
response = nebius.medical_consultation(
    patient_query="I have persistent headaches. Should I be concerned?",
    specialty="Neurology"
)

# Chat completion with custom parameters
messages = [
    {"role": "system", "content": "You are a medical AI assistant."},
    {"role": "user", "content": "Explain diabetes symptoms."}
]

response = nebius.chat_completion(
    messages=messages,
    max_tokens=1024,
    temperature=0.5
)
```

### 2. `NebiusModel` - Hospital AI Wrapper

A specialized wrapper for hospital-specific use cases:

```python
from src.models.nebius_model import NebiusModel

# Initialize the model
model = NebiusModel()

# Check availability
if model.is_available():
    # Generate medical response
    response = model.generate_response(
        prompt="What are the symptoms of pneumonia?",
        specialty="Pulmonology"
    )
    
    # Analyze symptoms
    symptoms = ["chest pain", "shortness of breath", "fatigue"]
    analysis = model.analyze_symptoms(symptoms, specialty="Cardiology")
    
    # Create medical summary
    patient_data = {
        "symptoms": "chronic back pain, leg numbness",
        "medical_history": "previous herniated disc",
        "specialty": "Orthopedics"
    }
    summary = model.create_medical_summary(patient_data)
```

## 🏥 Medical Use Cases

### 1. General Medical Consultation

```python
response = nebius.medical_consultation(
    patient_query="I have a persistent cough for two weeks with yellow mucus.",
    specialty="Pulmonology"
)
```

### 2. Symptom Analysis

```python
symptoms = [
    "chest tightness when exercising",
    "shortness of breath",
    "irregular heartbeat"
]

analysis = model.analyze_symptoms(symptoms, specialty="Cardiology")
```

### 3. Emergency Triage

```python
emergency_query = """
Patient presents with:
- Severe chest pain radiating to left arm
- Profuse sweating
- Nausea and vomiting
- Pain started 30 minutes ago

Assess urgency and recommend immediate actions.
"""

response = nebius.medical_consultation(
    patient_query=emergency_query,
    specialty="Emergency Medicine"
)
```

### 4. Multi-Specialty Consultations

```python
specialties = {
    "Cardiology": "Heart-related symptoms and conditions",
    "Neurology": "Nervous system and brain disorders",
    "Orthopedics": "Bone, joint, and muscle problems",
    "Psychiatry": "Mental health and behavioral issues",
    "Gastroenterology": "Digestive system disorders"
}

for specialty, description in specialties.items():
    response = model.generate_response(
        prompt=f"Explain common conditions in {description}",
        specialty=specialty
    )
```

## 🌊 Streaming Responses

For real-time user interaction, use streaming:

```python
# Streaming consultation
def stream_consultation(query, specialty):
    response_generator = model.generate_response(
        prompt=query,
        specialty=specialty,
        stream=True,
        max_tokens=800
    )
    
    print("AI Response: ", end="")
    for chunk in response_generator:
        print(chunk, end="", flush=True)
    print()

# Usage
stream_consultation(
    "Explain diabetes management strategies",
    "Endocrinology"
)
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEBIUS_API_KEY` | Your Nebius API key | Required |
| `NEBIUS_MODEL` | Model to use | `meta-llama/Llama-3.3-70B-Instruct` |
| `NEBIUS_MAX_TOKENS` | Maximum tokens per response | `2048` |
| `NEBIUS_TEMPERATURE` | Response creativity (0.0-2.0) | `0.7` |
| `NEBIUS_TOP_P` | Nucleus sampling parameter | `0.9` |
| `NEBIUS_TIMEOUT` | Request timeout in seconds | `30` |

### Medical-Specific Settings

```python
# For medical accuracy, use lower temperature
medical_response = nebius.chat_completion(
    messages=messages,
    temperature=0.3,  # More conservative for medical advice
    max_tokens=1024
)

# For emergency situations, use faster responses
emergency_response = nebius.simple_completion(
    prompt="Emergency: Patient unconscious, what should I do?",
    max_tokens=512,
    temperature=0.1  # Very conservative for emergencies
)
```

## 🔒 Safety and Disclaimers

The integration includes built-in medical safety prompts:

```python
def _build_medical_system_prompt(self, specialty: Optional[str] = None) -> str:
    """Build system prompt for medical consultations"""
    base_prompt = '''You are a helpful medical AI assistant designed to provide general health information and guidance. 

IMPORTANT DISCLAIMERS:
- You are not a replacement for professional medical advice
- Always recommend consulting with healthcare professionals for serious concerns
- Do not provide specific diagnoses or prescribe medications
- Focus on general health education and when to seek medical attention

Please provide helpful, accurate, and safe medical information while emphasizing the importance of professional medical care.'''
```

## 📊 Model Information

- **Model**: meta-llama/Llama-3.3-70B-Instruct
- **Provider**: Nebius Studio
- **API Endpoint**: https://api.studio.nebius.ai/v1
- **Context Length**: Up to 8,192 tokens
- **Optimal Use**: Medical consultations, healthcare guidance, symptom analysis

## 🧪 Testing and Examples

Run the comprehensive examples:

```bash
# Basic functionality test
python infer.py

# Complete usage examples
python examples/nebius_usage.py

# Integration wrapper test
python src/models/nebius_model.py
```

## 🚨 Error Handling

The integration includes comprehensive error handling:

```python
try:
    response = nebius.medical_consultation(
        patient_query="What causes headaches?",
        specialty="Neurology"
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔧 Integration with Gradio

To integrate with your Gradio interface:

```python
import gradio as gr
from src.models.nebius_model import NebiusModel

# Initialize model
nebius_model = NebiusModel()

def medical_consultation(query, specialty, context=""):
    """Gradio interface function"""
    if not nebius_model.is_available():
        return "❌ Nebius model not available. Please configure API key."
    
    try:
        response = nebius_model.generate_response(
            prompt=query,
            context=context if context else None,
            specialty=specialty,
            temperature=0.4  # Conservative for medical use
        )
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio interface
interface = gr.Interface(
    fn=medical_consultation,
    inputs=[
        gr.Textbox(label="Medical Query", placeholder="Describe your symptoms or medical question..."),
        gr.Dropdown(
            choices=["General Medicine", "Cardiology", "Neurology", "Orthopedics", "Psychiatry"],
            label="Medical Specialty",
            value="General Medicine"
        ),
        gr.Textbox(label="Additional Context (Optional)", placeholder="Medical history, medications, etc.")
    ],
    outputs=gr.Textbox(label="AI Medical Guidance"),
    title="Hospital AI Helper - Nebius Integration",
    description="Get medical guidance using Llama 3.3 70B model via Nebius API"
)
```

## 📚 Additional Resources

- [Nebius Studio Documentation](https://studio.nebius.com/api-reference)
- [Llama 3.3 Model Information](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct)
- [Hospital AI Helper Project](./README.md)

## 🤝 Contributing

To contribute to the Nebius integration:

1. Fork the repository
2. Create a feature branch
3. Add your enhancements to the integration
4. Include tests and documentation
5. Submit a pull request

## 📄 License

This integration follows the same license as the main Hospital AI Helper project.

---

**⚠️ Important Medical Disclaimer**: This AI integration is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns. 