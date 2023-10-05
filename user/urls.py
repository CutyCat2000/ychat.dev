from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('login/2fa', views.user_2fa_login, name='mfa_login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('settings', views.settings, name="settings"),
    path('2fa/enable', views.enable_2fa, name="enable_2fa"),
    path('2fa/disable', views.disable_2fa, name="disable_2fa"),
]
