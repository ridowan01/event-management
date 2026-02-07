from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import RegisterForm, UserForm

User = get_user_model()

# Create your views here.
class LogupView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "users/logup.html", {"form": form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # weather email already exits or not
            email = form.cleaned_data["email"]
            email_exists = User.objects.filter(email=email).exists()

            # email not found and chekcing password correctness
            if not email_exists and form.cleaned_data["password"] == form.cleaned_data["confirm_password"]:
                user = form.save(commit=False)
                user.is_active = False # not activated
                user.set_password(form.cleaned_data["password"]) # password saved as hash
                user.save()

                participant_group = Group.objects.get(name="Participant")
                user.groups.add(participant_group)
                
                messages.success(request, "Account created successfully! Please check your email to activate your account.")
                return redirect("login")
            else:
                if email_exists:
                    messages.error(request, "Email already exists.")
                if form.cleaned_data["password"] != form.cleaned_data["confirm_password"]:
                    messages.error(request, "Passwords do not match.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return render(request, "users/logup.html", {"form": form})

class LoginView(View):
    def get(self, request):
        return render(request, "users/login.html")
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_superuser or user.groups.filter(name="Organizer").exists():
                return redirect("event-create")
            elif user.groups.filter(name="Participant").exists():
                return redirect("index")
        else:
            messages.error(request, "Invalid username or password.")
        
        return render(request, "users/login.html")


def logout(request):
    auth_logout(request)
    return redirect("home")

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully!")
            return redirect("login")
        else:
            return HttpResponse("Invalid activation link.")
    except User.DoesNotExist:
        return HttpResponse("User not found.")

class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context["email"] = user.email
        context["name"] = user.get_full_name() if user.get_full_name() else user.username
        context["bio"] = user.bio
        context["profile_image"] = user.profile_image.url if user.profile_image else "/static/users/images/profile.jpg"
        return context

class EditProfileView(LoginRequiredMixin, FormView):
    template_name = "users/edit_profile.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = UserForm(instance=user)
        
        return render(request, self.template_name, {
            'user_form': user_form,
        })
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserForm(request.POST, request.FILES, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, self.template_name, {
                'user_form': user_form,
            })
    

class ChangePasswordView(PasswordChangeView):
    template_name = "users/changepassword.html"

    def get_success_url(self):
        messages.success(self.request, "Password changed successfully!")
        return reverse_lazy("profile")

class ResetPasswordEmailView(PasswordResetView):
    template_name = "users/password_reset_email.html"
    email_template_name = "users/password_reset_email_message.html"

    def get_success_url(self):
        messages.success(self.request, 'Password reset email sent successfully! Check your inbox')
        return reverse_lazy("login")

class ResetPasswordView(PasswordResetConfirmView):
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password reset successfully!")
        return super().form_valid(form)
