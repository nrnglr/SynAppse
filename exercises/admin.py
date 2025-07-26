from django.contrib import admin
from .problem_chain.models import ProblemChainSession
from .word_bridge.models import WordBridgeExercise  
from .memory.models import MemoryExercise

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

# Diğer egzersizler için placeholder admin'ler
@admin.register(WordBridgeExercise)
class WordBridgeExerciseAdmin(admin.ModelAdmin):
    pass

@admin.register(MemoryExercise)  
class MemoryExerciseAdmin(admin.ModelAdmin):
    pass
