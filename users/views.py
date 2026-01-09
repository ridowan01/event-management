from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

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

                return redirect("login")
            else:
                print("Email exits or Passwords do not match")
        else:
            print(form.errors)

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
                return redirect("event-create")
            else:
                print("User not found")
        else:
            print(form.errors)

    return render(request, "users/login.html", {"form": form})

def logout(request):
    auth_logout(request)
    return redirect("login")