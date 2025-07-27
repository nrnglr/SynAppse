from django.urls import path
from .views import (
    MemoryStartView,
    MemoryGenerateView, 
    MemorySubmitView,
    MemoryCompleteView
)

app_name = 'memory'

urlpatterns = [
    # Start memory exercise with difficulty selection
    path('start/', MemoryStartView.as_view(), name='start'),
    
    # Generate text based on selected topic 
    path('generate/', MemoryGenerateView.as_view(), name='generate'),
    
    # Submit user responses (recall + synthesis)
    path('submit/', MemorySubmitView.as_view(), name='submit'),
    
    # Complete exercise and get results
    path('complete/', MemoryCompleteView.as_view(), name='complete'),
]
