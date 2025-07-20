from django.urls import path
from .views import (
    CreativityTestPageView,
    MemoryTestPageView,
    CreateCreativityExerciseView,
    ListCreativityExercisesView,
    CompleteCreativityExerciseView,
    CreateMemoryExerciseView, 
    ListMemoryExercisesView,
    CompleteMemoryExerciseView,
)

app_name = 'ai'

urlpatterns = [
    # Ana Egzersiz Sayfaları
    path('creativity/', CreativityTestPageView.as_view(), name='creativity-test-page'),
    path('memory/', MemoryTestPageView.as_view(), name='memory-test-page'),

    # Yaratıcılık API Endpoints
    path('api/creativity/create/', CreateCreativityExerciseView.as_view(), name='create-creativity-exercise'),
    path('api/creativity/exercises/', ListCreativityExercisesView.as_view(), name='list-creativity-exercises'),
    path('api/creativity/exercises/<int:exercise_id>/complete/', CompleteCreativityExerciseView.as_view(), name='complete-creativity-exercise'),

    # Hafıza API Endpoints
    path('api/memory/create/', CreateMemoryExerciseView.as_view(), name='create-memory-exercise'),
    path('api/memory/exercises/', ListMemoryExercisesView.as_view(), name='list-memory-exercises'),
    path('api/memory/exercises/<int:exercise_id>/complete/', CompleteMemoryExerciseView.as_view(), name='complete-memory-exercise'),
]
