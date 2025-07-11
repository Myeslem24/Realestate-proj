from django.contrib import admin
from django.urls import path, include
from properties.views import home_view, we_are_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('properties/', include('properties.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('we-are/', we_are_view, name='we_are'),
    path('vehicles/', include('vehicles.urls')),  # روابط السيارات ✅
]

# مهم جداً لعرض الصور المخزنة في MEDIA_ROOT
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

