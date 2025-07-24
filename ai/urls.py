from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('exercise/', views.exercise_view, name='exercise'),
    
    # Test pages
    path('test/problem-chain/', views.problem_chain_test, name='problem_chain_test'),
]
