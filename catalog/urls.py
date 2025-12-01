# catalog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog_list, name='catalog_list'), 
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]