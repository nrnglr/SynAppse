from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ProblemChainSession
from .prompts import (
    PROBLEM_CHAIN_START_PROMPTS,
    PROBLEM_CHAIN_NEXT_PROMPT,
    PROBLEM_CHAIN_EVALUATION_PROMPT,
    FALLBACK_PROBLEMS,
    GEMINI_ERROR_FALLBACK
)
from services.gemini_service import GeminiService
import logging
import random

logger = logging.getLogger(__name__)

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
            difficulty = request.data.get('difficulty', 'medium')
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
            
            # Generate first problem using Gemini
            gemini_service = GeminiService()
            prompt = PROBLEM_CHAIN_START_PROMPTS[difficulty]
            
            first_problem = gemini_service.generate_problem_chain_content(prompt)
            
            # Use fallback if Gemini fails
            if not first_problem:
                logger.warning(f"Gemini failed for session {session.session_id}, using fallback")
                first_problem = random.choice(FALLBACK_PROBLEMS[difficulty])
            
            # Add problem to session
            session.add_problem(first_problem)
            
            # Store session_id in Django session
            request.session['problem_chain_session_id'] = str(session.session_id)
            
            return Response({
                "session_id": str(session.session_id),
                "round": session.current_round,
                "total_rounds": session.total_rounds,
                "problem": first_problem,
                "is_completed": False,
                "difficulty": difficulty
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
                session_id = request.data.get('session_id')
            
            if not session_id:
                return Response(
                    {"error": "No active session found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user solution
            user_solution = request.data.get('solution', '').strip()
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
            
            # Generate next problem using Gemini
            previous_problem = session.problems[-1]  # Last problem
            gemini_service = GeminiService()
            
            next_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
                previous_problem=previous_problem,
                user_solution=user_solution
            )
            
            next_problem = gemini_service.generate_problem_chain_content(next_prompt)
            
            # Use fallback if Gemini fails
            if not next_problem:
                logger.warning(f"Gemini failed for next problem in session {session.session_id}")
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
                session_id = request.data.get('session_id')
            
            if not session_id:
                return Response(
                    {"error": "No active session found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get final solution
            final_solution = request.data.get('solution', '').strip()
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
                return Response({
                    "is_completed": True,
                    "final_feedback": session.final_feedback,
                    "scores": {
                        "creativity": session.creativity_score,
                        "practicality": session.practicality_score,
                        "total": (session.creativity_score or 0) + (session.practicality_score or 0)
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
            
            # Clear session
            if 'problem_chain_session_id' in request.session:
                del request.session['problem_chain_session_id']
            
            return Response({
                "is_completed": True,
                "final_feedback": session.final_feedback,
                "scores": {
                    "creativity": session.creativity_score,
                    "practicality": session.practicality_score,
                    "total": session.creativity_score + session.practicality_score
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
