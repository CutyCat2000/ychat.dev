from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf.urls.static import static
from . import views
import config
import os
from server import views as serverviews
from pathlib import Path

handler404 = "django_project.views.redirecthome"
admin.site.site_header = config.NAME + " - Admin"
admin.site.site_title = config.NAME + " - Admin"
admin.site.index_title = "Admin Panel"
admin.site.site_url_available = False
admin.site.login_template = 'user/adminlogin.html'
admin.site.enable_nav_sidebar = False

# Main URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('user/', include('user.urls')),
    path('server/', include('server.urls')),
    path('channel/', include('channel.urls')),
    path('dm/', include('dm.urls')),
    path('join/<str:invite>', serverviews.join),
    path('<str:invite>', serverviews.join),
]
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

urlpatterns += static(settings.MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += [
    path('media/<path:path>', serve, {'document_root': MEDIA_ROOT}),
    path('static/<path:path>', serve, {'document_root': STATIC_ROOT}),
]
