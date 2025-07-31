from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with remember me functionality
    """
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-main bg-gray-100 border-gray-300 rounded focus:ring-main focus:ring-2',
            'id': 'remember_me'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Kullanıcı adı veya email',
            'autofocus': True
        })
        
        # Customize password field
        self.fields['password'].widget.attrs.update({
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Şifre'
        })


class CustomRegisterForm(UserCreationForm):
    """
    Custom registration form with additional fields
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Email adresiniz'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Adınız'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Soyadınız'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Kullanıcı adı',
            'autofocus': True
        })
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Şifre'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full bg-transparent border border-gray-400 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-main',
            'placeholder': 'Şifre tekrar'
        })
        
        # Update help texts
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email adresi zaten kullanılıyor.")
        return email
    
    def save(self, commit=True):
        """Save user and update profile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # UserProfile otomatik oluşturulacak (signals ile)
        
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'email_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-main focus:border-transparent',
                'rows': 4,
                'placeholder': 'Kendiniz hakkında kısa bilgi...'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-main bg-gray-100 border-gray-300 rounded focus:ring-main focus:ring-2'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-main focus:border-transparent',
                'accept': 'image/*'
            })
        }
