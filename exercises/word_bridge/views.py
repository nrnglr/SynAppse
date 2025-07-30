from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import WordBridgeSession
from .prompts import (
    WORD_BRIDGE_WORD_GENERATION_PROMPT,
    WORD_BRIDGE_SOLUTION_GENERATION_PROMPT,
    WORD_BRIDGE_HINTS_GENERATION_PROMPT,
    WORD_BRIDGE_EVALUATION_PROMPT,
    WORD_BRIDGE_ALTERNATIVES_PROMPT
)
from services.gemini_service import GeminiService
from users.activity_utils import create_exercise_activity, complete_exercise_activity

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

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeStartView(APIView):
    """
    Word Bridge egzersizini başlatır - kelimeler üretir ve session oluşturur
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = parse_request_data(request)
            difficulty = data.get('difficulty', 'easy')
            
            # Zorluk seviyesi validasyonu
            if difficulty not in ['easy', 'medium', 'hard']:
                return Response({
                    'error': 'Geçersiz zorluk seviyesi'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Gemini ile kelimeler üret
            gemini_service = GeminiService()
            word_prompt = WORD_BRIDGE_WORD_GENERATION_PROMPT.format(difficulty=difficulty)
            
            word_response = gemini_service.generate_content(word_prompt)
            word_data = gemini_service.parse_json_response(word_response)
            
            # Yeni session oluştur
            session = WordBridgeSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                difficulty=difficulty,
                target_word=word_data['target_word'],
                start_word_options=word_data['start_options'],
                time_limit=self._get_time_limit(difficulty)
            )
            
            # Create user activity tracking (if user is authenticated)
            if request.user.is_authenticated:
                activity = create_exercise_activity(
                    user=request.user,
                    exercise_type='word_bridge',
                    session_id=str(session.session_id),
                    difficulty=difficulty
                )
            
            return Response({
                'session_id': str(session.session_id),
                'target_word': session.target_word,
                'start_options': session.start_word_options,
                'time_limit': session.time_limit,
                'difficulty': session.difficulty
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Word Bridge start error: {e}")
            return Response({
                'error': 'Egzersiz başlatılırken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_time_limit(self, difficulty):
        """Zorluk seviyesine göre süre limiti"""
        time_limits = {
            'easy': None,
            'medium': 120,  # 2 dakika
            'hard': 60     # 1 dakika
        }
        return time_limits.get(difficulty)

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeSelectStartView(APIView):
    """
    Kullanıcının başlangıç kelimesini seçmesi ve AI çözümünün hazırlanması
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = parse_request_data(request)
            session_id = data.get('session_id')
            selected_word = data.get('selected_word')
            
            if not session_id or not selected_word:
                return Response({
                    'error': 'Session ID ve seçilen kelime gerekli'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Session kontrolü
            try:
                session = WordBridgeSession.objects.get(session_id=session_id)
            except WordBridgeSession.DoesNotExist:
                return Response({
                    'error': 'Geçersiz session'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Seçilen kelimenin geçerli olup olmadığını kontrol et
            if selected_word not in session.start_word_options:
                return Response({
                    'error': 'Geçersiz başlangıç kelimesi'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Başlangıç kelimesini kaydet
            session.selected_start_word = selected_word
            session.save()
            
            # Gemini ile çözüm ve hint üret
            gemini_service = GeminiService()
            
            # Çözüm yolu üret
            solution_prompt = WORD_BRIDGE_SOLUTION_GENERATION_PROMPT.format(
                start_word=selected_word,
                target_word=session.target_word,
                difficulty=session.difficulty
            )
            solution_response = gemini_service.generate_content(solution_prompt)
            solution_data = gemini_service.parse_json_response(solution_response)
            
            # Hint sistemi üret
            hints_prompt = WORD_BRIDGE_HINTS_GENERATION_PROMPT.format(
                solution_path=' → '.join(solution_data['solution_path']),
                target_word=session.target_word
            )
            hints_response = gemini_service.generate_content(hints_prompt)
            hints_data = gemini_service.parse_json_response(hints_response)
            
            # Session'ı güncelle
            session.ai_solution_path = solution_data['solution_path']
            session.hints = hints_data['hints']
            session.save()
            
            return Response({
                'message': 'Başlangıç kelimesi seçildi, egzersiz hazır',
                'session_id': str(session.session_id),
                'start_word': session.selected_start_word,
                'target_word': session.target_word,
                'current_step': session.current_step,
                'max_words': 6,
                'time_limit': session.time_limit
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Word Bridge select start error: {e}")
            return Response({
                'error': 'Başlangıç kelimesi seçilirken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeSubmitWordView(APIView):
    """
    Kullanıcının kelime submit etmesi
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = parse_request_data(request)
            session_id = data.get('session_id')
            word = data.get('word', '').strip()
            
            if not session_id or not word:
                return Response({
                    'error': 'Session ID ve kelime gerekli'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Session kontrolü
            try:
                session = WordBridgeSession.objects.get(session_id=session_id)
            except WordBridgeSession.DoesNotExist:
                return Response({
                    'error': 'Geçersiz session'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Session durumu kontrolü
            if session.status != 'active':
                return Response({
                    'error': 'Session aktif değil'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Süre kontrolü
            if session.time_limit and self._is_time_expired(session):
                session.status = 'timeout'
                session.save()
                return Response({
                    'error': 'Süre doldu',
                    'status': 'timeout'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Maksimum kelime kontrolü
            if len(session.submitted_words) >= 6:
                return Response({
                    'error': 'Maksimum kelime sayısına ulaşıldı'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kelimeyi ekle
            session.submitted_words.append(word)
            session.current_step = len(session.submitted_words)
            session.save()
            
            return Response({
                'message': 'Kelime başarıyla eklendi',
                'current_step': session.current_step,
                'submitted_words': session.submitted_words,
                'can_submit_more': session.can_submit_more_words(),
                'word_chain': session.get_full_word_chain()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Word Bridge submit word error: {e}")
            return Response({
                'error': 'Kelime submit edilirken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_time_expired(self, session):
        """Sürenin dolup dolmadığını kontrol et"""
        if not session.time_limit:
            return False
        
        elapsed = (timezone.now() - session.started_at).total_seconds()
        return elapsed > session.time_limit

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeGetHintView(APIView):
    """
    Kullanıcının hint istemesi
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = parse_request_data(request)
            session_id = data.get('session_id')
            hint_level = data.get('hint_level', 1)  # 1, 2, veya 3
            
            if not session_id:
                return Response({
                    'error': 'Session ID gerekli'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Session kontrolü
            try:
                session = WordBridgeSession.objects.get(session_id=session_id)
            except WordBridgeSession.DoesNotExist:
                return Response({
                    'error': 'Geçersiz session'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Hint seviyesi kontrolü
            if hint_level not in [1, 2, 3]:
                return Response({
                    'error': 'Geçersiz hint seviyesi (1, 2, veya 3 olmalı)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Bu hint daha önce kullanılmış mı?
            if hint_level in session.hints_used:
                return Response({
                    'error': 'Bu hint daha önce kullanılmış'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Hint'i kullanıldı olarak işaretle
            session.hints_used.append(hint_level)
            session.save()
            
            # Hint metnini bul
            hint_text = ""
            for hint in session.hints:
                if hint['level'] == hint_level:
                    hint_text = hint['text']
                    break
            
            return Response({
                'hint_level': hint_level,
                'hint_text': hint_text,
                'hints_used': session.hints_used,
                'penalty': session.get_hint_penalty()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Word Bridge get hint error: {e}")
            return Response({
                'error': 'Hint alınırken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeCompleteView(APIView):
    """
    Egzersizi tamamlama ve değerlendirme
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = parse_request_data(request)
            session_id = data.get('session_id')
            
            if not session_id:
                return Response({
                    'error': 'Session ID gerekli'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Session kontrolü
            try:
                session = WordBridgeSession.objects.get(session_id=session_id)
            except WordBridgeSession.DoesNotExist:
                return Response({
                    'error': 'Geçersiz session'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Zaten tamamlanmış mı?
            if session.is_completed:
                return Response({
                    'error': 'Egzersiz zaten tamamlanmış'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # En az bir kelime girilmiş mi?
            if not session.submitted_words:
                return Response({
                    'error': 'En az bir kelime girilmeli'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Session'ı tamamlandı olarak işaretle
            session.is_completed = True
            session.status = 'completed'
            session.completed_at = timezone.now()
            
            # Kullanıcının tam çözümü
            user_solution = session.get_full_word_chain()
            
            # Gemini ile değerlendirme yap
            gemini_service = GeminiService()
            
            # Değerlendirme
            evaluation_prompt = WORD_BRIDGE_EVALUATION_PROMPT.format(
                user_solution=' → '.join(user_solution),
                ai_solution=' → '.join(session.ai_solution_path),
                target_word=session.target_word,
                hints_used=len(session.hints_used)
            )
            evaluation_response = gemini_service.generate_content(evaluation_prompt)
            evaluation_data = gemini_service.parse_json_response(evaluation_response)
            
            # Add overall score if not present
            scores = evaluation_data.get('scores', {})
            if 'overall' not in scores:
                scores['overall'] = self._calculate_overall_score(scores)
                evaluation_data['scores'] = scores
            
            # Alternatif çözümler
            alternatives_prompt = WORD_BRIDGE_ALTERNATIVES_PROMPT.format(
                start_word=session.selected_start_word,
                target_word=session.target_word,
                current_solution=' → '.join(user_solution)
            )
            alternatives_response = gemini_service.generate_content(alternatives_prompt)
            alternatives_data = gemini_service.parse_json_response(alternatives_response)
            
            # Sonuçları kaydet
            session.final_score = scores
            session.ai_evaluation = evaluation_data['evaluation_text']
            session.alternative_solutions = alternatives_data['alternatives']
            session.save()
            
            # Complete user activity tracking (if user is authenticated)
            if session.user:
                overall_score = scores.get('overall', 0)
                complete_exercise_activity(
                    user=session.user,
                    session_id=str(session.session_id),
                    scores=scores,
                    overall_score=overall_score,
                    exercise_data=evaluation_data
                )
            
            return Response({
                'message': 'Egzersiz başarıyla tamamlandı!',
                'session_id': str(session.session_id),
                'user_solution': user_solution,
                'scores': session.final_score,
                'evaluation': session.ai_evaluation,
                'connection_analysis': evaluation_data.get('connection_analysis', []),
                'suggestions': evaluation_data.get('suggestions', ''),
                'alternative_solutions': session.alternative_solutions,
                'ai_solution': session.ai_solution_path,
                'hints_used': len(session.hints_used),
                'penalty': session.get_hint_penalty(),
                'completion_time': self._get_completion_time(session)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Word Bridge complete error: {e}")
            return Response({
                'error': 'Egzersiz tamamlanırken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_overall_score(self, scores):
        """Calculate overall score from individual scores"""
        score_values = [
            scores.get('logic', 0),
            scores.get('creativity', 0),
            scores.get('efficiency', 0)
        ]
        return round(sum(score_values) / len(score_values), 1) if score_values else 0
    
    def _get_completion_time(self, session):
        """Tamamlanma süresini hesapla"""
        if session.completed_at and session.started_at:
            duration = session.completed_at - session.started_at
            return int(duration.total_seconds())
        return None

@method_decorator(csrf_exempt, name='dispatch')
class WordBridgeSessionStatusView(APIView):
    """
    Session durumu kontrolü
    """
    permission_classes = [AllowAny]
    
    def get(self, request, session_id):
        try:
            session = WordBridgeSession.objects.get(session_id=session_id)
            
            # Süre kontrolü
            time_remaining = None
            if session.time_limit and session.status == 'active':
                elapsed = (timezone.now() - session.started_at).total_seconds()
                time_remaining = max(0, session.time_limit - elapsed)
                
                # Süre dolduysa
                if time_remaining <= 0:
                    session.status = 'timeout'
                    session.save()
            
            return Response({
                'session_id': str(session.session_id),
                'status': session.status,
                'current_step': session.current_step,
                'submitted_words': session.submitted_words,
                'hints_used': session.hints_used,
                'time_remaining': time_remaining,
                'can_submit_more': session.can_submit_more_words(),
                'word_chain': session.get_full_word_chain(),
                'target_word': session.target_word,
                'selected_start_word': session.selected_start_word
            }, status=status.HTTP_200_OK)
            
        except WordBridgeSession.DoesNotExist:
            return Response({
                'error': 'Session bulunamadı'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Word Bridge session status error: {e}")
            return Response({
                'error': 'Session durumu alınırken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
