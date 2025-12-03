# homepage/models.py
from django.db import models
from django.core.validators import RegexValidator

class Booking(models.Model):
    MASTER_CHOICES = [
        ('alexander', 'Александр Петров'),
        ('mikhail', 'Михаил Козлов'), 
        ('dmitry', 'Дмитрий Соколов'),
    ]
    
    SERVICE_CHOICES = [
        ('male_haircut', 'Мужская стрижка'),
        ('machine_haircut', 'Стрижка машинкой'),
        ('model_haircut', 'Модельная стрижка'),
        ('styling', 'Укладка и стайлинг'),
        ('beard_trim', 'Стрижка бороды'),
        ('royal_shave', 'Королевское бритье'),
        ('beard_complex', 'Комплекс "Борода+"'),
        ('gray_camouflage', 'Камуфляж седины'),
    ]

    name = models.CharField(max_length=100, verbose_name='Имя клиента')
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон',
        validators=[RegexValidator(regex=r'^\+?[78]\d{10}$', message='Неверный формат телефона')]
    )
    master = models.CharField(max_length=20, choices=MASTER_CHOICES, verbose_name='Мастер')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name='Услуга')
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        unique_together = ['master', 'date', 'time']
    
    def __str__(self):
        return f"{self.name} - {self.get_master_display()} - {self.date} {self.time}" 
    
# Добавьте после существующей модели Booking

class MasterAccount(models.Model):
    """Модель для учетных данных мастеров"""
    
    MASTER_CHOICES = [
        ('alexander', 'Александр Петров'),
        ('mikhail', 'Михаил Козлов'), 
        ('dmitry', 'Дмитрий Соколов'),
        ('admin', 'Администратор'),
    ]
    
    username = models.CharField(max_length=50, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=100, verbose_name='Пароль')
    master_code = models.CharField(max_length=20, choices=MASTER_CHOICES, verbose_name='Код мастера')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Аккаунт мастера'
        verbose_name_plural = 'Аккаунты мастеров'
    
    def __str__(self):
        return f"{self.get_master_code_display()} ({self.username})"
    
    @property
    def is_admin(self):
        return self.master_code == 'admin'