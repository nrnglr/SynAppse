from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    # Hem /api/... hem de /creativity, /memory gibi yolları yakalamak için:
    path('', include('ai.urls')),
]
