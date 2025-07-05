from django.urls import path
from .views import ExerciseGenerateView, ExerciseSubmitView

urlpatterns = [
    # Egzersiz oluşturma endpointleri
    path('critical/', ExerciseGenerateView.as_view(), {'exercise_type': 'critical'}, name='exercise-critical'),
    path('memory/', ExerciseGenerateView.as_view(), {'exercise_type': 'memory'}, name='exercise-memory'),
    path('creativity/', ExerciseGenerateView.as_view(), {'exercise_type': 'creativity'}, name='exercise-creativity'),
    path('strategy/', ExerciseGenerateView.as_view(), {'exercise_type': 'strategy'}, name='exercise-strategy'),
    
    # Submit endpointleri
    path('critical/submit/', ExerciseSubmitView.as_view(), {'exercise_type': 'critical'}, name='submit-critical'),
    path('memory/submit/', ExerciseSubmitView.as_view(), {'exercise_type': 'memory'}, name='submit-memory'),
    path('creativity/submit/', ExerciseSubmitView.as_view(), {'exercise_type': 'creativity'}, name='submit-creativity'),
    path('strategy/submit/', ExerciseSubmitView.as_view(), {'exercise_type': 'strategy'}, name='submit-strategy'),
]
