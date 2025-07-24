from django.urls import path
from .views import WordBridgeCreateView, WordBridgeListView, WordBridgeCompleteView

urlpatterns = [
    path('create/', WordBridgeCreateView.as_view(), name='word-bridge-create'),
    path('list/', WordBridgeListView.as_view(), name='word-bridge-list'),
    path('<int:exercise_id>/complete/', WordBridgeCompleteView.as_view(), name='word-bridge-complete'),
]
