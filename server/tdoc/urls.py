from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .app import urls

urlpatterns = [
    path('', include(urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
