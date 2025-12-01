# homepage/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Booking
from .forms import BookingForm
from datetime import datetime
from django.shortcuts import render 
from django.http import HttpResponse 
from reviews.models import Master, Review  
from reviews.review_tokens import token_manager


def index(request): 
    # Получаем всех мастеров с рейтингами
    masters_with_ratings = Master.objects.all()
    # Берем 6 последних ОПУБЛИКОВАННЫХ отзывов
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:6]
    
    return render(request, 'homepage/index.html', {
        'reviews': reviews  # Передаем отзывы в шаблон
    }) 
def catalog(request):
    return render(request, 'homepage/catalog.html')

def about(request):
    return render(request, 'homepage/about.html') 

@csrf_exempt
@require_POST
def create_booking(request):
    """Создание новой записи через AJAX"""
    try:
        data = json.loads(request.body)
        form = BookingForm(data)
        
        if form.is_valid():
            booking = form.save()
            
            # Генерируем токен для отзыва
            token = token_manager.generate_token(
                phone=booking.phone,
                client_name=booking.name,
                master_code=booking.master,
                booking_id=booking.id
            )
            
            # Создаем ссылку для отзыва
            review_url = request.build_absolute_uri(
                f'/reviews/add/{token}/'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Запись успешно оформлена!\n{booking.get_master_display()}\n{booking.get_service_display()}\n{booking.date} в {booking.time.strftime("%H:%M")}',
                'review_url': review_url
            })
        else:
            errors = []
            for field_errors in form.errors.values():
                errors.extend(field_errors)
            return JsonResponse({
                'success': False,
                'message': '❌ ' + '\n'.join(errors)
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'❌ Ошибка сервера: {str(e)}'
        })

def get_available_time_slots(request):
    """Получение доступных временных слотов для мастера и даты"""
    master = request.GET.get('master')
    date_str = request.GET.get('date')
    
    if not master or not date_str:
        return JsonResponse({'available_slots': []})
    
    try:
        # Получаем все занятые слоты для этого мастера и даты
        booked_slots = Booking.objects.filter(
            master=master, 
            date=date_str
        ).values_list('time', flat=True)
        
        # Конвертируем в строки для удобства
        booked_times = [slot.strftime('%H:%M') for slot in booked_slots]
        
        return JsonResponse({
            'booked_slots': booked_times,
            'available_slots': generate_time_slots(master, date_str, booked_times)
        })
        
    except Exception as e:
        return JsonResponse({'available_slots': [], 'error': str(e)})

def generate_time_slots(master, date_str, booked_times):
    """Генерация доступных временных слотов"""
    # Расписание мастеров
    masters_schedule = {
        'alexander': {'start': 10, 'end': 20, 'break': (14, 15)},
        'mikhail': {'start': 11, 'end': 19, 'break': None},
        'dmitry': {'start': 10, 'end': 18, 'break': (13, 14)},
    }
    
    schedule = masters_schedule.get(master, {'start': 10, 'end': 18, 'break': None})
    available_slots = []
    
    for hour in range(schedule['start'], schedule['end']):
        for minute in [0, 30]:  # Слоты каждые 30 минут
            time_str = f"{hour:02d}:{minute:02d}"
            
            # Проверяем, не в перерыве ли время
            is_break = False
            if schedule['break']:
                break_start, break_end = schedule['break']
                current_time = hour + minute/60
                if break_start <= current_time < break_end:
                    is_break = True
            
            # Добавляем слот, если он не занят и не в перерыве
            if time_str not in booked_times and not is_break:
                available_slots.append(time_str)
    
    return available_slots 
def about(request):
    # Получаем конкретных мастеров по именам
    alexander = Master.objects.filter(name="Александр Петров").first()
    mikhail = Master.objects.filter(name="Михаил Козлов").first()
    dmitry = Master.objects.filter(name="Дмитрий Соколов").first()
    
    context = {
        'alexander': alexander,
        'mikhail': mikhail,
        'dmitry': dmitry,
    }
    return render(request, 'homepage/about.html', context)
    #"""View-функция для главной страницы."""
    #return render(request, 'homepage/index.html') # Указываем путь к шаблону