from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('portal-control/', admin.site.urls),
    path('', include('core.urls')),
    path('events/', include('events.urls')),
    path('opportunities/', include('opportunities.urls')),
    path('articles/', include('articles.urls')),
    path('telegram/', include('telegram_bot.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('analytics/', include('analytics.urls')),
]

# Serve static and media files even when DEBUG=False for local testing
from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Admin customization
admin.site.site_header = "Nordic University Portal"
admin.site.site_title = "Nordic University Admin"
admin.site.index_title = "Welcome to Nordic University Admin Panel"
