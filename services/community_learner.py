"""
Community Learning Service
Handles real-time learning from user interactions and feedback
"""

import logging
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict, Optional
from django.db.models import Avg, Count, Q

from exercises.problem_chain.models import ProblemChainSession, CommunityLearningData, CommunityProblemMetrics

logger = logging.getLogger(__name__)


class CommunityLearner:
    """
    Main service for processing community feedback and learning from successful interactions
    """
    
    @staticmethod
    def process_session_completion(session: ProblemChainSession):
        """
        Process a completed session and extract learning data if successful
        """
        try:
            overall_score = session.get_overall_score()
            session_rating = session.overall_session_rating or 0
            
            # Define success criteria
            is_high_quality_session = (
                overall_score >= 4.0 and  # High creativity + practicality
                session_rating >= 4 and   # User liked the experience
                session.is_completed      # Actually finished
            )
            
            if is_high_quality_session:
                # Extract learning data from each successful round
                for round_index in range(len(session.problems)):
                    if round_index < len(session.solutions):
                        learning_data = CommunityLearningData.create_from_session(session, round_index)
                        if learning_data:
                            # Analyze and categorize the problem
                            learning_data.problem_category = learning_data.categorize_problem()
                            learning_data.success_pattern = learning_data.extract_success_pattern()
                            learning_data.save()
                            
                            logger.info(f"Created learning data from session {session.session_id}, round {round_index + 1}")
                
                # Update community metrics for this session
                CommunityLearner.update_community_metrics(session)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing session completion: {e}", exc_info=True)
            return False
    
    @staticmethod
    def process_positive_feedback(problem_text: str, rating: int, session_data: dict):
        """
        Process immediate positive feedback on a problem
        """
        try:
            if rating >= 4:  # Good rating
                # Update problem metrics immediately
                metrics, created = CommunityProblemMetrics.objects.get_or_create_for_problem(
                    problem_text, 
                    session_data.get('difficulty', 'medium')
                )
                
                metrics.update_metrics(
                    rating=rating,
                    engagement_time=session_data.get('engagement_time'),
                    was_successful=True
                )
                
                logger.info(f"Processed positive feedback: rating {rating} for problem")
                return True
                
        except Exception as e:
            logger.error(f"Error processing positive feedback: {e}", exc_info=True)
            return False
    
    @staticmethod
    def process_negative_feedback(problem_text: str, rating: int, session_data: dict):
        """
        Process negative feedback to avoid similar problems
        """
        try:
            if rating <= 2:  # Poor rating
                # Update metrics to mark as problematic
                metrics, created = CommunityProblemMetrics.objects.get_or_create_for_problem(
                    problem_text,
                    session_data.get('difficulty', 'medium')
                )
                
                metrics.update_metrics(
                    rating=rating,
                    engagement_time=session_data.get('engagement_time'),
                    was_successful=False
                )
                
                logger.info(f"Processed negative feedback: rating {rating} for problem")
                return True
                
        except Exception as e:
            logger.error(f"Error processing negative feedback: {e}", exc_info=True)
            return False
    
    @staticmethod
    def update_community_metrics(session: ProblemChainSession):
        """
        Update community-wide metrics based on session data
        """
        try:
            for i, problem in enumerate(session.problems):
                if i < len(session.solutions):
                    metrics, created = CommunityProblemMetrics.objects.get_or_create_for_problem(
                        problem, session.difficulty
                    )
                    
                    # Update with session data
                    problem_rating = None
                    if session.problem_ratings and i < len(session.problem_ratings):
                        problem_rating = session.problem_ratings[i]
                    
                    engagement_time = None
                    if session.engagement_times and i < len(session.engagement_times):
                        engagement_time = session.engagement_times[i]
                    
                    metrics.update_metrics(
                        rating=problem_rating,
                        engagement_time=engagement_time,
                        was_successful=session.is_completed
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating community metrics: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_learning_insights(difficulty: str) -> Dict:
        """
        Get insights from community learning data for AI optimization
        """
        try:
            # Get recent successful examples
            successful_examples = CommunityLearningData.get_successful_examples(difficulty)
            
            if not successful_examples.exists():
                return {
                    'has_data': False,
                    'message': 'Insufficient community data for learning'
                }
            
            # Analyze patterns
            patterns = CommunityLearningData.get_pattern_analysis(difficulty)
            
            # Get best performing examples
            best_examples = successful_examples.filter(overall_score__gte=4.5)[:3]
            
            insights = {
                'has_data': True,
                'total_examples': successful_examples.count(),
                'patterns': patterns,
                'best_examples': [
                    {
                        'problem': example.problem_text,
                        'solution': example.solution_text,
                        'score': example.overall_score,
                        'category': example.problem_category
                    }
                    for example in best_examples
                ],
                'success_categories': list(
                    successful_examples.values_list('problem_category', flat=True).distinct()
                ),
                'avg_engagement_time': successful_examples.aggregate(
                    avg_time=Avg('engagement_time')
                )['avg_time'] or 0
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}", exc_info=True)
            return {'has_data': False, 'error': str(e)}
    
    @staticmethod
    def get_avoid_patterns(difficulty: str) -> Dict:
        """
        Get patterns to avoid based on negative feedback
        """
        try:
            # Get problems with consistently low ratings
            problem_hashes = CommunityProblemMetrics.objects.filter(
                difficulty_level=difficulty,
                avg_rating__lte=2.5,
                rating_count__gte=3  # At least 3 ratings to be confident
            ).values_list('problem_hash', flat=True)
            
            avoid_examples = CommunityLearningData.objects.filter(
                problem_hash__in=problem_hashes,
                difficulty=difficulty
            )
            
            if not avoid_examples.exists():
                return {'has_data': False}
            
            avoid_patterns = {
                'has_data': True,
                'avoid_categories': list(avoid_examples.values_list('problem_category', flat=True).distinct()),
                'common_issues': [
                    'Too complex for difficulty level',
                    'Unclear problem statement',
                    'Unrealistic scenarios'
                ],
                'low_rated_examples': [
                    example.problem_text[:100] + "..." if len(example.problem_text) > 100 else example.problem_text
                    for example in avoid_examples[:3]
                ]
            }
            
            return avoid_patterns
            
        except Exception as e:
            logger.error(f"Error getting avoid patterns: {e}", exc_info=True)
            return {'has_data': False, 'error': str(e)}


class CommunityAnalyzer:
    """
    Advanced analysis of community learning patterns
    """
    
    @staticmethod
    def daily_pattern_analysis():
        """
        Run daily analysis of community learning patterns
        """
        try:
            # Analyze yesterday's data
            yesterday = timezone.now() - timedelta(days=1)
            recent_data = CommunityLearningData.objects.filter(
                created_at__gte=yesterday
            )
            
            if not recent_data.exists():
                logger.info("No recent data for daily analysis")
                return False
            
            # Categorize problems automatically
            for data in recent_data.filter(problem_category__isnull=True):
                data.problem_category = data.categorize_problem()
                data.success_pattern = data.extract_success_pattern()
                data.save()
            
            logger.info(f"Completed daily analysis for {recent_data.count()} entries")
            return True
            
        except Exception as e:
            logger.error(f"Error in daily pattern analysis: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_trending_patterns():
        """
        Get currently trending successful patterns
        """
        try:
            # Get last week's high-performing data
            week_ago = timezone.now() - timedelta(days=7)
            recent_successes = CommunityLearningData.objects.filter(
                created_at__gte=week_ago,
                overall_score__gte=4.0
            )
            
            if not recent_successes.exists():
                return {}
            
            # Analyze trending categories
            category_performance = recent_successes.values('problem_category').annotate(
                count=Count('id'),
                avg_score=Avg('overall_score'),
                avg_rating=Avg('user_rating')
            ).order_by('-avg_score')
            
            trending = {
                'top_categories': list(category_performance[:3]),
                'emerging_patterns': [],
                'declining_patterns': []
            }
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending patterns: {e}", exc_info=True)
            return {}
