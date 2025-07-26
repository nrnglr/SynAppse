from django.urls import path
from .views import MemoryCreateView, MemoryListView, MemoryCompleteView

urlpatterns = [
    path('create/', MemoryCreateView.as_view(), name='memory-create'),
    path('list/', MemoryListView.as_view(), name='memory-list'),
    path('<int:exercise_id>/complete/', MemoryCompleteView.as_view(), name='memory-complete'),
]
