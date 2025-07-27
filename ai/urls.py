from django.urls import path
from . import views
from .views import (
    CreativityTestPageView,
    MemoryTestPageView,
    CreateCreativityExerciseView,
    ListCreativityExercisesView,
    CompleteCreativityExerciseView,
    CreateMemoryExerciseView, 
    ListMemoryExercisesView,
    CompleteMemoryExerciseView,
    SignupView,
    LoginView,
    LogoutView,
    ProfileView,
)

app_name = 'ai'

urlpatterns = [
    
    # Ana Egzersiz Sayfaları
    path('creativity/', CreativityTestPageView.as_view(), name='creativity-test-page'),
    path('memory/', MemoryTestPageView.as_view(), name='memory-test-page'),

    # Yardımcı Sayfalar
    path('', views.index, name='index'),
    path('exercise/', views.exercise_view, name='exercise'),
    path('brain/', views.brain_view, name='brain'),
    path('sss/', views.sss_view, name='sss'),
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.signup_view, name='signup'),  
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),  

    # Yaratıcılık API Endpoints
    path('api/creativity/create/', CreateCreativityExerciseView.as_view(), name='create-creativity-exercise'),
    path('api/creativity/exercises/', ListCreativityExercisesView.as_view(), name='list-creativity-exercises'),
    path('api/creativity/exercises/<int:exercise_id>/complete/', CompleteCreativityExerciseView.as_view(), name='complete-creativity-exercise'),

    # Hafıza API Endpoints
    path('api/memory/create/', CreateMemoryExerciseView.as_view(), name='create-memory-exercise'),
    path('api/memory/exercises/', ListMemoryExercisesView.as_view(), name='list-memory-exercises'),
    path('api/memory/exercises/<int:exercise_id>/complete/', CompleteMemoryExerciseView.as_view(), name='complete-memory-exercise'),

    #Login ve Signup endpoints
    path('api/login/', LoginView.as_view(), name='api-login'),  # API ile kayıt işlemi
    path('api/signup/', SignupView.as_view(), name='api-signup'), 
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
     path('api/profile/', ProfileView.as_view(), name='api-profile'),
]
