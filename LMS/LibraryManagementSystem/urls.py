from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include  # Example imports

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LibraryManagementApp.urls'))
]

# Add this to serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)