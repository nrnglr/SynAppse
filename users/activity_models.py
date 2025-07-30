from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UserExerciseActivity(models.Model):
    """
    Kullanıcı egzersiz aktivitelerini detaylı takip eder
    """
    EXERCISE_TYPES = [
        ('memory', 'Hafıza Egzersizi'),
        ('word_bridge', 'Kelime Köprüsü'),
        ('problem_chain', 'Problem Zinciri'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ]
    
    STATUS_CHOICES = [
        ('started', 'Başlatıldı'),
        ('completed', 'Tamamlandı'),
        ('abandoned', 'Yarıda Bırakıldı'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_activities')
    
    # Exercise info
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    session_id = models.CharField(max_length=100, help_text="Original exercise session ID")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Performance data
    scores = models.JSONField(null=True, blank=True, help_text="Exercise specific scores")
    overall_score = models.FloatField(null=True, blank=True)
    completion_time = models.IntegerField(null=True, blank=True, help_text="Time in seconds")
    
    # Exercise specific data
    exercise_data = models.JSONField(null=True, blank=True, help_text="Exercise specific responses/answers")
    
    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_exercise_activities'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'exercise_type']),
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['status', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_exercise_type_display()} - {self.status}"
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.completion_time:
            return round(self.completion_time / 60, 1)
        return None
    
    def mark_completed(self, scores=None, overall_score=None, exercise_data=None):
        """Mark activity as completed with scores"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        if scores:
            self.scores = scores
        if overall_score:
            self.overall_score = overall_score
        if exercise_data:
            self.exercise_data = exercise_data
            
        # Calculate completion time
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            self.completion_time = int(duration.total_seconds())
        
        self.save()
        
        # Update user profile stats
        profile = self.user.userprofile
        profile.update_exercise_stats(
            exercise_type=self.exercise_type,
            score=self.overall_score,
            time_spent=self.completion_time
        )
    
    def mark_abandoned(self):
        """Mark activity as abandoned"""
        self.status = 'abandoned'
        self.save()


class DailyUserStats(models.Model):
    """
    Günlük kullanıcı istatistikleri için özetleme tablosu
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    
    # Daily counts
    total_exercises = models.IntegerField(default=0)
    memory_exercises = models.IntegerField(default=0)
    word_bridge_exercises = models.IntegerField(default=0)
    problem_chain_exercises = models.IntegerField(default=0)
    
    # Daily performance
    average_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    total_time_spent = models.IntegerField(default=0)  # in seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_user_stats'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.total_exercises} exercises"
