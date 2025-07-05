from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .gemini.client import (
    generate_critical_exercise,
    generate_memory_exercise,
    generate_creativity_exercise,
    generate_strategy_exercise
)
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ExerciseGenerateView(APIView):
    def get(self, request, exercise_type=None):
        generators = {
            "critical": generate_critical_exercise,
            "memory": generate_memory_exercise,
            "creativity": generate_creativity_exercise,
            "strategy": generate_strategy_exercise
        }

        if exercise_type not in generators:
            return Response({"error": "Geçersiz egzersiz tipi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = generators[exercise_type]()
            return Response({
                "type": exercise_type,
                "exercise": content
            })
        except Exception as e:
            logger.error(f"Hata: {str(e)}", exc_info=True)
            if settings.DEBUG:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": "Sunucu hatası"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExerciseSubmitView(APIView):
    def post(self, request, exercise_type=None):
        answer = request.data.get("answer")
        if not answer:
            return Response({"error": "Cevap gönderilmedi"}, status=status.HTTP_400_BAD_REQUEST)

        # İleride doğrulama, puanlama vb. eklenecek
        return Response({
            "status": "Cevap başarıyla alındı.",
            "type": exercise_type,
            "answer": answer
        })
