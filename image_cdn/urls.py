from django.urls import path
from . import views

urlpatterns = [
    path('resize/', views.resize_image, name='resize_image'),
]
