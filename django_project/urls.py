from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views
import config
from . import routing
from server import views as serverviews

admin.site.site_header = config.NAME + " - Admin"
admin.site.site_title = config.NAME + " - Admin"
admin.site.index_title = "Admin Panel"
admin.site.site_url_available = False
admin.site.login_template = 'user/login.html'
admin.site.enable_nav_sidebar = False
# Main URL patterns
urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.home, name="home"),
    path('user/', include('user.urls')),
    path('server/', include('server.urls')),
    path('channel/', include('channel.urls')),
    path('dm/', include('dm.urls')),
    path('join/<str:invite>', serverviews.join),
    path('<str:invite>', serverviews.join),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
