from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

from .analytics import calculate_user_brain_health
from .models import BrainHealthScore, DailyAnalytics

logger = logging.getLogger(__name__)


class BrainHealthAnalyticsView(APIView):
    """
    Main API endpoint for brain health analytics
    GET /brain-analytics/health-score/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get brain health score for authenticated user"""
        try:
            force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
            
            # Calculate brain health score
            result = calculate_user_brain_health(request.user, force_refresh=force_refresh)
            
            if result.get('error'):
                return Response(
                    {"error": result.get('message', 'Analiz hesaplanamadı')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "success": True,
                "data": result,
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in BrainHealthAnalyticsView: {e}", exc_info=True)
            return Response(
                {"error": "Beyin sağlığı analizi alınamadı. Lütfen tekrar deneyin."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserAnalyticsHistoryView(APIView):
    """
    Get user's analytics history
    GET /brain-analytics/history/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's exercise history and trends"""
        try:
            days = int(request.GET.get('days', 30))
            days = min(days, 90)  # Max 90 days
            
            # Get daily analytics
            daily_analytics = DailyAnalytics.objects.filter(
                user=request.user
            ).order_by('-date')[:days]
            
            history_data = []
            for day in daily_analytics:
                history_data.append({
                    'date': day.date.isoformat(),
                    'exercises_completed': day.exercises_completed,
                    'average_score': day.average_score,
                    'exercise_breakdown': {
                        'memory': day.memory_count,
                        'word_bridge': day.word_bridge_count,
                        'problem_chain': day.problem_chain_count,
                    },
                    'difficulty_breakdown': {
                        'easy': day.easy_exercises,
                        'medium': day.medium_exercises,
                        'hard': day.hard_exercises,
                    }
                })
            
            return Response({
                "success": True,
                "data": {
                    "history": history_data,
                    "period_days": days,
                    "total_records": len(history_data),
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UserAnalyticsHistoryView: {e}", exc_info=True)
            return Response(
                {"error": "Geçmiş veriler alınamadı."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@require_http_methods(["GET"])
def brain_health_summary(request):
    """
    Quick brain health summary for profile page
    Simple JSON endpoint for frontend
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': True,
            'message': 'Giriş yapmanız gerekiyor.',
            'score': 0.0
        })
    
    try:
        # Get or calculate brain health score
        result = calculate_user_brain_health(request.user)
        
        if result.get('error'):
            return JsonResponse({
                'error': True,
                'message': result.get('message', 'Analiz mevcut değil'),
                'score': 0.0
            })
        
        # Prepare summary data
        # Handle both cached (get_score_breakdown) and fresh (calculate_brain_health_score) results
        if 'metadata' in result:
            # Fresh calculation result
            metadata = result.get('metadata', {})
            summary = {
                'error': False,
                'brain_health_score': result.get('final_score', 0.0),
                'score_breakdown': result.get('core_metrics', {}),
                'bonuses': result.get('bonuses', {}),
                'total_exercises': metadata.get('total_exercises', 0),
                'exercise_distribution': metadata.get('exercise_breakdown', {}),
                'analysis_date': metadata.get('calculation_timestamp'),
                'has_sufficient_data': not metadata.get('insufficient_data', False),
            }
        else:
            # Cached result from get_score_breakdown
            summary = {
                'error': False,
                'brain_health_score': result.get('final_score', 0.0),
                'score_breakdown': result.get('core_metrics', {}),
                'bonuses': result.get('bonuses', {}),
                'total_exercises': result.get('total_exercises', 0),
                'exercise_distribution': result.get('exercise_distribution', {}),
                'analysis_date': None,
                'has_sufficient_data': result.get('total_exercises', 0) >= 5,
            }
        
        return JsonResponse(summary)
        
    except Exception as e:
        logger.error(f"Error in brain_health_summary: {e}", exc_info=True)
        return JsonResponse({
            'error': True,
            'message': 'Analiz yüklenirken hata oluştu.',
            'score': 0.0
        })


@require_http_methods(["POST"])
def refresh_brain_health(request):
    """
    Force refresh brain health calculation
    POST /brain-analytics/refresh/
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Giriş yapmanız gerekiyor.'
        })
    
    try:
        # Force recalculation
        result = calculate_user_brain_health(request.user, force_refresh=True)
        
        return JsonResponse({
            'success': not result.get('error', False),
            'data': result,
            'message': 'Beyin sağlığı analizi güncellendi!' if not result.get('error') else result.get('message')
        })
        
    except Exception as e:
        logger.error(f"Error in refresh_brain_health: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Analiz güncellenirken hata oluştu.'
        })
