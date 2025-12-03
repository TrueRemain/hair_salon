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
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MasterLoginForm
from .masters_auth import MasterAuth
from django.utils import timezone 
from django.http import HttpResponseForbidden


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

def master_login(request):
    """Страница входа для мастеров"""
    if request.method == 'POST':
        form = MasterLoginForm(request.POST)
        if form.is_valid():
            master_account = form.cleaned_data['master_account']
            # Сохраняем информацию о мастере в сессии
            request.session['master_id'] = master_account.id
            request.session['master_username'] = master_account.username
            request.session['master_code'] = master_account.master_code
            request.session['master_name'] = master_account.get_master_code_display()
            request.session['is_admin'] = master_account.master_code == 'admin'
            
            # Если это админ - перенаправляем в админ-панель
            if master_account.master_code == 'admin':
                return redirect('admin_panel')
            else:
                return redirect('master_dashboard')
    else:
        form = MasterLoginForm()
    
    return render(request, 'homepage/master_login.html', {'form': form})

def master_dashboard(request, master_code=None):
    """Личный кабинет мастера"""
    # Если передан master_code - это админ зашел от имени мастера
    if master_code and request.session.get('is_admin'):
        # Проверяем, существует ли мастер с таким кодом
        from .models import MasterAccount
        try:
            master_account = MasterAccount.objects.get(master_code=master_code)
            request.session['master_id'] = master_account.id
            request.session['master_username'] = master_account.username
            request.session['master_code'] = master_account.master_code
            request.session['master_name'] = master_account.get_master_code_display()
            request.session['is_admin'] = False  # Временно снимаем права админа
        except MasterAccount.DoesNotExist:
            messages.error(request, 'Мастер не найден')
            return redirect('admin_panel')
    
    # Проверяем авторизацию
    elif 'master_id' not in request.session:
        messages.error(request, 'Пожалуйста, войдите в систему')
        return redirect('master_login')
    
    master_code = request.session.get('master_code')
    master_name = request.session.get('master_name')
    
    # Получаем предстоящие записи (начиная с сегодняшнего дня)
    today = timezone.now().date()
    upcoming_bookings = Booking.objects.filter(
        master=master_code,
        date__gte=today
    ).order_by('date', 'time')
    
    # Получаем прошедшие записи (до сегодняшнего дня)
    past_bookings = Booking.objects.filter(
        master=master_code,
        date__lt=today
    ).order_by('-date', '-time')[:50]  # Ограничиваем 50 последними записями
    
    # Группируем записи по дате
    def group_bookings_by_date(bookings):
        bookings_by_date = {}
        for booking in bookings:
            date_str = booking.date.strftime('%d.%m.%Y')
            if date_str not in bookings_by_date:
                bookings_by_date[date_str] = []
            bookings_by_date[date_str].append(booking)
        return bookings_by_date
    
    context = {
        'master_name': master_name,
        'upcoming_by_date': group_bookings_by_date(upcoming_bookings),
        'past_by_date': group_bookings_by_date(past_bookings),
        'total_upcoming': upcoming_bookings.count(),
        'total_past': past_bookings.count(),
        'today': today.strftime('%d.%m.%Y'),
        'is_admin_view': master_code is not None and 'temp_admin' in request.session,
    }
    
    return render(request, 'homepage/master_dashboard.html', context)

def admin_panel(request):
    """Админ-панель для просмотра всех записей"""
    # Проверяем, что пользователь - админ
    if not request.session.get('is_admin'):
        return HttpResponseForbidden("Доступ запрещен")
    
    from .models import MasterAccount, Booking
    from django.utils import timezone
    
    # Получаем всех мастеров (кроме админа)
    masters = MasterAccount.objects.exclude(master_code='admin')
    
    # Получаем все записи
    today = timezone.now().date()
    all_bookings = Booking.objects.all().order_by('date', 'time')
    upcoming_bookings = all_bookings.filter(date__gte=today)
    past_bookings = all_bookings.filter(date__lt=today)
    
    # Группируем записи по мастерам
    bookings_by_master = {}
    for master in masters:
        master_bookings = all_bookings.filter(master=master.master_code)
        bookings_by_master[master.master_code] = {
            'upcoming': master_bookings.filter(date__gte=today).count(),
            'past': master_bookings.filter(date__lt=today).count(),
            'total': master_bookings.count(),
            'name': master.get_master_code_display()
        }
    
    context = {
        'masters': masters,
        'bookings_by_master': bookings_by_master,
        'total_bookings': all_bookings.count(),
        'upcoming_count': upcoming_bookings.count(),
        'past_count': past_bookings.count(),
        'today': today.strftime('%d.%m.%Y'),
    }
    
    return render(request, 'homepage/admin_panel.html', context)

def switch_to_master(request, master_code):
    """Админ переключается в кабинет мастера"""
    if not request.session.get('is_admin'):
        return HttpResponseForbidden("Доступ запрещен")
    
    # Сохраняем флаг, что это временный вход от админа
    request.session['temp_admin'] = True
    return redirect('master_dashboard_master', master_code=master_code)

def master_logout(request):
    """Выход из личного кабинета"""
    # Если это был временный вход от админа - возвращаемся в админку
    if request.session.get('temp_admin'):
        del request.session['temp_admin']
        request.session['is_admin'] = True
        return redirect('admin_panel')
    
    # Обычный выход
    if 'master_id' in request.session:
        del request.session['master_id']
        del request.session['master_username']
        del request.session['master_code']
        del request.session['master_name']
        del request.session['is_admin']
        messages.success(request, 'Вы успешно вышли из системы')
    return redirect('master_login')

def return_to_admin(request):
    """Возврат из кабинета мастера в админку"""
    # Очищаем сессию мастера
    for key in ['master_id', 'master_username', 'master_code', 'master_name', 'temp_admin']:
        if key in request.session:
            del request.session[key]
    
    # Устанавливаем флаг админа
    request.session['is_admin'] = True
    return redirect('admin_panel')