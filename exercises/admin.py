from django.contrib import admin
from .problem_chain.models import ProblemChainSession
from .word_bridge.models import WordBridgeSession
from .memory.models import MemorySession

@admin.register(ProblemChainSession)
class ProblemChainSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'difficulty', 'current_round', 'is_completed', 'created_at']
    list_filter = ['difficulty', 'is_completed', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user', 'ip_address', 'difficulty')
        }),
        ('Progress', {
            'fields': ('current_round', 'total_rounds', 'is_completed', 'completion_time')
        }),
        ('Content', {
            'fields': ('problems', 'solutions'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('final_feedback', 'creativity_score', 'practicality_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WordBridgeSession)
class WordBridgeSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'user', 'difficulty', 'selected_start_word', 
        'target_word', 'current_step', 'status', 'is_completed', 'created_at'
    ]
    list_filter = [
        'difficulty', 'status', 'is_completed', 'created_at'
    ]
    search_fields = [
        'session_id', 'user__username', 'target_word', 'selected_start_word'
    ]
    readonly_fields = [
        'session_id', 'created_at', 'updated_at', 'started_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Session Bilgileri', {
            'fields': ('session_id', 'user', 'difficulty', 'status')
        }),
        ('Egzersiz Kelilmeleri', {
            'fields': ('target_word', 'start_word_options', 'selected_start_word')
        }),
        ('Kullanıcı İlerlemesi', {
            'fields': ('submitted_words', 'current_step', 'is_completed', 'time_limit')
        }),
        ('AI Desteği', {
            'fields': ('ai_solution_path', 'hints', 'hints_used'),
            'classes': ('collapse',)
        }),
        ('Sonuçlar', {
            'fields': ('final_score', 'ai_evaluation', 'alternative_solutions'),
            'classes': ('collapse',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Queryset'i optimize et"""
        return super().get_queryset(request).select_related('user')
    
    def word_chain_display(self, obj):
        """Kelime zincirini güzel bir şekilde göster"""
        chain = obj.get_full_word_chain()
        return ' → '.join(chain) if chain else '-'
    word_chain_display.short_description = 'Kelime Zinciri'
    
    def hints_count(self, obj):
        """Kullanılan hint sayısı"""
        return len(obj.hints_used)
    hints_count.short_description = 'Kullanılan Hint'
    
    def completion_time_display(self, obj):
        """Tamamlanma süresini göster"""
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            return f"{int(duration.total_seconds())}s"
        return '-'
    completion_time_display.short_description = 'Süre'

@admin.register(MemorySession)  
class MemorySessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'difficulty', 'selected_topic', 'is_completed', 'created_at']
    list_filter = ['difficulty', 'is_completed', 'question_is_relevant', 'created_at']
    search_fields = ['session_id', 'selected_topic']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'difficulty', 'selected_topic', 'is_completed')
        }),
        ('Content', {
            'fields': ('topic_options', 'original_text', 'text_keywords'),
            'classes': ('collapse',),
        }),
        ('User Responses', {
            'fields': ('user_recall', 'user_keywords', 'user_question', 'ai_answer', 'question_is_relevant'),
            'classes': ('collapse',),
        }),
        ('Performance', {
            'fields': ('scores', 'reading_time', 'ai_feedback'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
