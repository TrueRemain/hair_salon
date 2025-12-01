from django.contrib import admin
from .models import Master, Review

# Регистрируем модель Master в админке
@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization']  # Что показывать в списке
    search_fields = ['name']  # Поиск по имени

# Регистрируем модель Review в админке  
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'master', 'stars', 'created_at', 'is_published']
    list_filter = ['master', 'stars', 'is_published']  # Фильтры справа
    search_fields = ['client_name', 'text']  # Поиск по имени и тексту
    list_editable = ['is_published']  # Можно менять опубликован прямо из списка