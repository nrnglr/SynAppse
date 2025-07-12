from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from .gemini.service import GeminiService
from lobsmart.settings import supabase
import logging

logger = logging.getLogger(__name__)

class CreativityTestPageView(TemplateView):
    """
    Yaratıcılık egzersizlerini oluşturmak ve listelemek için kullanılan test sayfasını render eder.
    """
    template_name = "ai/test_creativity.html"

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
