# homepage/urls.py

# Импортируем функцию path для определения маршрутов
from django.urls import path
from . import views 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from homepage import views as homepage_views  # Импортируем views из homepage 
from django.http import JsonResponse

def debug_urls(request):
    """Функция для отладки - проверяет доступность URLs"""
    return JsonResponse({
        'message': 'Debug endpoint is working!',
        'available_urls': [
            '/',
            '/about/', 
            '/catalog/',
            '/api/booking/create/',
            '/api/booking/slots/'
        ]
    })

urlpatterns = [
    # Если пользователь зайдет на корневой адрес ('' - пустая строка),
    # то нужно вызвать функцию index из файла views.py
    path('', views.index, name='index'), 
    path('admin/', admin.site.urls),
    #path('', homepage_views.index, name='index'),  # Главная страница
    path('reviews/', include('reviews.urls')),     # ВСЕ маршруты отзывов 
    path('api/booking/create/', views.create_booking, name='create_booking'),
    path('api/booking/slots/', views.get_available_time_slots, name='get_slots'), 
    path('debug/', debug_urls, name='debug_urls'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)