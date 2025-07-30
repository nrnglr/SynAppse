from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import UserProfile
from .forms import CustomLoginForm, CustomRegisterForm, UserProfileForm


@method_decorator(csrf_protect, name='dispatch')
class LoginView(View):
    """
    Custom login view with remember me functionality
    """
    template_name = 'user/login.html'
    form_class = CustomLoginForm
    
    def get(self, request):
        """Show login form"""
        if request.user.is_authenticated:
            return redirect('ai:index')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process login"""
        form = self.form_class(data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Login user
                login(request, user)
                
                # Set session expiry based on remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                
                messages.success(request, f'Hoş geldin, {user.first_name or user.username}!')
                
                # Redirect to next or home
                next_url = request.GET.get('next', 'ai:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
        else:
            messages.error(request, 'Form verilerinde hata var.')
        
        return render(request, self.template_name, {'form': form})


@method_decorator(csrf_protect, name='dispatch')
class RegisterView(View):
    """
    User registration view
    """
    template_name = 'user/signup.html'
    form_class = CustomRegisterForm
    
    def get(self, request):
        """Show registration form"""
        if request.user.is_authenticated:
            return redirect('ai:index')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process registration"""
        form = self.form_class(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Auto login after registration
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f'Hoş geldin, {user.first_name}! Hesabın başarıyla oluşturuldu.')
                return redirect('ai:index')
        else:
            messages.error(request, 'Kayıt sırasında hata oluştu. Lütfen bilgileri kontrol edin.')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """
    User logout view
    """
    def get(self, request):
        """Process logout"""
        if request.user.is_authenticated:
            username = request.user.first_name or request.user.username
            logout(request)
            messages.success(request, f'Güle güle, {username}!')
        
        return redirect('ai:index')
    
    def post(self, request):
        """Also handle POST logout"""
        return self.get(request)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    User profile view
    """
    template_name = 'user/profile.html'
    
    def get(self, request):
        """Show user profile"""
        profile = request.user.userprofile
        form = UserProfileForm(instance=profile)
        
        context = {
            'profile': profile,
            'form': form,
            'user': request.user
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Update user profile"""
        profile = request.user.userprofile
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Profil güncellenirken hata oluştu.')
        
        context = {
            'profile': profile,
            'form': form,
            'user': request.user
        }
        return render(request, self.template_name, context)


# API Views for AJAX requests
@login_required
def get_user_stats(request):
    """Get user exercise statistics as JSON"""
    profile = request.user.userprofile
    
    stats = {
        'total_exercises': profile.total_exercises_completed,
        'average_score': profile.average_score,
        'best_score': profile.best_score,
        'exercise_distribution': profile.get_exercise_distribution(),
        'favorite_difficulty': profile.get_favorite_difficulty_display(),
        'completion_rate': profile.completion_rate,
    }
    
    return JsonResponse(stats)
