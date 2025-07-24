from rest_framework import serializers
from .models import BaseExercise

class BaseExerciseSerializer(serializers.ModelSerializer):
    """
    Base serializer for all exercises
    """
    class Meta:
        abstract = True
        fields = ['id', 'difficulty', 'title', 'instructions', 'metadata', 
                 'is_completed', 'user_response', 'ai_feedback', 'created_at']
