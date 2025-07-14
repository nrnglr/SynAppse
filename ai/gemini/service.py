import os
import logging
import google.generativeai as genai
from lobsmart.settings import supabase
from ai.huggingface.service import generate_image_from_text
from ai.supabase.service import upload_image_to_supabase
from lobs.frontal import (
    CREATIVITY_EXERCISE_PROMPT,
    SHORT_CHARACTER_PROMPT,  # Eski prompt yerine yenisini kullanıyoruz
    HARD_SETTING_PROMPT
)

from lobs.temporal import (
    MEMORY_EASY_EXERCISE_PROMPT,
    MEMORY_MEDIUM_EXERCISE_PROMPT,
    MEMORY_HARD_EXERCISE_PROMPT,
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
            image_url = None # Değişkeni başlangıçta tanımla

            # 2. Orta ve Zor seviyeler için karakter üret VE resim oluştur
            if difficulty in ['medium', 'hard']:
                character = self.generate_text(SHORT_CHARACTER_PROMPT)
                if not character:
                    logger.warning("Gemini'den karakter üretilemedi.")
                else:
                    # Karakter başarıyla üretildiyse, bunu resim prompt'u olarak kullan
                    try:
                        image_prompt = (
                            f"A high-resolution, photorealistic image of '{character}'. "
                            "The image must look like a professional photograph taken with a DSLR camera, "
                            "featuring realistic lighting, textures, and a shallow depth of field (bokeh). "
                            "The subject should be the clear focus. "
                            "IMPORTANT: The image must be a photograph, not a drawing, illustration, or 3D render. "
                            "Absolutely no text, letters, or numbers should be visible in the image."
                        )
                        
                        generated_image = generate_image_from_text(prompt=image_prompt)

                        if generated_image:
                            image_url = upload_image_to_supabase(image=generated_image, bucket_name="exercise-images")
                            if image_url:
                                logger.info(f"Resim başarıyla Supabase'e yüklendi: {image_url}")
                            else:
                                logger.error("Resim Supabase'e yüklenemedi.")
                        else:
                            logger.error("Hugging Face'den resim üretilemedi.")
                    except Exception as img_exc:
                        logger.error(f"Resim üretme/yükleme sürecinde hata: {img_exc}", exc_info=True)


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

            exercise_data = {
                "title": title,
                "content": content,
                "difficulty": difficulty,
                "category": "creativity",
                "metadata": {
                    "image_url": image_url or f"https://via.placeholder.com/500x300.png?text=Image+Not+Generated", # Resim yoksa placeholder kullan
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

    def generate_and_save_memory_exercise(self, difficulty: str = 'easy') -> dict:
        try:
            # Prompt'ı seç
            if difficulty == 'easy':
                prompt = MEMORY_EASY_EXERCISE_PROMPT
            elif difficulty == 'medium':
                prompt = MEMORY_MEDIUM_EXERCISE_PROMPT
            elif difficulty == 'hard':
                prompt = MEMORY_HARD_EXERCISE_PROMPT
            else:
                raise ValueError("Geçersiz zorluk seviyesi!")

            # AI'dan kelimeleri al
            generated_text = self.generate_text(prompt)
            words = [word.strip() for word in generated_text.split(',') if word.strip()]
            if not words or len(words) < 3:
                logger.error("Memory egzersizi için yeterli kelime üretilemedi.")
                return None

            title = f"Hafıza Egzersizi ({difficulty.title()}): {', '.join(words)}"
            content = (
                "Yukarıdaki kelimeleri sırayla ekranda göreceksin. "
                "Her kelime için, bir önceki kelimeyle bağlantılı anlamlı bir cümle kur. "
                "En sonda AI sana başka örnek cümleler gösterecek.\n\n"
                f"Kelimeler: {', '.join(words)}"
            )

            exercise_data = {
                "title": title,
                "content": content,
                "difficulty": difficulty,
                "category": "memory",
                "metadata": {
                    "raw_words": words
                }
            }

            response = supabase.table('exercises').insert(exercise_data).execute()
            if not response.data:
                logger.error(f"Supabase'e hafıza egzersizi eklenemedi.")
                return None

            saved_exercise = response.data[0]
            logger.info(f"Yeni hafıza egzersizi eklendi: ID {saved_exercise.get('id')}")
            return saved_exercise

        except Exception as e:
            logger.error(f"[generate_and_save_memory_exercise Error]: {e}", exc_info=True)
            return None
