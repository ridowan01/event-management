from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm, LoginForm

# Create your views here.
def logup(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # weather email already exits or not
            email = form.cleaned_data["email"]
            email_exists = User.objects.filter(email=email).exists()

            # email not found and chekcing password correctness
            if not email_exists and form.cleaned_data["password"] == form.cleaned_data["confirm_password"]:
                user = form.save(commit=False)
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

def login(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_superuser or user.groups.filter(name="Organizer").exists():
                    return redirect("event-create")
                elif user.groups.filter(name="Participant").exists():
                    return redirect("index")
            else:
                print("User not found")
        else:
            print(form.errors)

    return render(request, "users/login.html", {"form": form})

def logout(request):
    auth_logout(request)
    return redirect("home")