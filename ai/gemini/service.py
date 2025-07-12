import os
import logging
import google.generativeai as genai
from lobsmart.settings import supabase
from lobs.frontal import (
    CREATIVITY_EXERCISE_PROMPT,
    MEDIUM_CHARACTER_PROMPT,
    HARD_SETTING_PROMPT
)

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"[GeminiService Error]: {e}", exc_info=True)
            return "AI yanıtı üretilemedi."

    def generate_and_save_creative_exercise(self, difficulty: str = 'easy') -> dict:
        """
        Yaratıcılık egzersizi üretir, Supabase'e kaydeder ve kaydedilen veriyi döndürür.
        
        Args:
            difficulty (str): 'easy', 'medium', veya 'hard'.
            
        Returns:
            Kaydedilen egzersiz verilerini içeren bir dictionary veya hata durumunda None.
        """
        try:
            # 1. Her seviye için temel kelimeleri üret
            generated_text = self.generate_text(CREATIVITY_EXERCISE_PROMPT)
            if not generated_text or "," not in generated_text:
                logger.error("Gemini'den beklenen formatta kelime üretilemedi.")
                return None
            
            words = [word.strip() for word in generated_text.split(',')]
            if len(words) < 2:
                logger.error("Gemini'den yeterli sayıda kelime alınamadı.")
                return None
            word1, word2 = words[0], words[1]

            character = None
            setting = None

            # 2. Orta seviye için karakter üret
            if difficulty in ['medium', 'hard']:
                character = self.generate_text(MEDIUM_CHARACTER_PROMPT)
                if not character:
                    logger.warning("Gemini'den karakter üretilemedi.")

            # 3. Zor seviye için mekan üret
            if difficulty == 'hard':
                setting = self.generate_text(HARD_SETTING_PROMPT)
                if not setting:
                    logger.warning("Gemini'den mekan üretilemedi.")
            
            # 4. Veritabanı için egzersiz verilerini hazırla
            title = f"Yaratıcılık Egzersizi: {word1} & {word2}"
            
            content_parts = [f"Verilen kelimeler: {word1}, {word2}."]
            if character:
                content_parts.append(f"Kullanılacak karakter: {character}.")
            if setting:
                content_parts.append(f"Hikayenin geçeceği mekan: {setting}.")
            content_parts.append("Bu öğeleri kullanarak kısa bir hikaye yazın.")
            content = " ".join(content_parts)

            image_url = f"https://via.placeholder.com/500x300.png?text={word1}+{word2}"

            exercise_data = {
                "title": title,
                "content": content,
                "difficulty": difficulty,
                "category": "creativity",
                "metadata": {
                    "image_url": image_url,
                    "raw_words": words,
                    "raw_character": character,
                    "raw_setting": setting
                }
            }

            # 5. Supabase'e kaydet
            response = supabase.table('exercises').insert(exercise_data).execute()
            
            if not response.data:
                 logger.error(f"Supabase'e egzersiz eklenemedi: {response.error.message if response.error else 'No data returned'}")
                 return None

            saved_exercise = response.data[0]
            logger.info(f"Yeni yaratıcılık egzersizi Supabase'e eklendi: ID {saved_exercise.get('id')}")
            
            # 6. Kaydedilen egzersiz verisini döndür
            return saved_exercise

        except Exception as e:
            logger.error(f"[generate_and_save_creative_exercise Error]: {e}", exc_info=True)
            return None
