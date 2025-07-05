from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Synappse Ana Sayfa")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('ai.urls')),
]
