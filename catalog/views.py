# catalog/views.py

from django.shortcuts import render
from django.http import HttpResponse

def catalog_list(request):
    """View-функция для страницы со списком услуг."""
    return render(request, 'catalog/catalog.html') 

def product_detail(request, product_id):
    """View-функция для страницы конкретной прически"""
    # product_id автоматически передается из URL
    return HttpResponse(f"Прическа №{product_id}")
