from django.urls import path
from . import views

urlpatterns = [
      path('<int:server_id>/<int:channel_id>', views.home),
      path('<str:server_id>/<int:channel_id>/latest.json', views.latestMessage),
      path('latest/<str:user_id>', views.updateMessages),
      path('fetch/<str:message_id>/message.json', views.fetchMessage),
    path('<str:server_id>/<int:channel_id>/send_message', views.sendMessage),
    path('<str:server_id>/<int:channel_id>/edit_message/<int:message_id>', views.editMessage),
    path('<str:server_id>/<int:channel_id>/delete_message/<int:message_id>', views.deleteMessage),
    path('<str:server_id>/<int:channel_id>/update_reaction/<int:message_id>/<str:reaction_type>', views.updateReaction),
]