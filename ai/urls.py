from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('exercise/', views.exercise_view, name='exercise'),
    path('sss/', views.sss, name='sss'),
    path('whysynappse/', views.whysynappse, name='whysynappse'),
    path('brainhealth/', views.brainhealth, name='brainhealth'),

    
    # Test pages
    path('test/problem-chain/', views.problem_chain_test, name='problem_chain_test'),
    path('test/word-bridge/', views.word_bridge_test, name='word_bridge_test'),
    path('test/memory/', views.memory_test, name='memory_test'),
]
