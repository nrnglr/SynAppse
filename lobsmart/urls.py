from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render

def home(request):
    return render(request, 'ai/test_creativity.html')

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('ai.urls')),
]
