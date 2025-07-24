import os
import logging
import json
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service for interacting with Google Gemini API
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
    
    def generate_content(self, prompt: str, temperature: float = 0.9, max_retries: int = 3) -> str:
        """
        Generate content using Gemini API with retry mechanism
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=1000
                    )
                )
                
                if response.text and response.text.strip():
                    return response.text.strip()
                    
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
        
        return None
    
    def generate_problem_chain_content(self, prompt: str) -> str:
        """
        Generate problem chain content with specific settings
        """
        return self.generate_content(prompt, temperature=1.0, max_retries=3)
    
    def parse_evaluation_response(self, response_text: str) -> dict:
        """
        Parse Gemini evaluation response to extract scores and feedback
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate required fields
                if 'creativity_score' in parsed and 'practicality_score' in parsed and 'feedback' in parsed:
                    return {
                        'creativity_score': int(parsed['creativity_score']),
                        'practicality_score': int(parsed['practicality_score']),
                        'feedback': parsed['feedback']
                    }
            
            # Fallback parsing failed
            logger.warning("Failed to parse Gemini evaluation response")
            return {
                'creativity_score': 3,
                'practicality_score': 3,
                'feedback': 'Yaratıcı çözümler ürettiniz! Gelişiminizi sürdürün.'
            }
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Error parsing evaluation response: {e}")
            return {
                'creativity_score': 3,
                'practicality_score': 3,
                'feedback': 'Egzersizi tamamladınız! Problem çözme becerinizi geliştirmeye devam edin.'
            }
