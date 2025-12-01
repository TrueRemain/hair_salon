from django import template

register = template.Library()

@register.filter
def pluralize_reviews(number):
    """
    Функция для правильного склонения слова "отзыв" в зависимости от числа
    """
    if not number:
        return "отзывов"
    
    number = int(number)
    
    if number % 10 == 1 and number % 100 != 11:
        return "отзыв"
    elif number % 10 in [2, 3, 4] and number % 100 not in [12, 13, 14]:
        return "отзыва"
    else:
        return "отзывов"