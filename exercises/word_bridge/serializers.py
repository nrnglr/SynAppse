from rest_framework import serializers
from .models import WordBridgeExercise
from exercises.serializers import BaseExerciseSerializer

class WordBridgeSerializer(BaseExerciseSerializer):
    """
    Serializer for Word Bridge exercises
    """
    class Meta(BaseExerciseSerializer.Meta):
        model = WordBridgeExercise
