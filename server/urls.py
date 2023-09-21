from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>', views.home),
    path('settings/<int:id>', views.settings),
    path('new', views.new),
    path('join/<str:invite>', views.join),
    path('delete/<int:server_id>', views.delete_server),
    path('discover', views.discoverView),
]