from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),

    path('brain/', views.brain_view, name='brain'),
    path('sss/', views.sss_view, name='sss'),
    path('profile/', views.profile_view, name='profile'),
    #path('signup/', signup_view, name='signup'),  
    #path('login/', login_view, name='login'),  
    #path('logout/', logout_view, name='logout'),  

    # Yaratıcılık API Endpoints
    path('api/creativity/create/', CreateCreativityExerciseView.as_view(), name='create-creativity-exercise'),
    path('api/creativity/exercises/', ListCreativityExercisesView.as_view(), name='list-creativity-exercises'),
    path('api/creativity/exercises/<int:exercise_id>/complete/', CompleteCreativityExerciseView.as_view(), name='complete-creativity-exercise'),

    # Hafıza API Endpoints
    path('api/memory/create/', CreateMemoryExerciseView.as_view(), name='create-memory-exercise'),
    path('api/memory/exercises/', ListMemoryExercisesView.as_view(), name='list-memory-exercises'),
    path('api/memory/exercises/<int:exercise_id>/complete/', CompleteMemoryExerciseView.as_view(), name='complete-memory-exercise'),

    
    # Test pages
    path('test/problem-chain/', views.problem_chain_test, name='problem_chain_test'),

]
