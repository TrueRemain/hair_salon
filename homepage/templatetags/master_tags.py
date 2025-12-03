# homepage/templatetags/master_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получение элемента из словаря по ключу в шаблоне"""
    return dictionary.get(key, {})