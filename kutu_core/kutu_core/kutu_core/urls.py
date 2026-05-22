from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Matches your React Native fetch URLs (http://172.17.113.112:8000/api/...)
    path('api/', include('accounts.urls')), 
]

# This allows Django to serve media files (images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)