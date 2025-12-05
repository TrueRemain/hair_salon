# homepage/urls.py

# Импортируем функцию path для определения маршрутов
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
    path('admin/', admin.site.urls),
    #path('', homepage_views.index, name='index'),  # Главная страница
    path('reviews/', include('reviews.urls')),     # ВСЕ маршруты отзывов 
    path('api/booking/create/', views.create_booking, name='create_booking'),
    path('api/booking/slots/', views.get_available_time_slots, name='get_slots'), 
    path('api/feedback/stats/', views.get_feedback_stats, name='feedback_stats'),
    path('debug/', debug_urls, name='debug_urls'), 
    # для личного кабинета
    path('masters/login/', views.master_login, name='master_login'),
    path('masters/dashboard/', views.master_dashboard, name='master_dashboard'),
    path('masters/dashboard/<str:master_code>/', views.master_dashboard, name='master_dashboard_master'),
    path('masters/admin/', views.admin_panel, name='admin_panel'),
    path('masters/switch/<str:master_code>/', views.switch_to_master, name='switch_to_master'),
    path('masters/return-admin/', views.return_to_admin, name='return_to_admin'),
    path('masters/logout/', views.master_logout, name='master_logout'), 
    path('catalog/style-consultation/', views.style_consultation, name='style_consultation'), 
    path('feedback/submit/', views.service_feedback, name='service_feedback'), 
    path('style_consultation/', views.style_consultation, name='style_consultation'),
    path('service_feedback/', views.service_feedback, name='service_feedback'), 
    path('', views.index, name='index'), 
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)