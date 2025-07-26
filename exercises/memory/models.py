from django.db import models
from exercises.models import BaseExercise

class MemoryExercise(BaseExercise):
    """
    Memory exercise model
    """
    # Memory specific fields will be added here
    
    class Meta:
        db_table = 'memory_exercises'
