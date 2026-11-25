from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm

User = get_user_model()

def _home_for(user):
    if user.is_staff:
        return reverse("dashboard:admin_dashboard")
    return reverse("dashboard:student_dashboard")


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_home_for(request.user))

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if request.POST.get("remember_me"):
            request.session.set_expiry(60 * 60 * 24 * 14)   
        else:
            request.session.set_expiry(0)                   
        return redirect(request.GET.get("next") or _home_for(user))

    return render(request, "accounts/login.html", {"form": form})

def register_view(request, role):
    if role not in ("student", "admin"):
        return redirect("accounts:login")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(role)
        if role == "admin":
            messages.success(request, "Admin account created. A superuser must activate it first.")
        else:
            messages.success(request, "Account created. You can log in now.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html", {"form": form, "role": role})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")

def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session["reset_user_id"] = form.user.pk
        return redirect("accounts:reset_password")
    return render(request, "accounts/forgot_password.html", {"form": form})


def reset_password_view(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("accounts:forgot_password")

    user = User.objects.filter(pk=user_id, is_active=True, is_staff=False).first()
    if not user:
        request.session.pop("reset_user_id", None)
        return redirect("accounts:forgot_password")

    form = ResetPasswordForm(request.POST or None, user=user)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["password1"])
        user.save()
        request.session.pop("reset_user_id", None)
        messages.success(request, "Password changed. You can log in now.")
        return redirect("accounts:login")

    return render(request, "accounts/reset_password.html", {"form": form})