from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for caching daily exercises
    """
    
    @staticmethod
    def get_daily_exercise_key(exercise_type: str, difficulty: str, date: str) -> str:
        """
        Generate cache key for daily exercises
        """
        return f"daily_exercise_{exercise_type}_{difficulty}_{date}"
    
    @staticmethod
    def get_daily_exercise(exercise_type: str, difficulty: str, date: str) -> dict:
        """
        Get daily exercise from cache
        """
        cache_key = CacheService.get_daily_exercise_key(exercise_type, difficulty, date)
        return cache.get(cache_key)
    
    @staticmethod
    def set_daily_exercise(exercise_type: str, difficulty: str, date: str, exercise_data: dict, timeout: int = 86400) -> None:
        """
        Set daily exercise in cache (default 24 hours)
        """
        cache_key = CacheService.get_daily_exercise_key(exercise_type, difficulty, date)
        cache.set(cache_key, exercise_data, timeout)
    
    @staticmethod
    def clear_daily_exercises(date: str = None) -> None:
        """
        Clear daily exercises cache
        """
        if date:
            # Clear specific date
            for exercise_type in ['word_bridge', 'problem_chain', 'memory']:
                for difficulty in ['easy', 'medium', 'hard']:
                    cache_key = CacheService.get_daily_exercise_key(exercise_type, difficulty, date)
                    cache.delete(cache_key)
        else:
            # Clear all cache (use with caution)
            cache.clear()
