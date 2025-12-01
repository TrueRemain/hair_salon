# reviews.forms.txt
from django import forms
from .models import Review, Master
from homepage.models import Booking  # Импортируем модель Booking из homepage
import re

class ReviewForm(forms.ModelForm):
    # Переопределяем поле stars чтобы убрать пустой выбор
    stars = forms.ChoiceField(
        choices=[
            (1, '★☆☆☆☆'),
            (2, '★★☆☆☆'),
            (3, '★★★☆☆'),
            (4, '★★★★☆'),
            (5, '★★★★★'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'star-rating'}),
        label='Оценка'
    )
    
    # Добавляем поле телефона в форму
    phone = forms.CharField(
        max_length=18,
        label='Номер телефона',
        help_text='Введите номер, который использовали при записи к мастеру',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        })
    )
    
    class Meta:
        model = Review
        fields = ['master', 'client_name', 'phone', 'stars', 'text']
        widgets = {
            'master': forms.Select(attrs={'class': 'form-control'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваш отзыв', 'rows': 4}),
        }
        labels = {
            'master': 'Выберите мастера',
            'client_name': 'Ваше имя',
            'text': 'Текст отзыва',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исправляем placeholder для мастера
        self.fields['master'].empty_label = 'Выберите мастера'
    
    def clean_phone(self):
        """Очистка и валидация номера телефона"""
        phone = self.cleaned_data['phone']
        
        # Удаляем все нецифровые символы
        cleaned_phone = re.sub(r'\D', '', phone)
        
        # Проверяем длину
        if len(cleaned_phone) not in [10, 11]:
            raise forms.ValidationError("Номер телефона должен содержать 10 или 11 цифр")
        
        return cleaned_phone
    
    def clean(self):
        """Проверка, что клиент действительно записывался к мастеру"""
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        master = cleaned_data.get('master')
        client_name = cleaned_data.get('client_name')
        
        if phone and master and client_name:
            # Нормализуем номер из формы отзыва
            search_phone = re.sub(r'\D', '', phone)
            
            # Маппинг имен мастеров между формой записи и отзыва
            master_name_mapping = {
                'Александр Петров': 'alexander',
                'Михаил Козлов': 'mikhail', 
                'Дмитрий Соколов': 'dmitry',
            }
            
            # Получаем код мастера для поиска в Booking
            master_code = master_name_mapping.get(master.name)
            
            if not master_code:
                raise forms.ValidationError("Ошибка: мастер не найден в системе записей")
            
            # Ищем записи с этим номером у выбранного мастера
            # Сравниваем нормализованные номера
            bookings = Booking.objects.filter(master=master_code)
            
            booking_found = False
            for booking in bookings:
                # Нормализуем номер из базы
                booking_phone_clean = re.sub(r'\D', '', booking.phone)
                
                # Сравниваем номера (последние 10 цифр)
                phone_last_10 = search_phone[-10:] if len(search_phone) > 10 else search_phone
                booking_phone_last_10 = booking_phone_clean[-10:] if len(booking_phone_clean) > 10 else booking_phone_clean
                
                if phone_last_10 == booking_phone_last_10:
                    # Дополнительно проверяем имя (примерное совпадение)
                    if client_name.lower() in booking.name.lower() or booking.name.lower() in client_name.lower():
                        booking_found = True
                        break
            
            if not booking_found:
                raise forms.ValidationError(
                    "Не найдено записей с указанными данными у выбранного мастера. "
                    "Пожалуйста, убедитесь, что:\n"
                    "1. Номер телефона и имя введены правильно\n" 
                    "2. Вы записывались именно к этому мастеру\n"
                    "3. Запись была сделана через нашу систему"
                )
            else:
                # Если клиент подтвержден, помечаем отзыв как проверенный
                cleaned_data['is_verified'] = True
        
        return cleaned_data