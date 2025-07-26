from django.db import models
from django.contrib.auth.models import User
from exercises.models import BaseExercise
import uuid

class ProblemChainSession(models.Model):
    """
    Problem Chain exercise session model
    Manages the interactive problem-solution chain
    """
    # Session identification
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Anonim için null
    ip_address = models.GenericIPAddressField()  # Spam kontrolü için
    
    # Exercise configuration
    difficulty = models.CharField(
        max_length=10, 
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    
    # Session data
    problems = models.JSONField(default=list)  # ["İlk problem", "İkinci problem", ...]
    solutions = models.JSONField(default=list)  # ["İlk çözüm", "İkinci çözüm", ...]
    current_round = models.IntegerField(default=1)  # 1-5 arası
    total_rounds = models.IntegerField(default=5)
    
    # Status
    is_completed = models.BooleanField(default=False)
    completion_time = models.IntegerField(null=True, blank=True)  # Saniye cinsinden
    
    # Final results
    final_feedback = models.TextField(null=True, blank=True)
    creativity_score = models.IntegerField(null=True, blank=True)  # 1-5
    practicality_score = models.IntegerField(null=True, blank=True)  # 1-5
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'problem_chain_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Round {self.current_round}/{self.total_rounds}"
    
    @property
    def is_session_expired(self):
        """Check if session is older than 1 hour"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at > timedelta(hours=1)
    
    def add_problem(self, problem_text):
        """Add new problem to the chain"""
        self.problems.append(problem_text)
        self.save()
    
    def add_solution(self, solution_text):
        """Add user solution to the chain"""
        self.solutions.append(solution_text)
        self.current_round += 1
        self.save()
    
    def get_context_for_gemini(self):
        """Get problem-solution history for Gemini context"""
        context = []
        for i, (problem, solution) in enumerate(zip(self.problems, self.solutions)):
            context.append({
                'round': i + 1,
                'problem': problem,
                'solution': solution
            })
        return context
