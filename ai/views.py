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
