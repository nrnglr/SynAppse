from django.urls import path
from .views import (
    WordBridgeStartView,
    WordBridgeSelectStartView,
    WordBridgeSubmitWordView,
    WordBridgeGetHintView,
    WordBridgeCompleteView,
    WordBridgeSessionStatusView
)

urlpatterns = [
    # Egzersiz başlatma
    path('start/', WordBridgeStartView.as_view(), name='word-bridge-start'),
    
    # Başlangıç kelimesi seçimi
    path('select-start/', WordBridgeSelectStartView.as_view(), name='word-bridge-select-start'),
    
    # Kelime submit etme
    path('submit-word/', WordBridgeSubmitWordView.as_view(), name='word-bridge-submit-word'),
    
    # Hint alma
    path('get-hint/', WordBridgeGetHintView.as_view(), name='word-bridge-get-hint'),
    
    # Egzersiz tamamlama
    path('complete/', WordBridgeCompleteView.as_view(), name='word-bridge-complete'),
    
    # Session durumu kontrolü
    path('status/<uuid:session_id>/', WordBridgeSessionStatusView.as_view(), name='word-bridge-status'),
]
