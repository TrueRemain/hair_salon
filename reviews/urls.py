from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/', views.add_review, name='add_review'),
    path('check-phone/', views.check_phone_verification, name='check_phone'),
    #path('api/create-booking/', views.create_booking_api, name='create_booking_api'),  
    path('', views.review_info, name='review_info'),  # Информационная страница
    path('add/<str:token>/', views.add_review, name='add_review_with_token'),  # Одноразовая ссылка
    path('success/', views.review_success, name='review_success'),  # Успешная отправка
]