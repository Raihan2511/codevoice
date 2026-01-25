# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     # The default Django admin panel (http://localhost:8000/admin/)
#     path('admin/', admin.site.urls),
# ]

from django.contrib import admin
from django.urls import path
from django.shortcuts import render

# Simple view function to render the HTML
def test_view(request):
    return render(request, 'test_room.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view),  # <--- New Route
]