from django.urls import path, include

app_name = 'exercises'

urlpatterns = [
    path('word-bridge/', include('exercises.word_bridge.urls')),
    path('problem-chain/', include('exercises.problem_chain.urls')),
    path('memory/', include('exercises.memory.urls')),
]
