# homepage/admin.py
from django.contrib import admin
from .models import Booking  # ДОБАВЬТЕ этот импорт

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'master', 'service', 'date', 'time', 'created_at']
    list_filter = ['master', 'date', 'service']
    search_fields = ['name', 'phone']
    ordering = ['-date', '-time']