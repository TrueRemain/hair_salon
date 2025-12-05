# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from homepage.models import Booking, StyleConsultation
from reviews.models import Review
from django.utils import timezone 
from .models import CustomUser

class RegisterView(View):
    """Регистрация нового пользователя"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('users:profile')
        
        return render(request, 'users/register.html', {'form': form})

class LoginView(View):
    """Вход пользователя"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        
        form = CustomAuthenticationForm()
        return render(request, 'users/login.html', {'form': form})
    
    def post(self, request):
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Пробуем аутентифицировать по username
            user = authenticate(username=username, password=password)
            
            # Если не получилось, пробуем по email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Вы вошли как {user.username}')
                next_url = request.GET.get('next', 'users:profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль')
        
        return render(request, 'users/login.html', {'form': form})

@login_required
def profile_view(request):
    """Личный кабинет пользователя"""
    user = request.user
    
    # Получаем данные пользователя
    bookings = user.bookings.all().order_by('-date', '-time')
    consultations = user.consultations.all().order_by('-created_at')
    reviews = Review.objects.filter(client_name=user.username)
    
    # Разделяем на будущие и прошедшие записи
    today = timezone.now().date()
    upcoming_bookings = bookings.filter(date__gte=today)
    past_bookings = bookings.filter(date__lt=today)
    
    context = {
        'user': user,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'consultations': consultations,
        'reviews': reviews,
        'total_bookings': bookings.count(),
        'total_consultations': consultations.count(),
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile_view(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.preferences = request.POST.get('preferences', user.preferences)
        
        # Обработка аватара
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('users:profile')
    
    return render(request, 'users/edit_profile.html')

def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')