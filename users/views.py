from django.shortcuts import render
from .forms import RegisterForm

# Create your views here.
def logup(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # chekcing password correctness
            if form.cleaned_data["password"] == form.cleaned_data["confirm_password"]:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])
                user.save()
            else:
                print("Passwords do not match")
        else:
            print(form.errors)
    
    context = {
        "form": form,
    }
    return render(request, "users/logup.html", context=context)