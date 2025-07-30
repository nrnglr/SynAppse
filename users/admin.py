from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserExerciseActivity, DailyUserStats


class UserProfileInline(admin.StackedInline):
    """Inline UserProfile in User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'avatar', 'bio', 
        'total_exercises_completed', 'average_score', 'best_score',
        'email_notifications', 'supabase_synced'
    )
    readonly_fields = (
        'total_exercises_completed', 'average_score', 'best_score',
        'memory_exercises_completed', 'word_bridge_exercises_completed', 
        'problem_chain_exercises_completed', 'total_time_spent'
    )


class CustomUserAdmin(UserAdmin):
    """Custom User Admin with Profile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_total_exercises')
    list_filter = UserAdmin.list_filter
    
    def get_total_exercises(self, obj):
        """Get total exercises completed"""
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.total_exercises_completed
        return 0
    get_total_exercises.short_description = 'Total Exercises'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """UserProfile Admin"""
    list_display = (
        'user', 'total_exercises_completed', 
        'average_score', 'best_score', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'last_sync_at')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('Exercise Statistics', {
            'fields': (
                'total_exercises_completed', 
                'memory_exercises_completed', 'word_bridge_exercises_completed',
                'problem_chain_exercises_completed', 'average_score', 'best_score',
                'total_time_spent'
            )
        }),
        ('Preferences', {
            'fields': ('email_notifications',)
        }),
        ('Supabase Integration', {
            'fields': ('supabase_synced', 'supabase_user_id', 'last_sync_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


# Unregister the default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserExerciseActivity)
class UserExerciseActivityAdmin(admin.ModelAdmin):
    """User Exercise Activity Admin"""
    list_display = (
        'user', 'exercise_type', 'difficulty', 'status', 
        'overall_score', 'duration_minutes', 'started_at'
    )
    list_filter = (
        'exercise_type', 'difficulty', 'status', 'started_at'
    )
    search_fields = ('user__username', 'user__email', 'session_id')
    readonly_fields = ('id', 'started_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Activity Info', {
            'fields': ('id', 'user', 'exercise_type', 'difficulty', 'session_id')
        }),
        ('Status', {
            'fields': ('status', 'started_at', 'completed_at')
        }),
        ('Performance', {
            'fields': ('scores', 'overall_score', 'completion_time'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('exercise_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def duration_minutes(self, obj):
        """Display duration in minutes"""
        return obj.duration_minutes
    duration_minutes.short_description = 'Duration (min)'


@admin.register(DailyUserStats)
class DailyUserStatsAdmin(admin.ModelAdmin):
    """Daily User Stats Admin"""
    list_display = (
        'user', 'date', 'total_exercises', 'average_score', 
        'best_score', 'total_time_spent'
    )
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Date & User', {
            'fields': ('user', 'date')
        }),
        ('Exercise Counts', {
            'fields': (
                'total_exercises', 'memory_exercises', 
                'word_bridge_exercises', 'problem_chain_exercises'
            )
        }),
        ('Performance', {
            'fields': ('average_score', 'best_score', 'total_time_spent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
