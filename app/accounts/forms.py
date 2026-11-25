from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import Profile

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Student ID Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 024A-XXXX", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    )


class RegisterForm(forms.Form):
    id_number = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder": "e.g. 024A-XXXX"}))
    first_name = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"placeholder": "Last Name"}))
    middle_initial = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={"placeholder": "M.I"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"].strip()
        if User.objects.filter(username__iexact=id_number).exists():
            raise forms.ValidationError("This ID number is already registered.")
        return id_number

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match.")
            else:
                try:
                    validate_password(p1)
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return data

    def save(self, role):
        d = self.cleaned_data
        user = User.objects.create_user(
            username=d["id_number"],
            password=d["password1"],
            first_name=d["first_name"],
            last_name=d["last_name"],
        )
        if role == "admin":
            user.is_staff = True
            user.is_active = False   
            user.save()
        Profile.objects.create(user=user, role=role, middle_initial=d["middle_initial"])
        return user

class ForgotPasswordForm(forms.Form):
    id_number = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder": "e.g. 024A-XXXX"}))
    first_name = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"placeholder": "Last Name"}))

    def clean(self):
        data = super().clean()
        id_number = data.get("id_number")
        first = data.get("first_name")
        last = data.get("last_name")
        if id_number and first and last:
            user = User.objects.filter(
                username__iexact=id_number.strip(),
                first_name__iexact=first.strip(),
                last_name__iexact=last.strip(),
                is_active=True,
                is_staff=False,
            ).first()
            if not user:
                raise forms.ValidationError("We couldn't find a student account matching those details.")
            self.user = user
        return data


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match.")
            else:
                try:
                    validate_password(p1, self.user)
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return data