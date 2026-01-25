from django.contrib import admin
from django.urls import path

urlpatterns = [
    # The default Django admin panel (http://localhost:8000/admin/)
    path('admin/', admin.site.urls),
]