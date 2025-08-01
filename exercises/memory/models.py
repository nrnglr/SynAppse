from django.db import models
import uuid


class MemorySession(models.Model):
    """
    Memory Exercise Session Model
    Tracks user's memory and synthesis performance
    """
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ]
    
    # Q&A related choices - no longer needed but keeping for migration compatibility
    SYNTHESIS_TYPE_CHOICES = [
        ('simplify', 'Basitleştirme'),
        ('connect', 'Bağlantı Kurma'),
    ]
    
    # Session Management
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    
    # Exercise Configuration
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    selected_topic = models.CharField(max_length=100, blank=True)
    topic_options = models.JSONField(default=list)  # Store 3 topic options
    
    # Content
    original_text = models.TextField(blank=True)
    text_keywords = models.JSONField(default=list)  # AI-generated keywords from text
    
    # User Responses
    user_recall = models.TextField(blank=True)  # What user learned/understood
    user_keywords = models.JSONField(default=list)  # [keyword1, keyword2, keyword3]
    
    # Q&A System - replaces synthesis
    user_question = models.TextField(blank=True)  # User's question about the text
    ai_answer = models.TextField(blank=True)  # Gemini's answer to user's question
    question_is_relevant = models.BooleanField(default=False)  # Gemini validation result
    
    # Performance Metrics - synthesis score removed
    scores = models.JSONField(default=dict)  # {recall: 8, keywords: 7, overall: 8}
    reading_time = models.IntegerField(default=0)  # Seconds spent reading
    
    # AI Analysis
    ai_feedback = models.TextField(blank=True)
    alternative_keywords = models.JSONField(default=list)  # AI suggestions
    
    class Meta:
        db_table = 'memory_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Memory Session {self.session_id} - {self.difficulty} - {self.selected_topic}"
    
    def get_overall_score(self):
        """Calculate overall score from individual metrics (no synthesis)"""
        if not self.scores:
            return 0
        
        scores_list = [
            self.scores.get('recall', 0),
            self.scores.get('keywords', 0)
        ]
        
        return round(sum(scores_list) / len(scores_list), 1) if scores_list else 0
    
    def get_progress_percentage(self):
        """Return completion progress as percentage"""
        if self.is_completed:
            return 100
        elif self.user_question:
            return 75
        elif self.user_recall:
            return 50
        elif self.original_text:
            return 25
        else:
            return 0
