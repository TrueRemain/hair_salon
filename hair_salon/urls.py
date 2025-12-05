# hair_salon/urls.py
"""
from django.contrib import admin
# Импортируем функцию include, чтобы подключать другие urls.py
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls), # Стандартная админка Django
    path('', include('homepage.urls')), # Подключаем маршруты из приложения homepage
    path('catalog/', include('catalog.urls')),  
    path('about/', include('about.urls')), 
    path('reviews/', include('reviews.urls'))
] 
""" 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from homepage import views as homepage_views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', homepage_views.index, name='index'),
    path('catalog/', homepage_views.catalog, name='catalog'),      # ДОБАВЬТЕ
    path('about/', homepage_views.about, name='about'),            # ДОБАВЬТЕ
    path('reviews/', include('reviews.urls')), 
    path('users/', include('users.urls', namespace='users')), 
    path('', include('homepage.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)