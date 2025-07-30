from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json


class BrainHealthScore(models.Model):
    """
    Stores calculated brain health scores for users
    Updated every 4 hours when user visits profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='brain_health')
    
    # Core Metrics (0-10 scale)
    frequency_score = models.FloatField(default=0.0, help_text="Daily exercise frequency (7-day window)")
    performance_score = models.FloatField(default=0.0, help_text="Average overall scores")
    consistency_score = models.FloatField(default=0.0, help_text="Score consistency (lower std dev = higher score)")
    improvement_score = models.FloatField(default=0.0, help_text="Linear regression trend")
    
    # Bonus Metrics
    exercise_variety_bonus = models.FloatField(default=0.0, help_text="Bonus for doing different exercise types")
    difficulty_bonus = models.FloatField(default=0.0, help_text="Bonus for harder exercises")
    streak_bonus = models.FloatField(default=0.0, help_text="Bonus for consecutive days")
    
    # Final Score
    brain_health_score = models.FloatField(default=0.0, help_text="Final calculated score (0-10)")
    
    # Metadata
    total_exercises = models.IntegerField(default=0)
    analysis_period_days = models.IntegerField(default=7)
    
    # Exercise Type Breakdown
    memory_exercises = models.IntegerField(default=0)
    word_bridge_exercises = models.IntegerField(default=0)
    problem_chain_exercises = models.IntegerField(default=0)
    
    # Cache Management
    last_calculated = models.DateTimeField(auto_now=True)
    is_cache_valid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brain_health_scores'
        verbose_name = 'Brain Health Score'
        verbose_name_plural = 'Brain Health Scores'
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.brain_health_score:.1f}/10"
    
    def is_cache_expired(self):
        """Check if cache is older than 4 hours"""
        if not self.last_calculated:
            return True
        return timezone.now() - self.last_calculated > timedelta(hours=4)
    
    def get_exercise_distribution(self):
        """Return exercise type distribution as percentages"""
        total = self.total_exercises
        if total == 0:
            return {
                'memory': 0, 'word_bridge': 0, 'problem_chain': 0,
                'memory_percentage': 0.0, 'word_bridge_percentage': 0.0, 'problem_chain_percentage': 0.0
            }
        
        memory_pct = round((self.memory_exercises / total) * 100, 1)
        word_bridge_pct = round((self.word_bridge_exercises / total) * 100, 1)
        problem_chain_pct = round((self.problem_chain_exercises / total) * 100, 1)
        
        return {
            'memory': self.memory_exercises,
            'word_bridge': self.word_bridge_exercises,
            'problem_chain': self.problem_chain_exercises,
            'memory_percentage': memory_pct,
            'word_bridge_percentage': word_bridge_pct,
            'problem_chain_percentage': problem_chain_pct,
        }
    
    def get_score_breakdown(self):
        """Return detailed score breakdown for frontend"""
        return {
            'core_metrics': {
                'frequency': self.frequency_score,
                'performance': self.performance_score,
                'consistency': self.consistency_score,
                'improvement': self.improvement_score,
            },
            'bonuses': {
                'variety': self.exercise_variety_bonus,
                'difficulty': self.difficulty_bonus,
                'streak': self.streak_bonus,
            },
            'final_score': self.brain_health_score,
            'total_exercises': self.total_exercises,
            'exercise_distribution': self.get_exercise_distribution(),
        }


class DailyAnalytics(models.Model):
    """
    Daily aggregated analytics for faster calculations
    Used for trend analysis and historical data
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_analytics')
    date = models.DateField()
    
    # Daily Metrics
    exercises_completed = models.IntegerField(default=0)
    average_score = models.FloatField(null=True, blank=True)
    
    # Exercise Type Counts
    memory_count = models.IntegerField(default=0)
    word_bridge_count = models.IntegerField(default=0)
    problem_chain_count = models.IntegerField(default=0)
    
    # Performance Metrics
    best_score = models.FloatField(null=True, blank=True)
    total_time_spent = models.IntegerField(default=0)  # seconds
    
    # Difficulty Distribution
    easy_exercises = models.IntegerField(default=0)
    medium_exercises = models.IntegerField(default=0)
    hard_exercises = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_analytics'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.exercises_completed} exercises)"


class AnalyticsCache(models.Model):
    """
    Cache storage for expensive calculations
    Used to store intermediate results and avoid recalculation
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_cache')
    cache_key = models.CharField(max_length=200, db_index=True)
    cache_data = models.JSONField()
    expires_at = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_cache'
        unique_together = ['user', 'cache_key']
        indexes = [
            models.Index(fields=['cache_key', 'expires_at']),
            models.Index(fields=['user', 'cache_key']),
        ]
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @classmethod
    def get_cache(cls, user, cache_key):
        """Get cached data if valid"""
        try:
            cache = cls.objects.get(user=user, cache_key=cache_key)
            if cache.is_expired():
                cache.delete()
                return None
            return cache.cache_data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cache(cls, user, cache_key, data, hours=4):
        """Set cache data with expiration"""
        expires_at = timezone.now() + timedelta(hours=hours)
        cache, created = cls.objects.update_or_create(
            user=user,
            cache_key=cache_key,
            defaults={
                'cache_data': data,
                'expires_at': expires_at
            }
        )
        return cache
