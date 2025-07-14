from django.db import models
from django.contrib.auth.models import User

class CreativityExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10)  # easy, medium, hard
    words = models.JSONField()  # Egzersiz için üretilen kelimeler
    image_path = models.CharField(max_length=255, blank=True, null=True)  # Üretilen resmin yolu
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.difficulty} exercise at {self.created_at}"
