import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from . import routing

application = ProtocolTypeRouter({
    "http":
    get_asgi_application(),
    "websocket":
    AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
})
