# homepage/forms.py
from django import forms
from .models import Booking

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