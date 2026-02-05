from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # auth
    path("log-up/", views.LogupView.as_view(), name="logup"),
    path("log-in/", views.LoginView.as_view(), name="login"),
    path("log-out/", LogoutView.as_view(next_page="home"), name="logout"),
    path("activate/<int:user_id>/<str:token>/", views.activate_user, name="activate-user"),
    # profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.EditProfileView.as_view(), name="edit-profile"),
    # password
    path("password/change/", views.ChangePasswordView.as_view(), name="change-password"),
    path("password/reset/", views.ResetPasswordEmailView.as_view(), name="reset-password"),
    path("password/reset/<uidb64>/<token>/", views.ResetPasswordView.as_view(), name="reset-password-confirm"),
]