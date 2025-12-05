# homepage/forms.py
from django import forms
from .models import Booking, StyleConsultation, MasterAccount, ServiceFeedback
from django.core.exceptions import ValidationError
import re

class MasterLoginForm(forms.Form):
    """Форма входа для мастеров"""
    username = forms.CharField(
        label='Логин',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш логин'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            from .masters_auth import MasterAuth
            master_account = MasterAuth.authenticate(username, password)
            if not master_account:
                raise forms.ValidationError('Неверный логин или пароль')
            cleaned_data['master_account'] = master_account
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'master', 'service', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request', None)
            super().__init__(*args, **kwargs)
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and self.request.user.is_authenticated:
            instance.user = self.request.user
            instance.name = self.request.user.get_full_name() or self.request.user.username
            if self.request.user.phone:
                instance.phone = self.request.user.phone
            
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        # Проверяем, не занято ли время у мастера
        if master and date and time:
            if Booking.objects.filter(master=master, date=date, time=time).exists():
                raise forms.ValidationError('Это время у выбранного мастера уже занято!')
        
        return cleaned_data 
    
class StyleConsultationForm(forms.ModelForm):
    """Форма консультации по стилю с расширенной валидацией"""
    
    class Meta:
        model = StyleConsultation
        fields = [
            'name', 'phone', 'email', 'age', 
            'hair_type', 'face_shape', 'current_style', 
            'desired_style', 'preferences'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван Иванов',
                'pattern': '^[А-Яа-яЁёA-Za-z\s\-]+$',
                'title': 'Только буквы, пробелы и дефисы'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67',
                'pattern': '^(\+7|8)[\-\s]?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}$',
                'title': 'Формат: +7(900)123-45-67 или 89001234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '25',
                'min': '12',
                'max': '100'
            }),
            'hair_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'face_shape': forms.Select(attrs={
                'class': 'form-select'
            }),
            'current_style': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Например: короткая стрижка с пробором сбоку...',
                'minlength': '10'
            }),
            'desired_style': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Например: хочу современную стрижку с текстурированием...',
                'minlength': '10'
            }),
            'preferences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Например: не люблю слишком короткие виски...'
            }),
        }
        labels = {
            'name': 'Ваше имя*',
            'phone': 'Номер телефона*',
            'email': 'Email (необязательно)',
            'age': 'Возраст*',
            'hair_type': 'Тип ваших волос*',
            'face_shape': 'Форма вашего лица*',
            'current_style': 'Ваша текущая стрижка*',
            'desired_style': 'Какой образ вы хотите получить?*',
            'preferences': 'Ваши предпочтения и пожелания',
        }
    
    def clean_name(self):
        """Валидация имени"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('Это поле обязательно для заполнения')
        
        # Проверка на минимальную длину
        if len(name) < 2:
            raise ValidationError('Имя должно содержать минимум 2 символа')
        
        # Проверка на максимальную длину
        if len(name) > 100:
            raise ValidationError('Имя не должно превышать 100 символов')
        
        # Проверка на допустимые символы
        if not re.match(r'^[А-Яа-яЁёA-Za-z\s\-]+$', name):
            raise ValidationError('Имя может содержать только буквы, пробелы и дефисы')
        
        # Проверка на заглавную первую букву
        if not name[0].isupper():
            raise ValidationError('Имя должно начинаться с заглавной буквы')
        
        # Проверка на отсутствие множественных пробелов
        if '  ' in name:
            raise ValidationError('Уберите лишние пробелы в имени')
        
        return name
    
    def clean_phone(self):
        """Валидация телефона"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            raise ValidationError('Это поле обязательно для заполнения')
        
        # Удаляем все нецифровые символы кроме +
        phone_digits = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем различные форматы
        phone_patterns = [
            r'^\+7\d{10}$',      # +79001234567
            r'^8\d{10}$',        # 89001234567
            r'^7\d{10}$',        # 79001234567
        ]
        
        valid = False
        for pattern in phone_patterns:
            if re.match(pattern, phone_digits):
                valid = True
                break
        
        if not valid:
            raise ValidationError(
                'Введите корректный номер телефона. Примеры: '
                '+7(900)123-45-67, 89001234567, 79001234567'
            )
        
        # Нормализуем к формату +79001234567
        if phone_digits.startswith('8'):
            phone_digits = '+7' + phone_digits[1:]
        elif phone_digits.startswith('7'):
            phone_digits = '+' + phone_digits
        
        return phone_digits
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email', '').strip()
        
        if email:  # Поле необязательное, но если заполнено - валидируем
            # Проверка формата через Django
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError('Введите корректный email адрес')
            
            # Дополнительные проверки
            if len(email) > 254:
                raise ValidationError('Email слишком длинный')
            
            # Проверка на валидный домен (базовая)
            if '@' in email:
                local_part, domain = email.rsplit('@', 1)
                if len(local_part) > 64:
                    raise ValidationError('Локальная часть email слишком длинная')
                
                # Проверка на наличие точки в домене
                if '.' not in domain:
                    raise ValidationError('Некорректный домен в email')
        
        return email
    
    def clean_age(self):
        """Валидация возраста"""
        age = self.cleaned_data.get('age')
        
        if age is None:
            raise ValidationError('Это поле обязательно для заполнения')
        
        # Проверка типа данных
        if not isinstance(age, int):
            try:
                age = int(age)
            except (ValueError, TypeError):
                raise ValidationError('Возраст должен быть числом')
        
        # Проверка диапазона
        if age < 12:
            raise ValidationError('Минимальный возраст - 12 лет')
        
        if age > 100:
            raise ValidationError('Максимальный возраст - 100 лет')
        
        return age
    
    def clean_current_style(self):
        """Валидация описания текущей стрижки"""
        current_style = self.cleaned_data.get('current_style', '').strip()
        
        if not current_style:
            raise ValidationError('Это поле обязательно для заполнения')
        
        if len(current_style) < 10:
            raise ValidationError('Опишите вашу текущую стрижку подробнее (минимум 10 символов)')
        
        if len(current_style) > 1000:
            raise ValidationError('Описание слишком длинное (максимум 1000 символов)')
        
        return current_style
    
    def clean_desired_style(self):
        """Валидация описания желаемого образа"""
        desired_style = self.cleaned_data.get('desired_style', '').strip()
        
        if not desired_style:
            raise ValidationError('Это поле обязательно для заполнения')
        
        if len(desired_style) < 10:
            raise ValidationError('Опишите желаемый образ подробнее (минимум 10 символов)')
        
        if len(desired_style) > 1000:
            raise ValidationError('Описание слишком длинное (максимум 1000 символов)')
        
        return desired_style 
    
class ServiceFeedbackForm(forms.ModelForm):
    """Форма опроса о качестве обслуживания"""
    
    class Meta:
        model = ServiceFeedback
        fields = [
            'name', 'phone', 'email', 'visit_date',
            'cleanliness_rating', 'staff_friendliness', 'master_skill',
            'service_speed', 'price_quality', 'waiting_time',
            'master_choice', 'service_type', 'would_recommend',
            'improvements', 'other_comments'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван Иванов (необязательно)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67 (необязательно)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com (необязательно)'
            }),
            'visit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'waiting_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '120',
                'placeholder': 'Минуты'
            }),
            'improvements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваши предложения по улучшению...'
            }),
            'other_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные пожелания или комментарии...'
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'phone': 'Телефон',
            'email': 'Email',
            'visit_date': 'Дата посещения',
            'cleanliness_rating': 'Чистота в салоне',
            'staff_friendliness': 'Вежливость персонала',
            'master_skill': 'Профессионализм мастера',
            'service_speed': 'Скорость обслуживания',
            'price_quality': 'Соотношение цены и качества',
            'waiting_time': 'Сколько минут вы ждали мастера?',
            'master_choice': 'Какого мастера вы посещали?',
            'service_type': 'Какую услугу вы получали?',
            'would_recommend': 'Порекомендуете ли вы нас друзьям?',
            'improvements': 'Что мы можем улучшить?',
            'other_comments': 'Дополнительные комментарии',
        }    