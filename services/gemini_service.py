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
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")

    def generate_content(self, prompt: str, temperature: float = 0.9, max_retries: int = 2) -> str:
        """
        Generate content using Gemini API with retry mechanism
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=200  # Reduced for faster response
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
    
    def generate_daily_brain_tip(self) -> str:
        """
        Generate daily brain health tip focused on protecting against AI overuse
        """
        prompt = """
Kısa bir beyin sağlığı tavsiyesi ver. Sadece tavsiyenin kendisi olsun, açıklama yapma.

Örnek:
"Bugün bir problem çözerken ilk 10 dakika hiç araştırma yapmadan sadece kendi aklınla düşün."

Kurallar:
- Başlık kullanma 
- 1 cümle maksimum
- Yapay zeka bağımlılığından korunmaya odaklan
- Türkçe ve samimi dil
"""
        
        return self.generate_content(prompt, temperature=0.7, max_retries=2)
    
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
                
                # Validate required fields and ensure they are integers
                if 'creativity_score' in parsed and 'practicality_score' in parsed and 'feedback' in parsed:
                    creativity_score = parsed['creativity_score']
                    practicality_score = parsed['practicality_score']
                    
                    # Convert to int and ensure they are in valid range (1-5)
                    try:
                        creativity_score = max(1, min(5, int(creativity_score)))
                        practicality_score = max(1, min(5, int(practicality_score)))
                    except (ValueError, TypeError):
                        creativity_score = 3
                        practicality_score = 3
                    
                    return {
                        'creativity_score': creativity_score,
                        'practicality_score': practicality_score,
                        'feedback': str(parsed['feedback'])
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

    def parse_json_response(self, response_text: str) -> dict:
        """
        Parse Gemini JSON response for Word Bridge exercise
        """
        try:
            # Clean the response text
            clean_text = response_text.strip()
            
            # Try to find JSON in the response
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = clean_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, try parsing the whole response
            return json.loads(clean_text)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            
            # Return a default structure based on common Word Bridge responses
            return {
                'error': 'JSON parsing failed',
                'raw_response': response_text
            }
