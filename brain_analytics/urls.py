from django.urls import path
from . import views

app_name = 'brain_analytics'

urlpatterns = [
    # API Endpoints
    path('health-score/', views.BrainHealthAnalyticsView.as_view(), name='health_score'),
    path('history/', views.UserAnalyticsHistoryView.as_view(), name='analytics_history'),
    
    # AJAX Endpoints for Frontend
    path('summary/', views.brain_health_summary, name='brain_health_summary'),
    path('refresh/', views.refresh_brain_health, name='refresh_brain_health'),
]
