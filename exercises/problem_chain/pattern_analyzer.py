"""
Pattern Analysis Service for Problem Chain Exercise
Analyzes community data and provides insights for AI optimization
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ProblemChainSession, CommunityProblemMetrics, UserLearningPattern
import json
import logging

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """
    Analyzes user patterns and community data for AI optimization
    """
    
    @staticmethod
    def analyze_session_completion(session):
        """
        Analyze completed session and update community metrics
        Call this after each session completion
        """
        try:
            # Update community metrics for each problem
            for i, (problem, rating, engagement_time) in enumerate(
                zip(session.problems, 
                    session.problem_ratings + [None] * len(session.problems), 
                    session.engagement_times + [None] * len(session.problems))
            ):
                
                metrics = CommunityProblemMetrics.get_or_create_for_problem(
                    problem, session.difficulty
                )
                
                # Determine if this problem was "successful" (user continued or completed)
                was_successful = i < len(session.solutions)
                
                metrics.update_metrics(
                    rating=rating,
                    engagement_time=engagement_time,
                    was_successful=was_successful
                )
            
            # Update user learning pattern
            pattern = UserLearningPattern.get_or_create_for_user(
                user=session.user,
                ip_address=session.ip_address
            )
            pattern.update_from_session(session)
            
            logger.info(f"Pattern analysis completed for session {session.session_id}")
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}", exc_info=True)
    
    @staticmethod
    def get_community_insights():
        """
        Get current community insights for AI optimization
        """
        try:
            # Get high-performing problems
            high_performers = CommunityProblemMetrics.objects.filter(
                total_attempts__gte=3
            ).order_by('-user_preference_score')[:10]
            
            # Get low-performing problems to avoid
            low_performers = CommunityProblemMetrics.objects.filter(
                total_attempts__gte=3,
                avg_rating__lt=3.0
            ).order_by('user_preference_score')[:5]
            
            # Get difficulty distribution preferences
            difficulty_preferences = CommunityProblemMetrics.objects.values(
                'difficulty_level'
            ).annotate(
                avg_rating=Avg('avg_rating'),
                total_attempts=Count('id')
            ).order_by('-avg_rating')
            
            # Get engagement time patterns
            engagement_stats = CommunityProblemMetrics.objects.aggregate(
                avg_engagement=Avg('avg_engagement_time'),
                fast_problems=Count('id', filter=Q(avg_engagement_time__lt=45)),
                slow_problems=Count('id', filter=Q(avg_engagement_time__gt=120))
            )
            
            return {
                'high_performing_problems': [
                    {
                        'problem_text': p.problem_text,
                        'rating': p.avg_rating,
                        'success_rate': p.success_rate,
                        'attempts': p.total_attempts
                    } for p in high_performers
                ],
                'low_performing_problems': [
                    {
                        'problem_text': p.problem_text,
                        'rating': p.avg_rating,
                        'success_rate': p.success_rate
                    } for p in low_performers
                ],
                'difficulty_preferences': list(difficulty_preferences),
                'engagement_patterns': engagement_stats,
                'total_problems_tracked': CommunityProblemMetrics.objects.count(),
                'total_users_tracked': UserLearningPattern.objects.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting community insights: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def get_user_personalization(user=None, ip_address=None):
        """
        Get personalization data for a specific user
        """
        try:
            pattern = UserLearningPattern.get_or_create_for_user(
                user=user, ip_address=ip_address
            )
            
            # Get user's preferred problem types based on ratings
            user_sessions = ProblemChainSession.objects.filter(
                Q(user=user) | Q(ip_address=ip_address),
                is_completed=True,
                overall_session_rating__isnull=False
            ).order_by('-created_at')[:5]  # Last 5 sessions
            
            preferred_difficulty = pattern.preferred_difficulty
            if user_sessions.exists():
                # Calculate preferred difficulty based on ratings
                difficulty_scores = {}
                for session in user_sessions:
                    if session.overall_session_rating >= 4:
                        difficulty_scores[session.difficulty] = difficulty_scores.get(session.difficulty, 0) + 1
                
                if difficulty_scores:
                    preferred_difficulty = max(difficulty_scores, key=difficulty_scores.get)
            
            return {
                'learning_style': pattern.learning_style,
                'preferred_difficulty': preferred_difficulty,
                'avg_engagement_time': pattern.avg_engagement_time,
                'confidence_level': pattern.confidence_level,
                'total_sessions': pattern.total_sessions,
                'completion_rate': pattern.completion_rate,
                'personalization_available': pattern.total_sessions >= 2
            }
            
        except Exception as e:
            logger.error(f"Error getting user personalization: {e}", exc_info=True)
            return {'personalization_available': False}
    
    @staticmethod
    def get_optimization_recommendations():
        """
        Get recommendations for improving the exercise system
        """
        try:
            insights = PatternAnalyzer.get_community_insights()
            
            recommendations = []
            
            # Check if we have enough data
            if insights.get('total_problems_tracked', 0) < 10:
                recommendations.append({
                    'type': 'data_collection',
                    'message': 'Collect more user data for better insights',
                    'priority': 'low'
                })
                return recommendations
            
            # Analyze high performers
            high_performers = insights.get('high_performing_problems', [])
            if high_performers:
                avg_high_rating = sum(p['rating'] for p in high_performers[:3]) / min(3, len(high_performers))
                if avg_high_rating >= 4.0:
                    recommendations.append({
                        'type': 'content_optimization',
                        'message': f'Use patterns from top-rated problems (avg rating: {avg_high_rating:.1f})',
                        'priority': 'high',
                        'examples': [p['problem_text'][:50] + '...' for p in high_performers[:2]]
                    })
            
            # Analyze engagement times
            engagement = insights.get('engagement_patterns', {})
            avg_engagement = engagement.get('avg_engagement', 0)
            if avg_engagement > 0:
                if avg_engagement < 30:
                    recommendations.append({
                        'type': 'difficulty_adjustment',
                        'message': 'Problems may be too easy - consider increasing complexity',
                        'priority': 'medium'
                    })
                elif avg_engagement > 150:
                    recommendations.append({
                        'type': 'difficulty_adjustment',
                        'message': 'Problems may be too difficult - consider simplifying',
                        'priority': 'medium'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {e}", exc_info=True)
            return []


class CommunityInsightService:
    """
    Service for providing real-time community insights
    """
    
    @staticmethod
    def get_live_stats():
        """Get live community statistics"""
        try:
            # Get recent activity (last 24 hours)
            recent_sessions = ProblemChainSession.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            total_sessions_today = recent_sessions.count()
            completed_today = recent_sessions.filter(is_completed=True).count()
            avg_rating_today = recent_sessions.filter(
                overall_session_rating__isnull=False
            ).aggregate(avg_rating=Avg('overall_session_rating'))['avg_rating'] or 0
            
            # Get trending difficulty
            difficulty_stats = recent_sessions.values('difficulty').annotate(
                count=Count('id')
            ).order_by('-count')
            
            trending_difficulty = difficulty_stats[0]['difficulty'] if difficulty_stats else 'medium'
            
            return {
                'sessions_today': total_sessions_today,
                'completions_today': completed_today,
                'avg_rating_today': round(avg_rating_today, 1),
                'completion_rate_today': round((completed_today / max(total_sessions_today, 1)) * 100, 1),
                'trending_difficulty': trending_difficulty,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting live stats: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def get_problem_performance_summary():
        """Get summary of how different problem types are performing"""
        try:
            # Group problems by performance tiers
            excellent = CommunityProblemMetrics.objects.filter(
                avg_rating__gte=4.5, total_attempts__gte=3
            ).count()
            
            good = CommunityProblemMetrics.objects.filter(
                avg_rating__gte=3.5, avg_rating__lt=4.5, total_attempts__gte=3
            ).count()
            
            needs_improvement = CommunityProblemMetrics.objects.filter(
                avg_rating__lt=3.5, total_attempts__gte=3
            ).count()
            
            return {
                'excellent_problems': excellent,
                'good_problems': good,
                'needs_improvement': needs_improvement,
                'total_evaluated': excellent + good + needs_improvement
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}", exc_info=True)
            return {}
