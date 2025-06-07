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

from src.utils.env_loader import ensure_env_loaded
from src.core.infer import NebiusInference, NebiusConfig
from src.utils.logger import setup_logger

# Ensure .env file is loaded
ensure_env_loaded()

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

            if not api_key or api_key == "your-nebius-api-key-here":
                logger.warning(
                    "Nebius API key not configured. Model will be unavailable. "
                    "Please set the NEBIUS_API_KEY environment variable."
                )
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
        stream: bool = False,
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
                    patient_query=prompt, context=context, specialty=specialty
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
        temperature: float,
    ) -> Generator[str, None, None]:
        """Generate streaming response"""
        system_prompt = self.nebius._build_medical_system_prompt(specialty)

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append(
                {"role": "assistant", "content": f"Medical Context: {context}"}
            )

        messages.append({"role": "user", "content": prompt})

        try:
            for chunk in self.nebius.chat_completion(
                messages, max_tokens=max_tokens, temperature=temperature, stream=True
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
                "reason": "API key not configured",
            }

        try:
            model_info = self.nebius.get_model_info()
            return {
                "name": "Nebius Llama 3.3 70B",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "status": "available",
                "api_info": model_info,
            }
        except Exception as e:
            return {"name": "Nebius Llama 3.3 70B", "status": "error", "error": str(e)}

    def create_medical_summary(
        self, patient_data: Dict, include_recommendations: bool = True
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
            context_parts.append(
                f"Current Medications: {patient_data['current_medications']}"
            )

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
                specialty=patient_data.get("specialty", "General Medicine"),
            )
        except Exception as e:
            logger.error(f"Medical summary generation failed: {e}")
            raise

    def analyze_symptoms(
        self, symptoms: List[str], specialty: Optional[str] = None
    ) -> str:
        """
        Analyze symptoms and provide medical insights

        Args:
            symptoms: List of symptoms to analyze
            specialty: Medical specialty to focus on

        Returns:
            Analysis of symptoms
        """
        if not self.nebius:
            raise RuntimeError("Nebius model not initialized")

        symptoms_text = ", ".join(symptoms)

        prompt = f"Analyze these symptoms: {symptoms_text}"
        if specialty:
            prompt += f" from a {specialty} perspective"

        prompt += ". Provide possible conditions and recommendations."

        return self.nebius.medical_consultation(
            patient_query=prompt, specialty=specialty
        )

    def generate_sql_query(
        self,
        user_request: str,
        database_schema: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate SQL queries based on user requests and hospital database schema

        Args:
            user_request: Natural language request for data
            database_schema: Description of database schema (optional, uses hospital schema by default)
            max_tokens: Maximum tokens for the response
            temperature: Temperature for generation (low for deterministic SQL)

        Returns:
            Generated SQL query
        """
        if not self.nebius:
            raise RuntimeError("Nebius model not initialized")

        # Import hospital schema loader
        try:
            from ..utils.schema_loader import hospital_schema_loader

            # Use hospital schema context if no custom schema provided
            if database_schema is None:
                database_schema = hospital_schema_loader.get_sql_context()

            # Get interpretation rules for better query understanding
            interpretation_rules = hospital_schema_loader.get_interpretation_rules()

        except ImportError:
            logger.warning("Hospital schema loader not available, using basic schema")
            if database_schema is None:
                database_schema = "Basic hospital database schema"
            interpretation_rules = ""

        # Build a specialized prompt for SQL generation with hospital context
        system_prompt = f"""
        You are an expert SQL developer for a hospital management system. Generate precise, syntactically correct PostgreSQL queries based on user requests.
        
        HOSPITAL-SPECIFIC GUIDELINES:
        1. For blood group counts, query patient_records.blood_group (NOT hospital_inventory)
        2. For blood unit inventory, query hospital_inventory with item_type='blood_unit'
        3. Always filter by role='patient' when querying patient data from users table
        4. Use proper JOINs: users -> patient_records -> occupancy -> rooms
        5. Use meaningful table aliases (u=users, pr=patient_records, o=occupancy, r=rooms)
        6. Include appropriate WHERE clauses for filtering
        7. Use LIMIT clauses to prevent overwhelming results (typically 30-50 for lists)
        8. Order results logically
        9. Return ONLY the SQL query, no explanations
        10. Wrap the SQL query in ```sql blocks for easy extraction
        
        {interpretation_rules}
        """

        user_prompt = f"""
        {database_schema}
        
        USER REQUEST: {user_request}
        
        Generate a complete PostgreSQL query that fulfills this request. Consider all table relationships and use appropriate JOINs.
        Pay special attention to the query interpretation rules above.
        Return only the SQL query wrapped in ```sql blocks.
        """

        try:
            response = self.generate_response(
                prompt=user_prompt,
                context=system_prompt,
                specialty="Database",
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
            )

            return response

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
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
            "What are the warning signs of a heart attack?", specialty="Cardiology"
        )
        print(f"💬 Response: {response[:200]}...")

        # Test streaming
        print("\n🌊 Testing streaming response:")
        stream_response = model.generate_response(
            "Explain the importance of blood pressure monitoring",
            stream=True,
            max_tokens=200,
        )

        for chunk in stream_response:
            print(chunk, end="", flush=True)
        print("\n")

        # Test medical summary
        patient_data = {
            "symptoms": "chest pain, shortness of breath, fatigue",
            "medical_history": "hypertension, diabetes",
            "specialty": "Cardiology",
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
