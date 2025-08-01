from django.urls import path
from .views import (
    ProblemChainStartView, 
    ProblemChainNextView, 
    ProblemChainCompleteView,
    ProblemRatingView,
    EngagementTimeView,
    SessionRatingView,
    CommunityInsightsView,
    CommunityLearningStatsView
)

urlpatterns = [
    path('start/', ProblemChainStartView.as_view(), name='problem-chain-start'),
    path('next/', ProblemChainNextView.as_view(), name='problem-chain-next'),
    path('complete/', ProblemChainCompleteView.as_view(), name='problem-chain-complete'),
    path('rate-problem/', ProblemRatingView.as_view(), name='problem-chain-rate-problem'),
    path('engagement-time/', EngagementTimeView.as_view(), name='problem-chain-engagement-time'),
    path('rate-session/', SessionRatingView.as_view(), name='problem-chain-rate-session'),
    path('community-insights/', CommunityInsightsView.as_view(), name='problem-chain-community-insights'),
    path('learning-stats/', CommunityLearningStatsView.as_view(), name='problem-chain-learning-stats'),
]
