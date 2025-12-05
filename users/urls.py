# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Встроенные маршруты Django для смены пароля
    path('password_change/', 
     auth_views.PasswordChangeView.as_view(
         template_name='users/password_change.html',
         success_url=reverse_lazy('users:password_change_done')
     ), 
     name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), 
         name='password_change_done'),
    
    # Восстановление пароля
    path('password_reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='users/password_reset.html',
         email_template_name='users/emails/password_reset_email.html',
         success_url=reverse_lazy('users:password_reset_done')
     ), 
     name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html',
         success_url=reverse_lazy('users:password_reset_complete')
     ), 
     name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'), 
]