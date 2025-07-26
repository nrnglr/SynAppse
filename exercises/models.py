from django.db import models
from django.contrib.auth.models import User

class BaseExercise(models.Model):
    """
    Base model for all brain exercises
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    metadata = models.JSONField(default=dict)  # Exercise-specific data
    is_completed = models.BooleanField(default=False)
    user_response = models.JSONField(default=dict)  # User's answers
    ai_feedback = models.TextField(blank=True, null=True)  # Gemini feedback
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.title} ({self.difficulty})"
