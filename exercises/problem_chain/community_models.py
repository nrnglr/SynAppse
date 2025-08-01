from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib
import json

class CommunityProblemMetrics(models.Model):
    """
    Community-wide problem performance tracking
    Tracks how well problems perform across all users
    """
    # Problem identification
    problem_hash = models.CharField(max_length=64, unique=True, db_index=True)
    problem_text = models.TextField()
    difficulty_level = models.CharField(max_length=10)
    
    # Community metrics
    total_attempts = models.IntegerField(default=0)
    successful_completions = models.IntegerField(default=0)
    total_rating_sum = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Performance metrics
    avg_engagement_time = models.FloatField(default=0.0)  # Average seconds spent
    success_rate = models.FloatField(default=0.0)  # % of successful completions
    avg_rating = models.FloatField(default=0.0)  # Average user rating
    
    # Pattern categorization
    problem_category = models.CharField(max_length=50, null=True, blank=True)
    user_preference_score = models.FloatField(default=0.0)  # How much users like this type
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_problem_metrics'
        ordering = ['-avg_rating', '-success_rate']
    
    def __str__(self):
        return f"Problem #{self.problem_hash[:8]} - Rating: {self.avg_rating:.1f}"
    
    @classmethod
    def get_or_create_for_problem(cls, problem_text, difficulty):
        """Get or create metrics for a problem"""
        problem_hash = cls.generate_problem_hash(problem_text)
        
        metrics, created = cls.objects.get_or_create(
            problem_hash=problem_hash,
            defaults={
                'problem_text': problem_text,
                'difficulty_level': difficulty,
            }
        )
        return metrics
    
    @staticmethod
    def generate_problem_hash(problem_text):
        """Generate consistent hash for problem text"""
        # Normalize text for consistent hashing
        normalized_text = problem_text.strip().lower()
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
    
    def update_metrics(self, rating=None, engagement_time=None, was_successful=False):
        """Update metrics with new data point"""
        self.total_attempts += 1
        
        if was_successful:
            self.successful_completions += 1
        
        if rating is not None and 1 <= rating <= 5:
            self.total_rating_sum += rating
            self.rating_count += 1
            self.avg_rating = self.total_rating_sum / self.rating_count
        
        if engagement_time is not None and engagement_time > 0:
            # Calculate rolling average
            current_total_time = self.avg_engagement_time * (self.total_attempts - 1)
            self.avg_engagement_time = (current_total_time + engagement_time) / self.total_attempts
        
        # Update success rate
        self.success_rate = (self.successful_completions / self.total_attempts) * 100
        
        # Calculate user preference score (combination of rating and success rate)
        if self.avg_rating > 0:
            self.user_preference_score = (self.avg_rating * 0.7) + (self.success_rate * 0.003)  # Scale success_rate to 0-0.3
        
        self.save()
    
    def is_high_performing(self):
        """Check if this is a high-performing problem"""
        return (
            self.avg_rating >= 4.0 and 
            self.success_rate >= 70 and 
            self.total_attempts >= 5
        )
    
    def is_low_performing(self):
        """Check if this is a low-performing problem"""
        return (
            self.avg_rating <= 2.5 or 
            self.success_rate <= 30
        ) and self.total_attempts >= 3


class UserLearningPattern(models.Model):
    """
    Individual user learning patterns and preferences
    """
    user = models.OneToOneField(
        'auth.User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='learning_pattern'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # For anonymous users
    
    # Learning preferences
    preferred_difficulty = models.CharField(max_length=10, default='medium')
    avg_engagement_time = models.FloatField(default=0.0)
    problem_preference_scores = models.JSONField(default=dict)  # {"creative": 4.2, "logical": 3.8}
    
    # Performance metrics
    total_sessions = models.IntegerField(default=0)
    avg_session_rating = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)
    
    # Pattern classification
    learning_style = models.CharField(max_length=30, default='balanced')  # fast, methodical, creative, analytical
    confidence_level = models.FloatField(default=0.5)  # 0-1 how confident we are in this classification
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_learning_patterns'
    
    def __str__(self):
        user_str = self.user.username if self.user else f"Anonymous-{self.ip_address}"
        return f"{user_str} - Style: {self.learning_style}"
    
    @classmethod
    def get_or_create_for_user(cls, user=None, ip_address=None):
        """Get or create learning pattern for user"""
        if user and user.is_authenticated:
            pattern, created = cls.objects.get_or_create(
                user=user,
                defaults={'ip_address': ip_address}
            )
        else:
            pattern, created = cls.objects.get_or_create(
                ip_address=ip_address,
                user=None
            )
        return pattern
    
    def update_from_session(self, session):
        """Update pattern based on completed session"""
        self.total_sessions += 1
        
        # Update session rating average
        if session.overall_session_rating:
            current_total = self.avg_session_rating * (self.total_sessions - 1)
            self.avg_session_rating = (current_total + session.overall_session_rating) / self.total_sessions
        
        # Update completion rate
        completion_rate = 100 if session.is_completed else 0
        current_total_rate = self.completion_rate * (self.total_sessions - 1)
        self.completion_rate = (current_total_rate + completion_rate) / self.total_sessions
        
        # Update engagement time
        if session.engagement_times:
            avg_session_time = sum(session.engagement_times) / len(session.engagement_times)
            current_total_time = self.avg_engagement_time * (self.total_sessions - 1)
            self.avg_engagement_time = (current_total_time + avg_session_time) / self.total_sessions
        
        # Classify learning style based on patterns
        self._classify_learning_style()
        
        self.save()
    
    def _classify_learning_style(self):
        """Classify user's learning style based on patterns"""
        if self.avg_engagement_time < 30:
            self.learning_style = 'fast'
            self.confidence_level = min(0.8, self.total_sessions / 10)
        elif self.avg_engagement_time > 90:
            self.learning_style = 'methodical'
            self.confidence_level = min(0.8, self.total_sessions / 10)
        elif self.avg_session_rating >= 4.0:
            self.learning_style = 'engaged'
            self.confidence_level = min(0.9, self.total_sessions / 8)
        else:
            self.learning_style = 'balanced'
            self.confidence_level = min(0.6, self.total_sessions / 15)
