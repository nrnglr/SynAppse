from django.contrib.auth.models import User
from django.db import models
from .models import UserExerciseActivity
import logging

logger = logging.getLogger(__name__)


def create_exercise_activity(user, exercise_type, difficulty, session_id):
    """
    Yeni bir egzersiz aktivitesi oluştur
    """
    try:
        if user and user.is_authenticated:
            activity = UserExerciseActivity.objects.create(
                user=user,
                exercise_type=exercise_type,
                difficulty=difficulty,
                session_id=session_id
            )
            logger.info(f"Exercise activity created: {activity.id} for user {user.username}")
            return activity
        else:
            logger.warning("Anonymous user - exercise activity not created")
            return None
    except Exception as e:
        logger.error(f"Error creating exercise activity: {e}")
        return None


def complete_exercise_activity(user, session_id, scores=None, overall_score=None, exercise_data=None):
    """
    Egzersiz aktivitesini tamamlandı olarak işaretle
    """
    try:
        if user and user.is_authenticated:
            activity = UserExerciseActivity.objects.filter(
                user=user,
                session_id=session_id,
                status='started'
            ).first()
            
            if activity:
                activity.mark_completed(
                    scores=scores,
                    overall_score=overall_score,
                    exercise_data=exercise_data
                )
                logger.info(f"Exercise activity completed: {activity.id}")
                return activity
            else:
                logger.warning(f"No started activity found for session {session_id}")
                return None
        else:
            logger.warning("Anonymous user - exercise activity not completed")
            return None
    except Exception as e:
        logger.error(f"Error completing exercise activity: {e}")
        return None


def abandon_exercise_activity(user, session_id):
    """
    Egzersiz aktivitesini yarıda bırakıldı olarak işaretle
    """
    try:
        if user and user.is_authenticated:
            activity = UserExerciseActivity.objects.filter(
                user=user,
                session_id=session_id,
                status='started'
            ).first()
            
            if activity:
                activity.mark_abandoned()
                logger.info(f"Exercise activity abandoned: {activity.id}")
                return activity
        return None
    except Exception as e:
        logger.error(f"Error abandoning exercise activity: {e}")
        return None


def get_user_recent_activities(user, limit=10):
    """
    Kullanıcının son aktivitelerini getir
    """
    try:
        if user and user.is_authenticated:
            return UserExerciseActivity.objects.filter(
                user=user
            ).order_by('-started_at')[:limit]
        return []
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        return []


def get_user_activity_stats(user, days=30):
    """
    Kullanıcının belirli gün aralığındaki aktivite istatistikleri
    """
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        if user and user.is_authenticated:
            start_date = timezone.now() - timedelta(days=days)
            
            activities = UserExerciseActivity.objects.filter(
                user=user,
                started_at__gte=start_date,
                status='completed'
            )
            
            total_completed = activities.count()
            total_time = sum([a.completion_time or 0 for a in activities])
            avg_score = activities.aggregate(
                avg=models.Avg('overall_score')
            )['avg'] or 0
            
            exercise_breakdown = {
                'memory': activities.filter(exercise_type='memory').count(),
                'word_bridge': activities.filter(exercise_type='word_bridge').count(),
                'problem_chain': activities.filter(exercise_type='problem_chain').count(),
            }
            
            return {
                'total_completed': total_completed,
                'total_time_minutes': round(total_time / 60, 1),
                'average_score': round(avg_score, 1),
                'exercise_breakdown': exercise_breakdown,
                'days': days
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting activity stats: {e}")
        return {}
