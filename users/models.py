from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
import json

class UserProfile(models.Model):
    """
    Extended user profile for brain exercise statistics
    MVP version with essential fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Basic Profile Info
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Exercise Statistics
    total_exercises_completed = models.IntegerField(default=0)
    
    # Exercise Type Statistics
    memory_exercises_completed = models.IntegerField(default=0)
    word_bridge_exercises_completed = models.IntegerField(default=0)
    problem_chain_exercises_completed = models.IntegerField(default=0)
    
    # Performance Tracking
    average_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    total_time_spent = models.IntegerField(default=0)  # in seconds
    
    # User Preferences
    email_notifications = models.BooleanField(default=True)
    
    # Supabase Integration
    supabase_synced = models.BooleanField(default=False)
    supabase_user_id = models.CharField(max_length=100, null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def get_avatar_url(self):
        """Get avatar URL or default"""
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'
    
    @property
    def completion_rate(self):
        """Calculate completion rate percentage"""
        if self.total_exercises_completed == 0:
            return 0
        return round((self.total_exercises_completed / 100) * 100, 1)
    
    def get_exercise_distribution(self):
        """Get exercise type distribution as dictionary"""
        return {
            'memory': self.memory_exercises_completed,
            'word_bridge': self.word_bridge_exercises_completed,
            'problem_chain': self.problem_chain_exercises_completed,
        }
    
    def update_exercise_stats(self, exercise_type, score=None, time_spent=None):
        """Update exercise statistics"""
        # Update total count
        self.total_exercises_completed += 1
        
        # Update exercise type specific count
        if exercise_type == 'memory':
            self.memory_exercises_completed += 1
        elif exercise_type == 'word_bridge':
            self.word_bridge_exercises_completed += 1
        elif exercise_type == 'problem_chain':
            self.problem_chain_exercises_completed += 1
        
        # Update scores if provided
        if score is not None:
            if self.best_score < score:
                self.best_score = score
            
            # Calculate new average score
            total_score = (self.average_score * (self.total_exercises_completed - 1)) + score
            self.average_score = round(total_score / self.total_exercises_completed, 2)
        
        # Update time spent
        if time_spent is not None:
            self.total_time_spent += time_spent
        
        self.save()


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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)
