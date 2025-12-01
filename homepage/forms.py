# homepage/forms.py
from django import forms
from .models import Booking

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