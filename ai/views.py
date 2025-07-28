from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging

from services.supabase_service import SupabaseService
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# --- Function based views ---

def index(request):
    return render(request, 'index.html')

def exercise_view(request):
    return render(request, 'exercise.html')

def brain_view(request):
    return render(request, 'brain.html')

def sss_view(request):
    return render(request, 'sss.html')

def profile_view(request):
    return render(request, 'profile.html')

def signup_view(request):
    return render(request, 'user/signup.html')

def login_view(request):
    return render(request, 'user/login.html')

def logout_view(request):
    logout(request)
    return redirect('ai:index')

def problem_chain_test(request):
    return render(request, 'problem_chain_test.html')


def word_bridge_test(request):
    """Word Bridge test page"""
    return render(request, 'word_bridge_test.html')

def memory_test(request):
    """Memory exercise test page"""
    return render(request, 'memory_test.html')


# --- Class-based Template views ---

class CreativityTestPageView(TemplateView):
    template_name = "ai/test_creativity.html"

class MemoryTestPageView(TemplateView):
    template_name = "ai/test_memory.html"


# --- Authentication API Views ---

class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response(
                {"error": "Kullanıcı adı, email ve şifre gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Kullanıcı zaten var mı kontrol et
            if User.objects.filter(username=username).exists():
                return Response(
                    {"error": "Bu kullanıcı adı zaten kullanılıyor."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "Bu email zaten kullanılıyor."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Yeni kullanıcı oluştur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            return Response(
                {"success": "Hesap başarıyla oluşturuldu.", "user_id": user.id}, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Signup hatası: {e}", exc_info=True)
            return Response(
                {"error": "Sunucu hatası."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([username, password]):
            return Response(
                {"error": "Kullanıcı adı ve şifre gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return Response(
                    {
                        "success": "Giriş başarılı.", 
                        "user_id": user.id,
                        "username": user.username
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Geçersiz kullanıcı adı veya şifre."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            logger.error(f"Login hatası: {e}", exc_info=True)
            return Response(
                {"error": "Sunucu hatası."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    def post(self, request):
        try:
            logout(request)
            return Response(
                {"success": "Çıkış başarılı."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout hatası: {e}", exc_info=True)
            return Response(
                {"error": "Sunucu hatası."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Giriş yapmanız gerekiyor."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user_data = {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "date_joined": request.user.date_joined
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Profile hatası: {e}", exc_info=True)
            return Response(
                {"error": "Sunucu hatası."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Giriş yapmanız gerekiyor."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = request.user
            
            # Güncellenebilir alanlar
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                email = request.data['email']
                # Email zaten kullanılıyor mu kontrol et
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response(
                        {"error": "Bu email zaten kullanılıyor."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.email = email
            
            user.save()
            
            return Response(
                {"success": "Profil güncellendi."}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Profile update hatası: {e}", exc_info=True)
            return Response(
                {"error": "Sunucu hatası."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- API Views for Creativity ---

class CreateCreativityExerciseView(APIView):
    def post(self, request):
        difficulty = request.data.get('difficulty', 'easy')
        if difficulty not in ['easy', 'medium', 'hard']:
            return Response({"error": "Geçersiz zorluk seviyesi. 'easy', 'medium' veya 'hard' olmalı."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            gemini_service = GeminiService()
            saved_exercise = gemini_service.generate_and_save_creative_exercise(difficulty=difficulty)

            if not saved_exercise:
                return Response({"error": "Egzersiz üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(saved_exercise, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Creativity exercise oluşturulurken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListCreativityExercisesView(APIView):
    def get(self, request):
        try:
            difficulty = request.query_params.get('difficulty')
            query = SupabaseService.table('exercises').select('*').eq('category', 'creativity')
            if difficulty in ['easy', 'medium', 'hard']:
                query = query.eq('difficulty', difficulty)

            response = query.order('created_at', desc=True).execute()
            return Response(response.data or [], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Creativity egzersiz listesi hatası: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompleteCreativityExerciseView(APIView):
    def post(self, request, exercise_id, *args, **kwargs):
        user_story = request.data.get('user_story')
        if not user_story:
            return Response({"error": "Lütfen hikayenizi girin."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # SupabaseService kullanımını düzelttim
            supabase_service = SupabaseService()
            get_response = supabase_service.table('exercises').select('metadata').eq('id', exercise_id).single().execute()
            current_metadata = get_response.data.get('metadata', {})
            character = current_metadata.get('character')
            words = current_metadata.get('words')

            if not words:
                return Response({"error": "Anahtar kelimeler bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            # Bu kısım muhtemelen bir fonksiyon çağrısı olmalı, class instantiation değil
            # ai_feedback = CreativityTestPageView(words=words, user_story=user_story, character=character)
            # Şimdilik placeholder olarak bırakıyorum
            ai_feedback = "AI feedback will be implemented here"

            current_metadata['user_story'] = user_story
            if ai_feedback:
                current_metadata['ai_feedback'] = ai_feedback

            supabase_service.table('exercises').update({
                'metadata': current_metadata,
                'is_completed': True
            }).eq('id', exercise_id).execute()

            return Response({
                "success": "Hikayeniz kaydedildi.",
                "feedback": ai_feedback
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Creativity tamamlanırken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- API Views for Memory ---

class CreateMemoryExerciseView(APIView):
    def post(self, request):
        difficulty = request.data.get('difficulty', 'easy')
        if difficulty not in ['easy', 'medium', 'hard']:
            return Response({"error": "Geçersiz zorluk seviyesi."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            gemini_service = GeminiService()
            saved_exercise = gemini_service.generate_and_save_memory_exercise(difficulty=difficulty)
            if not saved_exercise:
                return Response({"error": "Egzersiz üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(saved_exercise, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Memory exercise oluşturulurken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListMemoryExercisesView(APIView):
    def get(self, request):
        try:
            difficulty = request.query_params.get('difficulty')
            supabase_service = SupabaseService()
            query = supabase_service.table('exercises').select('*').eq('category', 'memory')
            if difficulty:
                query = query.eq('difficulty', difficulty)

            response = query.order('created_at', desc=True).execute()
            return Response(response.data or [], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Memory egzersiz listesi hatası: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompleteMemoryExerciseView(APIView):
    def post(self, request, exercise_id, *args, **kwargs):
        user_paragraph = request.data.get('user_paragraph')
        if not user_paragraph:
            return Response({"error": "Paragraf eksik."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            supabase_service = SupabaseService()
            get_response = supabase_service.table('exercises').select('metadata').eq('id', exercise_id).single().execute()
            current_metadata = get_response.data.get('metadata', {})
            exercise_words = current_metadata.get('raw_words')

            if not exercise_words:
                return Response({"error": "Kelime listesi bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            # Bu kısım da muhtemelen bir fonksiyon çağrısı olmalı
            # ai_feedback = MemoryTestPageView(words=exercise_words, user_paragraph=user_paragraph)
            # Şimdilik placeholder olarak bırakıyorum
            ai_feedback = "AI feedback will be implemented here"

            current_metadata['user_paragraph'] = user_paragraph
            current_metadata['ai_feedback'] = ai_feedback

            supabase_service.table('exercises').update({
                'metadata': current_metadata,
                'is_completed': True
            }).eq('id', exercise_id).execute()

            return Response({
                "success": "Egzersiz tamamlandı.",
                "feedback": ai_feedback
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Memory tamamlanırken hata: {e}", exc_info=True)
            return Response({"error": "Sunucu hatası."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

