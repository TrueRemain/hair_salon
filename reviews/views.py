# reviews/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
import json
from datetime import datetime
from .models import Review, Master
from .forms import ReviewForm
from django.http import JsonResponse 
import re
from homepage.models import Booking
from .review_tokens import token_manager

def add_review(request, token=None):
    # Если токен передан, это одноразовая ссылка
    if token:
        is_valid, token_data = token_manager.validate_token(token)
        
        if not is_valid:
            messages.error(request, token_data)
            return render(request, 'reviews/review_invalid.html')
        
        # Если GET запрос - показываем предзаполненную форму
        if request.method == 'GET':
            # Маппинг кодов мастеров на имена
            master_mapping = {
                'alexander': 'Александр Петров',
                'mikhail': 'Михаил Козлов',
                'dmitry': 'Дмитрий Соколов'
            }
            
            # Находим мастера по коду
            master_name = master_mapping.get(token_data['master_code'])
            master = Master.objects.filter(name=master_name).first()
            
            if not master:
                messages.error(request, "Мастер не найден в системе")
                return render(request, 'reviews/review_invalid.html')
            
            # Создаем предзаполненную форму
            initial_data = {
                'client_name': token_data['client_name'],
                'phone': token_data['phone'],
                'master': master.id
            }
            form = ReviewForm(initial=initial_data)
            
            return render(request, 'reviews/add_review.html', {
                'form': form,
                'is_token_review': True,
                'token': token
            })
        
        # Если POST запрос - обрабатываем отправку отзыва
        elif request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                # Автоматически помечаем как проверенный
                review.is_verified = True
                review.is_published = True  # Автоматически публикуем
                review.save()
                
                # Помечаем токен как использованный
                token_manager.mark_token_used(token)
                
                messages.success(
                    request, 
                    '✅ Спасибо! Ваш отзыв успешно опубликован.'
                )
                return redirect('reviews:review_success')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')
    
    # Обычная форма отзыва (без токена)
    else:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                if form.cleaned_data.get('is_verified'):
                    review.is_verified = True
                review.save()
                
                messages.success(
                    request, 
                    'Спасибо! Ваш отзыв успешно отправлен и будет опубликован после проверки.'
                )
                return redirect('reviews:add_review')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')
        else:
            form = ReviewForm()
    
    return render(request, 'reviews/add_review.html', {
        'form': form,
        'is_token_review': False
    })

def review_success(request):
    """Страница успешной отправки отзыва"""
    return render(request, 'reviews/review_success.html')

def review_info(request):
    """Информационная страница о системе отзывов"""
    return render(request, 'reviews/review_info.html')

def save_review_to_file(review):
    """Сохраняет отзыв в JSON файл"""
    review_data = {
        'master': review.master.name,
        'client_name': review.client_name,
        'phone': review.phone,
        'stars': review.stars,
        'text': review.text,
        'is_verified': review.is_verified,
        'created_at': datetime.now().isoformat(),
    }
    
    try:
        with open('reviews_data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(review_data, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")

def get_reviews_for_homepage():
    """Получает опубликованные отзывы для главной страницы"""
    return Review.objects.filter(is_published=True).order_by('-created_at')[:6]

def check_phone_verification(request):
    """API endpoint для проверки номера телефона (для AJAX)"""
    if request.method == 'GET':
        phone = request.GET.get('phone', '')
        master_id = request.GET.get('master_id', '')
        client_name = request.GET.get('client_name', '')
        
        if phone and master_id:
            try:
                master = Master.objects.get(id=master_id)
                
                # Маппинг имен мастеров
                master_name_mapping = {
                    'Александр Петров': 'alexander',
                    'Михаил Козлов': 'mikhail', 
                    'Дмитрий Соколов': 'dmitry',
                }
                
                master_code = master_name_mapping.get(master.name)
                
                if not master_code:
                    return JsonResponse({'verified': False, 'message': 'Мастер не найден'})
                
                # Нормализуем номер из формы
                search_phone = re.sub(r'\D', '', phone)
                
                # Ищем записи
                bookings = Booking.objects.filter(master=master_code)
                booking_found = False
                
                for booking in bookings:
                    # Нормализуем номер из базы
                    booking_phone_clean = re.sub(r'\D', '', booking.phone)
                    
                    # Сравниваем последние 10 цифр
                    phone_last_10 = search_phone[-10:] if len(search_phone) > 10 else search_phone
                    booking_phone_last_10 = booking_phone_clean[-10:] if len(booking_phone_clean) > 10 else booking_phone_clean
                    
                    if phone_last_10 == booking_phone_last_10:
                        # Если указано имя, проверяем его
                        if client_name:
                            if client_name.lower() in booking.name.lower() or booking.name.lower() in client_name.lower():
                                booking_found = True
                                break
                        else:
                            booking_found = True
                            break
                
                return JsonResponse({
                    'verified': booking_found,
                    'message': 'Клиент подтвержден' if booking_found else 'Запись не найдена. Проверьте номер, имя и выбор мастера.'
                })
            except Master.DoesNotExist:
                return JsonResponse({'verified': False, 'message': 'Мастер не найден'})
        
        return JsonResponse({'verified': False, 'message': 'Недостаточно данных'})