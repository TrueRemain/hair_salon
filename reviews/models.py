# reviews.models.txt - УДАЛИТЬ модель Booking отсюда
# Оставляем только Master и Review
from django.db import models 
from django.db.models import Avg, Count
from django.core.validators import RegexValidator

class Master(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя мастера")
    photo = models.ImageField(upload_to='masters/', blank=True, null=True, verbose_name="Фото")
    specialization = models.CharField(max_length=200, verbose_name="Специализация")
    
    @property
    def average_rating(self):
        """Средний рейтинг из ВСЕХ отзывов (включая неопубликованные)"""
        result = self.review_set.aggregate(average=Avg('stars'))
        return result['average'] or 0
    
    @property 
    def reviews_count(self):
        """Количество всех отзывов"""
        return self.review_set.count()
    
    @property
    def rating_display(self):
        """Отображение рейтинга в виде HTML с Font Awesome звездами"""
        avg = self.average_rating
        if avg == 0:
            return '<span class="no-stars">Нет оценок</span>'
        
        stars_html = ''
        full_stars = int(avg)
        has_half_star = avg - full_stars >= 0.5
        
        # Полные звезды
        for i in range(full_stars):
            stars_html += '<i class="fas fa-star"></i>'
        
        # Половина звезды
        if has_half_star:
            stars_html += '<i class="fas fa-star-half-alt"></i>'
            full_stars += 1
        
        # Пустые звезды
        for i in range(5 - full_stars):
            stars_html += '<i class="far fa-star"></i>'
        
        return stars_html

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера" 

class Review(models.Model):
    STAR_CHOICES = [
        (5, '⭐⭐⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (3, '⭐⭐⭐'),
        (2, '⭐⭐'),
        (1, '⭐'),
    ]
    
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name="Мастер")
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(
        max_length=20, 
        verbose_name="Номер телефона",
        help_text="Введите номер, который использовали при записи"
    )
    stars = models.IntegerField(choices=STAR_CHOICES, verbose_name="Оценка")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    is_verified = models.BooleanField(default=False, verbose_name="Проверен (клиент подтвержден)")
    
    def __str__(self):
        return f"Отзыв от {self.client_name} для {self.master.name}"
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']