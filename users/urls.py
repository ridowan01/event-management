from django.urls import path
from . import views

urlpatterns = [
    path("log-up/", views.logup, name="logup"),
    
]