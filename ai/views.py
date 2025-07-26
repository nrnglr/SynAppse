from django.shortcuts import render

# Main pages
def index(request):
    """Main landing page"""
    return render(request, 'index.html')

def exercise_view(request):
    """Exercise selection page"""
    return render(request, 'exercise.html')


def brain_view(request):
    return render(request, 'brain.html')

def sss_view(request):
    return render(request, 'sss.html')

def profile_view(request):
    return render(request, 'profile.html')

class CreativityTestPageView(TemplateView):
    """
    Yaratıcılık egzersizlerini oluşturmak ve listelemek için kullanılan test sayfasını render eder.
    """
    template_name = "ai/test_creativity.html"

class MemoryTestPageView(TemplateView):
    """
    Hafıza egzersizlerini oluşturmak ve listelemek için kullanılan test sayfasını render eder.
    """
    template_name = "ai/test_memory.html"

class CreateCreativityExerciseView(APIView):
    """
    API'dan yeni bir yaratıcılık egzersizi üretir ve Supabase'e kaydeder.
    İstek gövdesinde 'difficulty' parametresini bekler: 'easy', 'medium', 'hard'.
    """
    def post(self, request):
        difficulty = request.data.get('difficulty', 'easy')
        if difficulty not in ['easy', 'medium', 'hard']:
            return Response(
                {"error": "Geçersiz zorluk seviyesi. 'easy', 'medium' veya 'hard' olmalı."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            gemini_service = GeminiService()
            # Bu fonksiyon artık veriyi üretip Supabase'e kaydediyor ve sonucu dönüyor.
            saved_exercise = gemini_service.generate_and_save_creative_exercise(difficulty=difficulty)

            if not saved_exercise:
                return Response(
                    {"error": "Yapay zekadan egzersiz verisi alınamadı veya kaydedilemedi."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(saved_exercise, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Creativity exercise oluşturulurken hata: {e}", exc_info=True)
            return Response(
                {"error": "Egzersiz oluşturulurken beklenmedik bir sunucu hatası oluştu."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ListCreativityExercisesView(APIView):
    """
    Supabase veritabanından yaratıcılık egzersizlerini listeler.
    Query parametresi olarak 'difficulty' kabul eder (örn: /api/ai/creativity/exercises/?difficulty=easy).
    """
    def get(self, request):
        try:
            difficulty = request.query_params.get('difficulty')
            
            query = supabase.table('exercises').select('*').eq('category', 'creativity')
            
            if difficulty and difficulty in ['easy', 'medium', 'hard']:
                query = query.eq('difficulty', difficulty)

            response = query.order('created_at', desc=True).execute()

            if not response.data:
                return Response([], status=status.HTTP_200_OK)

            return Response(response.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Egzersizler listelenirken hata: {e}", exc_info=True)
            return Response(
                {"error": "Egzersizler alınırken bir sunucu hatası oluştu."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompleteCreativityExerciseView(APIView):
    """
    Bir yaratıcılık egzersizini tamamlar ve kullanıcının yazdığı hikayeyi kaydeder.
    """
    def post(self, request, exercise_id, *args, **kwargs):
        """
        Kullanıcının gönderdiği hikayeyi alır, (eğer egzersiz seviyesi uygunsa) AI'dan geri bildirim üretir,
        hem hikayeyi hem de geri bildirimi veritabanına kaydeder ve sonucu döndürür.
        """
        user_story = request.data.get('user_story')
        if not user_story:
            return Response({"error": "Lütfen hikayenizi girin."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. İlgili egzersizin mevcut verilerini veritabanından al.
            get_response = supabase.table('exercises').select('metadata').eq('id', exercise_id).single().execute()
            current_metadata = get_response.data.get('metadata', {})
            
            character = current_metadata.get('character') # 'raw_character' yerine 'character' kullanılıyor
            words = current_metadata.get('words')

            logger.info(f"Geri bildirim için alınan veriler - Karakter: {character}, Kelimeler: {words}")

            # Anahtar kelimeler olmadan işlem yapamayız.
            if not words:
                return Response({"error": "Egzersize ait anahtar kelimeler bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            # 2. Geri bildirim üretme adımını başlat.
            # 'character' None olsa bile fonksiyon çağrılacak.
            ai_feedback = get_creativity_feedback(
                words=words,
                user_story=user_story,
                character=character  # Bu None olabilir ve sorun değil
            )
            
            # 3. Veritabanına kaydedilecek yeni metadata'yı hazırla.
            current_metadata['user_story'] = user_story
            if ai_feedback:
                current_metadata['ai_feedback'] = ai_feedback
            
            # 4. Veritabanını tek bir işlemle güncelle.
            supabase.table('exercises').update({
                'metadata': current_metadata,
                'is_completed': True
            }).eq('id', exercise_id).execute()

            # 5. Başarılı sonucu ve üretilen geri bildirimi (varsa) arayüze gönder.
            return Response({
                "success": "Hikayeniz başarıyla kaydedildi.",
                "feedback": ai_feedback  # Karakter yoksa (Kolay seviye) bu değer None olacaktır.
            }, status=status.HTTP_200_OK)

        except APIError as e:
            logger.error(f"Supabase Hatası (Yaratıcılık ID: {exercise_id}): {e.message}")
            return Response({"error": f"Veritabanı Hatası: {str(e.message)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Yaratıcılık Egzersizi Tamamlama Hatası (ID: {exercise_id}): {e}", exc_info=True)
            return Response({"error": "Sunucuda beklenmedik bir hata oluştu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CreateMemoryExerciseView(APIView):
    def post(self, request):
        difficulty = request.data.get('difficulty', 'easy')
        if difficulty not in ['easy', 'medium', 'hard']:
            return Response(
                {"error": "Geçersiz zorluk seviyesi. 'easy', 'medium' veya 'hard' olmalı."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            gemini_service = GeminiService()
            saved_exercise = gemini_service.generate_and_save_memory_exercise(difficulty=difficulty)
            if not saved_exercise:
                return Response({"error": "Egzersiz üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Supabase'e kayıt işlemi burada olmalı (gemini_service metodunda yapılmış olabilir)
            return Response(saved_exercise, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Hafıza egzersizi oluşturulurken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListMemoryExercisesView(APIView):
    def get(self, request, *args, **kwargs):
        difficulty = request.query_params.get('difficulty', None)
        
        try:
            query = supabase.table('exercises').select('*').eq('category', 'memory')
            if difficulty:
                query = query.eq('difficulty', difficulty)
            
            response = query.order('created_at', desc=True).execute()

            return Response(response.data, status=status.HTTP_200_OK)

        except APIError as e:
            logger.error(f"Supabase API Error: {e.message}")
            return Response({"error": "Veritabanından egzersizler alınamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Hafıza egzersizleri listelenirken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompleteMemoryExerciseView(APIView):
    """
    Bir hafıza egzersizini tamamlar ve kullanıcının yazdığı paragrafı kaydeder.
    """
    def post(self, request, exercise_id, *args, **kwargs):
        try:
            user_paragraph = request.data.get('user_paragraph')
            if not user_paragraph:
                return Response({"error": "Kullanıcı paragrafı eksik."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Egzersizin kelimelerini al
            get_response = supabase.table('exercises').select('metadata').eq('id', exercise_id).single().execute()
            current_metadata = get_response.data.get('metadata', {})
            exercise_words = current_metadata.get('raw_words')

            if not exercise_words:
                return Response({"error": "Egzersiz kelimeleri bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            # 2. Gemini'den geri bildirim üret (Yeni merkezi fonksiyonu kullanarak)
            ai_feedback = get_memory_feedback(
                words=exercise_words,
                user_paragraph=user_paragraph
            )
            
            # 3. Hem kullanıcı cevabını hem de AI geri bildirimini metadata'ya ekle
            current_metadata['user_paragraph'] = user_paragraph
            current_metadata['ai_feedback'] = ai_feedback
            
            # 4. Kaydı tek seferde güncelle
            supabase.table('exercises').update({
                'metadata': current_metadata,
                'is_completed': True
            }).eq('id', exercise_id).execute()

            # 5. Üretilen geri bildirimi arayüze gönder
            return Response({
                "success": "Egzersiz başarıyla tamamlandı.",
                "feedback": ai_feedback
            }, status=status.HTTP_200_OK)

        except APIError as e:
            logger.error(f"Supabase API Hatası: {e.message}")
            error_detail = str(e.message)
            return Response({"error": f"Veritabanı Hatası: {error_detail}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Egzersiz tamamlama hatası: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def problem_chain_test(request):
    """Problem Chain test page"""
    return render(request, 'problem_chain_test.html')
