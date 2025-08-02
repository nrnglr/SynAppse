from django.shortcuts import render
from django.http import JsonResponse
from services.daily_brain_tip_service import DailyBrainTipService
import logging

logger = logging.getLogger(__name__)

# Main pages
def index(request):
    """Main landing page"""
    return render(request, 'index.html')

def sss(request):
    """SSS page"""
    return render(request, 'sss.html')

def whysynappse(request):
    """Why SynAppse page"""
    return render(request, 'why_synappse.html')

def brainhealth(request):
    """Brain health page"""
    return render(request, 'brain_health.html')

def exercise_view(request):
    """Exercise selection page"""
    return render(request, 'exercise.html')

def problem_chain_test(request):
    """Problem Chain test page"""
    return render(request, 'problem_chain_test.html')

def word_bridge_test(request):
    """Word Bridge test page"""
    return render(request, 'word_bridge_test.html')

def memory_test(request):
    """Memory exercise test page"""
    return render(request, 'memory_test.html')

# API Endpoints
def daily_brain_tip(request):
    """API endpoint for daily brain health tip"""
    try:
        tip_data = DailyBrainTipService.get_daily_tip()
        return JsonResponse({
            'success': True,
            'data': tip_data
        })
    except Exception as e:
        logger.error(f"Error in daily_brain_tip view: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to get daily brain tip',
            'data': {
                'tip': "Bugün aldığın önemli bir kararda, yapay zeka yardımı almadan önce kendi görüşünü not et.",
                'is_fallback': True
            }
        }, status=500)
