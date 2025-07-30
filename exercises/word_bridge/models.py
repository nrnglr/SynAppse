from django.db import models
from django.contrib.auth.models import User
import uuid

class WordBridgeSession(models.Model):
    """
    Word Bridge exercise session model
    Tracks individual exercise sessions with step-by-step word submissions
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('completed', 'Tamamlandı'),
        ('timeout', 'Süre Doldu'),
        ('abandoned', 'Yarıda Bırakıldı'),
    ]
    
    # Session identifiers
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Exercise configuration
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    target_word = models.CharField(max_length=100)  # Hedef kelime
    start_word_options = models.JSONField(default=list)  # 3 başlangıç seçeneği
    selected_start_word = models.CharField(max_length=100, blank=True)  # Seçilen başlangıç
    
    # AI generated data
    ai_solution_path = models.JSONField(default=list)  # Gemini'nin örnek çözümü
    hints = models.JSONField(default=list)  # 3 seviyeli hint sistemi
    
    # User progress tracking
    submitted_words = models.JSONField(default=list)  # Kullanıcının submit ettiği kelimeler
    hints_used = models.JSONField(default=list)  # Kullanılan hint'ler [1,2,3]
    current_step = models.IntegerField(default=0)  # Hangi adımda
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timing
    time_limit = models.IntegerField(null=True, blank=True)  # Saniye cinsinden (60 veya 120)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Scoring
    final_score = models.JSONField(default=dict)  # {'logic': 8, 'creativity': 9, 'efficiency': 6, 'overall': 8}
    ai_evaluation = models.TextField(blank=True)  # Gemini'nin değerlendirmesi
    alternative_solutions = models.JSONField(default=list)  # Alternatif çözüm yolları
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'word_bridge_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"WordBridge: {self.selected_start_word} → {self.target_word} ({self.difficulty})"
    
    def get_time_limit_seconds(self):
        """Zorluk seviyesine göre süre limiti döndür"""
        if self.difficulty == 'medium':
            return 120  # 2 dakika
        elif self.difficulty == 'hard':
            return 60   # 1 dakika
        return None  # Kolay modda süre yok
    
    def get_hint_penalty(self):
        """Kullanılan hint sayısına göre puan kesintisi"""
        return len(self.hints_used) * 0.5
    
    def get_overall_score(self):
        """Calculate overall score from individual metrics"""
        if not self.final_score:
            return 0
        
        scores_list = [
            self.final_score.get('logic', 0),
            self.final_score.get('creativity', 0),
            self.final_score.get('efficiency', 0)
        ]
        
        return round(sum(scores_list) / len(scores_list), 1) if scores_list else 0
    
    def can_submit_more_words(self):
        """Daha fazla kelime submit edilebilir mi?"""
        return len(self.submitted_words) < 6 and self.status == 'active'
    
    def get_full_word_chain(self):
        """Tam kelime zincirini döndür: başlangıç + kullanıcı kelimeleri + hedef"""
        if not self.selected_start_word:
            return []
        
        chain = [self.selected_start_word]
        chain.extend(self.submitted_words)
        if self.is_completed:
            chain.append(self.target_word)
        return chain
