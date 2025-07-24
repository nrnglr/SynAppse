from django.db import models
from exercises.models import BaseExercise

class WordBridgeExercise(BaseExercise):
    """
    Word Bridge exercise model
    """
    # Word Bridge specific fields will be added here
    
    class Meta:
        db_table = 'word_bridge_exercises'
