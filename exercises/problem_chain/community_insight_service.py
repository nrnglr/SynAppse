"""
Community Insight Service
Provides analytics and insights for community learning system.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum, Max, Min
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CommunityInsightService:
    """Service for generating community insights and analytics"""
    
    @staticmethod
    def get_live_stats() -> Dict[str, Any]:
        """Get real-time community statistics"""
        try:
            from exercises.problem_chain.models import (
                ProblemChainSession, CommunityLearningData, CommunityProblemMetrics
            )
            
            # Cache key for live stats
            cache_key = "community_live_stats"
            cached_stats = cache.get(cache_key)
            
            if cached_stats:
                return cached_stats
            
            # Calculate time ranges
            now = timezone.now()
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)
            one_week_ago = now - timedelta(days=7)
            
            # Active sessions (last hour)
            active_sessions = ProblemChainSession.objects.filter(
                created_at__gte=one_hour_ago
            ).count()
            
            # Daily sessions
            daily_sessions = ProblemChainSession.objects.filter(
                created_at__gte=one_day_ago
            ).count()
            
            # Weekly sessions
            weekly_sessions = ProblemChainSession.objects.filter(
                created_at__gte=one_week_ago
            ).count()
            
            # Learning data statistics
            total_learning_entries = CommunityLearningData.objects.count()
            high_quality_entries = CommunityLearningData.objects.filter(
                overall_score__gte=4.0
            ).count()
            
            # Recent learning additions
            recent_learning = CommunityLearningData.objects.filter(
                created_at__gte=one_day_ago
            ).count()
            
            # Average scores
            avg_session_score = ProblemChainSession.objects.filter(
                is_completed=True,
                creativity_score__isnull=False,
                practicality_score__isnull=False
            ).aggregate(
                avg_creativity=Avg('creativity_score'),
                avg_practicality=Avg('practicality_score')
            )
            
            # Calculate combined average score
            combined_avg = 0
            if avg_session_score['avg_creativity'] and avg_session_score['avg_practicality']:
                combined_avg = (avg_session_score['avg_creativity'] + avg_session_score['avg_practicality']) / 2
            
            # AI utilization stats
            ai_references = CommunityLearningData.objects.aggregate(
                total_refs=Sum('times_referenced')
            ).get('total_refs', 0) or 0
            
            stats = {
                'active_sessions_last_hour': active_sessions,
                'daily_sessions': daily_sessions,
                'weekly_sessions': weekly_sessions,
                'total_learning_entries': total_learning_entries,
                'high_quality_entries': high_quality_entries,
                'recent_learning_additions': recent_learning,
                'average_session_score': round(combined_avg, 2),
                'ai_pattern_references': ai_references,
                'learning_quality_ratio': round(
                    (high_quality_entries / total_learning_entries * 100) 
                    if total_learning_entries > 0 else 0, 1
                ),
                'system_health': 'active' if active_sessions > 0 else 'stable',
                'last_updated': now.isoformat()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting live stats: {e}", exc_info=True)
            return {
                'error': 'Failed to get live statistics',
                'system_health': 'error',
                'last_updated': timezone.now().isoformat()
            }
    
    @staticmethod
    def get_problem_performance_summary() -> Dict[str, Any]:
        """Get summary of problem performance across categories"""
        try:
            from exercises.problem_chain.models import CommunityProblemMetrics
            
            cache_key = "problem_performance_summary"
            cached_summary = cache.get(cache_key)
            
            if cached_summary:
                return cached_summary
            
            # Get performance by category
            category_performance = CommunityProblemMetrics.objects.values(
                'problem_category'
            ).annotate(
                avg_rating=Avg('avg_rating'),
                total_attempts=Sum('total_attempts'),
                avg_success_rate=Avg('success_rate'),
                problem_count=Count('id')
            ).order_by('-avg_rating')
            
            # Get top performing problems
            top_problems = CommunityProblemMetrics.objects.filter(
                avg_rating__gte=4.0,
                total_attempts__gte=5
            ).order_by('-avg_rating', '-total_attempts')[:5]
            
            # Get problems needing improvement
            improvement_needed = CommunityProblemMetrics.objects.filter(
                avg_rating__lt=3.0,
                total_attempts__gte=3
            ).order_by('avg_rating', 'success_rate')[:5]
            
            summary = {
                'category_performance': list(category_performance),
                'top_performing_problems': [
                    {
                        'problem_hash': problem.problem_hash,
                        'category': problem.problem_category,
                        'rating': round(problem.avg_rating, 2),
                        'attempts': problem.total_attempts,
                        'success_rate': round(problem.success_rate, 1)
                    }
                    for problem in top_problems
                ],
                'improvement_candidates': [
                    {
                        'problem_hash': problem.problem_hash,
                        'category': problem.problem_category,
                        'rating': round(problem.avg_rating, 2),
                        'attempts': problem.total_attempts,
                        'success_rate': round(problem.success_rate, 1)
                    }
                    for problem in improvement_needed
                ],
                'total_problems_tracked': CommunityProblemMetrics.objects.count(),
                'generated_at': timezone.now().isoformat()
            }
            
            # Cache for 10 minutes
            cache.set(cache_key, summary, 600)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting problem performance summary: {e}", exc_info=True)
            return {
                'error': 'Failed to get performance summary',
                'generated_at': timezone.now().isoformat()
            }
    
    @staticmethod
    def get_learning_trends(days: int = 7) -> Dict[str, Any]:
        """Get learning trends over time"""
        try:
            from exercises.problem_chain.models import CommunityLearningData
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Daily learning additions
            daily_data = []
            for i in range(days):
                day_start = start_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_count = CommunityLearningData.objects.filter(
                    created_at__gte=day_start,
                    created_at__lt=day_end
                ).count()
                
                daily_data.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'learning_entries': day_count
                })
            
            # Category trends
            category_trends = CommunityLearningData.objects.filter(
                created_at__gte=start_date
            ).values('problem_category').annotate(
                count=Count('id'),
                avg_score=Avg('overall_score')
            ).order_by('-count')
            
            return {
                'daily_trends': daily_data,
                'category_trends': list(category_trends),
                'period_days': days,
                'total_period_entries': sum(day['learning_entries'] for day in daily_data),
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting learning trends: {e}", exc_info=True)
            return {
                'error': 'Failed to get learning trends',
                'generated_at': timezone.now().isoformat()
            }
    
    @staticmethod
    def get_ai_optimization_impact() -> Dict[str, Any]:
        """Analyze the impact of AI optimization using community data"""
        try:
            from exercises.problem_chain.models import (
                CommunityLearningData, ProblemChainSession
            )
            
            # Get sessions that used community-optimized AI
            # (sessions created after we have learning data)
            first_learning_date = CommunityLearningData.objects.aggregate(
                first_date=Min('created_at')
            ).get('first_date')
            
            if not first_learning_date:
                return {
                    'optimization_active': False,
                    'message': 'No learning data available yet for impact analysis'
                }
            
            # Compare sessions before and after learning data
            before_optimization = ProblemChainSession.objects.filter(
                created_at__lt=first_learning_date,
                is_completed=True,
                creativity_score__isnull=False,
                practicality_score__isnull=False
            ).aggregate(
                count=Count('id'),
                avg_creativity=Avg('creativity_score'),
                avg_practicality=Avg('practicality_score'),
                avg_completion_time=Avg('completion_time')
            )
            
            after_optimization = ProblemChainSession.objects.filter(
                created_at__gte=first_learning_date,
                is_completed=True,
                creativity_score__isnull=False,
                practicality_score__isnull=False
            ).aggregate(
                count=Count('id'),
                avg_creativity=Avg('creativity_score'),
                avg_practicality=Avg('practicality_score'),
                avg_completion_time=Avg('completion_time')
            )
            
            # Calculate combined scores
            before_combined_score = 0
            after_combined_score = 0
            
            if before_optimization['avg_creativity'] and before_optimization['avg_practicality']:
                before_combined_score = (before_optimization['avg_creativity'] + before_optimization['avg_practicality']) / 2
                
            if after_optimization['avg_creativity'] and after_optimization['avg_practicality']:
                after_combined_score = (after_optimization['avg_creativity'] + after_optimization['avg_practicality']) / 2
            
            # Calculate improvements
            score_improvement = 0
            time_improvement = 0
            
            if before_combined_score > 0 and after_combined_score > 0:
                score_improvement = (
                    (after_combined_score - before_combined_score) 
                    / before_combined_score * 100
                )
            
            if (before_optimization['avg_completion_time'] and after_optimization['avg_completion_time']):
                time_improvement = (
                    (before_optimization['avg_completion_time'] - after_optimization['avg_completion_time']) 
                    / before_optimization['avg_completion_time'] * 100
                )
            
            return {
                'optimization_active': True,
                'optimization_start_date': first_learning_date.isoformat(),
                'before_optimization': {
                    'session_count': before_optimization['count'] or 0,
                    'avg_score': round(before_combined_score, 2),
                    'avg_completion_time': round(before_optimization['avg_completion_time'] or 0, 1)
                },
                'after_optimization': {
                    'session_count': after_optimization['count'] or 0,
                    'avg_score': round(after_combined_score, 2),
                    'avg_completion_time': round(after_optimization['avg_completion_time'] or 0, 1)
                },
                'improvements': {
                    'score_improvement_percent': round(score_improvement, 1),
                    'time_improvement_percent': round(time_improvement, 1),
                    'overall_impact': 'positive' if score_improvement > 0 else 'neutral'
                },
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing AI optimization impact: {e}", exc_info=True)
            return {
                'error': 'Failed to analyze optimization impact',
                'generated_at': timezone.now().isoformat()
            }
