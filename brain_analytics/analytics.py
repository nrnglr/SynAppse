"""
Brain Health Analytics Core Algorithm
Calculates frequency, performance, consistency, and improvement scores
"""

import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from typing import Dict, List, Tuple
import logging

from users.models import UserExerciseActivity
from .models import BrainHealthScore, DailyAnalytics, AnalyticsCache

logger = logging.getLogger(__name__)


class BrainHealthAnalyzer:
    """
    Core brain health analysis engine
    Implements the 4-component algorithm with bonuses
    """
    
    def __init__(self, user, analysis_window_days=7):
        self.user = user
        self.window_days = analysis_window_days
        self.end_date = timezone.now().date()
        self.start_date = self.end_date - timedelta(days=analysis_window_days)
        
    def calculate_brain_health_score(self) -> Dict:
        """
        Main calculation method
        Returns complete brain health analysis
        """
        # Check cache first
        cache_key = f"brain_health_{self.user.id}_{self.window_days}"
        cached_data = AnalyticsCache.get_cache(self.user, cache_key)
        if cached_data:
            logger.info(f"Using cached brain health data for user {self.user.id}")
            return cached_data
        
        # Get exercise data
        exercises = self._get_exercise_data()
        
        if len(exercises) < 5:
            # Not enough data for analysis
            return self._insufficient_data_response()
        
        # Calculate core metrics
        frequency_score = self._calculate_frequency_score(exercises)
        performance_score = self._calculate_performance_score(exercises)
        consistency_score = self._calculate_consistency_score(exercises)
        improvement_score = self._calculate_improvement_score(exercises)
        
        # Calculate bonuses
        variety_bonus = self._calculate_variety_bonus(exercises)
        difficulty_bonus = self._calculate_difficulty_bonus(exercises)
        streak_bonus = self._calculate_streak_bonus(exercises)
        
        # Apply main formula
        base_score = (
            frequency_score * 0.3 +
            performance_score * 0.4 +
            consistency_score * 0.2 +
            improvement_score * 0.1
        )
        
        # Add bonuses (max 0.5 points total)
        total_bonus = min(0.5, variety_bonus + difficulty_bonus + streak_bonus)
        final_score = min(10.0, base_score + total_bonus)
        
        # Prepare result
        result = {
            'core_metrics': {
                'frequency': round(frequency_score, 2),
                'performance': round(performance_score, 2),
                'consistency': round(consistency_score, 2),
                'improvement': round(improvement_score, 2),
            },
            'bonuses': {
                'variety': round(variety_bonus, 3),
                'difficulty': round(difficulty_bonus, 3),
                'streak': round(streak_bonus, 3),
                'total_bonus': round(total_bonus, 3),
            },
            'final_score': round(final_score, 2),
            'metadata': {
                'total_exercises': len(exercises),
                'analysis_period': f"{self.start_date} to {self.end_date}",
                'exercise_breakdown': self._get_exercise_breakdown(exercises),
                'calculation_timestamp': timezone.now().isoformat(),
            }
        }
        
        # Cache the result
        AnalyticsCache.set_cache(self.user, cache_key, result, hours=4)
        
        # Update database record
        self._update_brain_health_record(result)
        
        return result
    
    def _get_exercise_data(self) -> List[Dict]:
        """Get exercise data from the last 7 days"""
        activities = UserExerciseActivity.objects.filter(
            user=self.user,
            started_at__date__gte=self.start_date,
            started_at__date__lte=self.end_date,
            status='completed'
        ).order_by('started_at')
        
        exercises = []
        for activity in activities:
            exercises.append({
                'date': activity.started_at.date(),
                'type': activity.exercise_type,
                'difficulty': activity.difficulty,
                'overall_score': activity.overall_score or 0,
                'completion_time': activity.completion_time,
                'scores': activity.scores or {},
            })
        
        return exercises
    
    def _calculate_frequency_score(self, exercises: List[Dict]) -> float:
        """
        Calculate frequency score (0-10)
        Based on daily exercise frequency in 7-day window
        """
        if not exercises:
            return 0.0
        
        # Count unique days with exercises
        exercise_dates = set(ex['date'] for ex in exercises)
        days_with_exercises = len(exercise_dates)
        
        # Score: 10 = every day, 7 = 5 days, 4 = 3 days, 0 = 1 day
        if days_with_exercises >= 7:
            return 10.0
        elif days_with_exercises >= 5:
            return 8.0
        elif days_with_exercises >= 3:
            return 6.0
        elif days_with_exercises >= 2:
            return 4.0
        else:
            return 2.0
    
    def _calculate_performance_score(self, exercises: List[Dict]) -> float:
        """
        Calculate performance score (0-10)
        Average of all overall scores
        """
        if not exercises:
            return 0.0
        
        scores = [ex['overall_score'] for ex in exercises if ex['overall_score'] > 0]
        if not scores:
            return 0.0
        
        return np.mean(scores)
    
    def _calculate_consistency_score(self, exercises: List[Dict]) -> float:
        """
        Calculate consistency score (0-10)
        Lower standard deviation = higher consistency
        """
        if len(exercises) < 3:
            return 5.0  # Neutral score for insufficient data
        
        scores = [ex['overall_score'] for ex in exercises if ex['overall_score'] > 0]
        if len(scores) < 3:
            return 5.0
        
        std_dev = np.std(scores)
        
        # Convert std dev to 0-10 scale (lower std = higher score)
        # std_dev 0 = 10 points, std_dev 3+ = 0 points
        consistency = max(0, 10 - (std_dev * 3.33))
        return consistency
    
    def _calculate_improvement_score(self, exercises: List[Dict]) -> float:
        """
        Calculate improvement score (0-10)
        Linear regression trend of scores over time
        """
        if len(exercises) < 3:
            return 5.0  # Neutral score
        
        scores = [ex['overall_score'] for ex in exercises if ex['overall_score'] > 0]
        if len(scores) < 3:
            return 5.0
        
        # Simple linear regression
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        # Convert slope to 0-10 scale
        # Positive slope = improvement, negative = decline
        if slope > 0:
            improvement = min(10, 5 + (slope * 5))
        else:
            improvement = max(0, 5 + (slope * 5))
        
        return improvement
    
    def _calculate_variety_bonus(self, exercises: List[Dict]) -> float:
        """
        Bonus for doing different exercise types
        +0.2 for all 3 types, +0.1 for 2 types
        """
        exercise_types = set(ex['type'] for ex in exercises)
        
        if len(exercise_types) >= 3:
            return 0.2
        elif len(exercise_types) >= 2:
            return 0.1
        else:
            return 0.0
    
    def _calculate_difficulty_bonus(self, exercises: List[Dict]) -> float:
        """
        Bonus for harder exercises
        +0.1 for 20% hard exercises, +0.05 for any hard exercises
        """
        if not exercises:
            return 0.0
        
        hard_exercises = sum(1 for ex in exercises if ex['difficulty'] == 'hard')
        hard_percentage = hard_exercises / len(exercises)
        
        if hard_percentage >= 0.2:
            return 0.1
        elif hard_exercises > 0:
            return 0.05
        else:
            return 0.0
    
    def _calculate_streak_bonus(self, exercises: List[Dict]) -> float:
        """
        Bonus for consecutive days of exercises
        +0.2 for 7+ days, +0.1 for 3+ days
        """
        if not exercises:
            return 0.0
        
        # Get unique exercise dates sorted
        exercise_dates = sorted(set(ex['date'] for ex in exercises))
        
        # Find longest consecutive streak
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(exercise_dates)):
            if exercise_dates[i] - exercise_dates[i-1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        if longest_streak >= 7:
            return 0.2
        elif longest_streak >= 3:
            return 0.1
        else:
            return 0.0
    
    def _get_exercise_breakdown(self, exercises: List[Dict]) -> Dict:
        """Get exercise type breakdown with counts and percentages"""
        breakdown = {'memory': 0, 'word_bridge': 0, 'problem_chain': 0}
        
        for ex in exercises:
            if ex['type'] in breakdown:
                breakdown[ex['type']] += 1
        
        # Add percentage calculation
        total = len(exercises)
        if total > 0:
            # Create a copy of keys to avoid RuntimeError
            exercise_types = list(breakdown.keys())
            for key in exercise_types:
                count = breakdown[key]
                breakdown[f'{key}_percentage'] = round((count / total) * 100, 1)
        else:
            # Create a copy of keys to avoid RuntimeError
            exercise_types = list(breakdown.keys())
            for key in exercise_types:
                breakdown[f'{key}_percentage'] = 0.0
        
        return breakdown
    
    def _insufficient_data_response(self) -> Dict:
        """Return response when insufficient data"""
        return {
            'core_metrics': {
                'frequency': 0.0,
                'performance': 0.0,
                'consistency': 0.0,
                'improvement': 0.0,
            },
            'bonuses': {
                'variety': 0.0,
                'difficulty': 0.0,
                'streak': 0.0,
                'total_bonus': 0.0,
            },
            'final_score': 0.0,
            'metadata': {
                'total_exercises': 0,
                'analysis_period': f"{self.start_date} to {self.end_date}",
                'exercise_breakdown': {'memory': 0, 'word_bridge': 0, 'problem_chain': 0},
                'insufficient_data': True,
                'message': 'En az 5 egzersiz tamamladıktan sonra analiz yapılabilir.',
            }
        }
    
    def _update_brain_health_record(self, result: Dict) -> None:
        """Update or create BrainHealthScore record"""
        try:
            score_record, created = BrainHealthScore.objects.get_or_create(
                user=self.user,
                defaults={
                    'brain_health_score': result['final_score'],
                    'frequency_score': result['core_metrics']['frequency'],
                    'performance_score': result['core_metrics']['performance'],
                    'consistency_score': result['core_metrics']['consistency'],
                    'improvement_score': result['core_metrics']['improvement'],
                    'exercise_variety_bonus': result['bonuses']['variety'],
                    'difficulty_bonus': result['bonuses']['difficulty'],
                    'streak_bonus': result['bonuses']['streak'],
                    'total_exercises': result['metadata']['total_exercises'],
                    'memory_exercises': result['metadata']['exercise_breakdown']['memory'],
                    'word_bridge_exercises': result['metadata']['exercise_breakdown']['word_bridge'],
                    'problem_chain_exercises': result['metadata']['exercise_breakdown']['problem_chain'],
                    'is_cache_valid': True,
                }
            )
            
            if not created:
                # Update existing record
                score_record.brain_health_score = result['final_score']
                score_record.frequency_score = result['core_metrics']['frequency']
                score_record.performance_score = result['core_metrics']['performance']
                score_record.consistency_score = result['core_metrics']['consistency']
                score_record.improvement_score = result['core_metrics']['improvement']
                score_record.exercise_variety_bonus = result['bonuses']['variety']
                score_record.difficulty_bonus = result['bonuses']['difficulty']
                score_record.streak_bonus = result['bonuses']['streak']
                score_record.total_exercises = result['metadata']['total_exercises']
                score_record.memory_exercises = result['metadata']['exercise_breakdown']['memory']
                score_record.word_bridge_exercises = result['metadata']['exercise_breakdown']['word_bridge']
                score_record.problem_chain_exercises = result['metadata']['exercise_breakdown']['problem_chain']
                score_record.is_cache_valid = True
                score_record.save()
                
        except Exception as e:
            logger.error(f"Error updating brain health record for user {self.user.id}: {e}")


def calculate_user_brain_health(user, force_refresh=False):
    """
    Main entry point for brain health calculation
    """
    try:
        if not force_refresh:
            # Check if we have recent valid data
            try:
                existing_score = BrainHealthScore.objects.get(user=user)
                if not existing_score.is_cache_expired():
                    return existing_score.get_score_breakdown()
            except BrainHealthScore.DoesNotExist:
                pass
        
        # Calculate new score
        analyzer = BrainHealthAnalyzer(user)
        return analyzer.calculate_brain_health_score()
        
    except Exception as e:
        logger.error(f"Error calculating brain health for user {user.id}: {e}")
        return {
            'error': True,
            'message': 'Beyin sağlığı analizi hesaplanırken hata oluştu.',
            'final_score': 0.0
        }
