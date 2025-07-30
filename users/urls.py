from django.urls import path
from .views import LoginView, RegisterView, LogoutView, ProfileView, get_user_stats

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # API URLs for AJAX
    path('api/stats/', get_user_stats, name='api-stats'),
]
