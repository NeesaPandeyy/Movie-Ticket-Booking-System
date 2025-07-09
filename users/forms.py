from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """A form for user registration.

    Attributes:
        username: This field requires characters between 2 and 20.
        email: This field requires a valid email address.
        password: The password box requires input.
        confirm_password:  This field must match the password field.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        help_texts = {
            "username": None,
            "password1": None,
            "password2": None,
        }

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="",
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput,
        help_text="",
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.Please choose another one")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already taken.Please choose another one")
        return email


class LoginForm(AuthenticationForm):
    pass
