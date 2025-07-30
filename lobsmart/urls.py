"""
SynAppse URL Configuration
Brain Exercise Platform - Main URL routing
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main app (homepage, basic pages)
    path('', include('ai.urls')),
    
    # Exercise modules
    path('exercises/', include('exercises.urls')),
    
    # Brain Analytics
    path('brain-analytics/', include('brain_analytics.urls')),
    
    # User management
    path('users/', include('users.urls')),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
