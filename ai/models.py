from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class CreativityExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10)  # easy, medium, hard
    words = models.JSONField()  # Egzersiz için üretilen kelimeler
    image_path = models.CharField(max_length=255, blank=True, null=True)  # Üretilen resmin yolu
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.difficulty} exercise at {self.created_at}"

class MemoryExercise(models.Model):
    difficulty = models.CharField(max_length=10)
    words = models.JSONField()
    image_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"MemoryExercise {self.id} - {self.difficulty}"
