from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegisterForm

def register(request):
    if request.user.is_authenticated: return redirect("accounts:profile")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(); login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("accounts:profile")
    return render(request, "accounts/register.html", {"form":form})

def login_view(request):
    if request.user.is_authenticated: return redirect("home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user()); messages.success(request, "Login successful.")
        return redirect(request.GET.get("next") or "home")
    return render(request, "accounts/login.html", {"form":form})

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid(): form.save(); messages.success(request, "Profile updated.")
    return render(request, "accounts/profile.html", {"form":form})
