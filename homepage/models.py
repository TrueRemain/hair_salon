# homepage/models.py
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator, ValidationError
import re 
from django.conf import settings

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
    
# Добавляем связь с пользователем
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ссылается на вашу кастомную модель
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_bookings',
        verbose_name='Пользователь'
    )
    
    def save(self, *args, **kwargs):
        """При сохранении записи, если есть аутентифицированный пользователь, связываем"""
        if not self.pk:  # только для новых записей
            from django.contrib.auth.models import AnonymousUser
            request = getattr(self, '_request', None)
            if request and not isinstance(request.user, AnonymousUser):
                self.user = request.user
        super().save(*args, **kwargs)

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

class ServiceFeedback(models.Model):
    """Модель для отзывов о качестве обслуживания"""
    
    RATING_CHOICES = [
        (1, '1 - Очень плохо'),
        (2, '2 - Плохо'),
        (3, '3 - Удовлетворительно'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]
    
    # Информация о клиенте
    name = models.CharField('Ваше имя', max_length=100, blank=True)
    phone = models.CharField(
        'Телефон',
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^(\+7|8)[\-\s]?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}$',
                message='Введите корректный номер телефона'
            )
        ],
        blank=True
    )
    email = models.EmailField('Email', blank=True)
    visit_date = models.DateField('Дата посещения', null=True, blank=True)
    
    # Вопросы с рейтингами
    cleanliness_rating = models.IntegerField('Чистота в салоне', choices=RATING_CHOICES, default=3)
    staff_friendliness = models.IntegerField('Вежливость персонала', choices=RATING_CHOICES, default=3)
    master_skill = models.IntegerField('Профессионализм мастера', choices=RATING_CHOICES, default=3)
    service_speed = models.IntegerField('Скорость обслуживания', choices=RATING_CHOICES, default=3)
    price_quality = models.IntegerField('Соотношение цены и качества', choices=RATING_CHOICES, default=3)
    waiting_time = models.IntegerField('Время ожидания (минут)', default=0)  # в минутах
    
    # Дополнительные вопросы
    master_choice = models.CharField(
        'Какого мастера вы посещали?',
        max_length=20,
        choices=Booking.MASTER_CHOICES,
        blank=True
    )
    
    service_type = models.CharField(
        'Какую услугу вы получали?',
        max_length=50,
        choices=Booking.SERVICE_CHOICES,
        blank=True
    )
    
    would_recommend = models.BooleanField('Порекомендуете ли вы нас друзьям?', default=True)
    
    # Дополнительные поля
    improvements = models.TextField(
        'Что мы можем улучшить?',
        help_text='Ваши предложения по улучшению нашего сервиса',
        blank=True
    )
    
    other_comments = models.TextField('Дополнительные комментарии', blank=True)
    
    created_at = models.DateTimeField('Дата заполнения', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отзыв о качестве'
        verbose_name_plural = 'Отзывы о качестве'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Отзыв от {self.name or "Аноним"} - {self.created_at.strftime("%d.%m.%Y")}'
    
    @property
    def average_rating(self):
        """Средний рейтинг по всем вопросам"""
        ratings = [
            self.cleanliness_rating,
            self.staff_friendliness,
            self.master_skill,
            self.service_speed,
            self.price_quality,
        ]
        valid_ratings = [r for r in ratings if r > 0]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return 0
    
    @property
    def rating_percentage(self):
        """Рейтинг в процентах"""
        return (self.average_rating / 5) * 100