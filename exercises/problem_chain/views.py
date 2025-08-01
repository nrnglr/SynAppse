from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import models
from datetime import timedelta
from .models import ProblemChainSession
from .prompts import (
    PROBLEM_CHAIN_START_PROMPTS,
    PROBLEM_CHAIN_NEXT_PROMPT,
    PROBLEM_CHAIN_EVALUATION_PROMPT,
    FALLBACK_PROBLEMS,
    GEMINI_ERROR_FALLBACK
)
from services.gemini_service import GeminiService
from services.community_aware_gemini import CommunityAwareGemini
from .community_learner import CommunityLearner
from .gemini_enhanced import CommunityAwareGemini as EnhancedGemini
from .pattern_analyzer import PatternAnalyzer
from users.activity_utils import create_exercise_activity, complete_exercise_activity
import logging
import random

logger = logging.getLogger(__name__)

def parse_request_data(request):
    """Parse JSON data from DRF or regular Django request"""
    if hasattr(request, 'data') and request.data:
        # DRF request
        return request.data
    else:
        # Regular Django request
        import json
        return json.loads(request.body.decode('utf-8')) if request.body else {}

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@method_decorator(csrf_exempt, name='dispatch')
class ProblemChainStartView(APIView):
    """
    Start new Problem Chain session
    POST /exercises/problem-chain/start/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Get difficulty from request
            difficulty = parse_request_data(request).get('difficulty', 'medium')
            if difficulty not in ['easy', 'medium', 'hard']:
                return Response(
                    {"error": "Invalid difficulty. Use 'easy', 'medium', or 'hard'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new session
            session = ProblemChainSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request),
                difficulty=difficulty
            )
            
            # Create user activity tracking (if user is authenticated)
            if request.user.is_authenticated:
                activity = create_exercise_activity(
                    user=request.user,
                    exercise_type='problem_chain',
                    session_id=str(session.session_id),
                    difficulty=difficulty
                )
            
            # Generate first problem using Community-Aware Gemini
            community_gemini = CommunityAwareGemini()
            first_problem = community_gemini.generate_community_optimized_problem(difficulty)
            
            # Use fallback if community generation fails
            if not first_problem or len(first_problem.strip()) < 30:
                logger.warning(f"Community Gemini failed for session {session.session_id}, using standard fallback")
                gemini_service = GeminiService()
                prompt = PROBLEM_CHAIN_START_PROMPTS[difficulty]
                first_problem = gemini_service.generate_problem_chain_content(prompt)
                
                if not first_problem:
                    logger.warning(f"Standard Gemini also failed, using static fallback")
                    first_problem = random.choice(FALLBACK_PROBLEMS[difficulty])
            
            # Add problem to session
            session.add_problem(first_problem)
            
            # Store session_id in Django session
            request.session['problem_chain_session_id'] = str(session.session_id)
            
            logger.info(f"Started community-aware session {session.session_id} with difficulty {difficulty}")
            
            return Response({
                "session_id": str(session.session_id),
                "round": session.current_round,
                "total_rounds": session.total_rounds,
                "problem": first_problem,
                "is_completed": False,
                "difficulty": difficulty,
                "community_optimized": True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error starting problem chain: {e}", exc_info=True)
            return Response(
                {"error": "Failed to start exercise. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class ProblemChainNextView(APIView):
    """
    Submit solution and get next problem
    POST /exercises/problem-chain/next/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Get session_id from Django session or request
            session_id = request.session.get('problem_chain_session_id')
            if not session_id:
                session_id = parse_request_data(request).get('session_id')
            
            if not session_id:
                return Response(
                    {"error": "No active session found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user solution
            user_solution = parse_request_data(request).get('solution', '').strip()
            if not user_solution:
                return Response(
                    {"error": "Solution is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get session
            try:
                session = ProblemChainSession.objects.get(session_id=session_id)
            except ProblemChainSession.DoesNotExist:
                return Response(
                    {"error": "Session not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if session is expired
            if session.is_session_expired:
                return Response(
                    {"error": "Session has expired. Please start a new game."},
                    status=status.HTTP_410_GONE
                )
            
            # Check if already completed
            if session.is_completed:
                return Response(
                    {"error": "Session is already completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if we're at the last round
            if session.current_round >= session.total_rounds:
                return Response(
                    {"error": "Session is complete. Use /complete/ endpoint."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add user solution
            session.add_solution(user_solution)
            
            # Check if this was the last round
            if session.current_round > session.total_rounds:
                return Response(
                    {"message": "All rounds completed. Use /complete/ endpoint for final evaluation."},
                    status=status.HTTP_200_OK
                )
            
            # Generate next problem using Community-Aware Gemini
            previous_problem = session.problems[-1]  # Last problem
            community_gemini = CommunityAwareGemini()
            
            next_problem = community_gemini.generate_next_problem_with_community_learning(
                previous_problem=previous_problem,
                user_solution=user_solution,
                difficulty=session.difficulty
            )
            
            # Use fallback if community generation fails
            if not next_problem or len(next_problem.strip()) < 20:
                logger.warning(f"Community Gemini failed for next problem in session {session.session_id}")
                gemini_service = GeminiService()
                next_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
                    previous_problem=previous_problem,
                    user_solution=user_solution
                )
                next_problem = gemini_service.generate_problem_chain_content(next_prompt)
                
                if not next_problem:
                    logger.warning(f"Basic Gemini also failed, using static fallback")
                    next_problem = random.choice(FALLBACK_PROBLEMS[session.difficulty])
            
            # Add next problem to session
            session.add_problem(next_problem)
            
            return Response({
                "round": session.current_round,
                "total_rounds": session.total_rounds,
                "problem": next_problem,
                "is_completed": False
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in problem chain next: {e}", exc_info=True)
            return Response(
                {"error": "Failed to generate next problem. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class ProblemChainCompleteView(APIView):
    """
    Submit final solution and get evaluation
    POST /exercises/problem-chain/complete/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Get session_id
            session_id = request.session.get('problem_chain_session_id')
            if not session_id:
                session_id = parse_request_data(request).get('session_id')
            
            if not session_id:
                return Response(
                    {"error": "No active session found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get final solution
            final_solution = parse_request_data(request).get('solution', '').strip()
            if not final_solution:
                return Response(
                    {"error": "Final solution is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get session
            try:
                session = ProblemChainSession.objects.get(session_id=session_id)
            except ProblemChainSession.DoesNotExist:
                return Response(
                    {"error": "Session not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if already completed
            if session.is_completed:
                # Safely calculate overall score
                creativity_score = session.creativity_score or 0
                practicality_score = session.practicality_score or 0
                overall_score = (creativity_score + practicality_score) / 2
                
                return Response({
                    "is_completed": True,
                    "final_feedback": session.final_feedback,
                    "scores": {
                        "creativity": creativity_score,
                        "practicality": practicality_score,
                        "overall": overall_score
                    },
                    "all_problems": session.problems,
                    "all_solutions": session.solutions
                }, status=status.HTTP_200_OK)
            
            # Add final solution
            session.add_solution(final_solution)
            
            # Calculate completion time
            completion_time = int((timezone.now() - session.created_at).total_seconds())
            session.completion_time = completion_time
            
            # Generate evaluation using Gemini
            gemini_service = GeminiService()
            
            # Prepare problem-solution history
            history = []
            for i, (problem, solution) in enumerate(zip(session.problems, session.solutions)):
                history.append(f"Tur {i+1}:\nProblem: {problem}\nÇözüm: {solution}\n")
            
            history_text = "\n".join(history)
            
            evaluation_prompt = PROBLEM_CHAIN_EVALUATION_PROMPT.format(
                problem_solution_history=history_text
            )
            
            evaluation_response = gemini_service.generate_problem_chain_content(evaluation_prompt)
            
            # Parse evaluation or use defaults
            if evaluation_response:
                evaluation_data = gemini_service.parse_evaluation_response(evaluation_response)
            else:
                logger.warning(f"Gemini evaluation failed for session {session.session_id}")
                evaluation_data = {
                    'creativity_score': 3,
                    'practicality_score': 3,
                    'feedback': 'Tüm turları başarıyla tamamladınız! Problem çözme becerinizi geliştirmeye devam edin.'
                }
            
            # Update session with results
            session.final_feedback = evaluation_data['feedback']
            session.creativity_score = evaluation_data['creativity_score']
            session.practicality_score = evaluation_data['practicality_score']
            session.is_completed = True
            session.save()
            
            # COMMUNITY LEARNING: Process session completion
            try:
                success = CommunityLearner.process_session_completion(session)
                if success:
                    logger.info(f"Community learning data extracted from session {session.session_id}")
                else:
                    logger.info(f"Session {session.session_id} did not meet quality criteria for learning")
            except Exception as e:
                logger.error(f"Community learning processing failed: {e}", exc_info=True)
            
            # Pattern analysis (existing)
            try:
                PatternAnalyzer.analyze_session_completion(session)
                logger.info(f"Pattern analysis completed for session {session.session_id}")
            except Exception as e:
                logger.error(f"Pattern analysis failed: {e}", exc_info=True)
            
            # Calculate final scores safely - USING AVERAGE NOT SUM
            creativity_score = evaluation_data['creativity_score'] or 0
            practicality_score = evaluation_data['practicality_score'] or 0
            overall_score = (creativity_score + practicality_score) / 2  # Average of both scores
            
            # Complete user activity tracking (if user is authenticated)
            if session.user:
                scores = {
                    'creativity': creativity_score,
                    'practicality': practicality_score,
                    'overall': overall_score
                }
                complete_exercise_activity(
                    user=session.user,
                    session_id=str(session.session_id),
                    scores=scores,
                    overall_score=overall_score,
                    exercise_data=evaluation_data
                )
            
            # Clear session
            if 'problem_chain_session_id' in request.session:
                del request.session['problem_chain_session_id']
            
            return Response({
                "is_completed": True,
                "final_feedback": session.final_feedback,
                "scores": {
                    "creativity": creativity_score,
                    "practicality": practicality_score,
                    "overall": overall_score
                },
                "completion_time": completion_time,
                "all_problems": session.problems,
                "all_solutions": session.solutions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error completing problem chain: {e}", exc_info=True)
            return Response(
                {"error": "Failed to complete exercise. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProblemRatingView(APIView):
    """
    Rate current problem
    POST /exercises/problem-chain/rate-problem/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = parse_request_data(request)
            session_id = data.get('session_id')
            rating = data.get('rating')
            problem_text = data.get('problem_text', '')  # NEW: Get problem text
            engagement_time = data.get('engagement_time', 0)  # NEW: Get engagement time
            
            if not session_id or not rating:
                return Response(
                    {"error": "session_id and rating are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if rating not in range(1, 6):
                return Response(
                    {"error": "Rating must be between 1 and 5."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get session
            try:
                session = ProblemChainSession.objects.get(session_id=session_id)
                session.add_problem_rating(rating)
                
                # COMMUNITY LEARNING: Process immediate feedback
                if problem_text:
                    feedback_data = {
                        'difficulty': session.difficulty,
                        'engagement_time': engagement_time,
                        'session_id': str(session_id),
                        'round': session.current_round
                    }
                    
                    if rating >= 4:
                        CommunityLearner.process_positive_feedback(problem_text, rating, feedback_data)
                        logger.info(f"Processed positive feedback for session {session_id}, rating {rating}")
                    elif rating <= 2:
                        CommunityLearner.process_negative_feedback(problem_text, rating, feedback_data)
                        logger.info(f"Processed negative feedback for session {session_id}, rating {rating}")
                
                return Response({"success": True, "community_learning_applied": True}, status=status.HTTP_200_OK)
            except ProblemChainSession.DoesNotExist:
                return Response(
                    {"error": "Session not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error rating problem: {e}", exc_info=True)
            return Response(
                {"error": "Failed to save rating."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class EngagementTimeView(APIView):
    """
    Save engagement time for current problem
    POST /exercises/problem-chain/engagement-time/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            session_id = parse_request_data(request).get('session_id')
            engagement_time = parse_request_data(request).get('engagement_time')
            
            if not session_id or engagement_time is None:
                return Response(
                    {"error": "session_id and engagement_time are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get session
            try:
                session = ProblemChainSession.objects.get(session_id=session_id)
                session.add_engagement_time(engagement_time)
                return Response({"success": True}, status=status.HTTP_200_OK)
            except ProblemChainSession.DoesNotExist:
                return Response(
                    {"error": "Session not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error saving engagement time: {e}", exc_info=True)
            return Response(
                {"error": "Failed to save engagement time."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SessionRatingView(APIView):
    """
    Rate overall session experience
    POST /exercises/problem-chain/rate-session/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            session_id = parse_request_data(request).get('session_id')
            rating = parse_request_data(request).get('rating')
            
            if not session_id or not rating:
                return Response(
                    {"error": "session_id and rating are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if rating not in range(1, 6):
                return Response(
                    {"error": "Rating must be between 1 and 5."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get session
            try:
                session = ProblemChainSession.objects.get(session_id=session_id)
                session.set_session_rating(rating)
                return Response({"success": True}, status=status.HTTP_200_OK)
            except ProblemChainSession.DoesNotExist:
                return Response(
                    {"error": "Session not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error rating session: {e}", exc_info=True)
            return Response(
                {"error": "Failed to save session rating."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class CommunityInsightsView(APIView):
    """
    Get community insights and analytics
    GET /exercises/problem-chain/community-insights/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from .community_insight_service import CommunityInsightService
            
            # Get live community stats
            live_stats = CommunityInsightService.get_live_stats()
            
            # NEW: Get community learning insights
            difficulty = request.GET.get('difficulty', 'medium')
            learning_insights = CommunityLearner.get_learning_insights(difficulty)
            
            # Get problem performance summary
            performance_summary = CommunityInsightService.get_problem_performance_summary()
            
            # Get optimization recommendations
            recommendations = PatternAnalyzer.get_optimization_recommendations()
            
            # NEW: Add learning data statistics
            from exercises.problem_chain.models import CommunityLearningData
            learning_stats = {
                'total_learning_entries': CommunityLearningData.objects.count(),
                'high_quality_entries': CommunityLearningData.objects.filter(overall_score__gte=4.0).count(),
                'categories_learned': CommunityLearningData.objects.values_list('problem_category', flat=True).distinct().count(),
                'avg_community_score': CommunityLearningData.objects.aggregate(
                    avg_score=models.Avg('overall_score')
                ).get('avg_score', 0) or 0
            }
            
            response_data = {
                "live_stats": live_stats,
                "learning_insights": learning_insights,
                "learning_statistics": learning_stats,
                "performance_summary": performance_summary,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "community_learning_active": True,
                "ai_learning_enabled": True,
                "last_updated": timezone.now().isoformat()
            }
            
            # Add success message if we have learning data
            if learning_insights.get('has_data', False):
                response_data["message"] = f"AI şu anda {learning_insights['total_examples']} topluluk örneğinden öğreniyor"
            else:
                response_data["message"] = "Topluluk verileri toplanıyor, AI öğrenmeye hazırlanıyor..."
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting community insights: {e}", exc_info=True)
            return Response(
                {"error": "Failed to get community insights."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class CommunityLearningStatsView(APIView):
    """
    Get detailed community learning statistics
    GET /exercises/problem-chain/learning-stats/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from exercises.problem_chain.models import CommunityLearningData
            from django.db.models import Count, Avg
            
            difficulty = request.GET.get('difficulty', 'all')
            
            # Base queryset
            queryset = CommunityLearningData.objects.all()
            if difficulty != 'all':
                queryset = queryset.filter(difficulty=difficulty)
            
            # Get statistics
            stats = {
                'total_entries': queryset.count(),
                'high_quality_entries': queryset.filter(overall_score__gte=4.0).count(),
                'category_breakdown': list(
                    queryset.values('problem_category')
                    .annotate(count=Count('id'), avg_score=Avg('overall_score'))
                    .order_by('-count')
                ),
                'difficulty_breakdown': list(
                    CommunityLearningData.objects.values('difficulty')
                    .annotate(count=Count('id'), avg_score=Avg('overall_score'))
                    .order_by('-count')
                ),
                'recent_additions': queryset.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'ai_utilization': {
                    'patterns_referenced': queryset.aggregate(
                        total_refs=models.Sum('times_referenced')
                    ).get('total_refs', 0) or 0,
                    'avg_success_when_used': queryset.filter(
                        times_referenced__gt=0
                    ).aggregate(
                        avg_success=Avg('avg_success_rate_when_used')
                    ).get('avg_success', 0) or 0
                }
            }
            
            return Response({
                'statistics': stats,
                'difficulty_filter': difficulty,
                'generated_at': timezone.now().isoformat(),
                'learning_status': 'active' if stats['total_entries'] > 0 else 'collecting'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}", exc_info=True)
            return Response(
                {"error": "Failed to get learning statistics."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            from .pattern_analyzer import CommunityInsightService
            
            # Get live community stats
            live_stats = CommunityInsightService.get_live_stats()
            
            # Get problem performance summary
            performance_summary = CommunityInsightService.get_problem_performance_summary()
            
            # Get optimization recommendations
            recommendations = PatternAnalyzer.get_optimization_recommendations()
            
            return Response({
                "live_stats": live_stats,
                "performance_summary": performance_summary,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "community_learning_active": True,
                "last_updated": timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting community insights: {e}", exc_info=True)
            return Response(
                {"error": "Failed to get community insights."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
