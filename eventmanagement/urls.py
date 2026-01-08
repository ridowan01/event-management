from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("events.urls")), # events.urls.py connected
    path("users/", include("users.urls")), # users.urls.py connected
]