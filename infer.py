"""
Nebius API Integration for Hospital AI Helper
Provides inference capabilities using meta-llama/Llama-3.3-70B-Instruct model
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Generator
import requests
import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class NebiusConfig:
    """Configuration for Nebius API"""
    api_key: str
    base_url: str = "https://api.studio.nebius.ai/v1"
    model: str = "meta-llama/Llama-3.3-70B-Instruct"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30


class NebiusInference:
    """Nebius API inference client for hospital AI applications"""

    def __init__(self, config: Optional[NebiusConfig] = None):
        """Initialize the Nebius inference client"""
        self.config = config or self._load_config()
        self.session = requests.Session()
        self._setup_session()

    def _load_config(self) -> NebiusConfig:
        """Load configuration from environment variables or config file"""
        # Try to load API key from environment
        api_key = os.getenv("NEBIUS_API_KEY")
        
        if not api_key:
            # Try to load from config file
            config_path = Path("config/nebius_config.json")
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                        api_key = config_data.get("api_key")
                except Exception as e:
                    logger.warning(f"Failed to load config file: {e}")
        
        if not api_key:
            raise ValueError(
                "Nebius API key not found. Please set NEBIUS_API_KEY environment variable "
                "or add it to config/nebius_config.json"
            )

        return NebiusConfig(
            api_key=api_key,
            model=os.getenv("NEBIUS_MODEL", "meta-llama/Llama-3.3-70B-Instruct"),
            max_tokens=int(os.getenv("NEBIUS_MAX_TOKENS", "2048")),
            temperature=float(os.getenv("NEBIUS_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("NEBIUS_TOP_P", "0.9")),
            timeout=int(os.getenv("NEBIUS_TIMEOUT", "30"))
        )

    def _setup_session(self):
        """Setup the HTTP session with appropriate headers"""
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: bool = False
    ) -> Union[Dict, Generator[Dict, None, None]]:
        """
        Create a chat completion using Nebius API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            
        Returns:
            Response dictionary or generator for streaming
        """
        url = f"{self.config.base_url}/chat/completions"
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "top_p": top_p or self.config.top_p,
            "stream": stream
        }

        try:
            if stream:
                return self._stream_completion(url, payload)
            else:
                response = self.session.post(
                    url, 
                    json=payload, 
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Nebius API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Nebius API response: {e}")
            raise

    def _stream_completion(self, url: str, payload: Dict) -> Generator[Dict, None, None]:
        """Handle streaming responses from Nebius API"""
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming request failed: {e}")
            raise

    def simple_completion(self, prompt: str, **kwargs) -> str:
        """
        Simple text completion interface
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for chat_completion
            
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        else:
            raise ValueError("Invalid response format from Nebius API")

    def medical_consultation(
        self, 
        patient_query: str, 
        context: Optional[str] = None,
        specialty: Optional[str] = None
    ) -> str:
        """
        Specialized method for medical consultations
        
        Args:
            patient_query: Patient's question or concern
            context: Additional medical context
            specialty: Medical specialty focus
            
        Returns:
            Medical guidance response
        """
        system_prompt = self._build_medical_system_prompt(specialty)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "assistant", 
                "content": f"Medical Context: {context}"
            })
        
        messages.append({"role": "user", "content": patient_query})
        
        response = self.chat_completion(
            messages,
            temperature=0.3,  # Lower temperature for medical accuracy
            max_tokens=1024
        )
        
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        else:
            raise ValueError("Invalid response format from Nebius API")

    def _build_medical_system_prompt(self, specialty: Optional[str] = None) -> str:
        """Build system prompt for medical consultations with LaTeX formatting support"""
        base_prompt = """You are a helpful medical AI assistant designed to provide general health information and guidance. 

IMPORTANT DISCLAIMERS:
- You are not a replacement for professional medical advice
- Always recommend consulting with healthcare professionals for serious concerns
- Do not provide specific diagnoses or prescribe medications
- Focus on general health education and when to seek medical attention

FORMATTING INSTRUCTIONS:
- Use LaTeX formatting for mathematical expressions, formulas, and medical calculations
- For inline math, use \\( and \\) delimiters (e.g., \\(BMI = \\frac{weight}{height^2}\\))
- For display math, use \\[ and \\] delimiters for centered equations
- Use LaTeX for drug dosages, lab values, and medical calculations
- Examples: 
  * BMI calculation: \\(BMI = \\frac{weight \\text{ (kg)}}{height^2 \\text{ (m)}}\\)
  * Creatinine clearance: \\(CrCl = \\frac{(140-age) \\times weight}{72 \\times serum\\_creatinine}\\)
  * Normal ranges: Temperature \\(36.5°C - 37.2°C\\) (\\(97.7°F - 99°F\\))

DATABASE ANALYSIS INSTRUCTIONS:
When provided with database results:
- Analyze the data comprehensively, don't just repeat it
- Provide insights, patterns, and relevant medical context
- Format medical values with LaTeX (weights, heights, lab values, doses, etc.)
- Highlight important findings or abnormal values
- Suggest follow-up actions when appropriate
- Present the information in a structured, professional manner with proper line breaks
- Use tables or lists to organize complex data when helpful
- Always use proper markdown formatting with headers, bullet points, and line breaks
- Each patient or data entry should be on a separate line or in a clear section

Please provide helpful, accurate, and safe medical information while emphasizing the importance of professional medical care. Use LaTeX formatting when presenting any mathematical content, formulas, calculations, or precise medical measurements."""

        if specialty:
            base_prompt += f"\n\nSpecialty Focus: {specialty}"
            base_prompt += f"\nProvide information relevant to {specialty} while maintaining general medical safety guidelines. Use appropriate LaTeX formatting for any {specialty.lower()}-specific calculations, formulas, or measurements."

        return base_prompt

    def get_model_info(self) -> Dict:
        """Get information about available models"""
        url = f"{self.config.base_url}/models"
        
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model info: {e}")
            raise

    def health_check(self) -> bool:
        """Check if the Nebius API is accessible"""
        try:
            self.get_model_info()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


def create_nebius_config_template():
    """Create a template configuration file for Nebius API"""
    config_path = Path("config/nebius_config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    if not config_path.exists():
        template_config = {
            "api_key": "your-nebius-api-key-here",
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "timeout": 30,
            "description": "Nebius API configuration for Hospital AI Helper"
        }
        
        with open(config_path, 'w') as f:
            json.dump(template_config, f, indent=2)
        
        print(f"Created Nebius config template at: {config_path}")
        print("Please add your Nebius API key to the configuration file.")


def main():
    """Demo/test function for Nebius integration"""
    # Create config template if it doesn't exist
    create_nebius_config_template()
    
    try:
        # Initialize the inference client
        nebius = NebiusInference()
        
        # Health check
        if not nebius.health_check():
            print("❌ Nebius API health check failed")
            return
        
        print("✅ Nebius API health check passed")
        
        # Test simple completion
        print("\n🔬 Testing simple completion...")
        response = nebius.simple_completion(
            "What are the common symptoms of influenza?",
            max_tokens=512,
            temperature=0.5
        )
        print(f"Response: {response}")
        
        # Test medical consultation
        print("\n🏥 Testing medical consultation...")
        medical_response = nebius.medical_consultation(
            patient_query="I have a persistent cough for 3 days. Should I be concerned?",
            specialty="General Medicine"
        )
        print(f"Medical Response: {medical_response}")
        
        # Test streaming
        print("\n🌊 Testing streaming response...")
        messages = [
            {"role": "user", "content": "Explain the importance of hand hygiene in hospitals in 3 key points."}
        ]
        
        print("Streaming response:")
        for chunk in nebius.chat_completion(messages, stream=True, max_tokens=300):
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure you have set your NEBIUS_API_KEY environment variable or configured config/nebius_config.json")


if __name__ == "__main__":
    main() 