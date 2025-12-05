# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации с дополнительными полями"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        })
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (900) 123-45-67'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш логин'
            }),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError('Логин должен содержать минимум 3 символа')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Убираем все символы кроме цифр
            digits = re.sub(r'\D', '', phone)
            if len(digits) != 11:
                raise ValidationError('Неверный формат телефона. Должно быть 11 цифр')
        return phone

class CustomAuthenticationForm(forms.Form):
    """Форма входа (можно использовать существующую AuthenticationForm)"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Логин или email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )