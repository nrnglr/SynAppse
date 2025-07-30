from django.shortcuts import render

# Main pages
def index(request):
    """Main landing page"""
    return render(request, 'index.html')

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
