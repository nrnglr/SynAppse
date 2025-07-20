import os
import logging
import json
import google.generativeai as genai
from lobsmart.settings import supabase
from ai.huggingface.service import generate_image_from_text
from ai.supabase.service import upload_image_to_supabase
from lobs.frontal import (
    CREATIVE_EXERCISE_GENERATOR_PROMPT,
    CREATIVE_FEEDBACK_PROMPT,
)
from lobs.temporal import (
    MEMORY_EASY_EXERCISE_PROMPT,
    MEMORY_MEDIUM_EXERCISE_PROMPT,
    MEMORY_HARD_EXERCISE_PROMPT,
    MEMORY_FEEDBACK_PROMPT,
)

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

    def generate_text(self, prompt: str, temperature: float = 0.9) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            # Yanıttan JSON bloğunu temizleme
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            return cleaned_text.strip()
        except Exception as e:
            logger.error(f"[GeminiService Error]: {e}", exc_info=True)
            return "AI yanıtı üretilemedi."

    def generate_and_save_creative_exercise(self, difficulty: str = 'easy') -> dict:
        try:
            # 1. Prompt'u zorluk seviyesiyle doldur
            prompt = CREATIVE_EXERCISE_GENERATOR_PROMPT.replace("[DIFFICULTY]", difficulty)
            
            # 2. Gemini'den JSON formatında yanıt al
            generated_json_str = self.generate_text(prompt, temperature=1.0)
            if not generated_json_str:
                logger.error("Gemini'den yaratıcılık egzersizi için yanıt alınamadı.")
                return None
            
            # 3. JSON'u ayrıştır
            try:
                exercise_data = json.loads(generated_json_str)
            except json.JSONDecodeError:
                logger.error(f"Gemini'den gelen yanıt geçerli bir JSON değil: {generated_json_str}")
                return None

            # 5. Gelen veriyi güvenli bir şekilde doğrula ve işle
            metadata = exercise_data.get("metadata", {})
            words = metadata.get("words", [])
            
            if len(words) < 2:
                logger.error(f"AI'dan gelen yanıtta yaratıcılık egzersizi için yeterli 'words' bulunamadı. Gelen veri: {exercise_data}")
                return None

            # 6. Resim üret (eğer 'medium' veya 'hard' ise)
            image_url = None
            image_prompt = exercise_data.get("image_prompt_en")
            if image_prompt:
                try:
                    generated_image = generate_image_from_text(prompt=image_prompt)
                    if generated_image:
                        image_url = upload_image_to_supabase(image=generated_image, bucket_name="exercise-images")
                        if not image_url:
                            logger.error("Üretilen resim Supabase'e yüklenemedi.")
                except Exception as img_exc:
                    logger.error(f"Resim üretme/yükleme sürecinde hata: {img_exc}", exc_info=True)

            # 7. Veritabanı için kaydı hazırla
            db_record = {
                "title": f"Yaratıcılık Egzersizi: {words[0]} & {words[1]}",
                "content": exercise_data.get("user_prompt_tr", "Lütfen bu öğelerle bir hikaye oluşturun."),
                "difficulty": difficulty,
                "category": "creativity",
                "metadata": {
                    "image_url": image_url or "https://via.placeholder.com/500x300.png?text=Image+Not+Generated",
                    **metadata
                }
            }
            
            # 8. Supabase'e kaydet
            response = supabase.table('exercises').insert(db_record).execute()
            if not response.data:
                logger.error(f"Supabase'e yaratıcılık egzersizi eklenemedi.")
                return None

            saved_exercise = response.data[0]
            logger.info(f"Yeni yaratıcılık egzersizi (JSON) Supabase'e eklendi: ID {saved_exercise.get('id')}")
            
            return saved_exercise

        except Exception as e:
            logger.error(f"[generate_and_save_creative_exercise Error]: {e}", exc_info=True)
            return None

    def generate_feedback_for_story(self, metadata: dict, user_story: str) -> str:
        try:
            # Metadata'yı string'e dönüştürerek prompt'a ekle
            metadata_str = json.dumps(metadata, ensure_ascii=False, indent=2)
            
            prompt = CREATIVE_FEEDBACK_PROMPT.replace("[METADATA]", metadata_str)
            prompt = prompt.replace("[USER_STORY]", user_story)
            
            feedback = self.generate_text(prompt, temperature=0.8)
            
            if not feedback or feedback == "AI yanıtı üretilemedi.":
                logger.warning("Gemini'den yaratıcılık geri bildirimi üretilemedi.")
                return "Değerlendirme alınamadı."
            
            return feedback
        except Exception as e:
            logger.error(f"[generate_feedback_for_story Error]: {e}", exc_info=True)
            return "Geri bildirim üretilirken bir hata oluştu."

    def generate_feedback_for_paragraph(self, words: list, user_paragraph: str) -> str:
        """
        Verilen kelimeler ve kullanıcı paragrafı için Gemini'den yapıcı geri bildirim alır.
        """
        try:
            prompt = MEMORY_FEEDBACK_PROMPT.replace("[KELİMELER]", ", ".join(words))
            prompt = prompt.replace("[KULLANICI_PARAGRAFI]", user_paragraph)
            
            feedback = self.generate_text(prompt, temperature=0.8)
            
            if not feedback:
                logger.warning("Gemini'den geri bildirim üretilemedi.")
                return "Değerlendirme alınamadı."
            
            return feedback

        except Exception as e:
            logger.error(f"[generate_feedback_for_paragraph Error]: {e}", exc_info=True)
            return "Geri bildirim üretilirken bir hata oluştu."

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
