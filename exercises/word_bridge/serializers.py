from rest_framework import serializers
from .models import WordBridgeSession

class WordBridgeSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Word Bridge sessions
    """
    session_id = serializers.UUIDField(read_only=True)
    word_chain = serializers.SerializerMethodField()
    hint_penalty = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = WordBridgeSession
        fields = [
            'session_id', 'difficulty', 'target_word', 'start_word_options',
            'selected_start_word', 'submitted_words', 'hints_used',
            'current_step', 'is_completed', 'status', 'time_limit',
            'final_score', 'word_chain', 'hint_penalty', 'time_remaining',
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'session_id', 'started_at', 'completed_at', 'final_score'
        ]
    
    def get_word_chain(self, obj):
        """Tam kelime zincirini döndür"""
        return obj.get_full_word_chain()
    
    def get_hint_penalty(self, obj):
        """Hint ceza puanını döndür"""
        return obj.get_hint_penalty()
    
    def get_time_remaining(self, obj):
        """Kalan süreyi döndür"""
        if not obj.time_limit or obj.status != 'active':
            return None
        
        from django.utils import timezone
        elapsed = (timezone.now() - obj.started_at).total_seconds()
        remaining = max(0, obj.time_limit - elapsed)
        return int(remaining)

class WordBridgeStartRequestSerializer(serializers.Serializer):
    """
    Egzersiz başlatma request serializer
    """
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='easy'
    )

class WordBridgeSelectStartRequestSerializer(serializers.Serializer):
    """
    Başlangıç kelimesi seçimi request serializer
    """
    session_id = serializers.UUIDField()
    selected_word = serializers.CharField(max_length=100)

class WordBridgeSubmitWordRequestSerializer(serializers.Serializer):
    """
    Kelime submit etme request serializer
    """
    session_id = serializers.UUIDField()
    word = serializers.CharField(max_length=100)
    
    def validate_word(self, value):
        """Kelime validasyonu"""
        if not value or not value.strip():
            raise serializers.ValidationError("Kelime boş olamaz")
        
        # Türkçe karakter ve boşluk kontrolü
        cleaned = value.strip().lower()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Kelime en az 2 karakter olmalı")
        
        return cleaned

class WordBridgeGetHintRequestSerializer(serializers.Serializer):
    """
    Hint alma request serializer
    """
    session_id = serializers.UUIDField()
    hint_level = serializers.ChoiceField(choices=[1, 2, 3])

class WordBridgeCompleteRequestSerializer(serializers.Serializer):
    """
    Egzersiz tamamlama request serializer
    """
    session_id = serializers.UUIDField()

class WordBridgeResultSerializer(serializers.Serializer):
    """
    Egzersiz sonucu response serializer
    """
    session_id = serializers.UUIDField()
    user_solution = serializers.ListField(child=serializers.CharField())
    scores = serializers.DictField()
    evaluation = serializers.CharField()
    connection_analysis = serializers.ListField(child=serializers.CharField())
    suggestions = serializers.CharField()
    alternative_solutions = serializers.ListField()
    ai_solution = serializers.ListField(child=serializers.CharField())
    hints_used = serializers.IntegerField()
    penalty = serializers.FloatField()
    completion_time = serializers.IntegerField(allow_null=True)
