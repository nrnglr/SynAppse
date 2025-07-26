from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extended user profile for brain exercise statistics
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_exercises_completed = models.IntegerField(default=0)
    favorite_difficulty = models.CharField(max_length=10, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
