# homepage/models.py
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator, ValidationError
import re

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
    
class StyleConsultation(models.Model):
    HAIR_TYPES = [
        ('straight', 'Прямые'),
        ('wavy', 'Волнистые'),
        ('curly', 'Кудрявые'),
        ('thin', 'Тонкие'),
        ('thick', 'Густые'),
    ]
    
    FACE_SHAPES = [
        ('oval', 'Овальное'),
        ('round', 'Круглое'),
        ('square', 'Квадратное'),
        ('heart', 'Сердцевидное'),
        ('diamond', 'Ромбовидное'),
    ]
    
    name = models.CharField(
        'Имя', 
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-яЁёA-Za-z\s\-]+$',
                message='Имя может содержать только буквы, пробелы и дефисы'
            )
        ]
    )
    phone = models.CharField(
        'Телефон', 
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^(\+7|8)[\-\s]?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}$',
                message='Введите корректный номер телефона. Пример: +7(900)123-45-67 или 89001234567'
            )
        ]
    )
    email = models.EmailField(
        'Email', 
        blank=True,
        validators=[EmailValidator(message='Введите корректный email адрес')]
    )
    age = models.IntegerField(
        'Возраст',
        validators=[
            MinValueValidator(12, message='Минимальный возраст - 12 лет'),
            MaxValueValidator(100, message='Максимальный возраст - 100 лет')
        ]
    )
    hair_type = models.CharField('Тип волос', max_length=50, choices=HAIR_TYPES)
    face_shape = models.CharField('Форма лица', max_length=50, choices=FACE_SHAPES)
    current_style = models.TextField('Текущая стрижка', help_text='Опишите вашу текущую прическу')
    desired_style = models.TextField('Желаемый образ', help_text='Какую стрижку вы хотите?')
    preferences = models.TextField('Предпочтения', help_text='Что вам нравится/не нравится в стрижках?', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Консультация по стилю'
        verbose_name_plural = 'Консультации по стилю'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.created_at.strftime("%d.%m.%Y")}'    

    def clean(self):
        """Дополнительная валидация на уровне модели"""
        super().clean()
        
        # Валидация имени (первая буква должна быть заглавной)
        if self.name and not self.name[0].isupper():
            raise ValidationError({'name': 'Имя должно начинаться с заглавной буквы'})
        
        # Валидация возраста (только целые числа)
        if not isinstance(self.age, int):
            raise ValidationError({'age': 'Возраст должен быть целым числом'})
        
        # Нормализация телефона
        if self.phone:
            # Удаляем все нецифровые символы кроме +
            phone_digits = re.sub(r'[^\d+]', '', self.phone)
            if phone_digits.startswith('8'):
                phone_digits = '+7' + phone_digits[1:]
            elif phone_digits.startswith('7'):
                phone_digits = '+' + phone_digits
            self.phone = phone_digits
