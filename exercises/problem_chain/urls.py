from django.urls import path
from .views import ProblemChainStartView, ProblemChainNextView, ProblemChainCompleteView

urlpatterns = [
    path('start/', ProblemChainStartView.as_view(), name='problem-chain-start'),
    path('next/', ProblemChainNextView.as_view(), name='problem-chain-next'),
    path('complete/', ProblemChainCompleteView.as_view(), name='problem-chain-complete'),
]
