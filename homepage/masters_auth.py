# homepage/masters_auth.py
from django.contrib.auth.hashers import make_password, check_password
from .models import MasterAccount

class MasterAuth:
    """Класс для аутентификации мастеров"""
    
    @staticmethod
    def authenticate(username, password):
        """Проверка логина и пароля мастера"""
        try:
            master_account = MasterAccount.objects.get(username=username, is_active=True)
            if check_password(password, master_account.password):
                return master_account
        except MasterAccount.DoesNotExist:
            return None
        return None
    
    @staticmethod
    def create_master_account(username, password, master_code):
        """Создание нового аккаунта мастера"""
        if MasterAccount.objects.filter(username=username).exists():
            return None
        
        hashed_password = make_password(password)
        master_account = MasterAccount.objects.create(
            username=username,
            password=hashed_password,
            master_code=master_code
        )
        return master_account
    
    @staticmethod
    def get_master_bookings(master_code):
        """Получение всех предстоящих записей для мастера"""
        from django.utils import timezone
        from .models import Booking
        
        today = timezone.now().date()
        # Получаем только будущие записи для указанного мастера
        bookings = Booking.objects.filter(
            master=master_code,
            date__gte=today
        ).order_by('date', 'time')
        
        return bookings