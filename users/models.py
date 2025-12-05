# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """Кастомная модель пользователя для клиентов парикмахерской"""
    
    # Дополнительные поля для клиентов
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        validators=[RegexValidator(regex=r'^\+?[78]\d{10}$', message='Неверный формат телефона')],
        blank=True
    )
    
    # Связь с вашими существующими моделями
    bookings = models.ManyToManyField('homepage.Booking', related_name='clients', blank=True)
    consultations = models.ManyToManyField('homepage.StyleConsultation', related_name='clients', blank=True)
    
    # Дата рождения (опционально)
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    
    # Фото профиля
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    
    # Дополнительная информация
    preferences = models.TextField(blank=True, verbose_name='Предпочтения в стрижках')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f'{self.username} ({self.email or self.phone})'
    
    @property
    def upcoming_bookings(self):
        """Будущие записи пользователя"""
        from datetime import date
        return self.bookings.filter(date__gte=date.today()).order_by('date', 'time')
    
    @property
    def past_bookings(self):
        """Прошедшие записи пользователя"""
        from datetime import date
        return self.bookings.filter(date__lt=date.today()).order_by('-date', '-time')