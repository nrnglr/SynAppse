import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set!")
        
        genai.configure(api_key=api_key)

        # Doğru model adı (v1 destekli)
        self.model = genai.GenerativeModel(model_name="gemini-2.5-pro")

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"[GeminiService Error]: {e}", exc_info=True)
            return "AI yanıtı üretilemedi."
