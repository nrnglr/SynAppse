from django.db import models
from django.contrib.auth.models import User
from exercises.models import BaseExercise
from django.utils import timezone
from datetime import timedelta
import hashlib
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
    
    # Data Collection for Pattern Recognition
    problem_ratings = models.JSONField(default=list)  # [4, 3, 5, 2, 4] her problem için rating
    engagement_times = models.JSONField(default=list)  # [45, 67, 23, 89, 34] her problem için süre (saniye)
    overall_session_rating = models.IntegerField(null=True, blank=True)  # 1-5 genel deneyim
    
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
    
    def add_problem_rating(self, rating):
        """Add rating for current problem (1-5)"""
        if rating in range(1, 6):
            self.problem_ratings.append(rating)
            self.save()
    
    def add_engagement_time(self, time_seconds):
        """Add engagement time for current problem"""
        self.engagement_times.append(int(time_seconds))
        self.save()
    
    def set_session_rating(self, rating):
        """Set overall session rating (1-5)"""
        if rating in range(1, 6):
            self.overall_session_rating = rating
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
    
    def get_overall_score(self):
        """Calculate overall score from individual metrics"""
        if not self.creativity_score or not self.practicality_score:
            return 0
        
        return round((self.creativity_score + self.practicality_score) / 2, 1)


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


class UserLearningPattern(models.Model):
    """
    Individual user learning patterns and preferences
    """
    user = models.OneToOneField(
        User, 
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


class CommunityLearningData(models.Model):
    """
    Stores successful problem-solution pairs for AI learning
    Tracks high-quality interactions that AI can learn from
    """
    # Problem-Solution pair
    problem_text = models.TextField()
    solution_text = models.TextField()
    problem_hash = models.CharField(max_length=64, db_index=True)
    
    # Quality metrics
    user_rating = models.IntegerField()  # 1-5 rating user gave
    overall_score = models.FloatField()  # Session overall score (creativity + practicality)
    creativity_score = models.IntegerField(null=True, blank=True)
    practicality_score = models.IntegerField(null=True, blank=True)
    session_rating = models.IntegerField(null=True, blank=True)  # Overall session rating
    
    # Context information
    difficulty = models.CharField(max_length=10)
    round_number = models.IntegerField()  # Which round in the chain (1-5)
    engagement_time = models.FloatField(null=True, blank=True)  # Time spent on this problem
    
    # Pattern analysis
    problem_category = models.CharField(max_length=50, null=True, blank=True)
    success_pattern = models.JSONField(default=dict)  # Pattern features that made it successful
    
    # Community metrics
    times_referenced = models.IntegerField(default=0)  # How many times AI used this as example
    avg_success_rate_when_used = models.FloatField(default=0.0)  # Success rate when AI used this pattern
    
    # User context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_learning_data'
        ordering = ['-overall_score', '-created_at']
        indexes = [
            models.Index(fields=['difficulty', 'overall_score']),
            models.Index(fields=['problem_hash']),
            models.Index(fields=['user_rating', 'overall_score']),
        ]
    
    def __str__(self):
        return f"Learning Data - Score: {self.overall_score} - Difficulty: {self.difficulty}"
    
    @classmethod
    def create_from_session(cls, session, round_index):
        """Create learning data from a successful session round"""
        if round_index >= len(session.problems) or round_index >= len(session.solutions):
            return None
        
        problem_text = session.problems[round_index]
        solution_text = session.solutions[round_index]
        
        # Generate consistent hash for the problem
        problem_hash = hashlib.sha256(problem_text.encode()).hexdigest()
        
        return cls.objects.create(
            problem_text=problem_text,
            solution_text=solution_text,
            problem_hash=problem_hash,
            user_rating=session.problem_ratings[round_index] if session.problem_ratings and len(session.problem_ratings) > round_index else 5,
            overall_score=session.get_overall_score(),
            creativity_score=session.creativity_score,
            practicality_score=session.practicality_score,
            session_rating=session.overall_session_rating,
            difficulty=session.difficulty,
            round_number=round_index + 1,
            engagement_time=session.engagement_times[round_index] if session.engagement_times and len(session.engagement_times) > round_index else None,
            user=session.user,
            ip_address=session.ip_address
        )
    
    @classmethod
    def get_successful_examples(cls, difficulty, min_score=4.0, limit=10):
        """Get successful problem examples for AI learning"""
        return cls.objects.filter(
            difficulty=difficulty,
            overall_score__gte=min_score,
            user_rating__gte=4
        ).order_by('-overall_score', '-user_rating')[:limit]
    
    @classmethod
    def get_pattern_analysis(cls, difficulty):
        """Analyze patterns in successful problems for given difficulty"""
        successful_data = cls.get_successful_examples(difficulty, limit=50)
        
        if not successful_data.exists():
            return {}
        
        # Basic pattern analysis
        patterns = {
            'avg_word_count': sum(len(data.problem_text.split()) for data in successful_data) / successful_data.count(),
            'avg_score': sum(data.overall_score for data in successful_data) / successful_data.count(),
            'most_common_length': 'medium',  # Can be enhanced with actual analysis
            'success_indicators': []
        }
        
        return patterns
    
    def categorize_problem(self):
        """Automatically categorize the problem type"""
        problem_lower = self.problem_text.lower()
        
        if any(word in problem_lower for word in ['teknoloji', 'yapay zeka', 'bilgisayar', 'internet']):
            return 'technology'
        elif any(word in problem_lower for word in ['çevre', 'doğa', 'iklim', 'kirlilik']):
            return 'environment'
        elif any(word in problem_lower for word in ['eğitim', 'okul', 'öğrenci', 'öğretmen']):
            return 'education'
        elif any(word in problem_lower for word in ['sağlık', 'hastane', 'doktor', 'hastalık']):
            return 'health'
        elif any(word in problem_lower for word in ['ekonomi', 'para', 'iş', 'ticaret']):
            return 'economy'
        else:
            return 'general'
    
    def extract_success_pattern(self):
        """Extract what made this problem-solution pair successful"""
        patterns = {
            'problem_length': len(self.problem_text.split()),
            'solution_length': len(self.solution_text.split()),
            'category': self.categorize_problem(),
            'engagement_score': min(5, self.engagement_time / 30) if self.engagement_time else 3,
            'rating_consistency': abs(self.user_rating - self.overall_score) <= 1,
        }
        
        return patterns
