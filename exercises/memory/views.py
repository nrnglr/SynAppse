from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MemoryExercise

class MemoryCreateView(APIView):
    """
    Create new Memory exercise
    """
    def post(self, request):
        # Memory exercise creation logic will be added here
        return Response({"message": "Memory exercise creation"}, status=status.HTTP_201_CREATED)

class MemoryListView(APIView):
    """
    List Memory exercises
    """
    def get(self, request):
        # Memory exercise listing logic will be added here
        return Response({"exercises": []}, status=status.HTTP_200_OK)

class MemoryCompleteView(APIView):
    """
    Complete Memory exercise
    """
    def post(self, request, exercise_id):
        # Memory completion logic will be added here
        return Response({"message": "Exercise completed"}, status=status.HTTP_200_OK)
