from django.urls import path , include
from .consumers import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
print("hi")
websocket_urlpatterns = [
	path("" , ChatConsumer.as_asgi()) , 
]
