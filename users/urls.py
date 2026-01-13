from django.urls import path
from . import views

urlpatterns = [
    path("log-up/", views.logup, name="logup"),
    path("log-in/", views.login, name="login"),
    path("log-out/", views.logout, name="logout"),
    path("activate/<int:user_id>/<str:token>/", views.activate_user, name="activate-user"),
]