from django.urls import path
from . import views

urlpatterns = [
    path("log-up/", views.LogupView.as_view(), name="logup"),
    path("log-in/", views.LoginView.as_view(), name="login"),
    path("log-out/", views.logout, name="logout"),
    path("activate/<int:user_id>/<str:token>/", views.activate_user, name="activate-user"),
]