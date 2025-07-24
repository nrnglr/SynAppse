from rest_framework import serializers
from .models import MemoryExercise
from exercises.serializers import BaseExerciseSerializer

class MemorySerializer(BaseExerciseSerializer):
    """
    Serializer for Memory exercises
    """
    class Meta(BaseExerciseSerializer.Meta):
        model = MemoryExercise
