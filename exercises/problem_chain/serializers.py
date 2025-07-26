from rest_framework import serializers
from .models import ProblemChainExercise
from exercises.serializers import BaseExerciseSerializer

class ProblemChainSerializer(BaseExerciseSerializer):
    """
    Serializer for Problem Chain exercises
    """
    class Meta(BaseExerciseSerializer.Meta):
        model = ProblemChainExercise
