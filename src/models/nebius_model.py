"""
Nebius Model Integration for Hospital AI Helper
Wraps the Nebius API for use within the hospital AI application
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Generator

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infer import NebiusInference, NebiusConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NebiusModel:
    """
    Hospital AI Helper integration wrapper for Nebius API
    Provides a standardized interface for medical AI consultations
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Nebius model wrapper"""
        self.config = config or {}
        self.nebius = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Nebius inference client"""
        try:
            # Check if API key is available
            api_key = os.getenv("NEBIUS_API_KEY")
            if not api_key:
                # Try to load from config file
                config_path = Path("config/nebius_config.json")
                if config_path.exists():
                    import json
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                        api_key = config_data.get("api_key")
                        if api_key == "your-nebius-api-key-here":
                            api_key = None

            if not api_key:
                logger.warning("Nebius API key not configured. Model will be unavailable.")
                return

            self.nebius = NebiusInference()
            logger.info("Nebius model initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Nebius model: {e}")
            self.nebius = None

    def is_available(self) -> bool:
        """Check if the Nebius model is available"""
        return self.nebius is not None and self.nebius.health_check()

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        specialty: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """
        Generate a medical consultation response
        
        Args:
            prompt: User's medical query
            context: Additional medical context
            specialty: Medical specialty focus
            max_tokens: Maximum tokens to generate
            temperature: Response creativity (0.0-1.0)
            stream: Whether to stream the response
            
        Returns:
            Generated response string or generator for streaming
        """
        if not self.nebius:
            raise RuntimeError("Nebius model not initialized")

        try:
            if stream:
                return self._stream_response(
                    prompt, context, specialty, max_tokens, temperature
                )
            else:
                return self.nebius.medical_consultation(
                    patient_query=prompt,
                    context=context,
                    specialty=specialty
                )

        except Exception as e:
            logger.error(f"Nebius generation failed: {e}")
            raise

    def _stream_response(
        self,
        prompt: str,
        context: Optional[str],
        specialty: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Generator[str, None, None]:
        """Generate streaming response"""
        system_prompt = self.nebius._build_medical_system_prompt(specialty)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "assistant", 
                "content": f"Medical Context: {context}"
            })
        
        messages.append({"role": "user", "content": prompt})

        try:
            for chunk in self.nebius.chat_completion(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            ):
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"Error: {str(e)}"

    def get_model_info(self) -> Dict:
        """Get information about the Nebius model"""
        if not self.nebius:
            return {
                "name": "Nebius Llama 3.3 70B",
                "status": "unavailable",
                "reason": "API key not configured"
            }

        try:
            model_info = self.nebius.get_model_info()
            return {
                "name": "Nebius Llama 3.3 70B",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "status": "available",
                "api_info": model_info
            }
        except Exception as e:
            return {
                "name": "Nebius Llama 3.3 70B",
                "status": "error",
                "error": str(e)
            }

    def create_medical_summary(
        self, 
        patient_data: Dict,
        include_recommendations: bool = True
    ) -> str:
        """
        Create a medical summary from patient data
        
        Args:
            patient_data: Dictionary containing patient information
            include_recommendations: Whether to include treatment recommendations
            
        Returns:
            Medical summary text
        """
        if not self.nebius:
            raise RuntimeError("Nebius model not initialized")

        # Build context from patient data
        context_parts = []
        
        if "symptoms" in patient_data:
            context_parts.append(f"Symptoms: {patient_data['symptoms']}")
        
        if "medical_history" in patient_data:
            context_parts.append(f"Medical History: {patient_data['medical_history']}")
        
        if "current_medications" in patient_data:
            context_parts.append(f"Current Medications: {patient_data['current_medications']}")
        
        if "vital_signs" in patient_data:
            context_parts.append(f"Vital Signs: {patient_data['vital_signs']}")

        context = "\n".join(context_parts)
        
        prompt = "Please provide a comprehensive medical summary based on the provided patient information."
        
        if include_recommendations:
            prompt += " Include general recommendations for next steps in care."

        try:
            return self.nebius.medical_consultation(
                patient_query=prompt,
                context=context,
                specialty=patient_data.get("specialty", "General Medicine")
            )
        except Exception as e:
            logger.error(f"Medical summary generation failed: {e}")
            raise

    def analyze_symptoms(self, symptoms: List[str], specialty: Optional[str] = None) -> str:
        """
        Analyze a list of symptoms and provide medical insights
        
        Args:
            symptoms: List of symptom descriptions
            specialty: Optional medical specialty focus
            
        Returns:
            Medical analysis of symptoms
        """
        if not self.nebius:
            raise RuntimeError("Nebius model not initialized")

        symptoms_text = ", ".join(symptoms)
        prompt = f"Please analyze these symptoms and provide general medical insights: {symptoms_text}"
        
        try:
            return self.nebius.medical_consultation(
                patient_query=prompt,
                specialty=specialty or "General Medicine"
            )
        except Exception as e:
            logger.error(f"Symptom analysis failed: {e}")
            raise


def test_nebius_model():
    """Test function for the Nebius model wrapper"""
    print("🧪 Testing Nebius Model Integration...")
    
    # Initialize model
    model = NebiusModel()
    
    # Check availability
    if not model.is_available():
        print("❌ Nebius model not available (API key not configured)")
        return False
    
    print("✅ Nebius model is available")
    
    # Test model info
    info = model.get_model_info()
    print(f"📊 Model Info: {info}")
    
    # Test simple response
    try:
        response = model.generate_response(
            "What are the warning signs of a heart attack?",
            specialty="Cardiology"
        )
        print(f"💬 Response: {response[:200]}...")
        
        # Test streaming
        print("\n🌊 Testing streaming response:")
        stream_response = model.generate_response(
            "Explain the importance of blood pressure monitoring",
            stream=True,
            max_tokens=200
        )
        
        for chunk in stream_response:
            print(chunk, end="", flush=True)
        print("\n")
        
        # Test medical summary
        patient_data = {
            "symptoms": "chest pain, shortness of breath, fatigue",
            "medical_history": "hypertension, diabetes",
            "specialty": "Cardiology"
        }
        
        summary = model.create_medical_summary(patient_data)
        print(f"📋 Medical Summary: {summary[:200]}...")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_nebius_model() 